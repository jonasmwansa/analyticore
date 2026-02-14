import React from 'react';
import { FolderKanban, Calendar, Database, BarChart3, LineChart, Activity, RefreshCw } from 'lucide-react';
import { Card } from '../ui/card';
import { MetricCard } from './MetricCard';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart as RePieChart, Pie, Cell
} from 'recharts';

const COLORS = ['#6366F1', '#14B8A6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#10B981', '#3B82F6'];

export function ProjectsSection({ projectAnalytics }) {
  if (!projectAnalytics) return <p className="text-slate-400">Loading project data...</p>;
  
  return (
    <div className="space-y-6" data-testid="projects-section">
      <h2 className="text-xl font-bold text-white">Project Analytics</h2>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard title="Total Projects" value={projectAnalytics.total_projects} icon={FolderKanban} color="indigo" />
        <MetricCard title="This Period" value={projectAnalytics.projects_this_period} subtext="Last 30 days" icon={Calendar} color="emerald" />
        <MetricCard title="Total Rows" value={(projectAnalytics.total_rows_processed || 0).toLocaleString()} icon={Database} color="blue" />
        <MetricCard title="Avg Rows/Project" value={(projectAnalytics.avg_rows_per_project || 0).toLocaleString()} icon={BarChart3} color="purple" />
      </div>

      {/* Analysis Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard title="Total Analyses" value={projectAnalytics.total_analyses} icon={LineChart} color="amber" />
        <MetricCard title="Analyses (30d)" value={projectAnalytics.analyses_this_period} icon={Activity} color="emerald" />
        <MetricCard title="Transformations" value={projectAnalytics.total_transformations} icon={RefreshCw} color="purple" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Breakdown */}
        <Card className="bg-slate-800 border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Project Status</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <RePieChart>
                <Pie
                  data={projectAnalytics.status_breakdown || []}
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  dataKey="count"
                  nameKey="status"
                  label={({ status, count }) => `${status}: ${count}`}
                >
                  {(projectAnalytics.status_breakdown || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
              </RePieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Source Breakdown */}
        <Card className="bg-slate-800 border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Data Sources</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={projectAnalytics.source_breakdown || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" stroke="#9CA3AF" />
                <YAxis type="category" dataKey="source_type" stroke="#9CA3AF" width={100} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
                <Bar dataKey="count" fill="#6366F1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Common Transformations */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Most Common Transformations</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {projectAnalytics.common_actions?.slice(0, 10).map((action, idx) => (
            <div key={idx} className="bg-slate-700/50 rounded-lg p-3 text-center">
              <p className="text-lg font-bold text-indigo-400">{action.count}</p>
              <p className="text-xs text-slate-400 capitalize">{action.action?.replace(/_/g, ' ')}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

export default ProjectsSection;
