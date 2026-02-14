from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'project_id', 'name', 'description', 'source_type', 'status',
            'original_filename', 'row_count', 'column_count', 'statistics',
            'ai_recommendations', 'applied_transformations', 'created_at',
            'updated_at', 'completed_at'
        ]
        read_only_fields = ['project_id', 'created_at', 'updated_at', 'completed_at']

class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'description', 'source_type']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)