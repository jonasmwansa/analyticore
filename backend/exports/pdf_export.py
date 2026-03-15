"""
PDF Export Service - Generate professional PDF reports from analysis results
"""
import io
import os
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart


class PDFExportService:
    """Generate professional PDF reports from analysis data"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1e293b'),
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#6366f1'),
            borderColor=colors.HexColor('#6366f1'),
            borderWidth=1,
            borderPadding=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.HexColor('#334155')
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportBodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            textColor=colors.HexColor('#475569'),
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='InsightText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.HexColor('#1e40af'),
            leftIndent=20,
            bulletIndent=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#6366f1'),
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER
        ))
    
    def generate_analysis_report(self, project_name: str, results: Dict[str, Any], 
                                  llm_insights: Dict[str, str] = None) -> bytes:
        """Generate a comprehensive PDF analysis report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        elements = []
        
        # Title Page
        elements.extend(self._create_title_page(project_name))
        elements.append(PageBreak())
        
        # Executive Summary
        elements.extend(self._create_executive_summary(results, llm_insights))
        elements.append(PageBreak())
        
        # Data Quality Section
        elements.extend(self._create_data_quality_section(results))
        
        # Statistics Section
        elements.extend(self._create_statistics_section(results))
        elements.append(PageBreak())
        
        # Correlation Section
        elements.extend(self._create_correlation_section(results))
        
        # Insights Section
        elements.extend(self._create_insights_section(results, llm_insights))
        elements.append(PageBreak())
        
        # Recommendations Section
        elements.extend(self._create_recommendations_section(results))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_title_page(self, project_name: str) -> List:
        """Create the title page"""
        elements = []
        
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph("DATA ANALYSIS REPORT", self.styles['ReportTitle']))
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(project_name, self.styles['SectionHeader']))
        elements.append(Spacer(1, inch))
        
        # Report metadata
        date_str = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(f"Generated: {date_str}", self.styles['ReportBodyText']))
        elements.append(Paragraph("Powered by AnalytiCore - Local AI Analysis", self.styles['ReportBodyText']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Privacy note
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(
            "✓ No external API calls  ✓ Data never leaves your system  ✓ Full privacy",
            self.styles['ReportBodyText']
        ))
        
        return elements
    
    def _create_executive_summary(self, results: Dict, llm_insights: Dict = None) -> List:
        """Create executive summary section"""
        elements = []
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        summary = results.get('summary', {})
        
        # Key metrics table
        metrics_data = [
            ['Total Rows', 'Total Columns', 'Quality Score', 'Quality Label'],
            [
                str(summary.get('total_rows', 0)),
                str(summary.get('total_columns', 0)),
                str(summary.get('quality_score', 'N/A')),
                summary.get('quality_label', 'N/A').capitalize()
            ]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 15),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f1f5f9')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Executive summary text
        exec_summary = summary.get('executive_summary', {})
        if exec_summary.get('text'):
            elements.append(Paragraph("Overview", self.styles['SubHeader']))
            elements.append(Paragraph(exec_summary['text'], self.styles['BodyText']))
        
        # LLM-generated summary
        if llm_insights and llm_insights.get('summary'):
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("AI-Generated Analysis", self.styles['SubHeader']))
            elements.append(Paragraph(llm_insights['summary'], self.styles['BodyText']))
        
        return elements
    
    def _create_data_quality_section(self, results: Dict) -> List:
        """Create data quality section"""
        elements = []
        elements.append(Paragraph("Data Quality Assessment", self.styles['SectionHeader']))
        
        cleaning = results.get('cleaning', {})
        data_quality = cleaning.get('data_quality', {})
        
        # Quality issues summary
        issues_data = [
            ['Issue Type', 'Count', 'Severity'],
            ['Critical Issues', str(data_quality.get('critical_issues', 0)), 'High'],
            ['Warning Issues', str(data_quality.get('warning_issues', 0)), 'Medium'],
            ['Info Issues', str(data_quality.get('info_issues', 0)), 'Low'],
        ]
        
        issues_table = Table(issues_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        issues_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ]))
        elements.append(issues_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Applied cleaning actions
        applied_actions = cleaning.get('applied_actions', [])
        if applied_actions:
            elements.append(Paragraph("Applied Cleaning Actions", self.styles['SubHeader']))
            for action in applied_actions[:10]:
                action_text = f"• {action.get('column', 'N/A')}: {action.get('strategy', 'N/A')} ({action.get('values_affected', 0)} values affected)"
                elements.append(Paragraph(action_text, self.styles['InsightText']))
        
        return elements
    
    def _create_statistics_section(self, results: Dict) -> List:
        """Create statistics section"""
        elements = []
        elements.append(Paragraph("Statistical Analysis", self.styles['SectionHeader']))
        
        statistics = results.get('statistics', {})
        numeric_summary = statistics.get('numeric_summary', {})
        
        if numeric_summary:
            elements.append(Paragraph("Numeric Column Statistics", self.styles['SubHeader']))
            
            # Create statistics table
            stats_data = [['Column', 'Mean', 'Std Dev', 'Min', 'Max']]
            for col, stats in list(numeric_summary.items())[:15]:
                stats_data.append([
                    col[:20],
                    f"{stats.get('mean', 0):.2f}",
                    f"{stats.get('std', 0):.2f}",
                    f"{stats.get('min', 0):.2f}",
                    f"{stats.get('max', 0):.2f}"
                ])
            
            stats_table = Table(stats_data, colWidths=[1.8*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.1*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
            ]))
            elements.append(stats_table)
        
        return elements
    
    def _create_correlation_section(self, results: Dict) -> List:
        """Create correlation section"""
        elements = []
        elements.append(Paragraph("Correlation Analysis", self.styles['SectionHeader']))
        
        correlation = results.get('correlation', {})
        top_correlations = correlation.get('top_correlations', [])
        
        if top_correlations:
            elements.append(Paragraph("Top Correlations", self.styles['SubHeader']))
            
            corr_data = [['Variable 1', 'Variable 2', 'Correlation', 'Strength']]
            for corr in top_correlations[:10]:
                corr_data.append([
                    corr.get('column1', '')[:15],
                    corr.get('column2', '')[:15],
                    f"{corr.get('correlation', 0):.3f}",
                    corr.get('strength', 'N/A')
                ])
            
            corr_table = Table(corr_data, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 1.2*inch])
            corr_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ]))
            elements.append(corr_table)
            
            # LLM correlation insight
            llm_insight = correlation.get('llm_insight')
            if llm_insight:
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph("AI Correlation Analysis", self.styles['SubHeader']))
                elements.append(Paragraph(llm_insight, self.styles['BodyText']))
        
        return elements
    
    def _create_insights_section(self, results: Dict, llm_insights: Dict = None) -> List:
        """Create insights section"""
        elements = []
        elements.append(Paragraph("Key Insights", self.styles['SectionHeader']))
        
        insights = results.get('insights', {})
        key_insights = insights.get('key_insights', [])
        
        if key_insights:
            for insight in key_insights[:10]:
                priority_color = {
                    'high': '#dc2626',
                    'medium': '#f59e0b',
                    'low': '#3b82f6'
                }.get(insight.get('priority', 'low'), '#64748b')
                
                elements.append(Paragraph(
                    f"<font color='{priority_color}'>●</font> <b>{insight.get('title', 'Insight')}</b>",
                    self.styles['BodyText']
                ))
                elements.append(Paragraph(insight.get('message', ''), self.styles['InsightText']))
                elements.append(Spacer(1, 0.1*inch))
        
        # LLM insights
        if llm_insights:
            if llm_insights.get('executive'):
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph("AI Executive Analysis", self.styles['SubHeader']))
                elements.append(Paragraph(llm_insights['executive'], self.styles['BodyText']))
        
        return elements
    
    def _create_recommendations_section(self, results: Dict) -> List:
        """Create recommendations section"""
        elements = []
        elements.append(Paragraph("Recommendations & Next Steps", self.styles['SectionHeader']))
        
        summary = results.get('summary', {})
        next_steps = summary.get('executive_summary', {}).get('next_steps', [])
        
        if not next_steps:
            next_steps = results.get('summary', {}).get('next_steps', [])
        
        if next_steps:
            for i, step in enumerate(next_steps[:5], 1):
                if isinstance(step, dict):
                    action = step.get('action', step.get('description', ''))
                else:
                    action = str(step)
                elements.append(Paragraph(f"{i}. {action}", self.styles['BodyText']))
        
        # Visualization recommendations
        viz = results.get('visualization', {})
        suggestions = viz.get('suggested_visualizations', [])
        
        if suggestions:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Suggested Visualizations", self.styles['SubHeader']))
            for viz_rec in suggestions[:5]:
                elements.append(Paragraph(
                    f"• <b>{viz_rec.get('title', 'Chart')}</b>: {viz_rec.get('description', '')}",
                    self.styles['BodyText']
                ))
        
        return elements


# Export function
def export_analysis_to_pdf(project_name: str, results: Dict[str, Any], 
                           llm_insights: Dict[str, str] = None) -> bytes:
    """Export analysis results to PDF"""
    service = PDFExportService()
    return service.generate_analysis_report(project_name, results, llm_insights)
