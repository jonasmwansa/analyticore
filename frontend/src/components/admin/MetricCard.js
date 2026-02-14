import React from 'react';
import { Card } from '../ui/card';

const COLOR_CLASSES = {
  indigo: 'bg-indigo-500/20 text-indigo-400',
  emerald: 'bg-emerald-500/20 text-emerald-400',
  amber: 'bg-amber-500/20 text-amber-400',
  red: 'bg-red-500/20 text-red-400',
  purple: 'bg-purple-500/20 text-purple-400',
  blue: 'bg-blue-500/20 text-blue-400',
};

export function MetricCard({ title, value, subtext, icon: Icon, color = 'indigo' }) {
  return (
    <Card className="bg-slate-800 border-slate-700 p-4">
      <div className="flex items-start gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${COLOR_CLASSES[color]}`}>
          <Icon size={20} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs text-slate-400 truncate">{title}</p>
          <p className="text-xl font-bold text-white">{value}</p>
          {subtext && <p className="text-xs text-slate-500 truncate">{subtext}</p>}
        </div>
      </div>
    </Card>
  );
}

export default MetricCard;
