import React, { useState, useEffect, useMemo } from 'react';
import { toast } from 'sonner';
import {
  BarChart, Bar, LineChart, Line, ScatterChart, Scatter, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell,
  AreaChart, Area
} from 'recharts';
import { 
  BarChart3, LineChart as LineIcon, PieChart as PieIcon, Activity,
  ScatterChart as ScatterIcon, TrendingUp, ArrowUpDown, Info, Table2,
  Sparkles, Settings2
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Tooltip as TooltipUI, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';
import { analysisAPI } from '../../api';
import QuickInsights from './QuickInsights';
import ColumnActions from './ColumnActions';

const CHART_COLORS = [
  '#6366F1', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981', 
  '#3B82F6', '#EF4444', '#14B8A6', '#F97316', '#84CC16'
];

const StatCard = ({ title, value, subtitle, icon: Icon, color = '#6366F1' }) => (
  <Card className="stat-card bg-white border border-slate-200 shadow-sm">
    <CardContent className="p-5">
      <div className="flex items-center gap-4">
        <div 
          className="w-12 h-12 rounded-xl flex items-center justify-center"
          style={{ backgroundColor: `${color}15` }}
        >
          <Icon className="w-6 h-6" style={{ color }} />
        </div>
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <p className="text-2xl font-bold text-slate-900">{value}</p>
          {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
        </div>
      </div>
    </CardContent>
  </Card>
);

const StatisticsTable = ({ data, title }) => {
  if (!data || Object.keys(data).length === 0) return null;
  
  const columns = Object.keys(data);
  const metrics = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max', 'missing', 'skewness'];
  
  return (
    <Card className="bg-white border border-slate-200 shadow-sm overflow-hidden">
      <CardHeader className="border-b border-slate-100 pb-4">
        <CardTitle className="text-lg font-semibold text-slate-900">{title}</CardTitle>
        <CardDescription>Descriptive statistics for numeric columns</CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50">
                <th className="text-left py-3 px-4 font-semibold text-slate-600 border-b border-slate-200">Metric</th>
                {columns.map(col => (
                  <th key={col} className="text-right py-3 px-4 font-semibold text-slate-600 border-b border-slate-200">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {metrics.map((metric, idx) => (
                <tr key={metric} className={idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}>
                  <td className="py-2.5 px-4 font-medium text-slate-700 capitalize border-b border-slate-100">
                    {metric === '50%' ? 'Median' : metric}
                  </td>
                  {columns.map(col => (
                    <td key={col} className="py-2.5 px-4 text-right text-slate-600 border-b border-slate-100 font-mono text-xs">
                      {data[col]?.[metric] !== undefined && data[col]?.[metric] !== null
                        ? typeof data[col][metric] === 'number' 
                          ? data[col][metric].toLocaleString(undefined, { maximumFractionDigits: 4 })
                          : data[col][metric]
                        : '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

const CorrelationHeatmap = ({ data, columns }) => {
  if (!data || data.length === 0) return null;
  
  const getCorrelationColor = (value) => {
    if (value === null || value === undefined) return '#f1f5f9';
    const intensity = Math.abs(value);
    if (value > 0) {
      return `rgba(99, 102, 241, ${intensity})`;
    } else {
      return `rgba(239, 68, 68, ${intensity})`;
    }
  };
  
  return (
    <Card className="bg-white border border-slate-200 shadow-sm">
      <CardHeader className="border-b border-slate-100 pb-4">
        <CardTitle className="text-lg font-semibold text-slate-900">Correlation Matrix</CardTitle>
        <CardDescription>Pearson correlation coefficients between numeric variables</CardDescription>
      </CardHeader>
      <CardContent className="p-4">
        <div className="overflow-x-auto">
          <div className="inline-block min-w-full">
            <div className="flex">
              <div className="w-24 flex-shrink-0"></div>
              {columns.map(col => (
                <div key={col} className="w-20 flex-shrink-0 text-center">
                  <span className="text-xs font-medium text-slate-600 truncate block px-1" title={col}>
                    {col.length > 10 ? col.slice(0, 10) + '...' : col}
                  </span>
                </div>
              ))}
            </div>
            {columns.map(row => (
              <div key={row} className="flex items-center">
                <div className="w-24 flex-shrink-0 py-1">
                  <span className="text-xs font-medium text-slate-600 truncate block" title={row}>
                    {row.length > 12 ? row.slice(0, 12) + '...' : row}
                  </span>
                </div>
                {columns.map(col => {
                  const cellData = data.find(d => d.x === col && d.y === row);
                  const value = cellData?.value;
                  return (
                    <div
                      key={`${row}-${col}`}
                      className="w-20 h-12 flex-shrink-0 flex items-center justify-center border border-slate-100 text-xs font-mono"
                      style={{ backgroundColor: getCorrelationColor(value) }}
                      title={`${row} vs ${col}: ${value?.toFixed(4) || 'N/A'}`}
                    >
                      <span className={value && Math.abs(value) > 0.5 ? 'text-white' : 'text-slate-700'}>
                        {value?.toFixed(2) || '-'}
                      </span>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
        <div className="flex items-center justify-center gap-4 mt-4 text-xs text-slate-500">
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: 'rgba(239, 68, 68, 0.8)' }}></div>
            <span>Negative</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded bg-slate-100"></div>
            <span>None</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: 'rgba(99, 102, 241, 0.8)' }}></div>
            <span>Positive</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const DistributionChart = ({ data, column }) => {
  if (!data || !data.histogram) return null;
  
  return (
    <Card className="bg-white border border-slate-200 shadow-sm">
      <CardHeader className="border-b border-slate-100 pb-4">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-semibold text-slate-900">Distribution: {column}</CardTitle>
            <CardDescription>
              {data.is_symmetric ? 'Symmetric' : data.distribution_type?.replace('_', ' ')} distribution
              {data.skewness !== null && ` (Skew: ${data.skewness})`}
            </CardDescription>
          </div>
          {data.normality_tests?.shapiro && (
            <Badge 
              className={data.normality_tests.shapiro.is_normal 
                ? 'bg-green-100 text-green-700' 
                : 'bg-amber-100 text-amber-700'
              }
            >
              {data.normality_tests.shapiro.is_normal ? 'Normal' : 'Non-Normal'}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="p-4">
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={data.histogram}>
            <defs>
              <linearGradient id="colorHist" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#6366F1" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis 
              dataKey="bin_center" 
              tick={{ fontSize: 11, fill: '#64748b' }}
              tickFormatter={(v) => v.toLocaleString(undefined, { maximumFractionDigits: 2 })}
            />
            <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#fff', 
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                fontSize: '12px'
              }}
              formatter={(value, name) => [value, 'Count']}
              labelFormatter={(label) => `Range: ${label.toLocaleString(undefined, { maximumFractionDigits: 2 })}`}
            />
            <Area 
              type="monotone" 
              dataKey="count" 
              stroke="#6366F1" 
              strokeWidth={2}
              fill="url(#colorHist)" 
            />
          </AreaChart>
        </ResponsiveContainer>
        
        {data.box_plot && (
          <div className="mt-4 p-4 bg-slate-50 rounded-lg">
            <h4 className="text-sm font-semibold text-slate-700 mb-3">Box Plot Statistics</h4>
            <div className="grid grid-cols-5 gap-4 text-center">
              <div>
                <p className="text-xs text-slate-500">Min</p>
                <p className="font-mono text-sm font-medium text-slate-900">{data.box_plot.whisker_low?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Q1 (25%)</p>
                <p className="font-mono text-sm font-medium text-slate-900">{data.box_plot.q1?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Median</p>
                <p className="font-mono text-sm font-medium text-indigo-600">{data.box_plot.median?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Q3 (75%)</p>
                <p className="font-mono text-sm font-medium text-slate-900">{data.box_plot.q3?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Max</p>
                <p className="font-mono text-sm font-medium text-slate-900">{data.box_plot.whisker_high?.toLocaleString()}</p>
              </div>
            </div>
            {data.box_plot.outliers_count > 0 && (
              <p className="mt-3 text-xs text-amber-600">
                {data.box_plot.outliers_count} outliers detected
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default function AnalysisDashboard({ projectId }) {
  const [loading, setLoading] = useState(true);
  const [statistics, setStatistics] = useState(null);
  const [correlation, setCorrelation] = useState(null);
  const [distribution, setDistribution] = useState(null);
  const [columns, setColumns] = useState({ numeric: [], categorical: [], datetime: [] });
  const [selectedDistColumn, setSelectedDistColumn] = useState('');
  const [chartData, setChartData] = useState(null);
  const [selectedChartType, setSelectedChartType] = useState('bar');
  const [xColumn, setXColumn] = useState('');
  const [yColumn, setYColumn] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (projectId) {
      loadAllData();
    }
  }, [projectId]);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [statsRes, corrRes, colsRes] = await Promise.all([
        analysisAPI.getStatistics(projectId),
        analysisAPI.getCorrelation(projectId),
        analysisAPI.getColumns(projectId)
      ]);
      
      setStatistics(statsRes.data);
      setCorrelation(corrRes.data);
      setColumns(colsRes.data);
      
      if (colsRes.data.numeric?.length > 0) {
        setSelectedDistColumn(colsRes.data.numeric[0]);
        setYColumn(colsRes.data.numeric[0]);
        loadDistribution(colsRes.data.numeric[0]);
      }
      
      if (colsRes.data.categorical?.length > 0) {
        setXColumn(colsRes.data.categorical[0]);
      } else if (colsRes.data.numeric?.length > 0) {
        setXColumn(colsRes.data.numeric[0]);
      }
    } catch (error) {
      toast.error('Failed to load analysis data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadDistribution = async (column) => {
    try {
      const res = await analysisAPI.getDistribution(projectId, column, 25);
      setDistribution(res.data.distributions?.[column]);
    } catch (error) {
      console.error('Failed to load distribution:', error);
    }
  };

  const loadChartData = async () => {
    if (!selectedChartType) return;
    
    try {
      const options = {};
      if (xColumn) options.x = xColumn;
      if (yColumn) options.y = yColumn;
      
      const res = await analysisAPI.getChartData(projectId, selectedChartType, options);
      setChartData(res.data);
    } catch (error) {
      toast.error('Failed to load chart data');
    }
  };

  useEffect(() => {
    if (projectId && (xColumn || yColumn)) {
      loadChartData();
    }
  }, [selectedChartType, xColumn, yColumn]);

  useEffect(() => {
    if (selectedDistColumn) {
      loadDistribution(selectedDistColumn);
    }
  }, [selectedDistColumn]);

  const renderChart = () => {
    if (!chartData || !chartData.data || chartData.data.length === 0) {
      return (
        <div className="flex items-center justify-center h-64 text-slate-400">
          <p>No data available for this chart type</p>
        </div>
      );
    }

    const commonProps = {
      data: chartData.data,
      margin: { top: 20, right: 30, left: 20, bottom: 20 }
    };

    switch (chartData.type) {
      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={350}>
            <ScatterChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="x" name={chartData.x_column} tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis dataKey="y" name={chartData.y_column} tick={{ fontSize: 11, fill: '#64748b' }} />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ borderRadius: '8px' }} />
              <Scatter name="Data" fill="#6366F1" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={350}>
            <LineChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="x" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
              <Tooltip contentStyle={{ borderRadius: '8px' }} />
              <Legend />
              <Line type="monotone" dataKey="y" stroke="#6366F1" strokeWidth={2} dot={{ fill: '#6366F1', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={350}>
            <BarChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="x" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
              <Tooltip contentStyle={{ borderRadius: '8px' }} />
              <Bar dataKey="y" fill="#6366F1" radius={[4, 4, 0, 0]}>
                {chartData.data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={chartData.data}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={120}
                label={({ name, percentage }) => `${name}: ${percentage}%`}
                labelLine={{ stroke: '#94a3b8' }}
              >
                {chartData.data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: '8px' }} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'histogram':
        return (
          <ResponsiveContainer width="100%" height={350}>
            <BarChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis 
                dataKey="x" 
                tick={{ fontSize: 11, fill: '#64748b' }}
                tickFormatter={(v) => v.toLocaleString(undefined, { maximumFractionDigits: 1 })}
              />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
              <Tooltip contentStyle={{ borderRadius: '8px' }} />
              <Bar dataKey="count" fill="#6366F1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'box':
        return (
          <div className="space-y-4">
            {chartData.data.map((item, idx) => (
              <div key={item.column} className="p-4 bg-slate-50 rounded-lg">
                <h4 className="font-medium text-slate-700 mb-3">{item.column}</h4>
                <div className="relative h-8 bg-white rounded border border-slate-200">
                  {/* Box plot visualization */}
                  <div 
                    className="absolute h-full bg-indigo-100 border-l-2 border-r-2 border-indigo-400"
                    style={{
                      left: `${((item.q1 - item.min) / (item.max - item.min)) * 100}%`,
                      width: `${((item.q3 - item.q1) / (item.max - item.min)) * 100}%`
                    }}
                  />
                  <div 
                    className="absolute w-0.5 h-full bg-indigo-600"
                    style={{ left: `${((item.median - item.min) / (item.max - item.min)) * 100}%` }}
                  />
                </div>
                <div className="flex justify-between mt-2 text-xs text-slate-500">
                  <span>{item.min?.toLocaleString()}</span>
                  <span>Q1: {item.q1?.toLocaleString()}</span>
                  <span>Med: {item.median?.toLocaleString()}</span>
                  <span>Q3: {item.q3?.toLocaleString()}</span>
                  <span>{item.max?.toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        );

      default:
        return <p className="text-center text-slate-400">Unsupported chart type</p>;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-500">Loading analysis...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="analysis-dashboard">
      {/* Summary Stats */}
      {statistics?.summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            title="Total Rows"
            value={statistics.summary.total_rows?.toLocaleString()}
            icon={Table2}
            color="#6366F1"
          />
          <StatCard
            title="Columns"
            value={statistics.summary.total_columns}
            subtitle={`${statistics.summary.numeric_columns} numeric`}
            icon={Activity}
            color="#10B981"
          />
          <StatCard
            title="Missing Values"
            value={statistics.summary.total_missing?.toLocaleString()}
            icon={Info}
            color="#F59E0B"
          />
          <StatCard
            title="Duplicates"
            value={statistics.summary.total_duplicates?.toLocaleString()}
            icon={ArrowUpDown}
            color="#EF4444"
          />
        </div>
      )}

      {/* Main Analysis Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="bg-white border border-slate-200 p-1 rounded-lg">
          <TabsTrigger 
            value="overview"
            data-testid="tab-overview"
            className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-md"
          >
            <Table2 className="w-4 h-4 mr-2" />
            Statistics
          </TabsTrigger>
          <TabsTrigger 
            value="correlation"
            data-testid="tab-correlation"
            className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-md"
          >
            <TrendingUp className="w-4 h-4 mr-2" />
            Correlation
          </TabsTrigger>
          <TabsTrigger 
            value="distribution"
            data-testid="tab-distribution"
            className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-md"
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            Distribution
          </TabsTrigger>
          <TabsTrigger 
            value="visualize"
            data-testid="tab-visualize"
            className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-md"
          >
            <PieIcon className="w-4 h-4 mr-2" />
            Visualize
          </TabsTrigger>
        </TabsList>

        {/* Statistics Tab */}
        <TabsContent value="overview" data-testid="statistics-content">
          <StatisticsTable data={statistics?.numeric} title="Numeric Column Statistics" />
          
          {statistics?.categorical && Object.keys(statistics.categorical).length > 0 && (
            <Card className="mt-6 bg-white border border-slate-200 shadow-sm">
              <CardHeader className="border-b border-slate-100 pb-4">
                <CardTitle className="text-lg font-semibold text-slate-900">Categorical Columns</CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(statistics.categorical).map(([col, stats]) => (
                    <div key={col} className="p-4 bg-slate-50 rounded-lg">
                      <h4 className="font-medium text-slate-800 mb-2">{col}</h4>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-slate-500">Unique</span>
                          <span className="font-medium">{stats.unique}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Top</span>
                          <span className="font-medium truncate ml-2" title={stats.top}>{stats.top}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Frequency</span>
                          <span className="font-medium">{stats.freq}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Missing</span>
                          <span className="font-medium">{stats.missing} ({stats.missing_pct}%)</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Correlation Tab */}
        <TabsContent value="correlation" data-testid="correlation-content">
          <div className="space-y-6">
            {correlation?.heatmap_data && correlation.columns?.length >= 2 ? (
              <>
                <CorrelationHeatmap data={correlation.heatmap_data} columns={correlation.columns} />
                
                {correlation.top_correlations?.length > 0 && (
                  <Card className="bg-white border border-slate-200 shadow-sm">
                    <CardHeader className="border-b border-slate-100 pb-4">
                      <CardTitle className="text-lg font-semibold text-slate-900">Top Correlations</CardTitle>
                      <CardDescription>Strongest relationships between variables</CardDescription>
                    </CardHeader>
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        {correlation.top_correlations.map((corr, idx) => (
                          <div key={idx} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                            <div className="flex items-center gap-2">
                              <Badge 
                                className={
                                  corr.strength === 'very_strong' ? 'bg-green-100 text-green-700' :
                                  corr.strength === 'strong' ? 'bg-blue-100 text-blue-700' :
                                  corr.strength === 'moderate' ? 'bg-yellow-100 text-yellow-700' :
                                  'bg-slate-100 text-slate-600'
                                }
                              >
                                {corr.strength.replace('_', ' ')}
                              </Badge>
                              <span className="text-sm font-medium text-slate-700">
                                {corr.column1} ↔ {corr.column2}
                              </span>
                            </div>
                            <span className={`font-mono text-sm font-bold ${corr.correlation >= 0 ? 'text-indigo-600' : 'text-red-500'}`}>
                              {corr.correlation.toFixed(4)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Card className="bg-white border border-slate-200 p-8 text-center">
                <TrendingUp className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-500">Need at least 2 numeric columns for correlation analysis</p>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Distribution Tab */}
        <TabsContent value="distribution" data-testid="distribution-content">
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-slate-600">Select Column:</span>
              <Select value={selectedDistColumn} onValueChange={setSelectedDistColumn}>
                <SelectTrigger className="w-64 bg-white" data-testid="distribution-column-select">
                  <SelectValue placeholder="Select column" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  {columns.numeric?.map(col => (
                    <SelectItem key={col} value={col}>{col}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            {distribution ? (
              <DistributionChart data={distribution} column={selectedDistColumn} />
            ) : (
              <Card className="bg-white border border-slate-200 p-8 text-center">
                <BarChart3 className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-500">Select a numeric column to view its distribution</p>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Visualize Tab */}
        <TabsContent value="visualize" data-testid="visualize-content">
          <Card className="bg-white border border-slate-200 shadow-sm">
            <CardHeader className="border-b border-slate-100 pb-4">
              <div className="flex flex-wrap items-center gap-4">
                <div>
                  <span className="text-sm font-medium text-slate-600 mr-2">Chart Type:</span>
                  <Select value={selectedChartType} onValueChange={setSelectedChartType}>
                    <SelectTrigger className="w-40 bg-white" data-testid="chart-type-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-white">
                      <SelectItem value="bar">Bar Chart</SelectItem>
                      <SelectItem value="line">Line Chart</SelectItem>
                      <SelectItem value="scatter">Scatter Plot</SelectItem>
                      <SelectItem value="pie">Pie Chart</SelectItem>
                      <SelectItem value="histogram">Histogram</SelectItem>
                      <SelectItem value="box">Box Plot</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                {['bar', 'scatter', 'line'].includes(selectedChartType) && (
                  <>
                    <div>
                      <span className="text-sm font-medium text-slate-600 mr-2">X Axis:</span>
                      <Select value={xColumn} onValueChange={setXColumn}>
                        <SelectTrigger className="w-40 bg-white" data-testid="x-column-select">
                          <SelectValue placeholder="Select" />
                        </SelectTrigger>
                        <SelectContent className="bg-white">
                          {columns.columns?.map(col => (
                            <SelectItem key={col.name} value={col.name}>{col.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-slate-600 mr-2">Y Axis:</span>
                      <Select value={yColumn} onValueChange={setYColumn}>
                        <SelectTrigger className="w-40 bg-white" data-testid="y-column-select">
                          <SelectValue placeholder="Select" />
                        </SelectTrigger>
                        <SelectContent className="bg-white">
                          {columns.numeric?.map(col => (
                            <SelectItem key={col} value={col}>{col}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </>
                )}
                
                {selectedChartType === 'pie' && (
                  <div>
                    <span className="text-sm font-medium text-slate-600 mr-2">Category:</span>
                    <Select value={xColumn} onValueChange={setXColumn}>
                      <SelectTrigger className="w-40 bg-white">
                        <SelectValue placeholder="Select" />
                      </SelectTrigger>
                      <SelectContent className="bg-white">
                        {columns.categorical?.map(col => (
                          <SelectItem key={col} value={col}>{col}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
                
                {selectedChartType === 'histogram' && (
                  <div>
                    <span className="text-sm font-medium text-slate-600 mr-2">Column:</span>
                    <Select value={xColumn} onValueChange={setXColumn}>
                      <SelectTrigger className="w-40 bg-white">
                        <SelectValue placeholder="Select" />
                      </SelectTrigger>
                      <SelectContent className="bg-white">
                        {columns.numeric?.map(col => (
                          <SelectItem key={col} value={col}>{col}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                <Button onClick={loadChartData} variant="outline" className="ml-auto">
                  Refresh Chart
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              {renderChart()}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
