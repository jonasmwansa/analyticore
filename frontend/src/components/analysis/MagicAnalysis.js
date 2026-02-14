import React, { useState } from 'react';
import { toast } from 'sonner';
import {
  Sparkles, CheckCircle2, AlertCircle, AlertTriangle, Info, TrendingUp,
  BarChart3, PieChart, Play, RefreshCw, ChevronRight, Download,
  Settings2, Zap, Target, Brain, Link2, Calendar, FileSpreadsheet, FileJson, FileText, MoreHorizontal
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Checkbox } from '../ui/checkbox';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '../ui/dropdown-menu';
import { analysisAPI } from '../../api';
import EnhancedExportModal from '../EnhancedExportModal';

const SEVERITY_COLORS = {
  critical: 'bg-red-100 text-red-700 border-red-200',
  warning: 'bg-amber-100 text-amber-700 border-amber-200',
  info: 'bg-blue-100 text-blue-700 border-blue-200',
  high: 'bg-red-100 text-red-700',
  medium: 'bg-amber-100 text-amber-700',
  low: 'bg-slate-100 text-slate-600'
};

const ICON_MAP = {
  success: CheckCircle2,
  alert: AlertTriangle,
  info: Info,
  link: Link2,
  chart: BarChart3,
  brain: Brain,
  calendar: Calendar
};

const QualityScoreRing = ({ score, label }) => {
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? '#10B981' : score >= 60 ? '#F59E0B' : score >= 40 ? '#F97316' : '#EF4444';
  
  return (
    <div className="relative w-32 h-32">
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="64"
          cy="64"
          r="45"
          stroke="#E2E8F0"
          strokeWidth="8"
          fill="none"
        />
        <circle
          cx="64"
          cy="64"
          r="45"
          stroke={color}
          strokeWidth="8"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-slate-900">{score}</span>
        <span className="text-xs text-slate-500">{label}</span>
      </div>
    </div>
  );
};

