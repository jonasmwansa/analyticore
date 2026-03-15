import React from 'react';
import { Activity, FileSpreadsheet, AlertCircle, BarChart3, Wand2 } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';

export function DataPreviewSection({ 
  project, 
  dataPreview, 
  analyzing, 
  onAnalyzeData, 
  onViewAnalysis, 
  onOneClickClean,
  oneClickCleaning = false
}) {
  const automation = project?.statistics?.automation;
  return (
    <div className="space-y-6">
      {project?.statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="stat-card bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-[#EEF2FF] rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-[#6366F1]" />
              </div>
              <div>
                <p className="text-sm text-[#94A3B8]">Total Rows</p>
                <p className="text-2xl font-bold text-[#0F172A] data-cell">{project.statistics.total_rows?.toLocaleString()}</p>
              </div>
            </div>
          </Card>
          
          <Card className="stat-card bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-[#F0FDFA] rounded-lg flex items-center justify-center">
                <FileSpreadsheet className="w-6 h-6 text-[#14B8A6]" />
              </div>
              <div>
                <p className="text-sm text-[#94A3B8]">Columns</p>
                <p className="text-2xl font-bold text-[#0F172A] data-cell">{project.statistics.total_columns}</p>
              </div>
            </div>
          </Card>

          <Card className="stat-card bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-[#FEF3F2] rounded-lg flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-[#F59E0B]" />
              </div>
              <div>
                <p className="text-sm text-[#94A3B8]">Missing Values</p>
                <p className="text-2xl font-bold text-[#0F172A] data-cell">
                  {Object.values(project.statistics.missing_values || {}).reduce((a, b) => a + b, 0)}
                </p>
              </div>
            </div>
          </Card>

          <Card className="stat-card bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex gap-2">
              <Button
                onClick={onAnalyzeData}
                disabled={analyzing}
                data-testid="analyze-data-btn"
                className="flex-1 bg-[#8B5CF6] hover:bg-[#7C3AED] text-white rounded-lg h-12 font-semibold shadow-md shadow-violet-500/20"
              >
                {analyzing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Running...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-5 h-5 mr-2" />
                    {automation ? 'Re-run Pipeline' : 'Run Pipeline'}
                  </>
                )}
              </Button>
              <Button
                onClick={onViewAnalysis}
                data-testid="view-analysis-btn"
                variant="outline"
                className="h-12 px-4"
              >
                <BarChart3 className="w-5 h-5" />
              </Button>
              <Button
                onClick={onOneClickClean}
                data-testid="one-click-clean-btn"
                variant="outline"
                className="h-12 px-4"
                disabled={oneClickCleaning}
              >
                {oneClickCleaning ? (
                  <>
                    <div className="w-4 h-4 border-2 border-slate-600 border-t-transparent rounded-full animate-spin mr-2"></div>
                    Cleaning...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-5 h-5 mr-2" />
                    Clean
                  </>
                )}
              </Button>
            </div>
          </Card>
        </div>
      )}

      {dataPreview && (
        <Card className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-200">
            <h3 className="text-lg font-bold text-[#0F172A]">Data Preview</h3>
            <p className="text-sm text-[#64748B]">Showing first 100 rows</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-slate-50">
                  {dataPreview.columns?.map((col, idx) => (
                    <th
                      key={idx}
                      className="text-left py-3 px-4 text-xs uppercase tracking-wider text-slate-500 font-semibold border-b border-slate-200"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {dataPreview.data?.slice(0, 20).map((row, rowIdx) => (
                  <tr key={rowIdx} className="hover:bg-slate-50/50 border-b border-slate-100">
                    {dataPreview.columns?.map((col, colIdx) => (
                      <td key={colIdx} className="py-3 px-4 text-sm text-[#0F172A] data-cell">
                        {row[col] !== null && row[col] !== undefined ? String(row[col]) : <span className="text-[#94A3B8] italic">null</span>}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}

export default DataPreviewSection;
