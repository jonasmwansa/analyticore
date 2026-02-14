import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { 
  Sparkles, AlertTriangle, TrendingUp, Lightbulb, CheckCircle2,
  Loader2, RefreshCw, AlertCircle, Info, ChevronDown, ChevronUp
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';
import { analysisAPI } from '../../api';

const severityColors = {
  critical: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', badge: 'bg-red-100 text-red-700' },
  high: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', badge: 'bg-red-100 text-red-700' },
  warning: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', badge: 'bg-amber-100 text-amber-700' },
  medium: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', badge: 'bg-amber-100 text-amber-700' },
  info: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', badge: 'bg-blue-100 text-blue-700' },
  low: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', badge: 'bg-blue-100 text-blue-700' }
};

const priorityColors = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-amber-100 text-amber-700',
  low: 'bg-green-100 text-green-700'
};

export default function QuickInsights({ projectId }) {
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState(null);
  const [expandedSections, setExpandedSections] = useState({
    findings: true,
    quality: true,
    patterns: false,
    recommendations: true
  });

  useEffect(() => {
    if (projectId) {
      loadInsights();
    }
  }, [projectId]);

  const loadInsights = async () => {
    setLoading(true);
    try {
      const response = await analysisAPI.getQuickInsights(projectId);
      setInsights(response.data);
    } catch (error) {
      toast.error('Failed to generate insights');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  if (loading) {
    return (
      <Card className="bg-white border border-slate-200 shadow-sm" data-testid="quick-insights-loading">
        <CardContent className="py-12">
          <div className="flex flex-col items-center justify-center text-center">
            <div className="relative">
              <div className="w-16 h-16 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 animate-pulse flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <Loader2 className="w-6 h-6 text-indigo-500 animate-spin absolute -bottom-1 -right-1" />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-slate-800">Generating AI Insights...</h3>
            <p className="text-sm text-slate-500 mt-1">Analyzing your data patterns and quality</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!insights) {
    return (
      <Card className="bg-white border border-slate-200 shadow-sm">
        <CardContent className="py-8 text-center">
          <AlertCircle className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p className="text-slate-500">Unable to generate insights</p>
          <Button onClick={loadInsights} variant="outline" className="mt-4">
            <RefreshCw className="w-4 h-4 mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4" data-testid="quick-insights">
      {/* Executive Summary */}
      <Card className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 shadow-sm">
        <CardContent className="py-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-800 mb-2">AI Summary</h3>
              <p className="text-slate-700 leading-relaxed" data-testid="executive-summary">
                {insights.executive_summary}
              </p>
            </div>
          </div>
          <div className="flex justify-end mt-4">
            <Button onClick={loadInsights} variant="ghost" size="sm" className="text-indigo-600">
              <RefreshCw className="w-4 h-4 mr-2" />
              Regenerate
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Key Findings */}
      {insights.key_findings?.length > 0 && (
        <Collapsible open={expandedSections.findings} onOpenChange={() => toggleSection('findings')}>
          <Card className="bg-white border border-slate-200 shadow-sm">
            <CollapsibleTrigger asChild>
              <CardHeader className="cursor-pointer hover:bg-slate-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                      <CheckCircle2 className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">Key Findings</CardTitle>
                      <CardDescription>{insights.key_findings.length} insights discovered</CardDescription>
                    </div>
                  </div>
                  {expandedSections.findings ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                </div>
              </CardHeader>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <CardContent className="pt-0">
                <div className="space-y-3" data-testid="key-findings">
                  {insights.key_findings.map((finding, idx) => (
                    <div key={idx} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
                      <Badge className={priorityColors[finding.importance] || priorityColors.low}>
                        {finding.importance}
                      </Badge>
                      <p className="text-sm text-slate-700 flex-1">{finding.finding}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </CollapsibleContent>
          </Card>
        </Collapsible>
      )}

      {/* Data Quality Issues */}
      {insights.data_quality_issues?.length > 0 && (
        <Collapsible open={expandedSections.quality} onOpenChange={() => toggleSection('quality')}>
          <Card className="bg-white border border-slate-200 shadow-sm">
            <CollapsibleTrigger asChild>
              <CardHeader className="cursor-pointer hover:bg-slate-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center">
                      <AlertTriangle className="w-5 h-5 text-amber-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">Data Quality Issues</CardTitle>
                      <CardDescription>{insights.data_quality_issues.length} issues found</CardDescription>
                    </div>
                  </div>
                  {expandedSections.quality ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                </div>
              </CardHeader>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <CardContent className="pt-0">
                <div className="space-y-3" data-testid="quality-issues">
                  {insights.data_quality_issues.map((issue, idx) => {
                    const colors = severityColors[issue.severity] || severityColors.info;
                    return (
                      <div key={idx} className={`p-4 rounded-lg border ${colors.bg} ${colors.border}`}>
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <Badge className={colors.badge}>{issue.severity}</Badge>
                              {issue.affected_columns?.length > 0 && (
                                <span className="text-xs text-slate-500">
                                  Affects: {issue.affected_columns.join(', ')}
                                </span>
                              )}
                            </div>
                            <p className={`text-sm ${colors.text}`}>{issue.issue}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </CollapsibleContent>
          </Card>
        </Collapsible>
      )}

      {/* Patterns Discovered */}
      {insights.patterns_discovered?.length > 0 && (
        <Collapsible open={expandedSections.patterns} onOpenChange={() => toggleSection('patterns')}>
          <Card className="bg-white border border-slate-200 shadow-sm">
            <CollapsibleTrigger asChild>
              <CardHeader className="cursor-pointer hover:bg-slate-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                      <TrendingUp className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">Patterns Discovered</CardTitle>
                      <CardDescription>{insights.patterns_discovered.length} patterns found</CardDescription>
                    </div>
                  </div>
                  {expandedSections.patterns ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                </div>
              </CardHeader>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <CardContent className="pt-0">
                <div className="space-y-3" data-testid="patterns">
                  {insights.patterns_discovered.map((pattern, idx) => (
                    <div key={idx} className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <p className="text-sm text-blue-800">{pattern.pattern}</p>
                      {pattern.columns_involved?.length > 0 && (
                        <div className="flex gap-2 mt-2">
                          {pattern.columns_involved.map((col, i) => (
                            <Badge key={i} variant="outline" className="bg-white text-blue-700 border-blue-300">
                              {col}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </CollapsibleContent>
          </Card>
        </Collapsible>
      )}

      {/* Recommendations */}
      {insights.recommendations?.length > 0 && (
        <Collapsible open={expandedSections.recommendations} onOpenChange={() => toggleSection('recommendations')}>
          <Card className="bg-white border border-slate-200 shadow-sm">
            <CollapsibleTrigger asChild>
              <CardHeader className="cursor-pointer hover:bg-slate-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                      <Lightbulb className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">Recommendations</CardTitle>
                      <CardDescription>{insights.recommendations.length} action items</CardDescription>
                    </div>
                  </div>
                  {expandedSections.recommendations ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                </div>
              </CardHeader>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <CardContent className="pt-0">
                <div className="space-y-3" data-testid="recommendations">
                  {insights.recommendations.map((rec, idx) => (
                    <div key={idx} className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                      <div className="flex items-start gap-3">
                        <Badge className={priorityColors[rec.priority] || priorityColors.low}>
                          {rec.priority}
                        </Badge>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-purple-900">{rec.action}</p>
                          {rec.reason && (
                            <p className="text-xs text-purple-700 mt-1">{rec.reason}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </CollapsibleContent>
          </Card>
        </Collapsible>
      )}
    </div>
  );
}
