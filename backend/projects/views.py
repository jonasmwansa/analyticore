from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import ProjectSerializer, ProjectCreateSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    lookup_field = 'project_id'
    
    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreateSerializer
        return ProjectSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, project_id=None):
        project = self.get_object()
        return Response(project.statistics)
    
    @action(detail=True, methods=['get'])
    def recommendations(self, request, project_id=None):
        project = self.get_object()
        return Response(project.ai_recommendations)