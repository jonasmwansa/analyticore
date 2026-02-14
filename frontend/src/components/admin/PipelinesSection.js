import React from 'react';
import { Zap, Play, Pause, CheckCircle2, RefreshCw, Calendar, Timer } from 'lucide-react';
import { Card } from '../ui/card';
import { MetricCard } from './MetricCard';
import {
  ResponsiveContainer, PieChart as RePieChart, Pie, Cell, Tooltip
} from 'recharts';

const COLORS = ['#6366F1', '#14B8A6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#10B981', '#3B82F6'];

export function PipelinesSection({ pipelineAnalytics }) {
  if (!pipelineAnalytics) return <p className="text-slate-400">Loading pipeline data...</p>;
  
  return (
    <div className="space-y-6" data-testid="pipelines-section">
      <h2 className="text-xl font-bold text-white">Pipeline Analytics</h2>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard title="Total Pipelines" value={pipelineAnalytics.total_pipelines} icon={Zap} color="indigo" />
        <MetricCard title="Active" value={pipelineAnalytics.active_pipelines} icon={Play} color="emerald" />
        <MetricCard title="Paused" value={pipelineAnalytics.paused_pipelines} icon={Pause} color="amber" />
        <MetricCard 
          title="Success Rate" 
          value={`${pipelineAnalytics.success_rate}%`} 
          icon={CheckCircle2} 
          color={pipelineAnalytics.success_rate >= 90 ? 'emerald' : pipelineAnalytics.success_rate >= 70 ? 'amber' : 'red'} 
        />
      </div>

      {/* Run Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard title="Total Runs" value={pipelineAnalytics.total_runs} icon={RefreshCw} color="blue" />
        <MetricCard title="Runs (30d)" value={pipelineAnalytics.runs_this_period} icon={Calendar} color="purple" />
        <MetricCard title="Avg Duration" value={`${pipelineAnalytics.avg_duration_seconds}s`} icon={Timer} color="amber" />
      </div>

      {/* Run Status Chart */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Run Status (Last 30 Days)</h3>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <RePieChart>
              <Pie
                data={pipelineAnalytics.run_status || []}
                cx="50%"
                cy="50%"
                outerRadius={70}
                dataKey="count"
                nameKey="status"
                label={({ status, count }) => `${status}: ${count}`}
              >
                {(pipelineAnalytics.run_status || []).map((entry, index) => {
                  const colors = { completed: '#10B981', failed: '#EF4444', running: '#6366F1', pending: '#F59E0B' };
                  return <Cell key={`cell-${index}`} fill={colors[entry.status] || COLORS[index]} />;
                })}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
            </RePieChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Top Pipelines */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Most Active Pipelines</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Pipeline</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Project</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Schedule</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Status</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Runs</th>
              </tr>
            </thead>
            <tbody>
              {pipelineAnalytics.top_pipelines?.map((pipeline, idx) => (
                <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-3 px-4 text-sm text-white">{pipeline.name}</td>
                  <td className="py-3 px-4 text-sm text-slate-400">{pipeline.project}</td>
                  <td className="py-3 px-4 text-sm text-slate-400 capitalize">{pipeline.schedule_type}</td>
                  <td className="py-3 px-4">
                    {pipeline.is_active ? (
                      <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded-full">Active</span>
                    ) : (
                      <span className="px-2 py-1 bg-amber-500/20 text-amber-400 text-xs rounded-full">Paused</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-sm font-bold text-indigo-400 text-right">{pipeline.run_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

export default PipelinesSection;
