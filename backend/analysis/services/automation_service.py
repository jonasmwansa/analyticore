import os

import numpy as np
import pandas as pd
from django.utils import timezone

from analysis.insights import generate_cleaning_recommendations_without_ai
from analysis.magic_analysis_service import run_magic_analysis
from analysis.models import AnalysisRun, TransformationLog
from analysis.statistics import StatisticalAnalyzer
from pipelines.base import Pipeline
from pipelines.context import PipelineContext
from pipelines.steps import ColumnUnderstandingStep

from .transformation_service import TransformationService


def _convert_to_serializable(obj):
    if isinstance(obj, dict):
        return {key: _convert_to_serializable(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_convert_to_serializable(value) for value in obj]
    if isinstance(obj, tuple):
        return [_convert_to_serializable(value) for value in obj]
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj) if not np.isnan(obj) else None
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.bool_):
        return bool(obj)
    if pd.isna(obj):
        return None
    return obj


def _build_project_statistics(df, metadata=None, automation=None):
    sample_data = []
    for _, row in df.head(5).iterrows():
        record = {}
        for column in df.columns:
            record[column] = _convert_to_serializable(row[column])
        sample_data.append(record)

    statistics = {
        'total_rows': int(len(df)),
        'total_columns': int(len(df.columns)),
        'columns': df.columns.tolist(),
        'data_types': {column: str(dtype) for column, dtype in df.dtypes.items()},
        'missing_values': {column: int(value) for column, value in df.isnull().sum().items()},
        'sample_data': sample_data,
    }

    if metadata:
        statistics['column_metadata'] = {
            name: _convert_to_serializable({
                'inferred_type': column_metadata.inferred_type,
                'confidence': column_metadata.confidence,
                'missing_percentage': column_metadata.missing_percentage,
                'unique_count': column_metadata.unique_count,
                'is_identifier': column_metadata.is_identifier,
                'statistics': column_metadata.statistics,
            })
            for name, column_metadata in metadata.items()
        }

    if automation:
        statistics['automation'] = _convert_to_serializable(automation)

    return _convert_to_serializable(statistics)


def _profile_dataframe(df, project_id):
    context = PipelineContext(
        project_id=str(project_id),
        original_df=df.copy(),
        current_df=df.copy(),
    )
    pipeline = Pipeline("Automated Profiling")
    pipeline.add_step(ColumnUnderstandingStep())
    return pipeline.execute(context)


def _stage_record(key, label, started_at, completed_at, summary, details=None, status='completed'):
    return {
        'key': key,
        'label': label,
        'status': status,
        'started_at': started_at.isoformat(),
        'completed_at': completed_at.isoformat(),
        'duration_seconds': round((completed_at - started_at).total_seconds(), 3),
        'summary': summary,
        'details': _convert_to_serializable(details or {}),
    }


def _recommended_actions_from_magic(analysis_result):
    suggestions = analysis_result.get('cleaning_suggestions', [])
    actions = []

    for suggestion in suggestions:
        options = suggestion.get('options', [])
        selected = next((option for option in options if option.get('recommended')), None)
        if not selected and options:
            selected = options[0]

        strategy = (selected or {}).get('strategy')
        if not strategy or strategy in {'keep_as_string'}:
            continue

        actions.append({
            'column': suggestion.get('column'),
            'issue': suggestion.get('issue'),
            'strategy': strategy,
            'value': (selected or {}).get('value'),
        })

    return actions


def _handle_missing_values(df, column, strategy, value=None):
    if column not in df.columns:
        return df, {'column': column, 'status': 'skipped', 'message': 'Column not found'}

    original_missing = int(df[column].isnull().sum())

    if strategy == 'mean':
        df[column] = df[column].fillna(df[column].mean())
    elif strategy == 'median':
        df[column] = df[column].fillna(df[column].median())
    elif strategy == 'mode':
        mode = df[column].mode()
        if len(mode) > 0:
            df[column] = df[column].fillna(mode.iloc[0])
    elif strategy == 'forward_fill':
        df[column] = df[column].fillna(method='ffill')
    elif strategy == 'backward_fill':
        df[column] = df[column].fillna(method='bfill')
    elif strategy == 'constant':
        df[column] = df[column].fillna(value if value is not None else 0)
    elif strategy == 'drop_rows':
        df = df.dropna(subset=[column])

    remaining_missing = int(df[column].isnull().sum()) if column in df.columns else 0

    return df, {
        'column': column,
        'issue': 'missing_values',
        'strategy': strategy,
        'values_filled': int(original_missing - remaining_missing),
        'rows_after': int(len(df)),
    }


