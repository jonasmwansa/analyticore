import React from 'react';
import { Database, AlertTriangle, XCircle, Activity, CheckCircle2 } from 'lucide-react';
import { Card } from '../ui/card';
import { MetricCard } from './MetricCard';

export function SystemSection({ systemHealth }) {
  if (!systemHealth) return <p className="text-slate-400">Loading system data...</p>;
  
  return (
    <div className="space-y-6" data-testid="system-section">
      <h2 className="text-xl font-bold text-white">System Health</h2>
      
      {/* Status Banner */}
      <Card className={`p-6 border ${
        systemHealth.status === 'healthy' ? 'bg-emerald-500/10 border-emerald-500/30' :
        systemHealth.status === 'warning' ? 'bg-amber-500/10 border-amber-500/30' :
        'bg-red-500/10 border-red-500/30'
      }`}>
        <div className="flex items-center gap-4">
          {systemHealth.status === 'healthy' ? (
            <CheckCircle2 className="w-12 h-12 text-emerald-400" />
          ) : systemHealth.status === 'warning' ? (
            <AlertTriangle className="w-12 h-12 text-amber-400" />
          ) : (
            <XCircle className="w-12 h-12 text-red-400" />
          )}
          <div>
            <h3 className="text-2xl font-bold text-white">System Status: {systemHealth.status?.toUpperCase()}</h3>
            <p className="text-slate-400">
              {systemHealth.status === 'healthy' ? 'All systems operational' : 
               systemHealth.status === 'warning' ? 'Some issues detected' : 
               'Critical issues require attention'}
            </p>
          </div>
        </div>
      </Card>

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard 
          title="Database Response" 
          value={`${systemHealth.db_response_ms}ms`} 
          icon={Database}
          color={systemHealth.db_response_ms < 100 ? 'emerald' : systemHealth.db_response_ms < 500 ? 'amber' : 'red'}
        />
        <MetricCard 
          title="Error Rate" 
          value={`${systemHealth.error_rate}%`} 
          icon={AlertTriangle}
          color={systemHealth.error_rate < 1 ? 'emerald' : systemHealth.error_rate < 5 ? 'amber' : 'red'}
        />
        <MetricCard 
          title="Errors (24h)" 
          value={systemHealth.errors_24h} 
          icon={XCircle}
          color={systemHealth.errors_24h === 0 ? 'emerald' : systemHealth.errors_24h < 10 ? 'amber' : 'red'}
        />
        <MetricCard 
          title="Operations (24h)" 
          value={systemHealth.total_operations_24h} 
          icon={Activity}
          color="blue"
        />
      </div>

      {/* Database Stats */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Database Statistics</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-700/50 rounded-lg p-4">
            <p className="text-slate-400 text-sm">Total Users in DB</p>
            <p className="text-3xl font-bold text-white">{systemHealth.total_users}</p>
          </div>
          <div className="bg-slate-700/50 rounded-lg p-4">
            <p className="text-slate-400 text-sm">Total Projects in DB</p>
            <p className="text-3xl font-bold text-white">{systemHealth.total_projects}</p>
          </div>
        </div>
      </Card>
    </div>
  );
}

export default SystemSection;
