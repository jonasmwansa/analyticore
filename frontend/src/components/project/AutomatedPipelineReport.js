import React, { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, RefreshCw } from 'lucide-react';

const STAGE_META = {
  cleaning: { icon: '🧹', color: '#00d4ff', short: 'CLEAN' },
  transformation: { icon: '⚙️', color: '#8b5cf6', short: 'TRANSFORM' },
  analysis: { icon: '📊', color: '#10b981', short: 'ANALYZE' },
  visualization: { icon: '📈', color: '#f59e0b', short: 'VISUALIZE' },
  summary: { icon: '📋', color: '#ef4444', short: 'SUMMARIZE' },
};

function StageMarkdown({ content }) {
  const lines = (content || '').split('\n');

  return (
    <div className="space-y-4">
      {lines.map((line, index) => {
        const trimmed = line.trim();

        if (!trimmed) {
          return <div key={index} className="h-2" />;
        }

        if (trimmed.startsWith('# ')) {
          return (
            <h2
              key={index}
              className="text-3xl font-bold text-white"
              style={{ fontFamily: "'Space Grotesk', sans-serif" }}
            >
              {trimmed.slice(2)}
            </h2>
          );
        }

        if (trimmed.startsWith('## ')) {
          return (
            <div key={index} className="pt-6">
              <h3
                className="text-xl font-semibold text-cyan-300"
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}
              >
                {trimmed.slice(3)}
              </h3>
              <div className="mt-3 border-b border-slate-800" />
            </div>
          );
        }

        if (trimmed.startsWith('› ')) {
          return (
            <div key={index} className="flex gap-3 text-[13px] leading-7 text-slate-300">
              <span className="mt-1 text-cyan-300">›</span>
              <span>{trimmed.slice(2)}</span>
            </div>
          );
        }

        return (
          <p key={index} className="text-[13px] leading-8 text-slate-400">
            {trimmed}
          </p>
        );
      })}
    </div>
  );
}