const InsightCard = ({ insight }) => {
  const IconComponent = ICON_MAP[insight.icon] || Info;
  const priorityColor = SEVERITY_COLORS[insight.priority] || SEVERITY_COLORS.info;
  
  return (
    <div className="p-4 bg-white border border-slate-200 rounded-xl hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
          insight.priority === 'high' ? 'bg-red-100' : 
          insight.priority === 'medium' ? 'bg-amber-100' : 'bg-blue-100'
        }`}>
          <IconComponent className={`w-5 h-5 ${
            insight.priority === 'high' ? 'text-red-600' :
            insight.priority === 'medium' ? 'text-amber-600' : 'text-blue-600'
          }`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-semibold text-slate-900 text-sm">{insight.title}</h4>
            <Badge className={`${priorityColor} text-xs`}>{insight.priority}</Badge>
          </div>
          <p className="text-sm text-slate-600">{insight.message}</p>
          {insight.columns && (
            <div className="flex flex-wrap gap-1 mt-2">
              {insight.columns.map(col => (
                <span key={col} className="px-2 py-0.5 bg-slate-100 rounded text-xs text-slate-600">
                  {col}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const CleaningSuggestionCard = ({ suggestion, isSelected, onToggle, onStrategyChange }) => {
  const [selectedStrategy, setSelectedStrategy] = useState(
    suggestion.options?.find(o => o.recommended)?.strategy || suggestion.options?.[0]?.strategy
  );
  
  const handleStrategyChange = (strategy) => {
    setSelectedStrategy(strategy);
    onStrategyChange(suggestion, strategy);
  };
  
  const priorityColor = SEVERITY_COLORS[suggestion.priority] || SEVERITY_COLORS.low;
  
  return (
    <div className={`p-4 bg-white border rounded-xl transition-all ${
      isSelected ? 'border-indigo-400 ring-2 ring-indigo-100' : 'border-slate-200'
    }`}>
      <div className="flex items-start gap-3">
        <Checkbox
          checked={isSelected}
          onCheckedChange={onToggle}
          className="mt-1"
          data-testid={`cleaning-checkbox-${suggestion.column}-${suggestion.issue}`}
        />
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium text-slate-900">
              {suggestion.column === '__all__' ? 'All Columns' : suggestion.column}
            </span>
            <Badge className={`${priorityColor} text-xs`}>{suggestion.priority}</Badge>
            <Badge variant="outline" className="text-xs">
              {suggestion.issue.replace('_', ' ')}
            </Badge>
          </div>
          <p className="text-sm text-slate-600 mb-2">
            {suggestion.count.toLocaleString()} affected ({suggestion.percentage}%)
          </p>
          {suggestion.reason && (
            <p className="text-xs text-slate-500 mb-3 italic">{suggestion.reason}</p>
          )}
          
          {suggestion.options && (
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-700">Choose strategy:</label>
              <Select value={selectedStrategy} onValueChange={handleStrategyChange}>
                <SelectTrigger className="w-full bg-white" data-testid={`strategy-select-${suggestion.column}`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  {suggestion.options.map(option => (
                    <SelectItem key={option.strategy} value={option.strategy}>
                      <div className="flex items-center gap-2">
                        {option.recommended && <Sparkles className="w-3 h-3 text-amber-500" />}
                        <span>{option.description}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const VisualizationSuggestionCard = ({ viz, onView }) => {
  const iconMap = {
    histogram: BarChart3,
    heatmap: TrendingUp,
    scatter: Target,
    bar: BarChart3,
    pie: PieChart,
    box: FileSpreadsheet
  };
  const Icon = iconMap[viz.type] || BarChart3;
  
  return (
    <div className="p-4 bg-gradient-to-br from-slate-50 to-white border border-slate-200 rounded-xl hover:shadow-md transition-all group">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
            <Icon className="w-5 h-5 text-indigo-600" />
          </div>
          <div>
            <h4 className="font-semibold text-slate-900 text-sm">{viz.title}</h4>
            <p className="text-xs text-slate-500 mt-0.5">{viz.description}</p>
            <div className="flex flex-wrap gap-1 mt-2">
              {viz.columns.slice(0, 3).map(col => (
                <span key={col} className="px-2 py-0.5 bg-slate-100 rounded text-xs text-slate-600">
                  {col}
                </span>
              ))}
            </div>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onView(viz)}
          className="opacity-0 group-hover:opacity-100 transition-opacity"
          data-testid={`view-viz-${viz.type}`}
        >
          <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};

export default function MagicAnalysis({ projectId, onDataChanged }) {
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [selectedCleanings, setSelectedCleanings] = useState({});
  const [cleaningStrategies, setCleaningStrategies] = useState({});
  const [activeTab, setActiveTab] = useState('summary');
  
  const runAnalysis = async () => {
    setLoading(true);
    try {
      const response = await analysisAPI.runMagicAnalysis(projectId);
      setAnalysisResult(response.data);
      setSelectedCleanings({});
      setCleaningStrategies({});
      toast.success('Magic analysis complete!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };
  
  const exportReport = async (format) => {
    setExporting(true);
    try {
      const response = await analysisAPI.exportAnalysisReport(projectId, format);
      const data = response.data;
      
      let blob;
      let filename = data.filename || `analysis_report.${format === 'excel' ? 'xlsx' : format}`;
      
      if (format === 'json') {
        // For JSON, it's the raw analysis data
        blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        filename = filename.endsWith('.json') ? filename : `${filename}.json`;
      } else if (format === 'csv') {
        // For CSV, content is plain text
        blob = new Blob([data.content], { type: 'text/csv' });
      } else if (format === 'excel') {
        // For Excel, content is base64 encoded
        const binaryString = atob(data.content);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        blob = new Blob([bytes], { 
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
        });
      }
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success(`Report exported as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Export failed');
    } finally {
      setExporting(false);
    }
  };
  
  const toggleCleaning = (suggestion) => {
    const key = `${suggestion.column}-${suggestion.issue}`;
    setSelectedCleanings(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
    
    // Set default strategy
    if (!cleaningStrategies[key]) {
      const defaultStrategy = suggestion.options?.find(o => o.recommended)?.strategy || 
                              suggestion.options?.[0]?.strategy;
      if (defaultStrategy) {
        setCleaningStrategies(prev => ({
          ...prev,
          [key]: defaultStrategy
        }));
      }
    }
  };
  
  const handleStrategyChange = (suggestion, strategy) => {
    const key = `${suggestion.column}-${suggestion.issue}`;
    setCleaningStrategies(prev => ({
      ...prev,
      [key]: strategy
    }));
  };
  
  const applySelectedCleanings = async () => {
    const actions = analysisResult.cleaning_suggestions
      .filter(s => selectedCleanings[`${s.column}-${s.issue}`])
      .map(s => ({
        column: s.column,
        issue: s.issue,
        strategy: cleaningStrategies[`${s.column}-${s.issue}`] || 
                  s.options?.find(o => o.recommended)?.strategy ||
                  s.options?.[0]?.strategy
      }));
    
    if (actions.length === 0) {
      toast.error('Please select at least one cleaning action');
      return;
    }
    
    setApplying(true);
    try {
      const response = await analysisAPI.applyMagicCleaning(projectId, actions);
      toast.success(`Applied ${actions.length} cleaning operations successfully!`);
      
      // Refresh analysis
      await runAnalysis();
      
      // Notify parent to refresh data
      if (onDataChanged) {
        onDataChanged();
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to apply cleaning');
    } finally {
      setApplying(false);
    }
  };
  
  const selectAllCleanings = () => {
    const newSelections = {};
    const newStrategies = {};
    analysisResult?.cleaning_suggestions?.forEach(s => {
      const key = `${s.column}-${s.issue}`;
      newSelections[key] = true;
      newStrategies[key] = s.options?.find(o => o.recommended)?.strategy || s.options?.[0]?.strategy;
    });
    setSelectedCleanings(newSelections);
    setCleaningStrategies(newStrategies);
  };
  
  const selectedCount = Object.values(selectedCleanings).filter(Boolean).length;
  const summary = analysisResult?.executive_summary;
  
  return (
    <div className="space-y-6" data-testid="magic-analysis">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="w-7 h-7 text-amber-500" />
            Magic Analysis
          </h2>
          <p className="text-slate-500 mt-1">One-click comprehensive data analysis with plain-English insights</p>
        </div>
        <div className="flex items-center gap-3">
          {analysisResult && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="outline"
                  disabled={exporting}
                  className="border-slate-300"
                  data-testid="export-report-btn"
                >
                  {exporting ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Download className="w-4 h-4 mr-2" />
                  )}
                  Export Report
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48 bg-white">
                <DropdownMenuItem 
                  onClick={() => exportReport('excel')}
                  className="cursor-pointer"
                >
                  <FileSpreadsheet className="w-4 h-4 mr-2 text-green-600" />
                  Export as Excel
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => exportReport('csv')}
                  className="cursor-pointer"
                >
                  <FileText className="w-4 h-4 mr-2 text-blue-600" />
                  Export as CSV
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => exportReport('json')}
                  className="cursor-pointer"
                >
                  <FileJson className="w-4 h-4 mr-2 text-amber-600" />
                  Export as JSON
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
          <Button
            onClick={runAnalysis}
            disabled={loading}
            className="bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-white shadow-lg shadow-indigo-500/25"
            data-testid="run-magic-analysis-btn"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 mr-2" />
                {analysisResult ? 'Re-analyze' : 'Analyze My Data'}
              </>
            )}
          </Button>
        </div>
      </div>
      
      {/* Loading State */}
      {loading && (
        <Card className="bg-gradient-to-br from-indigo-50 to-violet-50 border-indigo-200">
          <CardContent className="py-12 text-center">
            <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-lg font-medium text-indigo-900">Running Magic Analysis...</p>
            <p className="text-sm text-indigo-600 mt-1">Profiling data, detecting issues, generating insights</p>
          </CardContent>
        </Card>
      )}
      
      {/* Results */}
      {!loading && analysisResult && (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="bg-white border border-slate-200 p-1 rounded-lg">
            <TabsTrigger 
              value="summary"
              className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-md"
              data-testid="tab-magic-summary"
            >
              <FileSpreadsheet className="w-4 h-4 mr-2" />
              Summary
            </TabsTrigger>
            <TabsTrigger 
              value="quality"
              className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-md"
              data-testid="tab-magic-quality"
            >
              <AlertCircle className="w-4 h-4 mr-2" />
              Data Quality
              {analysisResult.data_quality?.critical_issues > 0 && (
                <span className="ml-2 px-1.5 py-0.5 bg-red-500 text-white text-xs rounded-full">
                  {analysisResult.data_quality.critical_issues}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger 
              value="cleaning"
              className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-md"
              data-testid="tab-magic-cleaning"
            >
              <Settings2 className="w-4 h-4 mr-2" />
              Cleaning
              {analysisResult.cleaning_suggestions?.length > 0 && (
                <span className="ml-2 px-1.5 py-0.5 bg-amber-500 text-white text-xs rounded-full">
                  {analysisResult.cleaning_suggestions.length}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger 
              value="insights"
              className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-md"
              data-testid="tab-magic-insights"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Insights
            </TabsTrigger>
            <TabsTrigger 
              value="visualize"
              className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-md"
              data-testid="tab-magic-visualize"
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Suggested Charts
            </TabsTrigger>
          </TabsList>
          
          {/* Summary Tab */}
          <TabsContent value="summary" className="space-y-6" data-testid="magic-summary-content">
            {/* Executive Summary Card */}
            <Card className="bg-gradient-to-br from-white to-slate-50 border-slate-200 overflow-hidden">
              <CardHeader className="border-b border-slate-100 pb-4">
                <CardTitle className="text-xl font-bold text-slate-900">Executive Summary</CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row gap-8">
                  <div className="flex justify-center">
                    <QualityScoreRing 
                      score={summary?.quality_score || 0} 
                      label={summary?.quality_label || 'N/A'} 
                    />
                  </div>
                  <div className="flex-1">
                    <p className="text-slate-700 leading-relaxed text-lg mb-6">
                      {summary?.text}
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="p-3 bg-white border border-slate-200 rounded-lg text-center">
                        <p className="text-2xl font-bold text-slate-900">{summary?.stats?.total_rows?.toLocaleString()}</p>
                        <p className="text-xs text-slate-500">Rows</p>
                      </div>
                      <div className="p-3 bg-white border border-slate-200 rounded-lg text-center">
                        <p className="text-2xl font-bold text-slate-900">{summary?.stats?.total_columns}</p>
                        <p className="text-xs text-slate-500">Columns</p>
                      </div>
                      <div className="p-3 bg-white border border-slate-200 rounded-lg text-center">
                        <p className="text-2xl font-bold text-amber-600">{summary?.stats?.missing_values?.toLocaleString()}</p>
                        <p className="text-xs text-slate-500">Missing</p>
                      </div>
                      <div className="p-3 bg-white border border-slate-200 rounded-lg text-center">
                        <p className="text-2xl font-bold text-red-600">{summary?.stats?.duplicate_rows?.toLocaleString()}</p>
                        <p className="text-xs text-slate-500">Duplicates</p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            {/* Next Steps */}
            {analysisResult.next_steps && analysisResult.next_steps.length > 0 && (
              <Card className="bg-white border-slate-200">
                <CardHeader className="border-b border-slate-100 pb-4">
                  <CardTitle className="text-lg font-bold text-slate-900">Recommended Next Steps</CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  <div className="space-y-3">
                    {analysisResult.next_steps.map((step, idx) => (
                      <div key={idx} className="flex items-start gap-4 p-3 bg-slate-50 rounded-lg">
                        <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-bold text-indigo-600">{step.step}</span>
                        </div>
                        <div>
                          <h4 className="font-semibold text-slate-900">{step.action}</h4>
                          <p className="text-sm text-slate-600">{step.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
          
          {/* Data Quality Tab */}
          <TabsContent value="quality" className="space-y-4" data-testid="magic-quality-content">
            {/* Quality Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="bg-white border-slate-200">
                <CardContent className="p-4 text-center">
                  <QualityScoreRing 
                    score={analysisResult.data_quality?.quality_score || 0} 
                    label="Quality"
                  />
                </CardContent>
              </Card>
              <Card className="bg-red-50 border-red-200">
                <CardContent className="p-4 text-center">
                  <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
                  <p className="text-3xl font-bold text-red-700">{analysisResult.data_quality?.critical_issues || 0}</p>
                  <p className="text-sm text-red-600">Critical Issues</p>
                </CardContent>
              </Card>
              <Card className="bg-amber-50 border-amber-200">
                <CardContent className="p-4 text-center">
                  <AlertTriangle className="w-8 h-8 text-amber-500 mx-auto mb-2" />
                  <p className="text-3xl font-bold text-amber-700">{analysisResult.data_quality?.warning_issues || 0}</p>
                  <p className="text-sm text-amber-600">Warnings</p>
                </CardContent>
              </Card>
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="p-4 text-center">
                  <Info className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                  <p className="text-3xl font-bold text-blue-700">{analysisResult.data_quality?.info_issues || 0}</p>
                  <p className="text-sm text-blue-600">Info</p>
                </CardContent>
              </Card>
            </div>
            
            {/* Issues List */}
            <Card className="bg-white border-slate-200">
              <CardHeader className="border-b border-slate-100 pb-4">
                <CardTitle className="text-lg font-bold text-slate-900">
                  Data Quality Issues ({analysisResult.data_quality?.total_issues || 0})
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                {analysisResult.data_quality?.issues?.length > 0 ? (
                  <div className="space-y-3">
                    {analysisResult.data_quality.issues.map((issue, idx) => (
                      <div 
                        key={idx} 
                        className={`p-3 rounded-lg border ${SEVERITY_COLORS[issue.severity]}`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {issue.severity === 'critical' && <AlertCircle className="w-4 h-4" />}
                            {issue.severity === 'warning' && <AlertTriangle className="w-4 h-4" />}
                            {issue.severity === 'info' && <Info className="w-4 h-4" />}
                            <span className="font-medium">{issue.message}</span>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {issue.type.replace('_', ' ')}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <CheckCircle2 className="w-12 h-12 text-green-500 mx-auto mb-2" />
                    <p className="text-lg font-medium text-green-700">No data quality issues found!</p>
                    <p className="text-sm text-green-600">Your data is in great shape.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Cleaning Tab */}
          <TabsContent value="cleaning" className="space-y-4" data-testid="magic-cleaning-content">
            {analysisResult.cleaning_suggestions?.length > 0 ? (
              <>
                {/* Actions Bar */}
                <div className="flex items-center justify-between bg-white p-4 rounded-lg border border-slate-200">
                  <div className="flex items-center gap-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={selectAllCleanings}
                      data-testid="select-all-cleanings-btn"
                    >
                      Select All ({analysisResult.cleaning_suggestions.length})
                    </Button>
                    <span className="text-sm text-slate-500">
                      {selectedCount} selected
                    </span>
                  </div>
                  <Button
                    onClick={applySelectedCleanings}
                    disabled={selectedCount === 0 || applying}
                    className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-lg"
                    data-testid="apply-magic-cleaning-btn"
                  >
                    {applying ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Applying...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Apply Selected ({selectedCount})
                      </>
                    )}
                  </Button>
                </div>
                
                {/* Suggestions Grid */}
                <div className="grid gap-4">
                  {analysisResult.cleaning_suggestions.map((suggestion, idx) => (
                    <CleaningSuggestionCard
                      key={`${suggestion.column}-${suggestion.issue}-${idx}`}
                      suggestion={suggestion}
                      isSelected={selectedCleanings[`${suggestion.column}-${suggestion.issue}`] || false}
                      onToggle={() => toggleCleaning(suggestion)}
                      onStrategyChange={handleStrategyChange}
                    />
                  ))}
                </div>
              </>
            ) : (
              <Card className="bg-white border-slate-200">
                <CardContent className="py-12 text-center">
                  <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
                  <p className="text-xl font-medium text-green-700">No cleaning needed!</p>
                  <p className="text-slate-500 mt-2">Your data is already clean and ready for analysis.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
          
          {/* Insights Tab */}
          <TabsContent value="insights" className="space-y-4" data-testid="magic-insights-content">
            {analysisResult.key_insights?.length > 0 ? (
              <div className="grid gap-4">
                {analysisResult.key_insights.map((insight, idx) => (
                  <InsightCard key={idx} insight={insight} />
                ))}
              </div>
            ) : (
              <Card className="bg-white border-slate-200">
                <CardContent className="py-12 text-center">
                  <Sparkles className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <p className="text-lg font-medium text-slate-600">No specific insights discovered</p>
                  <p className="text-slate-500 mt-2">Your data appears to be straightforward.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
          
          {/* Suggested Visualizations Tab */}
          <TabsContent value="visualize" className="space-y-4" data-testid="magic-visualize-content">
            {analysisResult.suggested_visualizations?.length > 0 ? (
              <div className="grid md:grid-cols-2 gap-4">
                {analysisResult.suggested_visualizations.map((viz, idx) => (
                  <VisualizationSuggestionCard
                    key={idx}
                    viz={viz}
                    onView={(v) => {
                      toast.info(`Navigate to Analysis > Visualize tab to create "${v.title}"`);
                    }}
                  />
                ))}
              </div>
            ) : (
              <Card className="bg-white border-slate-200">
                <CardContent className="py-12 text-center">
                  <BarChart3 className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <p className="text-lg font-medium text-slate-600">No visualization suggestions</p>
                  <p className="text-slate-500 mt-2">Add more data columns to get chart recommendations.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      )}
      
      {/* Empty State */}
      {!loading && !analysisResult && (
        <Card className="bg-gradient-to-br from-slate-50 to-white border-slate-200">
          <CardContent className="py-16 text-center">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-100 to-violet-100 flex items-center justify-center mx-auto mb-6">
              <Sparkles className="w-10 h-10 text-indigo-600" />
            </div>
            <h3 className="text-2xl font-bold text-slate-900 mb-2">Ready to analyze your data?</h3>
            <p className="text-slate-500 max-w-md mx-auto mb-8">
              Click the button above to run a comprehensive analysis. You'll get plain-English insights, 
              data quality assessment, and actionable cleaning recommendations.
            </p>
            <div className="flex justify-center gap-4">
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-2">
                  <FileSpreadsheet className="w-6 h-6 text-emerald-600" />
                </div>
                <p className="text-xs text-slate-600">Data Profile</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center mx-auto mb-2">
                  <AlertCircle className="w-6 h-6 text-amber-600" />
                </div>
                <p className="text-xs text-slate-600">Quality Check</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-2">
                  <Settings2 className="w-6 h-6 text-blue-600" />
                </div>
                <p className="text-xs text-slate-600">Auto-Clean</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-violet-100 flex items-center justify-center mx-auto mb-2">
                  <Sparkles className="w-6 h-6 text-violet-600" />
                </div>
                <p className="text-xs text-slate-600">AI Insights</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
