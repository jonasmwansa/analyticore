from django.urls import path
from . import views
from . import ml_views
from . import magic_views

app_name = 'analysis'

urlpatterns = [
    # Analysis endpoints
    path('<uuid:project_id>/analyze', views.analyze_data, name='analyze'),
    path('<uuid:project_id>/transform', views.apply_transformations, name='transform'),
    path('<uuid:project_id>/statistics', views.get_statistics, name='statistics'),
    path('<uuid:project_id>/correlation', views.get_correlation, name='correlation'),
    path('<uuid:project_id>/distribution', views.get_distribution, name='distribution'),
    path('<uuid:project_id>/chart', views.get_chart_data, name='chart'),
    path('<uuid:project_id>/column', views.get_column_info, name='column-info'),
    path('<uuid:project_id>/columns', views.get_columns, name='columns'),
    path('<uuid:project_id>/insights', views.get_quick_insights, name='insights'),
    path('<uuid:project_id>/column-actions', views.get_column_actions, name='column-actions'),
    path('<uuid:project_id>/apply-action', views.apply_column_action, name='apply-action'),
    
    # Magic Analysis endpoints
    path('<uuid:project_id>/magic-analyze', magic_views.run_magic_analysis, name='magic-analyze'),
    path('<uuid:project_id>/magic-apply-cleaning', magic_views.apply_magic_cleaning, name='magic-apply-cleaning'),
    
    # ML endpoints
    path('<uuid:project_id>/ml/info', ml_views.get_ml_info, name='ml-info'),
    path('<uuid:project_id>/ml/train', ml_views.train_model, name='ml-train'),
    path('<uuid:project_id>/ml/models', ml_views.list_models, name='ml-models'),
    path('<uuid:project_id>/ml/predict', ml_views.predict, name='ml-predict'),
    path('<uuid:project_id>/ml/models/<str:model_id>', ml_views.delete_model, name='ml-delete'),
    path('<uuid:project_id>/ml/auto', ml_views.auto_ml, name='ml-auto'),
    
    # Clustering endpoints
    path('<uuid:project_id>/ml/cluster/optimal', ml_views.find_optimal_clusters, name='cluster-optimal'),
    path('<uuid:project_id>/ml/cluster', ml_views.run_clustering, name='cluster'),
    
    # PCA endpoint
    path('<uuid:project_id>/ml/pca', ml_views.run_pca, name='pca'),
]
