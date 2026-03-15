import React from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { CheckCircle2, Clock, Sparkles, User } from 'lucide-react';

export default function TransformationHistory({ project, onRollback }) {
  const history = project?.applied_transformations || [];
  const stages = project?.statistics?.automation?.stages || [];

  if (history.length === 0 && stages.length === 0) return null;

  return (
    <Card className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold">Pipeline History</h3>
      </div>
      <div className="space-y-6">
        {stages.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
              <Sparkles className="w-4 h-4 text-[#6366F1]" />
              <span>Automated Stages</span>
            </div>
            {stages.map((stage) => (
              <div key={stage.key} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span className="font-semibold text-slate-900">{stage.label}</span>
                    </div>
                    <p className="mt-2 text-sm text-slate-600">{stage.summary}</p>
                    <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-500">
                      <span className="inline-flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {stage.completed_at || stage.started_at || 'unknown'}
                      </span>
                      <span>Status: {stage.status}</span>
                      {stage.duration_seconds !== undefined && <span>{stage.duration_seconds}s</span>}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {history.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
              <User className="w-4 h-4 text-slate-500" />
              <span>Applied Transformations</span>
            </div>
            {history.slice().reverse().map((entry, idx) => (
              <div key={idx} className="flex items-start justify-between gap-4 rounded-xl border border-slate-200 p-4">
                <div>
                  <div className="text-sm text-slate-500 flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>{entry.timestamp || 'unknown'}</span>
                    <span className="mx-2 text-xs">•</span>
                    <User className="w-4 h-4" />
                    <span>{entry.user || 'system'}</span>
                  </div>
                  <div className="mt-2 text-sm text-slate-700">
                    <div className="font-medium">Actions:</div>
                    <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(entry.actions || entry, null, 2)}</pre>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  {entry.backup_path ? (
                    <Button size="sm" variant="outline" onClick={() => onRollback(entry)}>
                      Rollback
                    </Button>
                  ) : (
                    <Button size="sm" variant="ghost" disabled>
                      No Backup
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
}