def _handle_duplicates(df, strategy):
    rows_before = len(df)

    if strategy == 'remove_duplicates':
        df = df.drop_duplicates()
    elif strategy == 'keep_first':
        df = df.drop_duplicates(keep='first')
    elif strategy == 'keep_last':
        df = df.drop_duplicates(keep='last')

    return df, {
        'column': '__all__',
        'issue': 'duplicates',
        'strategy': strategy,
        'rows_removed': int(rows_before - len(df)),
    }


def _handle_type_conversion(df, column, strategy):
    if column not in df.columns:
        return df, {'column': column, 'status': 'skipped', 'message': 'Column not found'}

    original_dtype = str(df[column].dtype)

    if strategy == 'to_numeric':
        df[column] = pd.to_numeric(df[column], errors='coerce')
    elif strategy == 'to_datetime':
        df[column] = pd.to_datetime(df[column], errors='coerce')
    elif strategy == 'to_string':
        df[column] = df[column].astype(str)
    elif strategy == 'to_category':
        df[column] = df[column].astype('category')

    return df, {
        'column': column,
        'issue': 'type_conversion',
        'strategy': strategy,
        'original_dtype': original_dtype,
        'new_dtype': str(df[column].dtype),
    }


def _handle_text_normalization(df, column, strategy):
    if column not in df.columns:
        return df, {'column': column, 'status': 'skipped', 'message': 'Column not found'}

    if strategy == 'trim':
        df[column] = df[column].astype(str).str.strip()
    elif strategy == 'lowercase':
        df[column] = df[column].astype(str).str.lower()
    elif strategy == 'uppercase':
        df[column] = df[column].astype(str).str.upper()
    elif strategy == 'remove_special':
        df[column] = df[column].astype(str).str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)

    return df, {
        'column': column,
        'issue': 'text_normalization',
        'strategy': strategy,
    }


def _handle_outliers(df, column, strategy):
    if column not in df.columns:
        return df, {'column': column, 'status': 'skipped', 'message': 'Column not found'}

    clean_series = df[column].dropna()
    if clean_series.empty:
        return df, {
            'column': column,
            'issue': 'outliers',
            'strategy': strategy,
            'rows_affected': 0,
        }

    q1 = clean_series.quantile(0.25)
    q3 = clean_series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    rows_before = len(df)

    if strategy == 'remove':
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    elif strategy == 'cap':
        df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)

    return df, {
        'column': column,
        'issue': 'outliers',
        'strategy': strategy,
        'rows_affected': int(rows_before - len(df)),
        'lower_bound': _convert_to_serializable(lower_bound),
        'upper_bound': _convert_to_serializable(upper_bound),
    }


def _apply_automation_actions(df, actions):
    working_df = df.copy()
    changes = []

    for action in actions:
        issue = action.get('issue')
        column = action.get('column')
        strategy = action.get('strategy')
        value = action.get('value')

        if issue == 'missing_values':
            working_df, change = _handle_missing_values(working_df, column, strategy, value)
        elif issue == 'duplicates':
            working_df, change = _handle_duplicates(working_df, strategy)
        elif issue == 'type_conversion':
            working_df, change = _handle_type_conversion(working_df, column, strategy)
        elif issue == 'text_normalization':
            working_df, change = _handle_text_normalization(working_df, column, strategy)
        elif issue == 'outliers':
            working_df, change = _handle_outliers(working_df, column, strategy)
        else:
            change = {
                'column': column,
                'issue': issue,
                'strategy': strategy,
                'status': 'skipped',
                'message': 'Unsupported automation action',
            }

        changes.append(_convert_to_serializable(change))

    return working_df, changes


def _percent(part, total):
    if not total:
        return 0
    return round((part / total) * 100, 2)


