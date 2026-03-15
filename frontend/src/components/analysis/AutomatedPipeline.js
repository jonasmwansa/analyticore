import React, { useState, useEffect, useCallback } from 'react';
import { automatedPipelineAPI } from '../../api';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { ScrollArea } from '../ui/scroll-area';
import {
  Play,
  Pause,
  Square,
  CheckCircle,
  XCircle,
  Clock,
  Cpu,
  Database,
  BarChart2,
  FileText,
  Sparkles,
  AlertCircle,
  RefreshCw,
  Download,
  ChevronRight,
  Brain,
  Loader2
} from 'lucide-react';

const STAGE_CONFIG = {
  ingestion: { icon: Database, label: 'Data Ingestion', color: 'bg-blue-500' },
  profiling: { icon: FileText, label: 'Data Profiling', color: 'bg-indigo-500' },
  cleaning: { icon: Sparkles, label: 'Data Cleaning', color: 'bg-purple-500' },
  transformation: { icon: RefreshCw, label: 'Transformation', color: 'bg-pink-500' },
  statistics: { icon: BarChart2, label: 'Statistical Analysis', color: 'bg-red-500' },
  correlation: { icon: Cpu, label: 'Correlation Analysis', color: 'bg-orange-500' },
  insights: { icon: Brain, label: 'AI Insights', color: 'bg-yellow-500' },
  visualization: { icon: BarChart2, label: 'Visualization', color: 'bg-green-500' },
  summary: { icon: FileText, label: 'Executive Summary', color: 'bg-teal-500' },
};

const STAGES_ORDER = ['ingestion', 'profiling', 'cleaning', 'transformation', 'statistics', 'correlation', 'insights', 'visualization', 'summary'];