export default function AutomatedPipelineReport({ project }) {
  const automation = project?.statistics?.automation;
  const stages = useMemo(() => (
    (automation?.stages || []).map((stage) => ({
      ...stage,
      ...(STAGE_META[stage.key] || {}),
    }))
  ), [automation]);

  const [stageStatus, setStageStatus] = useState({});
  const [activeStage, setActiveStage] = useState(null);
  const [selectedStage, setSelectedStage] = useState(null);

  useEffect(() => {
    if (!stages.length) return undefined;

    const nextStatus = {};
    stages.forEach((stage) => {
      nextStatus[stage.key] = 'queued';
    });

    setStageStatus(nextStatus);
    setActiveStage(stages[0].key);
    setSelectedStage(null);

    const timers = [];

    stages.forEach((stage, index) => {
      const startDelay = index * 850;
      const finishDelay = startDelay + 750;

      timers.push(setTimeout(() => {
        setActiveStage(stage.key);
        setStageStatus((prev) => ({ ...prev, [stage.key]: 'running' }));
      }, startDelay));

      timers.push(setTimeout(() => {
        setStageStatus((prev) => ({ ...prev, [stage.key]: 'done' }));

        if (index === stages.length - 1) {
          setActiveStage(null);
          setSelectedStage('summary');
        }
      }, finishDelay));
    });

    return () => timers.forEach((timer) => clearTimeout(timer));
  }, [stages]);

  if (!automation || stages.length === 0) {
    return null;
  }

  const selected = selectedStage ? stages.find((stage) => stage.key === selectedStage) : null;
  const completedCount = stages.filter((stage) => stageStatus[stage.key] === 'done').length;
  const animationDone = completedCount === stages.length;

  return (
    <section
      className="overflow-hidden rounded-3xl border border-slate-800 bg-[#070d18]"
      style={{ fontFamily: "'IBM Plex Mono', monospace", boxShadow: '0 24px 80px rgba(2, 6, 23, 0.55)' }}
    >
      <div className="flex flex-wrap items-center gap-4 border-b border-slate-800 px-6 py-5">
        <div className="flex items-center gap-4">
          <div
            className="flex h-12 w-12 items-center justify-center rounded-xl text-xl"
            style={{
              background: 'linear-gradient(135deg, #0ea5e9, #06b6d4)',
              boxShadow: '0 12px 30px rgba(6, 182, 212, 0.25)',
            }}
          >
            ⚡
          </div>
          <div>
            <div
              className="text-2xl font-bold text-white"
              style={{ fontFamily: "'Space Grotesk', sans-serif" }}
            >
              AutoAnalyst
            </div>
            <div className="text-[11px] uppercase tracking-[0.28em] text-slate-500">AI-Powered Data Pipeline</div>
          </div>
        </div>

        <div className="ml-auto flex flex-wrap gap-2">
          {stages.map((stage) => (
            <div
              key={stage.key}
              className="rounded-md border border-slate-700/80 bg-slate-950/40 px-3 py-1 text-[10px] tracking-[0.2em] text-slate-500"
            >
              {stage.short}
            </div>
          ))}
        </div>
      </div>

      <div className="px-6 py-6">
        {animationDone && (
          <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
            <div
              className="text-2xl font-semibold text-white"
              style={{ fontFamily: "'Space Grotesk', sans-serif" }}
            >
              <span className="text-emerald-400">Pipeline Complete</span>
              <span className="text-slate-400"> — </span>
              <span className="text-cyan-300">{project?.original_filename || project?.name}</span>
            </div>
          </div>
        )}

        <div className="grid gap-4 lg:grid-cols-5">
          {stages.map((stage) => {
            const status = stageStatus[stage.key] || 'queued';
            const isActive = activeStage === stage.key;
            const isSelected = selected?.key === stage.key;

            return (
              <button
                key={stage.key}
                type="button"
                onClick={() => status === 'done' && setSelectedStage(stage.key)}
                className={`group rounded-2xl border bg-[#0d1524] p-5 text-left transition-all duration-300 ${
                  isActive ? 'border-cyan-400' :
                  isSelected ? 'border-violet-500' :
                  'border-slate-800 hover:-translate-y-0.5 hover:border-slate-700'
                }`}
                style={{
                  boxShadow: isActive
                    ? '0 0 28px rgba(34, 211, 238, 0.18)'
                    : isSelected
                      ? '0 0 24px rgba(139, 92, 246, 0.16)'
                      : 'none',
                }}
              >
                <div className="mb-4 text-2xl">{stage.icon}</div>
                <div
                  className="text-lg font-semibold leading-7 text-white"
                  style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                >
                  {stage.label}
                </div>
                <div className="mt-4 flex items-center gap-2 text-xs">
                  {status === 'running' && (
                    <>
                      <RefreshCw className="h-3.5 w-3.5 animate-spin" style={{ color: stage.color }} />
                      <span style={{ color: stage.color }}>Processing...</span>
                    </>
                  )}
                  {status === 'done' && (
                    <>
                      <span className="h-2 w-2 rounded-full bg-emerald-400" />
                      <span className="text-emerald-400">Complete</span>
                    </>
                  )}
                  {status === 'queued' && (
                    <>
                      <span className="h-2 w-2 rounded-full border border-slate-600" />
                      <span className="text-slate-500">Queued</span>
                    </>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {!animationDone && !selected && (
          <div className="flex flex-col items-center justify-center px-6 py-20 text-center text-slate-500">
            <div className="pipeline-pulse mb-4 text-4xl">⚡</div>
            <p className="text-sm tracking-[0.12em] text-slate-500">AI is analyzing your data across all pipeline stages...</p>
          </div>
        )}

        {selected && (
          <div className="mt-8 overflow-hidden rounded-2xl border border-slate-800 bg-[#0d1524]">
            <div className="flex flex-wrap items-start gap-6 border-b border-slate-800 px-6 py-5">
              <div className="flex items-start gap-4">
                <div className="mt-1 text-2xl">{selected.icon}</div>
                <div>
                  <div
                    className="text-3xl font-semibold leading-tight text-white"
                    style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                  >
                    {selected.label}
                  </div>
                  <p className="mt-2 max-w-2xl text-sm leading-7 text-slate-400">{selected.summary}</p>
                </div>
              </div>

              <div className="ml-auto flex flex-wrap gap-2">
                {stages
                  .filter((stage) => stageStatus[stage.key] === 'done')
                  .map((stage) => (
                    <button
                      key={stage.key}
                      type="button"
                      onClick={() => setSelectedStage(stage.key)}
                      className={`rounded-lg border px-3 py-2 text-xs transition-colors ${
                        selected.key === stage.key
                          ? 'border-cyan-400 bg-cyan-500/10 text-cyan-300'
                          : 'border-slate-700 bg-slate-950/30 text-slate-500 hover:border-slate-600 hover:text-slate-300'
                      }`}
                    >
                      {stage.icon} {stage.label}
                    </button>
                  ))}
              </div>
            </div>

            <div className="max-h-[640px] overflow-y-auto px-7 py-7">
              <StageMarkdown content={selected.details?.content || selected.summary} />
            </div>
          </div>
        )}

        <div className="mt-6 flex flex-wrap gap-3 text-xs text-slate-500">
          <div className="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-950/40 px-3 py-1.5">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
            <span>{automation.actions_applied?.length || 0} automated actions applied</span>
          </div>
          <div className="rounded-full border border-slate-800 bg-slate-950/40 px-3 py-1.5">
            Quality score: {automation.quality_score_after ?? '--'}
          </div>
          <div className="rounded-full border border-slate-800 bg-slate-950/40 px-3 py-1.5">
            Rows processed: {automation.rows_after?.toLocaleString?.() || automation.rows_after}
          </div>
        </div>
      </div>
    </section>
  );
}