def _markdown_bullets(items):
    return '\n'.join(f"› {item}" for item in items if item)


def _top_missing_columns(df):
    missing = []
    for column, count in df.isnull().sum().items():
        if count > 0:
            missing.append((column, int(count), _percent(int(count), len(df))))
    missing.sort(key=lambda item: item[1], reverse=True)
    return missing[:5]


def _build_cleaning_report(df, initial_magic, applied_actions):
    quality = initial_magic.get('data_quality', {})
    missing_columns = _top_missing_columns(df)
    duplicates = int(df.duplicated().sum())
    issue_lines = []

    if missing_columns:
        issue_lines.extend(
            f"`{column}` has {count:,} missing values ({pct:.1f}%)."
            for column, count, pct in missing_columns
        )
    else:
        issue_lines.append('No missing-value hotspots were detected in the uploaded dataset.')

    if duplicates:
        issue_lines.append(f'{duplicates:,} duplicate rows were detected before automated cleaning.')
    else:
        issue_lines.append('No duplicate-row pressure was detected in the source data.')

    issue_lines.append(
        f"The quality scan surfaced {quality.get('total_issues', 0)} notable issues across completeness, consistency, and outlier behavior."
    )

    action_lines = []
    for action in applied_actions[:8]:
        column = action.get('column')
        strategy = action.get('strategy', 'default')
        issue = action.get('issue', 'cleaning')
        if column == '__all__':
            action_lines.append(f"Applied `{strategy}` for dataset-level `{issue}` remediation.")
        else:
            action_lines.append(f"Applied `{strategy}` on `{column}` to address `{issue}`.")
    if not action_lines:
        action_lines.append('The engine reviewed cleaning options but did not need to modify the dataset automatically.')

    return '\n\n'.join([
        '# Data Cleaning Assessment',
        '## Quality Snapshot',
        _markdown_bullets(issue_lines),
        '## Actions Applied',
        _markdown_bullets(action_lines),
        '## Operational Note',
        (
            'Automated cleaning favors reversible, analysis-safe updates first so the team can inspect the results '
            'before deeper feature engineering or business-rule transformations.'
        ),
    ])


def _build_transformation_report(df, recommendations, applied_actions):
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

    transformation_lines = []
    if applied_actions:
        transformation_lines.extend(
            f"`{action.get('column', '__all__')}` moved through `{action.get('strategy', 'default')}` handling."
            for action in applied_actions[:6]
        )
    else:
        transformation_lines.append('No irreversible transformations were auto-applied during this run.')

    opportunity_lines = []
    if numeric_columns:
        opportunity_lines.append(
            f"Standardization or normalization can be considered for numeric drivers such as {', '.join(numeric_columns[:4])}."
        )
    if categorical_columns:
        opportunity_lines.append(
            f"Encoding or grouping should be evaluated for categorical fields like {', '.join(categorical_columns[:4])}."
        )

    rename_recommendations = [rec for rec in recommendations if rec.get('action_type') == 'rename_column']
    if rename_recommendations:
        opportunity_lines.append(
            f"{len(rename_recommendations)} column naming cleanups were identified for downstream modeling and dashboard clarity."
        )

    if not opportunity_lines:
        opportunity_lines.append('The current structure is already analysis-ready with minimal transformation overhead.')

    return '\n\n'.join([
        '# Transformation Strategy',
        '## Current Transformation State',
        _markdown_bullets(transformation_lines),
        '## Feature Engineering Opportunities',
        _markdown_bullets(opportunity_lines),
        '## Delivery Guidance',
        (
            'Transformation remains intentionally transparent: every automated adjustment is recorded so analysts can '
            'review, extend, or roll back the pipeline without losing provenance.'
        ),
    ])


