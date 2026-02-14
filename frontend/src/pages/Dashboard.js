import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Plus, FileSpreadsheet, Upload, Database, ExternalLink, Folder, GitCompare } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { projectsAPI } from '../api';
import DashboardLayout from '../components/DashboardLayout';
import CompareProjectsModal from '../components/CompareProjectsModal';

function Dashboard({ user }) {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewProject, setShowNewProject] = useState(false);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    source_type: 'file_upload'
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await projectsAPI.list();
      const projectsData = response.data.results || response.data;
      setProjects(Array.isArray(projectsData) ? projectsData : []);
    } catch (error) {
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const createProject = async () => {
    if (!newProject.name.trim()) {
      toast.error('Please enter a project name');
      return;
    }

    try {
      const response = await projectsAPI.create(newProject);
      toast.success('Project created!');
      setShowNewProject(false);
      setNewProject({ name: '', source_type: 'file_upload' });
      navigate(`/projects/${response.data.project_id}`);
    } catch (error) {
      toast.error('Failed to create project');
    }
  };

  const getSourceIcon = (sourceType) => {
    if (sourceType === 'file_upload') return <Upload className="w-5 h-5" />;
    if (sourceType === 'database') return <Database className="w-5 h-5" />;
    return <ExternalLink className="w-5 h-5" />;
  };

  const getSourceLabel = (sourceType) => {
    if (sourceType === 'file_upload') return 'File Upload';
    if (sourceType === 'database') return 'Database';
    return 'API';
  };

  const getStatusBadge = (status) => {
    const styles = {
      created: 'bg-slate-100 text-slate-700',
      uploaded: 'bg-blue-100 text-blue-700',
      analyzed: 'bg-green-100 text-green-700',
      transformed: 'bg-emerald-100 text-emerald-700'
    };
    return (
      <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${styles[status] || styles.created}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  return (
    <DashboardLayout user={user}>
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-[#0F172A] mb-1" style={{ letterSpacing: '-0.02em' }}>
              Your Projects
            </h1>
            <p className="text-[#64748B]">Create and manage your data transformation pipelines</p>
          </div>
          <div className="flex gap-3">
            <Button
              onClick={() => setShowCompareModal(true)}
              variant="outline"
              className="border-slate-200 text-[#64748B] hover:text-[#6366F1] hover:border-[#6366F1]"
              data-testid="compare-projects-btn"
            >
              <GitCompare className="w-5 h-5 mr-2" />
              Compare
            </Button>
            <Dialog open={showNewProject} onOpenChange={setShowNewProject}>
            <DialogTrigger asChild>
              <Button
                data-testid="create-project-btn"
                className="bg-[#6366F1] hover:bg-[#4F46E5] text-white rounded-lg h-11 px-6 font-semibold shadow-md shadow-indigo-500/20"
              >
                <Plus className="w-5 h-5 mr-2" />
                New Project
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-white">
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold text-[#0F172A]">Create New Project</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <Label htmlFor="project-name" className="text-[#0F172A] font-medium mb-2 block">Project Name</Label>
                  <Input
                    id="project-name"
                    placeholder="My Data Pipeline"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    data-testid="project-name-input"
                    className="h-11 bg-white border-slate-200 rounded-lg"
                  />
                </div>
                <div>
                  <Label htmlFor="source-type" className="text-[#0F172A] font-medium mb-2 block">Data Source Type</Label>
                  <Select
                    value={newProject.source_type}
                    onValueChange={(value) => setNewProject({ ...newProject, source_type: value })}
                  >
                    <SelectTrigger data-testid="source-type-select" className="h-11 bg-white border-slate-200 rounded-lg">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-white">
                      <SelectItem value="file_upload">File Upload (CSV, Excel, JSON)</SelectItem>
                      <SelectItem value="database">Database Connection</SelectItem>
                      <SelectItem value="api">API Integration</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button
                  onClick={createProject}
                  data-testid="confirm-create-project-btn"
                  className="w-full bg-[#6366F1] hover:bg-[#4F46E5] text-white rounded-lg h-11 font-semibold shadow-md shadow-indigo-500/20"
                >
                  Create Project
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="w-12 h-12 border-4 border-[#6366F1] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-[#64748B]">Loading projects...</p>
            </div>
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-20">
            <Folder className="w-20 h-20 text-[#94A3B8] mx-auto mb-4" />
            <h3 className="text-xl font-bold text-[#0F172A] mb-2">No projects yet</h3>
            <p className="text-[#64748B] mb-6">Create your first data transformation project to get started</p>
            <Button
              onClick={() => setShowNewProject(true)}
              data-testid="empty-create-project-btn"
              className="bg-[#6366F1] hover:bg-[#4F46E5] text-white rounded-lg h-11 px-6 font-semibold shadow-md shadow-indigo-500/20"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create Project
            </Button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="projects-grid">
            {projects.map((project) => (
              <div
                key={project.project_id}
                onClick={() => navigate(`/projects/${project.project_id}`)}
                data-testid={`project-card-${project.project_id}`}
                className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm cursor-pointer hover:shadow-md hover:border-indigo-200 transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 bg-[#EEF2FF] rounded-lg flex items-center justify-center">
                    {getSourceIcon(project.source_type)}
                  </div>
                  {getStatusBadge(project.status)}
                </div>
                <h3 className="text-lg font-bold text-[#0F172A] mb-2">{project.name}</h3>
                <p className="text-sm text-[#64748B] mb-4">{getSourceLabel(project.source_type)}</p>
                {project.row_count && (
                  <div className="flex gap-4 text-sm">
                    <div>
                      <span className="text-[#94A3B8]">Rows:</span>
                      <span className="ml-1 font-semibold text-[#0F172A]">{project.row_count.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-[#94A3B8]">Columns:</span>
                      <span className="ml-1 font-semibold text-[#0F172A]">{project.column_count}</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default Dashboard;
