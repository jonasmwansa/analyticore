import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { 
  Settings2, AlertTriangle, Check, X, Play, Loader2, ChevronDown, ChevronRight,
  Trash2, Type, Hash, Calendar, RotateCcw, Scissors, ArrowUpDown
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Input } from '../ui/input';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';
import { analysisAPI } from '../../api';

const typeIcons = {
  numeric: <Hash className="w-4 h-4" />,
  categorical: <Type className="w-4 h-4" />,
  datetime: <Calendar className="w-4 h-4" />,
  text: <Type className="w-4 h-4" />
};

const typeColors = {
  numeric: 'bg-blue-100 text-blue-700 border-blue-200',
  categorical: 'bg-green-100 text-green-700 border-green-200',
  datetime: 'bg-purple-100 text-purple-700 border-purple-200',
  text: 'bg-slate-100 text-slate-700 border-slate-200'
};

const severityColors = {
  critical: 'bg-red-100 text-red-700',
  warning: 'bg-amber-100 text-amber-700',
  info: 'bg-blue-100 text-blue-700'
};

export default function ColumnActions({ projectId, onDataChanged }) {
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(null);
  const [columnActions, setColumnActions] = useState([]);
  const [expandedColumns, setExpandedColumns] = useState({});
  const [customValues, setCustomValues] = useState({});

  useEffect(() => {
    if (projectId) {
      loadColumnActions();
    }
  }, [projectId]);

  const loadColumnActions = async () => {
    setLoading(true);
    try {
      const response = await analysisAPI.getColumnActions(projectId);
      setColumnActions(response.data.columns || []);
      // Auto-expand columns with issues
      const expanded = {};
      (response.data.columns || []).forEach(col => {
        if (col.issues_detected?.length > 0) {
          expanded[col.column] = true;
        }
      });
      setExpandedColumns(expanded);
    } catch (error) {
      toast.error('Failed to load column actions');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const toggleColumn = (columnName) => {
    setExpandedColumns(prev => ({
      ...prev,
      [columnName]: !prev[columnName]
    }));
  };

  const applyAction = async (column, action, strategy = null) => {
    const actionKey = `${column}-${action}-${strategy}`;
    setApplying(actionKey);
    
    try {
      const data = {
        column,
        action,
        strategy,
        value: customValues[`${column}-constant`]
      };
      
      const response = await analysisAPI.applyColumnAction(projectId, data);
      toast.success(response.data.changes?.join('. ') || 'Action applied successfully');
      
      // Reload column actions and notify parent
      await loadColumnActions();
      if (onDataChanged) {
        onDataChanged();
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to apply action');
    } finally {
      setApplying(null);
    }
  };

  if (loading) {
    return (
      <Card className="bg-white border border-slate-200 shadow-sm">
        <CardContent className="py-12">
          <div className="flex flex-col items-center justify-center">
            <Loader2 className="w-10 h-10 text-indigo-500 animate-spin mb-4" />
            <p className="text-slate-500">Analyzing columns...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const columnsWithIssues = columnActions.filter(c => c.issues_detected?.length > 0);
  const columnsWithoutIssues = columnActions.filter(c => !c.issues_detected?.length);

  return (
    <div className="space-y-4" data-testid="column-actions">
      {/* Summary */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="bg-white border border-slate-200 shadow-sm">
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
                <Settings2 className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{columnActions.length}</p>
                <p className="text-xs text-slate-500">Total Columns</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white border border-slate-200 shadow-sm">
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{columnsWithIssues.length}</p>
                <p className="text-xs text-slate-500">With Issues</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white border border-slate-200 shadow-sm">
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                <Check className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{columnsWithoutIssues.length}</p>
                <p className="text-xs text-slate-500">Clean Columns</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Columns with Issues */}
      {columnsWithIssues.length > 0 && (
        <Card className="bg-white border border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-100 pb-4">
            <CardTitle className="text-lg flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-500" />
              Columns Requiring Attention
            </CardTitle>
            <CardDescription>Review and apply recommended actions</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            {columnsWithIssues.map((col, idx) => (
              <Collapsible 
                key={col.column}
                open={expandedColumns[col.column]}
                onOpenChange={() => toggleColumn(col.column)}
              >
                <CollapsibleTrigger asChild>
                  <div 
                    className={`px-4 py-3 cursor-pointer hover:bg-slate-50 transition-colors flex items-center justify-between ${idx !== columnsWithIssues.length - 1 ? 'border-b border-slate-100' : ''}`}
                    data-testid={`column-${col.column}`}
                  >
                    <div className="flex items-center gap-3">
                      {expandedColumns[col.column] ? (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-slate-400" />
                      )}
                      <div className={`w-8 h-8 rounded flex items-center justify-center ${typeColors[col.type]}`}>
                        {typeIcons[col.type]}
                      </div>
                      <div>
                        <span className="font-medium text-slate-800">{col.column}</span>
                        <Badge variant="outline" className="ml-2 text-xs">{col.type}</Badge>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {col.issues_detected?.map((issue, i) => (
                        <Badge key={i} className={severityColors[issue.severity]}>
                          {issue.type.replace('_', ' ')}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <div className="px-4 pb-4 pt-2 bg-slate-50 border-b border-slate-100">
                    {/* Issues */}
                    {col.issues_detected?.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Issues Detected</h4>
                        <div className="space-y-2">
                          {col.issues_detected.map((issue, i) => (
                            <div key={i} className={`p-2 rounded text-sm ${
                              issue.severity === 'critical' ? 'bg-red-50 text-red-700' :
                              issue.severity === 'warning' ? 'bg-amber-50 text-amber-700' :
                              'bg-blue-50 text-blue-700'
                            }`}>
                              {issue.description}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Actions */}
                    {col.recommended_actions?.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Available Actions</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {col.recommended_actions.map((action, i) => {
                            const actionKey = `${col.column}-${action.action}-${action.strategy}`;
                            const isApplying = applying === actionKey;
                            
                            return (
                              <div 
                                key={i} 
                                className="flex items-center justify-between p-3 bg-white rounded-lg border border-slate-200"
                              >
                                <div className="flex-1 mr-3">
                                  <p className="text-sm font-medium text-slate-800">{action.label}</p>
                                  <p className="text-xs text-slate-500">{action.description}</p>
                                </div>
                                
                                {action.strategy === 'constant' ? (
                                  <div className="flex items-center gap-2">
                                    <Input
                                      placeholder="Value"
                                      className="w-24 h-8 text-sm"
                                      value={customValues[`${col.column}-constant`] || ''}
                                      onChange={(e) => setCustomValues(prev => ({
                                        ...prev,
                                        [`${col.column}-constant`]: e.target.value
                                      }))}
                                    />
                                    <Button
                                      size="sm"
                                      onClick={() => applyAction(col.column, action.action, action.strategy)}
                                      disabled={isApplying || !customValues[`${col.column}-constant`]}
                                      className="h-8"
                                    >
                                      {isApplying ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                                    </Button>
                                  </div>
                                ) : (
                                  <Button
                                    size="sm"
                                    onClick={() => applyAction(col.column, action.action, action.strategy)}
                                    disabled={isApplying}
                                    className="h-8"
                                    data-testid={`apply-${col.column}-${action.action}`}
                                  >
                                    {isApplying ? (
                                      <Loader2 className="w-4 h-4 animate-spin" />
                                    ) : (
                                      <>
                                        <Play className="w-4 h-4 mr-1" />
                                        Apply
                                      </>
                                    )}
                                  </Button>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                </CollapsibleContent>
              </Collapsible>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Clean Columns */}
      {columnsWithoutIssues.length > 0 && (
        <Card className="bg-white border border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-100 pb-4">
            <CardTitle className="text-lg flex items-center gap-2">
              <Check className="w-5 h-5 text-green-500" />
              Clean Columns
            </CardTitle>
            <CardDescription>No issues detected in these columns</CardDescription>
          </CardHeader>
          <CardContent className="p-4">
            <div className="flex flex-wrap gap-2">
              {columnsWithoutIssues.map(col => (
                <Badge 
                  key={col.column} 
                  variant="outline" 
                  className={`px-3 py-1.5 ${typeColors[col.type]}`}
                >
                  <span className="mr-1.5">{typeIcons[col.type]}</span>
                  {col.column}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <Card className="bg-white border border-slate-200 shadow-sm">
        <CardHeader className="border-b border-slate-100 pb-4">
          <CardTitle className="text-lg">Quick Actions</CardTitle>
          <CardDescription>Apply common transformations to all applicable columns</CardDescription>
        </CardHeader>
        <CardContent className="p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Button
              variant="outline"
              className="h-auto py-4 flex flex-col items-center gap-2"
              onClick={() => toast.info('Select a column to remove duplicates')}
            >
              <Trash2 className="w-5 h-5 text-red-500" />
              <span className="text-sm">Remove Duplicates</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto py-4 flex flex-col items-center gap-2"
              onClick={() => toast.info('Select a column to trim text')}
            >
              <Scissors className="w-5 h-5 text-blue-500" />
              <span className="text-sm">Trim All Text</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto py-4 flex flex-col items-center gap-2"
              onClick={() => toast.info('Select a column to convert type')}
            >
              <ArrowUpDown className="w-5 h-5 text-purple-500" />
              <span className="text-sm">Convert Types</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto py-4 flex flex-col items-center gap-2"
              onClick={loadColumnActions}
            >
              <RotateCcw className="w-5 h-5 text-slate-500" />
              <span className="text-sm">Refresh Analysis</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