def _build_analysis_report(statistics, correlation, final_magic):
    summary = statistics.get('summary', {})
    insights = final_magic.get('key_insights', [])
    top_correlations = correlation.get('top_correlations', []) if correlation else []

    finding_lines = [
        f"The processed dataset contains {summary.get('total_rows', 0):,} rows and {summary.get('total_columns', 0)} columns after automation.",
        f"{summary.get('numeric_columns', 0)} numeric columns and {summary.get('categorical_columns', 0)} categorical columns are available for statistical interpretation.",
    ]

    if top_correlations:
        strongest = top_correlations[0]
        finding_lines.append(
            f"The strongest measured relationship is between `{strongest['column1']}` and `{strongest['column2']}` with correlation {strongest['correlation']:.2f}."
        )

    insight_lines = [
        insight.get('message')
        for insight in insights[:5]
        if insight.get('message')
    ]
    if not insight_lines:
        insight_lines.append('The analysis completed without flagging unusually strong anomalies or concentration risk.')

    return '\n\n'.join([
        '# Statistical Analysis',
        '## Analytical Readout',
        _markdown_bullets(finding_lines),
        '## Priority Insights',
        _markdown_bullets(insight_lines),
        '## Confidence Signal',
        (
            'These findings are generated from the observed distributions, variance structure, and correlation behavior '
            'present in the dataset rather than a fixed canned summary.'
        ),
    ])


def _build_visualization_report(final_magic):
    suggestions = final_magic.get('suggested_visualizations', [])
    visualization_lines = []

    for suggestion in suggestions[:6]:
        columns = ', '.join(suggestion.get('columns', [])[:4])
        visualization_lines.append(
            f"{suggestion.get('title')}: use a `{suggestion.get('type')}` view on {columns or 'the primary fields'} to reveal {suggestion.get('description', 'key movement in the data')}."
        )

    if not visualization_lines:
        visualization_lines.append('No high-priority visualizations were generated for this dataset shape.')

    return '\n\n'.join([
        '# Visualization Recommendations',
        '## Suggested Views',
        _markdown_bullets(visualization_lines),
        '## Executive Delivery Angle',
        (
            'These chart recommendations are chosen to support quick interpretation in dashboards, board packs, and '
            'operational reviews rather than exploratory visuals alone.'
        ),
    ])


def _build_summary_report(project_name, statistics, final_magic, correlation, recommendations):
    summary = statistics.get('summary', {})
    quality = final_magic.get('data_quality', {})
    executive = final_magic.get('executive_summary', {})
    top_correlations = correlation.get('top_correlations', []) if correlation else []

    overview = (
        f'This analysis of "{project_name}" covers {summary.get("total_rows", 0):,} records across '
        f'{summary.get("total_columns", 0)} fields, with {summary.get("numeric_columns", 0)} numeric dimensions '
        f'and {summary.get("categorical_columns", 0)} categorical dimensions available for operational and strategic review. '
        f'The dataset quality score is {executive.get("quality_score", 0)}/100, providing a '
        f'{executive.get("quality_label", "measured")} confidence baseline for decision-making.'
    )

    key_findings = []
    if quality.get('total_issues', 0) == 0:
        key_findings.append('The processed dataset is operating with no material data quality issues after automation.')
    else:
        key_findings.append(
            f"{quality.get('total_issues', 0)} quality signals remain visible, with {quality.get('critical_issues', 0)} critical items requiring attention."
        )
    if top_correlations:
        strongest = top_correlations[0]
        key_findings.append(
            f"Correlation analysis highlights `{strongest['column1']}` and `{strongest['column2']}` as the strongest paired signal at {strongest['correlation']:.2f}."
        )
    key_findings.append(
        f"The dataset retains full analytical breadth across {summary.get('total_columns', 0)} tracked variables, supporting multi-factor reporting and performance segmentation."
    )
    if summary.get('total_missing', 0) == 0:
        key_findings.append('No missing values remain in the current processed dataset, which materially improves model and reporting stability.')
    else:
        key_findings.append(
            f"{summary.get('total_missing', 0):,} missing values remain and should be considered in downstream forecasting assumptions."
        )

    quality_assessment = (
        f"Data quality is currently rated {executive.get('quality_label', 'measured')}, with "
        f"{quality.get('warning_issues', 0)} warnings and {quality.get('info_issues', 0)} informational observations still visible. "
        'The pipeline has already applied automated remediation where it was safe to do so, and the remaining interpretation should be treated as auditable and reviewable.'
    )

    next_steps = [
        step.get('description') or step.get('action')
        for step in final_magic.get('next_steps', [])[:3]
    ]
    if not next_steps:
        next_steps = [
            rec.get('recommendation') or rec.get('action')
            for rec in recommendations[:3]
        ]

    confidence = (
        f"Confidence in this report is anchored by {summary.get('total_rows', 0):,} observations and a quality score of "
        f"{executive.get('quality_score', 0)}/100. Standard limitations still apply: external market conditions, "
        'unobserved business variables, and future structural shifts are not captured inside the uploaded dataset alone.'
    )

    return '\n\n'.join([
        f'# Executive Summary: {project_name}',
        '## Dataset Overview',
        overview,
        '## Key Findings',
        _markdown_bullets(key_findings[:5]),
        '## Data Quality Assessment',
        quality_assessment,
        '## Recommended Next Steps',
        _markdown_bullets(next_steps[:3]),
        '## Confidence & Limitations',
        confidence,
    ])