export default function AutomatedPipeline({ projectId, projectName, onComplete }) {
  const [pipelineId, setPipelineId] = useState(null);
  const [status, setStatus] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [llmStatus, setLLMStatus] = useState(null);
  const [llmEnabled, setLLMEnabled] = useState(true);
  const [activeTab, setActiveTab] = useState('progress');
  const [results, setResults] = useState(null);
  const [exporting, setExporting] = useState(false);

  // Check LLM status on mount
  useEffect(() => {
    automatedPipelineAPI.getLLMStatus()
      .then(res => setLLMStatus(res.data))
      .catch(() => setLLMStatus({ available: false, mode: 'rule_based' }));
  }, []);

  // Download file from base64
  const downloadFile = (content, filename, contentType) => {
    const byteCharacters = atob(content);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  // Export handlers
  const exportPDF = async () => {
    if (!pipelineId) return;
    setExporting(true);
    try {
      const response = await automatedPipelineAPI.exportPDF(pipelineId);
      downloadFile(response.data.content, response.data.filename, response.data.content_type);
    } catch (err) {
      setError('Failed to export PDF');
    }
    setExporting(false);
  };

  const exportExcel = async () => {
    if (!pipelineId) return;
    setExporting(true);
    try {
      const response = await automatedPipelineAPI.exportExcel(pipelineId);
      downloadFile(response.data.content, response.data.filename, response.data.content_type);
    } catch (err) {
      setError('Failed to export Excel');
    }
    setExporting(false);
  };

  const exportCSV = async (section) => {
    if (!pipelineId) return;
    setExporting(true);
    try {
      const response = await automatedPipelineAPI.exportCSV(pipelineId, section);
      downloadFile(response.data.content, response.data.filename, response.data.content_type);
    } catch (err) {
      setError(`Failed to export ${section} CSV`);
    }
    setExporting(false);
  };

  const exportChart = async (chartType, columns = []) => {
    if (!pipelineId) return;
    setExporting(true);
    try {
      const response = await automatedPipelineAPI.exportChart(pipelineId, chartType, columns);
      downloadFile(response.data.content, response.data.filename, response.data.content_type);
    } catch (err) {
      setError(`Failed to export chart`);
    }
    setExporting(false);
  };

  // Start the pipeline
  const startPipeline = async () => {
    setError(null);
    setIsRunning(true);
    setResults(null);
    
    try {
      const response = await automatedPipelineAPI.start(projectId, llmEnabled);
      setPipelineId(response.data.pipeline_id);
      
      if (response.data.status === 'completed') {
        setStatus({
          status: 'completed',
          progress_percent: 100,
          current_stage: 'summary',
          stages_completed: STAGES_ORDER.map(s => ({ stage: s }))
        });
        setResults(response.data.results);
        setIsRunning(false);
        if (onComplete) onComplete(response.data.results);
      } else if (response.data.status === 'failed') {
        setError(response.data.error || 'Pipeline failed');
        setIsRunning(false);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start pipeline');
      setIsRunning(false);
    }
  };

  // Cancel pipeline
  const cancelPipeline = async () => {
    if (!pipelineId) return;
    try {
      await automatedPipelineAPI.cancel(pipelineId);
      setStatus(prev => ({ ...prev, status: 'cancelled' }));
      setIsRunning(false);
    } catch (err) {
      setError('Failed to cancel pipeline');
    }
  };

  // Pause pipeline
  const pausePipeline = async () => {
    if (!pipelineId) return;
    try {
      await automatedPipelineAPI.pause(pipelineId);
      setStatus(prev => ({ ...prev, status: 'paused' }));
    } catch (err) {
      setError('Failed to pause pipeline');
    }
  };

  // Resume pipeline
  const resumePipeline = async () => {
    if (!pipelineId) return;
    try {
      const response = await automatedPipelineAPI.resume(pipelineId);
      if (response.data.status === 'completed') {
        setStatus(prev => ({ ...prev, status: 'completed', progress_percent: 100 }));
        setResults(response.data.results);
        setIsRunning(false);
        if (onComplete) onComplete(response.data.results);
      }
    } catch (err) {
      setError('Failed to resume pipeline');
    }
  };

  const getStatusBadge = (s) => {
    const badges = {
      pending: <Badge variant="secondary"><Clock className="w-3 h-3 mr-1" />Pending</Badge>,
      running: <Badge variant="default" className="bg-blue-500"><Loader2 className="w-3 h-3 mr-1 animate-spin" />Running</Badge>,
      paused: <Badge variant="outline" className="border-yellow-500 text-yellow-500"><Pause className="w-3 h-3 mr-1" />Paused</Badge>,
      completed: <Badge variant="default" className="bg-green-500"><CheckCircle className="w-3 h-3 mr-1" />Completed</Badge>,
      cancelled: <Badge variant="destructive"><XCircle className="w-3 h-3 mr-1" />Cancelled</Badge>,
      failed: <Badge variant="destructive"><AlertCircle className="w-3 h-3 mr-1" />Failed</Badge>,
    };
    return badges[s] || <Badge variant="secondary">{s}</Badge>;
  };

  const getCurrentStageIndex = () => {
    if (!status?.current_stage) return -1;
    return STAGES_ORDER.indexOf(status.current_stage);
  };

  const isStageComplete = (stage) => {
    if (!status?.stages_completed) return false;
    return status.stages_completed.some(s => s.stage === stage);
  };

  const renderStageProgress = () => {
    const currentIndex = getCurrentStageIndex();
    
    return (
      <div className="space-y-3">
        {STAGES_ORDER.map((stage, index) => {
          const config = STAGE_CONFIG[stage];
          const Icon = config.icon;
          const isComplete = isStageComplete(stage);
          const isCurrent = status?.current_stage === stage && status?.status === 'running';
          const isPending = index > currentIndex;
          
          return (
            <div 
              key={stage}
              className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-300 ${
                isComplete ? 'bg-green-50 dark:bg-green-900/20' :
                isCurrent ? 'bg-blue-50 dark:bg-blue-900/20 animate-pulse' :
                'bg-gray-50 dark:bg-gray-800'
              }`}
            >
              <div className={`p-2 rounded-full ${
                isComplete ? 'bg-green-500' :
                isCurrent ? config.color :
                'bg-gray-300 dark:bg-gray-600'
              }`}>
                {isComplete ? (
                  <CheckCircle className="w-4 h-4 text-white" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 text-white animate-spin" />
                ) : (
                  <Icon className="w-4 h-4 text-white" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className={`font-medium ${
                    isComplete ? 'text-green-700 dark:text-green-400' :
                    isCurrent ? 'text-blue-700 dark:text-blue-400' :
                    'text-gray-500'
                  }`}>
                    {config.label}
                  </span>
                  {isComplete && (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  )}
                  {isCurrent && (
                    <span className="text-xs text-blue-500">Processing...</span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderResults = () => {
    if (!results) return null;

    return (
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-6 mb-4">
          <TabsTrigger value="summary">Summary</TabsTrigger>
          <TabsTrigger value="cleaning">Cleaning</TabsTrigger>
          <TabsTrigger value="statistics">Statistics</TabsTrigger>
          <TabsTrigger value="correlation">Correlation</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="visualization">Visuals</TabsTrigger>
        </TabsList>

        <TabsContent value="summary" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Executive Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              {results.summary && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">{results.summary.total_rows?.toLocaleString()}</div>
                      <div className="text-sm text-gray-600">Total Rows</div>
                    </div>
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{results.summary.total_columns}</div>
                      <div className="text-sm text-gray-600">Columns</div>
                    </div>
                    <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">{results.summary.quality_score || 0}</div>
                      <div className="text-sm text-gray-600">Quality Score</div>
                    </div>
                    <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">{results.summary.quality_label || 'N/A'}</div>
                      <div className="text-sm text-gray-600">Quality Label</div>
                    </div>
                  </div>
                  
                  {results.summary.llm_summary && (
                    <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Brain className="w-5 h-5 text-purple-500" />
                        <span className="font-medium text-purple-700 dark:text-purple-300">AI-Generated Summary</span>
                      </div>
                      <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{results.summary.llm_summary}</p>
                    </div>
                  )}

                  {results.summary.executive_summary?.text && (
                    <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <p className="text-gray-700 dark:text-gray-300">{results.summary.executive_summary.text}</p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="cleaning" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                Data Cleaning Results
              </CardTitle>
            </CardHeader>
            <CardContent>
              {results.cleaning && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="text-lg font-bold">{results.cleaning.rows_before?.toLocaleString()}</div>
                      <div className="text-sm text-gray-600">Rows Before</div>
                    </div>
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="text-lg font-bold text-green-600">{results.cleaning.rows_after?.toLocaleString()}</div>
                      <div className="text-sm text-gray-600">Rows After</div>
                    </div>
                  </div>

                  {results.cleaning.applied_actions?.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Applied Cleaning Actions:</h4>
                      <div className="space-y-2">
                        {results.cleaning.applied_actions.map((action, idx) => (
                          <div key={idx} className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                            <CheckCircle className="w-4 h-4 text-green-500" />
                            <span className="font-mono text-sm">{action.column}</span>
                            <ChevronRight className="w-4 h-4 text-gray-400" />
                            <Badge variant="outline">{action.strategy}</Badge>
                            {action.values_affected && (
                              <span className="text-xs text-gray-500">({action.values_affected} values)</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {results.cleaning.llm_insight && (
                    <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Brain className="w-4 h-4 text-purple-500" />
                        <span className="font-medium text-purple-700">AI Cleaning Insight</span>
                      </div>
                      <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{results.cleaning.llm_insight}</p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="statistics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart2 className="w-5 h-5" />
                Statistical Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              {results.statistics && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <div className="text-lg font-bold">{results.statistics.summary?.total_rows?.toLocaleString()}</div>
                      <div className="text-xs text-gray-600">Total Rows</div>
                    </div>
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="text-lg font-bold">{results.statistics.summary?.numeric_columns}</div>
                      <div className="text-xs text-gray-600">Numeric Columns</div>
                    </div>
                    <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                      <div className="text-lg font-bold">{results.statistics.summary?.categorical_columns}</div>
                      <div className="text-xs text-gray-600">Categorical</div>
                    </div>
                    <div className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                      <div className="text-lg font-bold">{results.statistics.summary?.total_missing?.toLocaleString()}</div>
                      <div className="text-xs text-gray-600">Missing Values</div>
                    </div>
                  </div>

                  {results.statistics.numeric_summary && Object.keys(results.statistics.numeric_summary).length > 0 && (
                    <ScrollArea className="h-64">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-100 dark:bg-gray-800">
                          <tr>
                            <th className="p-2 text-left">Column</th>
                            <th className="p-2 text-right">Mean</th>
                            <th className="p-2 text-right">Std</th>
                            <th className="p-2 text-right">Min</th>
                            <th className="p-2 text-right">Max</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(results.statistics.numeric_summary).map(([col, stats]) => (
                            <tr key={col} className="border-b">
                              <td className="p-2 font-mono">{col}</td>
                              <td className="p-2 text-right">{stats.mean?.toFixed(2)}</td>
                              <td className="p-2 text-right">{stats.std?.toFixed(2)}</td>
                              <td className="p-2 text-right">{stats.min?.toFixed(2)}</td>
                              <td className="p-2 text-right">{stats.max?.toFixed(2)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </ScrollArea>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="correlation" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Cpu className="w-5 h-5" />
                Correlation Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              {results.correlation && (
                <div className="space-y-4">
                  {results.correlation.top_correlations?.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-3">Top Correlations:</h4>
                      <div className="space-y-2">
                        {results.correlation.top_correlations.slice(0, 10).map((corr, idx) => (
                          <div key={idx} className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                            <span className="font-mono text-sm">{corr.column1}</span>
                            <span className="text-gray-400">↔</span>
                            <span className="font-mono text-sm">{corr.column2}</span>
                            <div className="flex-1" />
                            <Badge variant={corr.correlation > 0.7 ? 'default' : 'secondary'}>
                              {corr.correlation?.toFixed(3)}
                            </Badge>
                            <Badge variant="outline">{corr.strength}</Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {results.correlation.llm_insight && (
                    <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Brain className="w-4 h-4 text-purple-500" />
                        <span className="font-medium text-purple-700">AI Correlation Insight</span>
                      </div>
                      <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{results.correlation.llm_insight}</p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5" />
                AI-Powered Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              {results.insights && (
                <div className="space-y-4">
                  {results.insights.key_insights?.map((insight, idx) => (
                    <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-full ${
                          insight.priority === 'high' ? 'bg-red-100 text-red-500' :
                          insight.priority === 'medium' ? 'bg-yellow-100 text-yellow-500' :
                          'bg-blue-100 text-blue-500'
                        }`}>
                          <Sparkles className="w-4 h-4" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium">{insight.title}</h4>
                          <p className="text-sm text-gray-600 mt-1">{insight.message}</p>
                          <Badge variant="outline" className="mt-2">{insight.type}</Badge>
                        </div>
                      </div>
                    </div>
                  ))}

                  {results.insights.llm_insights?.executive && (
                    <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Brain className="w-5 h-5 text-purple-500" />
                        <span className="font-medium text-purple-700">Executive AI Insight</span>
                      </div>
                      <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{results.insights.llm_insights.executive}</p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="visualization" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <BarChart2 className="w-5 h-5" />
                  Smart Visualization Recommendations
                </CardTitle>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => exportCSV('visualizations')}
                  disabled={exporting}
                  className="flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Export CSV
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {/* Smart Recommendations */}
              {results.visualization?.smart_recommendations?.recommendations?.length > 0 ? (
                <div className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    {results.visualization.smart_recommendations.recommendations.map((rec, idx) => (
                      <div key={idx} className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">{rec.title}</h4>
                            <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{rec.description}</p>
                          </div>
                          <Badge variant="secondary" className="ml-2">
                            Priority: {rec.priority}/10
                          </Badge>
                        </div>
                        <div className="flex flex-wrap items-center gap-2 mt-3">
                          <Badge variant="default" className="bg-purple-500">{rec.chart_type}</Badge>
                          {rec.columns?.slice(0, 3).map((col, i) => (
                            <Badge key={i} variant="outline">{col}</Badge>
                          ))}
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 italic">
                          {rec.reasoning}
                        </p>
                        {results.visualization?.llm_chart_insights?.[rec.chart_type] && (
                          <div className="mt-3 p-2 bg-purple-50 dark:bg-purple-900/20 rounded text-sm">
                            <div className="flex items-center gap-1 text-purple-600 dark:text-purple-400 font-medium mb-1">
                              <Brain className="w-3 h-3" /> AI Insight
                            </div>
                            <p className="text-gray-700 dark:text-gray-300 text-xs">
                              {results.visualization.llm_chart_insights[rec.chart_type].narrative}
                            </p>
                          </div>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          className="mt-3"
                          onClick={() => exportChart(rec.chart_type, rec.columns)}
                          disabled={exporting}
                        >
                          <Download className="w-3 h-3 mr-1" />
                          Export Chart
                        </Button>
                      </div>
                    ))}
                  </div>
                  
                  {/* Data Summary */}
                  {results.visualization?.smart_recommendations?.data_summary && (
                    <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <h5 className="font-medium text-blue-800 dark:text-blue-300 mb-2">Data Profile</h5>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                        <div>
                          <span className="text-gray-600 dark:text-gray-400">Numeric Columns:</span>
                          <span className="ml-2 font-medium">{results.visualization.smart_recommendations.data_summary.numeric_columns}</span>
                        </div>
                        <div>
                          <span className="text-gray-600 dark:text-gray-400">Categorical:</span>
                          <span className="ml-2 font-medium">{results.visualization.smart_recommendations.data_summary.categorical_columns}</span>
                        </div>
                        <div>
                          <span className="text-gray-600 dark:text-gray-400">DateTime:</span>
                          <span className="ml-2 font-medium">{results.visualization.smart_recommendations.data_summary.datetime_columns}</span>
                        </div>
                        <div>
                          <span className="text-gray-600 dark:text-gray-400">Best Charts:</span>
                          <span className="ml-2 font-medium">{results.visualization.smart_recommendations.data_summary.best_chart_types?.join(', ')}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : results.visualization?.suggested_visualizations?.length > 0 ? (
                <div className="grid gap-4 md:grid-cols-2">
                  {results.visualization.suggested_visualizations.map((viz, idx) => (
                    <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <h4 className="font-medium">{viz.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{viz.description}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant="default">{viz.type}</Badge>
                        {viz.columns?.slice(0, 3).map((col, i) => (
                          <Badge key={i} variant="outline">{col}</Badge>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No visualization recommendations available.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-purple-500" />
                Automated Analysis Pipeline
              </CardTitle>
              <CardDescription>
                End-to-end data analysis with AI-powered insights
              </CardDescription>
            </div>
            {status && getStatusBadge(status.status)}
          </div>
        </CardHeader>
        <CardContent>
          {/* LLM Status */}
          <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="flex items-center gap-2">
              <Brain className={`w-5 h-5 ${llmStatus?.available ? 'text-green-500' : 'text-gray-400'}`} />
              <span className="text-sm">
                Local AI: {llmStatus?.available ? 
                  <span className="text-green-600 font-medium">Available ({llmStatus?.model})</span> : 
                  <span className="text-gray-500">Using rule-based analysis</span>
                }
              </span>
            </div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={llmEnabled}
                onChange={(e) => setLLMEnabled(e.target.checked)}
                disabled={!llmStatus?.available || isRunning}
                className="rounded"
              />
              <span className="text-sm">Enable AI Insights</span>
            </label>
          </div>

          {/* Control Buttons */}
          <div className="flex items-center gap-3">
            {!isRunning && status?.status !== 'completed' && (
              <Button onClick={startPipeline} className="flex items-center gap-2">
                <Play className="w-4 h-4" />
                Start Analysis
              </Button>
            )}
            
            {isRunning && status?.status === 'running' && (
              <>
                <Button variant="outline" onClick={pausePipeline} className="flex items-center gap-2">
                  <Pause className="w-4 h-4" />
                  Pause
                </Button>
                <Button variant="destructive" onClick={cancelPipeline} className="flex items-center gap-2">
                  <Square className="w-4 h-4" />
                  Cancel
                </Button>
              </>
            )}
            
            {status?.status === 'paused' && (
              <>
                <Button onClick={resumePipeline} className="flex items-center gap-2">
                  <Play className="w-4 h-4" />
                  Resume
                </Button>
                <Button variant="destructive" onClick={cancelPipeline} className="flex items-center gap-2">
                  <Square className="w-4 h-4" />
                  Cancel
                </Button>
              </>
            )}
            
            {status?.status === 'completed' && (
              <Button onClick={startPipeline} variant="outline" className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4" />
                Re-run Analysis
              </Button>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 rounded-lg flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Progress Display */}
      {(isRunning || status) && status?.status !== 'completed' && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Pipeline Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">
                  {status?.current_stage ? STAGE_CONFIG[status.current_stage]?.label : 'Starting...'}
                </span>
                <span className="text-sm text-gray-500">{status?.progress_percent || 0}%</span>
              </div>
              <Progress value={status?.progress_percent || 0} className="h-2" />
            </div>
            {renderStageProgress()}
          </CardContent>
        </Card>
      )}

      {/* Results Display */}
      {status?.status === 'completed' && results && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  Analysis Complete
                </CardTitle>
                <CardDescription>
                  Processed in {status?.duration_seconds?.toFixed(1)} seconds
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={exportPDF}
                  disabled={exporting}
                  className="flex items-center gap-2"
                >
                  {exporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                  PDF Report
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={exportExcel}
                  disabled={exporting}
                  className="flex items-center gap-2"
                >
                  {exporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                  Excel
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {renderResults()}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
