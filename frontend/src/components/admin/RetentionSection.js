import React from 'react';
import { Clock, Calendar, Target } from 'lucide-react';
import { Card } from '../ui/card';
import { MetricCard } from './MetricCard';

export function RetentionSection({ retention, funnel }) {
  return (
    <div className="space-y-6" data-testid="retention-section">
      <h2 className="text-xl font-bold text-white">Retention & Funnel Analytics</h2>
      
      {/* Retention Metrics */}
      {retention && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <MetricCard title="Day 1 Retention" value={`${retention.day1_retention}%`} icon={Clock} color="indigo" />
            <MetricCard title="Day 7 Retention" value={`${retention.day7_retention}%`} icon={Calendar} color="emerald" />
            <MetricCard title="Day 30 Retention" value={`${retention.day30_retention}%`} icon={Target} color="purple" />
          </div>

          {/* Cohort Table */}
          <Card className="bg-slate-800 border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Cohort Retention</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Cohort</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Users</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Month 1</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Month 2</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Month 3</th>
                  </tr>
                </thead>
                <tbody>
                  {retention.cohort_retention?.map((cohort, idx) => (
                    <tr key={idx} className="border-b border-slate-700/50">
                      <td className="py-3 px-4 text-sm text-white">{cohort.cohort}</td>
                      <td className="py-3 px-4 text-sm text-slate-400 text-right">{cohort.total}</td>
                      <td className="py-3 px-4 text-sm text-right">
                        {cohort.month_1 !== undefined ? (
                          <span className={cohort.month_1 > 30 ? 'text-emerald-400' : 'text-amber-400'}>{cohort.month_1}%</span>
                        ) : '-'}
                      </td>
                      <td className="py-3 px-4 text-sm text-right">
                        {cohort.month_2 !== undefined ? (
                          <span className={cohort.month_2 > 20 ? 'text-emerald-400' : 'text-amber-400'}>{cohort.month_2}%</span>
                        ) : '-'}
                      </td>
                      <td className="py-3 px-4 text-sm text-right">
                        {cohort.month_3 !== undefined ? (
                          <span className={cohort.month_3 > 15 ? 'text-emerald-400' : 'text-amber-400'}>{cohort.month_3}%</span>
                        ) : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}

      {/* User Journey Funnel */}
      {funnel && (
        <Card className="bg-slate-800 border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">User Journey Funnel</h3>
          <div className="space-y-3">
            {funnel.funnel?.map((stage, idx) => (
              <div key={idx} className="flex items-center gap-4">
                <div className="w-32 text-sm text-slate-400">{stage.stage}</div>
                <div className="flex-1 bg-slate-700 rounded-full h-8 overflow-hidden relative">
                  <div 
                    className="h-full rounded-full transition-all bg-gradient-to-r from-indigo-600 to-indigo-400"
                    style={{ width: `${stage.rate}%` }}
                  />
                  <span className="absolute inset-0 flex items-center justify-center text-sm font-medium text-white">
                    {stage.count} ({stage.rate}%)
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}

export default RetentionSection;
