import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, ArrowLeft } from 'lucide-react';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';

export function ProjectHeader({ project, exporting, onExport }) {
  const navigate = useNavigate();
  
  return (
    <nav className="bg-white border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/dashboard')}
            data-testid="back-to-dashboard-btn"
            className="text-slate-700 hover:text-[#6366F1]"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back
          </Button>
          <div className="h-8 w-px bg-slate-200"></div>
          <div className="flex items-center gap-2">
            <Database className="w-6 h-6 text-[#6366F1]" />
            <span className="text-xl font-bold text-[#0F172A]">{project?.name}</span>
          </div>
        </div>
        
        {project?.file_path && (
          <div className="flex items-center gap-2">
            <Select onValueChange={onExport} disabled={exporting}>
              <SelectTrigger className="w-40 bg-white" data-testid="export-select">
                <SelectValue placeholder={exporting ? "Exporting..." : "Export Data"} />
              </SelectTrigger>
              <SelectContent className="bg-white">
                <SelectItem value="csv">Export CSV</SelectItem>
                <SelectItem value="xlsx">Export Excel</SelectItem>
                <SelectItem value="json">Export JSON</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}
      </div>
    </nav>
  );
}

export default ProjectHeader;
