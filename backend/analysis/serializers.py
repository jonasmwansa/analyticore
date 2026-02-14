from rest_framework import serializers
from .models import AnalysisRun, TransformationLog

class AnalysisRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisRun
        fields = ['analysis_id', 'recommendations', 'statistics', 'change_log', 'created_at']
        read_only_fields = ['analysis_id', 'created_at']

class TransformationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransformationLog
        fields = ['log_id', 'step_name', 'action', 'target', 'reason', 'impact', 'confidence', 'reversible', 'applied_at']
        read_only_fields = ['log_id', 'applied_at']