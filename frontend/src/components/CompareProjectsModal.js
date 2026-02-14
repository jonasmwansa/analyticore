import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { GitCompare, X, Loader2, Database, Check, ExternalLink } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Checkbox } from './ui/checkbox';
import { compareAPI } from '../api';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';

export function CompareProjectsModal({ open, onOpenChange }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);
  const [projects, setProjects] = useState([]);
  const [selectedProjects, setSelectedProjects] = useState([]);

  useEffect(() => {
    if (open) {
      fetchProjects();
    }
  }, [open]);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await compareAPI.getComparableProjects();
      setProjects(response.data.projects || []);
    } catch (error) {
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const toggleProjectSelection = (projectId) => {
    if (selectedProjects.includes(projectId)) {
      setSelectedProjects(selectedProjects.filter(id => id !== projectId));
    } else if (selectedProjects.length < 4) {
      setSelectedProjects([...selectedProjects, projectId]);
    } else {
      toast.error('Maximum 4 projects can be compared');
    }
  };

  const handleCompare = () => {
    if (selectedProjects.length < 2) {
      toast.error('Select at least 2 projects');
      return;
    }
    
    // Navigate to compare page with selected projects
    const params = new URLSearchParams();
    selectedProjects.forEach(id => params.append('projects', id));
    navigate(`/compare?${params.toString()}`);
    onOpenChange(false);
  };

  const goToComparePage = () => {
    navigate('/compare');
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] bg-white">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-[#0F172A]">
            <GitCompare className="w-5 h-5 text-[#6366F1]" />
            Compare Projects
          </DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-[#6366F1] animate-spin" />
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-8">
            <Database className="w-12 h-12 text-[#94A3B8] mx-auto mb-4" />
            <p className="text-[#64748B] mb-4">No projects with data available</p>
            <p className="text-sm text-[#94A3B8]">Upload data to at least 2 projects to use comparison</p>
          </div>
        ) : (
          <>
            <p className="text-sm text-[#64748B] mb-4">
              Select 2-4 projects to compare their data quality and statistics
            </p>
            
            <div className="max-h-[300px] overflow-y-auto space-y-2">
              {projects.map((project) => (
                <Card
                  key={project.project_id}
                  className={`p-3 cursor-pointer transition-all ${
                    selectedProjects.includes(project.project_id)
                      ? 'border-[#6366F1] bg-[#EEF2FF]'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                  onClick={() => toggleProjectSelection(project.project_id)}
                  data-testid={`modal-project-${project.project_id}`}
                >
                  <div className="flex items-center gap-3">
                    <Checkbox
                      checked={selectedProjects.includes(project.project_id)}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-[#0F172A] truncate">{project.name}</p>
                      <p className="text-xs text-[#94A3B8]">
                        {project.row_count?.toLocaleString() || '?'} rows • {new Date(project.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    {selectedProjects.includes(project.project_id) && (
                      <Check className="w-5 h-5 text-[#6366F1]" />
                    )}
                  </div>
                </Card>
              ))}
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-200 mt-4">
              <Button
                variant="ghost"
                onClick={goToComparePage}
                className="text-[#64748B] hover:text-[#6366F1]"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                Open Full Page
              </Button>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => onOpenChange(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCompare}
                  disabled={selectedProjects.length < 2 || comparing}
                  className="bg-[#6366F1] hover:bg-[#4F46E5] text-white"
                  data-testid="modal-compare-btn"
                >
                  {comparing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <GitCompare className="w-4 h-4 mr-2" />
                      Compare ({selectedProjects.length})
                    </>
                  )}
                </Button>
              </div>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

export default CompareProjectsModal;
