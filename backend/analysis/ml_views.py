"""
Machine Learning API Views for AnalytiCore
Endpoints for model training, evaluation, clustering, and predictions
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import pandas as pd
import os

from projects.models import Project


def load_project_dataframe(project):
    """Helper to load project data into a DataFrame"""
    file_path = project.processed_file_path or project.file_path
    
    if not file_path or not os.path.exists(file_path):
        return None
    
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file_path)
    elif file_path.endswith('.json'):
        return pd.read_json(file_path)
    return None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ml_info(request, project_id):
    """Get ML-ready information about the dataset"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    import numpy as np
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Determine potential targets
    potential_regression_targets = []
    potential_classification_targets = []
    
    for col in numeric_cols:
        unique_ratio = df[col].nunique() / len(df)
        if unique_ratio > 0.1:  # More than 10% unique values
            potential_regression_targets.append(col)
        if df[col].nunique() <= 10:  # 10 or fewer unique values
            potential_classification_targets.append(col)
    
    for col in categorical_cols:
        if df[col].nunique() <= 20:  # 20 or fewer unique categories
            potential_classification_targets.append(col)
    
    return Response({
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': numeric_cols,
        'categorical_columns': categorical_cols,
        'potential_regression_targets': potential_regression_targets,
        'potential_classification_targets': potential_classification_targets,
        'available_algorithms': {
            'regression': [
                {'id': 'linear_regression', 'name': 'Linear Regression', 'description': 'Simple linear model'},
                {'id': 'ridge', 'name': 'Ridge Regression', 'description': 'L2 regularized linear model'},
                {'id': 'lasso', 'name': 'Lasso Regression', 'description': 'L1 regularized linear model'},
                {'id': 'random_forest_regressor', 'name': 'Random Forest', 'description': 'Ensemble of decision trees'},
                {'id': 'gradient_boosting_regressor', 'name': 'Gradient Boosting', 'description': 'Boosted decision trees'}
            ],
            'classification': [
                {'id': 'logistic_regression', 'name': 'Logistic Regression', 'description': 'Linear classification model'},
                {'id': 'random_forest_classifier', 'name': 'Random Forest', 'description': 'Ensemble of decision trees'},
                {'id': 'gradient_boosting_classifier', 'name': 'Gradient Boosting', 'description': 'Boosted decision trees'},
                {'id': 'knn', 'name': 'K-Nearest Neighbors', 'description': 'Instance-based learning'},
                {'id': 'decision_tree', 'name': 'Decision Tree', 'description': 'Single decision tree'}
            ]
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def train_model(request, project_id):
    """Train a machine learning model"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    model_type = request.data.get('model_type')  # regression or classification
    algorithm = request.data.get('algorithm')
    target_col = request.data.get('target')
    feature_cols = request.data.get('features')  # Optional, uses all numeric if not specified
    test_size = request.data.get('test_size', 0.2)
    
    if not model_type or not algorithm or not target_col:
        return Response(
            {'detail': 'model_type, algorithm, and target are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if target_col not in df.columns:
        return Response({'detail': f'Target column {target_col} not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from .ml_service import MLService
        
        ml_service = MLService(df, str(project_id), settings.PIPELINE_STORAGE_PATH)
        result = ml_service.train_model(
            model_type=model_type,
            algorithm=algorithm,
            target_col=target_col,
            feature_cols=feature_cols,
            test_size=test_size
        )
        
        return Response(result)
    except Exception as e:
        return Response({'detail': f'Training failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_models(request, project_id):
    """List all trained models for a project"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'models': []})
    
    try:
        from .ml_service import MLService
        
        ml_service = MLService(df, str(project_id), settings.PIPELINE_STORAGE_PATH)
        models = ml_service.list_models()
        
        return Response({'models': models})
    except Exception as e:
        return Response({'detail': f'Failed to list models: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict(request, project_id):
    """Make predictions using a trained model"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    model_id = request.data.get('model_id')
    if not model_id:
        return Response({'detail': 'model_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from .ml_service import MLService
        
        ml_service = MLService(df, str(project_id), settings.PIPELINE_STORAGE_PATH)
        result = ml_service.predict(model_id)
        
        return Response(result)
    except Exception as e:
        return Response({'detail': f'Prediction failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_model(request, project_id, model_id):
    """Delete a trained model"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from .ml_service import MLService
        
        ml_service = MLService(df, str(project_id), settings.PIPELINE_STORAGE_PATH)
        success = ml_service.delete_model(model_id)
        
        if success:
            return Response({'message': 'Model deleted successfully'})
        else:
            return Response({'detail': 'Model not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': f'Delete failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def find_optimal_clusters(request, project_id):
    """Find optimal number of clusters using elbow method"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    feature_cols = request.query_params.getlist('features')
    max_k = int(request.query_params.get('max_k', 10))
    
    try:
        from .ml_service import ClusteringService
        
        clustering_service = ClusteringService(df)
        result = clustering_service.find_optimal_k(
            feature_cols=feature_cols if feature_cols else None,
            max_k=max_k
        )
        
        return Response(result)
    except Exception as e:
        return Response({'detail': f'Analysis failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_clustering(request, project_id):
    """Run clustering analysis"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    algorithm = request.data.get('algorithm', 'kmeans')
    n_clusters = request.data.get('n_clusters', 3)
    feature_cols = request.data.get('features')
    eps = request.data.get('eps', 0.5)
    min_samples = request.data.get('min_samples', 5)
    
    try:
        from .ml_service import ClusteringService
        
        clustering_service = ClusteringService(df)
        
        if algorithm == 'kmeans':
            result = clustering_service.run_kmeans(
                n_clusters=n_clusters,
                feature_cols=feature_cols
            )
        elif algorithm == 'dbscan':
            result = clustering_service.run_dbscan(
                eps=eps,
                min_samples=min_samples,
                feature_cols=feature_cols
            )
        else:
            return Response({'detail': f'Unknown algorithm: {algorithm}'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result)
    except Exception as e:
        return Response({'detail': f'Clustering failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def run_pca(request, project_id):
    """Run PCA analysis"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    n_components = request.query_params.get('n_components')
    feature_cols = request.query_params.getlist('features')
    
    try:
        from .ml_service import PCAService
        
        pca_service = PCAService(df)
        result = pca_service.run_pca(
            n_components=int(n_components) if n_components else None,
            feature_cols=feature_cols if feature_cols else None
        )
        
        return Response(result)
    except Exception as e:
        return Response({'detail': f'PCA failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_ml(request, project_id):
    """Run Auto-ML to find the best model"""
    try:
        project = Project.objects.get(project_id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    df = load_project_dataframe(project)
    if df is None:
        return Response({'detail': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    model_type = request.data.get('model_type')  # regression or classification
    target_col = request.data.get('target')
    feature_cols = request.data.get('features')
    
    if not model_type or not target_col:
        return Response(
            {'detail': 'model_type and target are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from .ml_service import MLService
        
        ml_service = MLService(df, str(project_id), settings.PIPELINE_STORAGE_PATH)
        
        # Algorithms to try
        if model_type == 'regression':
            algorithms = ['linear_regression', 'ridge', 'random_forest_regressor', 'gradient_boosting_regressor']
            score_key = 'r2_score'
        else:
            algorithms = ['logistic_regression', 'random_forest_classifier', 'gradient_boosting_classifier', 'knn']
            score_key = 'accuracy'
        
        results = []
        best_result = None
        best_score = -float('inf')
        
        for algo in algorithms:
            try:
                result = ml_service.train_model(
                    model_type=model_type,
                    algorithm=algo,
                    target_col=target_col,
                    feature_cols=feature_cols
                )
                
                score = result['metrics'].get(score_key, 0)
                results.append({
                    'algorithm': algo,
                    'model_id': result['model_id'],
                    'score': score,
                    'metrics': result['metrics']
                })
                
                if score > best_score:
                    best_score = score
                    best_result = result
            except Exception as e:
                results.append({
                    'algorithm': algo,
                    'error': str(e)
                })
        
        return Response({
            'model_type': model_type,
            'target': target_col,
            'best_model': best_result,
            'all_results': results,
            'comparison_metric': score_key
        })
    except Exception as e:
        return Response({'detail': f'Auto-ML failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
