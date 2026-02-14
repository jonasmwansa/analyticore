import React from 'react';
import { 
  Users, UserCheck, Calendar, TrendingUp, TrendingDown, 
  Target, UserPlus, UserMinus, RefreshCw 
} from 'lucide-react';
import { Card } from '../ui/card';
import { MetricCard } from './MetricCard';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

export function UserMetricsSection({ userMetrics, userGrowth }) {
  if (!userMetrics) return <p className="text-slate-400">Loading user metrics...</p>;
  
  return (
    <div className="space-y-6" data-testid="user-metrics-section">
      <h2 className="text-xl font-bold text-white">User Metrics</h2>
      
      {/* Core Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <MetricCard title="Total Users" value={userMetrics.total_users} icon={Users} color="indigo" />
        <MetricCard title="DAU" value={userMetrics.dau} subtext="Active Today" icon={UserCheck} color="emerald" />
        <MetricCard title="WAU" value={userMetrics.wau} subtext="Active This Week" icon={Calendar} color="blue" />
        <MetricCard title="MAU" value={userMetrics.mau} subtext="Active This Month" icon={TrendingUp} color="purple" />
        <MetricCard title="Stickiness" value={`${userMetrics.stickiness}%`} subtext="DAU/MAU" icon={Target} color="amber" />
      </div>

      {/* Growth & Churn */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="New Today" 
          value={userMetrics.new_users_today} 
          icon={UserPlus} 
          color="emerald" 
        />
        <MetricCard 
          title="Growth Rate" 
          value={`${userMetrics.growth_rate > 0 ? '+' : ''}${userMetrics.growth_rate}%`} 
          subtext="Week over Week"
          icon={userMetrics.growth_rate >= 0 ? TrendingUp : TrendingDown} 
          color={userMetrics.growth_rate >= 0 ? 'emerald' : 'red'} 
        />
        <MetricCard 
          title="Churned Users" 
          value={userMetrics.churned_users} 
          subtext="Inactive 30+ days"
          icon={UserMinus} 
          color="red" 
        />
        <MetricCard 
          title="Returning" 
          value={userMetrics.returning_users} 
          subtext="Active today & before"
          icon={RefreshCw} 
          color="blue" 
        />
      </div>

      {/* Verification Stats */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Email Verification</h3>
        <div className="flex items-center gap-8">
          <div>
            <p className="text-4xl font-bold text-emerald-400">{userMetrics.verified_users}</p>
            <p className="text-slate-400">Verified Users</p>
          </div>
          <div className="flex-1 bg-slate-700 rounded-full h-4 overflow-hidden">
            <div 
              className="bg-emerald-500 h-full rounded-full transition-all"
              style={{ width: `${userMetrics.verification_rate}%` }}
            />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{userMetrics.verification_rate}%</p>
            <p className="text-slate-400">Verification Rate</p>
          </div>
        </div>
      </Card>

      {/* User Growth Chart */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">User Growth Trend</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={userGrowth.slice(-14)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" tick={{ fontSize: 10 }} />
              <YAxis stroke="#9CA3AF" />
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
              <Bar dataKey="new_users" fill="#6366F1" name="New Users" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}

export default UserMetricsSection;
