from django.urls import path
from . import views
from . import enhanced_views

app_name = 'exports'

urlpatterns = [
    path('<uuid:project_id>/export', views.export_data, name='export-data'),
    path('<uuid:project_id>/charts', views.generate_charts, name='generate-charts'),
    
    # Enhanced Export Endpoints
    path('<uuid:project_id>/export-statistics', enhanced_views.export_summary_statistics, name='export-statistics'),
    path('<uuid:project_id>/export-correlation', enhanced_views.export_correlation_matrix, name='export-correlation'),
    path('<uuid:project_id>/export-distribution', enhanced_views.export_distribution_analysis, name='export-distribution'),
    path('<uuid:project_id>/export-visualization', enhanced_views.export_visualization, name='export-visualization'),
    
    # PDF Export
    path('<uuid:project_id>/export-pdf', enhanced_views.export_pdf_report, name='export-pdf'),
    
    # Pipeline Results Export
    path('pipeline/<uuid:pipeline_id>/export-pdf', enhanced_views.export_pipeline_pdf, name='export-pipeline-pdf'),
    path('pipeline/<uuid:pipeline_id>/export-excel', enhanced_views.export_pipeline_excel, name='export-pipeline-excel'),
]