from django.urls import path
from . import views

app_name = 'pipelines'

urlpatterns = [
    # Scheduled Pipelines
    path('schedules/', views.list_schedules, name='list-schedules'),
    path('schedules/create/', views.create_schedule, name='create-schedule'),
    path('schedules/stats/', views.get_schedule_stats, name='schedule-stats'),
    path('schedules/<uuid:schedule_id>/', views.get_schedule, name='get-schedule'),
    path('schedules/<uuid:schedule_id>/update/', views.update_schedule, name='update-schedule'),
    path('schedules/<uuid:schedule_id>/delete/', views.delete_schedule, name='delete-schedule'),
    path('schedules/<uuid:schedule_id>/toggle/', views.toggle_schedule, name='toggle-schedule'),
    path('schedules/<uuid:schedule_id>/run/', views.run_now, name='run-now'),
    
    # Pipeline Runs
    path('runs/', views.get_run_history, name='run-history'),
    path('runs/<uuid:run_id>/', views.get_run_details, name='run-details'),
]
