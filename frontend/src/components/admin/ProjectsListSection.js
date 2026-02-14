import React from 'react';
import { Card } from '../ui/card';

export function ProjectsListSection({ projects }) {
  return (
    <div className="space-y-6" data-testid="projects-list-section">
      <h2 className="text-xl font-bold text-white">All Projects ({projects.length})</h2>
      
      <Card className="bg-slate-800 border-slate-700 p-6">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Project</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">User</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Source</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Status</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Rows</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Created</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((project, idx) => (
                <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-3 px-4 text-sm font-medium text-white">{project.name}</td>
                  <td className="py-3 px-4 text-sm text-slate-400">{project.user_email}</td>
                  <td className="py-3 px-4 text-sm text-slate-400 capitalize">{project.source_type?.replace('_', ' ')}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full capitalize">{project.status}</span>
                  </td>
                  <td className="py-3 px-4 text-sm text-slate-400">{project.row_count?.toLocaleString() || '-'}</td>
                  <td className="py-3 px-4 text-sm text-slate-400">{new Date(project.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

export default ProjectsListSection;