class AutomatedAnalysisService:
    @classmethod
    def run(cls, project, df, actor=None, auto_apply_cleaning=True, source='manual'):
        pipeline_started_at = timezone.now()
        original_df = df.copy()

        profile_context = _profile_dataframe(original_df, project.project_id)
        initial_statistics = _build_project_statistics(original_df, metadata=profile_context.metadata)

        cleaned_df = original_df.copy()
        applied_actions = []
        cleaned_output_path = project.processed_file_path
        backup_path = None

        cleaning_started_at = timezone.now()
        recommendations = generate_cleaning_recommendations_without_ai(original_df)
        initial_magic = run_magic_analysis(original_df, project.name)
        if auto_apply_cleaning:
            recommended_actions = _recommended_actions_from_magic(initial_magic)
            if recommended_actions:
                cleaned_df, applied_actions = _apply_automation_actions(original_df, recommended_actions)
                cleaned_output_path, backup_path = TransformationService.save_processed_data(cleaned_df, project.project_id)
                project.processed_file_path = cleaned_output_path

                for applied_action in applied_actions:
                    TransformationLog.objects.create(
                        project=project,
                        step_name='Automated Pipeline',
                        action=applied_action.get('issue', 'automation'),
                        target=applied_action.get('column', '__all__'),
                        reason=f"Automatically applied {applied_action.get('strategy', 'default')} strategy",
                        impact=applied_action,
                        confidence=0.9,
                    )

                existing_history = project.applied_transformations or []
                existing_history.append(_convert_to_serializable({
                    'type': 'automation',
                    'stage': 'auto_cleaning',
                    'timestamp': timezone.now().isoformat(),
                    'user': getattr(actor, 'email', 'system') if actor else 'system',
                    'source': source,
                    'actions': applied_actions,
                    'backup_path': backup_path,
                    'original_shape': list(original_df.shape),
                    'new_shape': list(cleaned_df.shape),
                    'processed_file_path': cleaned_output_path,
                }))
                project.applied_transformations = existing_history

                cleaning_summary = (
                    f"Automatically applied {len(applied_actions)} cleaning actions. "
                    f"Rows changed from {len(original_df):,} to {len(cleaned_df):,}."
                )
                cleaning_details = {
                    'auto_apply_cleaning': True,
                    'actions_applied': applied_actions,
                    'processed_file_path': cleaned_output_path,
                    'backup_path': backup_path,
                }
            else:
                cleaning_summary = 'No recommended cleaning actions needed. Dataset moved directly to summary.'
                cleaning_details = {
                    'auto_apply_cleaning': True,
                    'actions_applied': [],
                }
        else:
            cleaning_summary = 'Automatic cleaning skipped. Recommendations are available for review.'
            cleaning_details = {
                'auto_apply_cleaning': False,
                'actions_applied': [],
            }
        cleaning_completed_at = timezone.now()

        transformation_started_at = timezone.now()
        cleaned_statistics = StatisticalAnalyzer(cleaned_df).get_descriptive_statistics()
        transformation_completed_at = timezone.now()

        analysis_started_at = timezone.now()
        correlation = StatisticalAnalyzer(cleaned_df).get_correlation_matrix()
        final_profile_context = _profile_dataframe(cleaned_df, project.project_id)
        final_magic = run_magic_analysis(cleaned_df, project.name)
        analysis_completed_at = timezone.now()

        visualization_started_at = timezone.now()
        visualization_report = _build_visualization_report(final_magic)
        visualization_completed_at = timezone.now()

        summary_started_at = timezone.now()
        summary_report = _build_summary_report(project.name, cleaned_statistics, final_magic, correlation, recommendations)
        summary_completed_at = timezone.now()

        stages = [
            _stage_record(
                'cleaning',
                'Data Cleaning',
                cleaning_started_at,
                cleaning_completed_at,
                cleaning_summary,
                {
                    **cleaning_details,
                    'content': _build_cleaning_report(original_df, initial_magic, applied_actions),
                },
            ),
            _stage_record(
                'transformation',
                'Transformation',
                transformation_started_at,
                transformation_completed_at,
                'Prepared the dataset structure for downstream analysis and feature work.',
                {
                    'content': _build_transformation_report(cleaned_df, recommendations, applied_actions),
                    'recommendation_count': len(recommendations),
                },
            ),
            _stage_record(
                'analysis',
                'Statistical Analysis',
                analysis_started_at,
                analysis_completed_at,
                'Computed descriptive statistics, distribution signals, and correlation patterns.',
                {
                    'content': _build_analysis_report(cleaned_statistics, correlation, final_magic),
                    'top_correlations': correlation.get('top_correlations', [])[:5],
                },
            ),
            _stage_record(
                'visualization',
                'Visualizations',
                visualization_started_at,
                visualization_completed_at,
                'Generated chart recommendations suited for executive review and exploration.',
                {
                    'content': visualization_report,
                    'suggestions': final_magic.get('suggested_visualizations', []),
                },
            ),
            _stage_record(
                'summary',
                'Executive Summary',
                summary_started_at,
                summary_completed_at,
                final_magic.get('executive_summary', {}).get('text', 'Executive summary generated.'),
                {
                    'content': summary_report,
                    'quality_score': final_magic.get('executive_summary', {}).get('quality_score'),
                    'quality_label': final_magic.get('executive_summary', {}).get('quality_label'),
                },
            ),
        ]

        quality_before = initial_magic.get('executive_summary', {}).get('quality_score')
        quality_after = final_magic.get('executive_summary', {}).get('quality_score')
        pipeline_completed_at = timezone.now()

        automation = {
            'status': 'completed',
            'source': source,
            'auto_apply_cleaning': auto_apply_cleaning,
            'started_at': pipeline_started_at.isoformat(),
            'completed_at': pipeline_completed_at.isoformat(),
            'duration_seconds': round((pipeline_completed_at - pipeline_started_at).total_seconds(), 3),
            'stages': stages,
            'initial_summary': initial_magic.get('executive_summary', {}),
            'final_summary': {
                **final_magic.get('executive_summary', {}),
                'report_markdown': summary_report,
            },
            'quality_score_before': quality_before,
            'quality_score_after': quality_after,
            'quality_score_delta': None if quality_before is None or quality_after is None else quality_after - quality_before,
            'rows_before': int(len(original_df)),
            'rows_after': int(len(cleaned_df)),
            'actions_applied': applied_actions,
            'processed_file_path': cleaned_output_path if cleaned_output_path and os.path.exists(cleaned_output_path) else '',
            'report_title': f'Executive Summary: {project.name}',
        }

        final_statistics = _build_project_statistics(cleaned_df, metadata=final_profile_context.metadata, automation=automation)
        final_statistics['original_profile'] = {
            'rows': int(len(original_df)),
            'columns': int(len(original_df.columns)),
            'missing_values': initial_statistics.get('missing_values', {}),
        }

        AnalysisRun.objects.create(
            project=project,
            recommendations=recommendations,
            statistics={
                'initial_summary': initial_magic.get('executive_summary', {}),
                'final_summary': automation['final_summary'],
                'automation': automation,
            },
            change_log=stages,
        )

        project.statistics = final_statistics
        project.ai_recommendations = recommendations
        project.row_count = len(cleaned_df)
        project.column_count = len(cleaned_df.columns)
        project.status = 'completed'
        project.completed_at = pipeline_completed_at
        project.save()

        return {
            'statistics': final_statistics,
            'recommendations': recommendations,
            'automation': automation,
        }
