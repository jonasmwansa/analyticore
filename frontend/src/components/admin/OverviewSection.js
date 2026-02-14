import React from 'react';
import { Users, UserCheck, FolderKanban, Zap, CheckCircle2 } from 'lucide-react';
import { Card } from '../ui/card';
import { MetricCard } from './MetricCard';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Line, PieChart as RePieChart, Pie, Cell
} from 'recharts';

const COLORS = ['#6366F1', '#14B8A6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#10B981', '#3B82F6'];

export function OverviewSection({ summary, userMetrics, userGrowth, systemHealth }) {
  if (!summary) return null;
  
  return (
    <div className="space-y-6" data-testid="overview-section">
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="Total Users" 
          value={summary.users?.total || 0}
          subtext={`+${summary.users?.new_today || 0} today`}
          icon={Users}
          trend="up"
          color="indigo"
        />
        <MetricCard 
          title="Active Today (DAU)" 
          value={userMetrics?.dau || 0}
          subtext={`${userMetrics?.stickiness || 0}% stickiness`}
          icon={UserCheck}
          color="emerald"
        />
        <MetricCard 
          title="Total Projects" 
          value={summary.projects?.total || 0}
          subtext={`+${summary.projects?.new_today || 0} today`}
          icon={FolderKanban}
          color="amber"
        />
        <MetricCard 
          title="Pipeline Runs Today" 
          value={summary.pipelines?.runs_today || 0}
          subtext={`${summary.pipelines?.successful || 0} successful`}
          icon={Zap}
          color="purple"
        />
      </div>

      {/* User Growth Chart */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">User Growth (Last 30 Days)</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={userGrowth}>
              <defs>
                <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#6366F1" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" tick={{ fontSize: 11 }} />
              <YAxis stroke="#9CA3AF" tick={{ fontSize: 11 }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                labelStyle={{ color: '#9CA3AF' }}
              />
              <Area type="monotone" dataKey="total_users" stroke="#6366F1" fillOpacity={1} fill="url(#colorUsers)" name="Total Users" />
              <Line type="monotone" dataKey="new_users" stroke="#14B8A6" strokeWidth={2} name="New Users" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* System Health & Subscriptions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health Card */}
        <Card className="bg-slate-800 border-slate-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">System Health</h3>
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
              systemHealth?.status === 'healthy' ? 'bg-emerald-500/20 text-emerald-400' :
              systemHealth?.status === 'warning' ? 'bg-amber-500/20 text-amber-400' :
              'bg-red-500/20 text-red-400'
            }`}>
              {systemHealth?.status?.toUpperCase() || 'UNKNOWN'}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-700/50 rounded-lg p-4">
              <p className="text-slate-400 text-sm">DB Response</p>
              <p className="text-2xl font-bold text-white">{systemHealth?.db_response_ms || 0}ms</p>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4">
              <p className="text-slate-400 text-sm">Error Rate (24h)</p>
              <p className="text-2xl font-bold text-white">{systemHealth?.error_rate || 0}%</p>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4">
              <p className="text-slate-400 text-sm">Errors (24h)</p>
              <p className="text-2xl font-bold text-red-400">{systemHealth?.errors_24h || 0}</p>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4">
              <p className="text-slate-400 text-sm">Operations (24h)</p>
              <p className="text-2xl font-bold text-emerald-400">{systemHealth?.total_operations_24h || 0}</p>
            </div>
          </div>
        </Card>

        {/* Subscription Breakdown */}
        <Card className="bg-slate-800 border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Subscription Breakdown</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <RePieChart>
                <Pie
                  data={summary.subscriptions || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  dataKey="count"
                  nameKey="plan"
                  label={({ plan, count }) => `${plan}: ${count}`}
                >
                  {(summary.subscriptions || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
              </RePieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default OverviewSection;
