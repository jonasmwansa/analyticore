import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { 
  GitCompare, ArrowLeft, Check, X, Loader2, BarChart3, 
  Database, FileSpreadsheet, AlertCircle, TrendingUp, Award
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Checkbox } from '../components/ui/checkbox';
import DashboardLayout from '../components/DashboardLayout';
import { compareAPI } from '../api';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend
} from 'recharts';

const COLORS = ['#6366F1', '#14B8A6', '#F59E0B', '#EC4899'];

function CompareProjects({ user }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);
  const [projects, setProjects] = useState([]);
  const [selectedProjects, setSelectedProjects] = useState([]);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await compareAPI.getComparableProjects();
      setProjects(response.data.projects || []);
    } catch (error) {
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const toggleProjectSelection = (projectId) => {
    if (selectedProjects.includes(projectId)) {
      setSelectedProjects(selectedProjects.filter(id => id !== projectId));
    } else if (selectedProjects.length < 4) {
      setSelectedProjects([...selectedProjects, projectId]);
    } else {
      toast.error('Maximum 4 projects can be compared');
    }
  };

  const runComparison = async () => {
    if (selectedProjects.length < 2) {
      toast.error('Select at least 2 projects to compare');
      return;
    }

    setComparing(true);
    try {
      const response = await compareAPI.compareProjects(selectedProjects);
      setComparisonResult(response.data);
      setActiveTab('overview');
      toast.success('Comparison complete!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Comparison failed');
    } finally {
      setComparing(false);
    }
  };

  const getQualityColor = (score) => {
    if (score >= 80) return 'text-emerald-500';
    if (score >= 60) return 'text-amber-500';
    return 'text-red-500';
  };

  const getQualityBg = (score) => {
    if (score >= 80) return 'bg-emerald-500/10 border-emerald-500/30';
    if (score >= 60) return 'bg-amber-500/10 border-amber-500/30';
    return 'bg-red-500/10 border-red-500/30';
  };

  if (loading) {
    return (
      <DashboardLayout user={user}>
        <div className="min-h-screen flex items-center justify-center">
          <Loader2 className="w-12 h-12 text-[#6366F1] animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout user={user}>
      <div className="p-6 max-w-7xl mx-auto" data-testid="compare-projects-page">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              onClick={() => navigate('/dashboard')}
              className="text-slate-600 hover:text-[#6366F1]"
              data-testid="back-btn"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-[#0F172A]">Compare Projects</h1>
              <p className="text-sm text-[#64748B]">Compare data quality and statistics across projects</p>
            </div>
          </div>
          {selectedProjects.length >= 2 && (
            <Button
              onClick={runComparison}
              disabled={comparing}
              className="bg-[#6366F1] hover:bg-[#4F46E5] text-white"
              data-testid="compare-btn"
            >
              {comparing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Comparing...
                </>
              ) : (
                <>
                  <GitCompare className="w-4 h-4 mr-2" />
                  Compare ({selectedProjects.length})
                </>
              )}
            </Button>
          )}
        </div>

        {/* Project Selection */}
        {!comparisonResult && (
          <Card className="p-6 mb-8" data-testid="project-selection">
            <h2 className="text-lg font-semibold text-[#0F172A] mb-4">
              Select Projects to Compare (2-4)
            </h2>
            {projects.length === 0 ? (
              <div className="text-center py-8">
                <Database className="w-12 h-12 text-[#94A3B8] mx-auto mb-4" />
                <p className="text-[#64748B]">No projects with data available</p>
                <Button
                  onClick={() => navigate('/dashboard')}
                  className="mt-4 bg-[#6366F1] hover:bg-[#4F46E5] text-white"
                >
                  Create a Project
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {projects.map((project) => (
                  <Card
                    key={project.project_id}
                    className={`p-4 cursor-pointer transition-all ${
                      selectedProjects.includes(project.project_id)
                        ? 'border-[#6366F1] ring-2 ring-[#6366F1]/20 bg-[#EEF2FF]'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                    onClick={() => toggleProjectSelection(project.project_id)}
                    data-testid={`project-card-${project.project_id}`}
                  >
                    <div className="flex items-start gap-3">
                      <Checkbox
                        checked={selectedProjects.includes(project.project_id)}
                        className="mt-1"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-[#0F172A] truncate">{project.name}</p>
                        <p className="text-sm text-[#64748B]">
                          {project.row_count?.toLocaleString() || '?'} rows
                        </p>
                        <p className="text-xs text-[#94A3B8]">
                          {new Date(project.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </Card>
        )}

        {/* Comparison Results */}
        {comparisonResult && (
          <div className="space-y-6">
            {/* Action Bar */}
            <div className="flex items-center justify-between">
              <div className="flex gap-2">
                {['overview', 'charts', 'details'].map((tab) => (
                  <Button
                    key={tab}
                    variant={activeTab === tab ? 'default' : 'outline'}
                    onClick={() => setActiveTab(tab)}
                    className={activeTab === tab ? 'bg-[#6366F1]' : ''}
                    data-testid={`tab-${tab}`}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </Button>
                ))}
              </div>
              <Button
                variant="outline"
                onClick={() => setComparisonResult(null)}
                data-testid="new-comparison-btn"
              >
                New Comparison
              </Button>
            </div>

            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6" data-testid="overview-tab">
                {/* Comparison Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <Card className="p-4 bg-[#EEF2FF] border-[#6366F1]/20">
                    <Award className="w-8 h-8 text-[#6366F1] mb-2" />
                    <p className="text-sm text-[#64748B]">Best Quality</p>
                    <p className="text-lg font-bold text-[#0F172A]">
                      {comparisonResult.comparison_metrics.best_quality}
                    </p>
                  </Card>
                  <Card className="p-4 bg-[#F0FDFA] border-[#14B8A6]/20">
                    <TrendingUp className="w-8 h-8 text-[#14B8A6] mb-2" />
                    <p className="text-sm text-[#64748B]">Most Complete</p>
                    <p className="text-lg font-bold text-[#0F172A]">
                      {comparisonResult.comparison_metrics.most_complete}
                    </p>
                  </Card>
                  <Card className="p-4 bg-[#FFFBEB] border-[#F59E0B]/20">
                    <Database className="w-8 h-8 text-[#F59E0B] mb-2" />
                    <p className="text-sm text-[#64748B]">Most Rows</p>
                    <p className="text-lg font-bold text-[#0F172A]">
                      {comparisonResult.comparison_metrics.most_rows}
                    </p>
                  </Card>
                  <Card className="p-4 bg-[#FDF2F8] border-[#EC4899]/20">
                    <AlertCircle className="w-8 h-8 text-[#EC4899] mb-2" />
                    <p className="text-sm text-[#64748B]">Fewest Issues</p>
                    <p className="text-lg font-bold text-[#0F172A]">
                      {comparisonResult.comparison_metrics.fewest_issues}
                    </p>
                  </Card>
                </div>

                {/* Side by Side Comparison */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold text-[#0F172A] mb-4">Side-by-Side Comparison</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-slate-200">
                          <th className="text-left py-3 px-4 text-sm font-semibold text-[#64748B]">Metric</th>
                          {comparisonResult.projects.map((p, i) => (
                            <th key={p.project_id} className="text-center py-3 px-4 text-sm font-semibold" style={{ color: COLORS[i] }}>
                              {p.project_name}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="border-b border-slate-100 hover:bg-slate-50">
                          <td className="py-3 px-4 text-sm text-[#64748B]">Quality Score</td>
                          {comparisonResult.projects.map((p) => (
                            <td key={p.project_id} className={`py-3 px-4 text-center font-bold ${getQualityColor(p.quality_score)}`}>
                              {p.quality_score}%
                            </td>
                          ))}
                        </tr>
                        <tr className="border-b border-slate-100 hover:bg-slate-50">
                          <td className="py-3 px-4 text-sm text-[#64748B]">Total Rows</td>
                          {comparisonResult.projects.map((p) => (
                            <td key={p.project_id} className="py-3 px-4 text-center font-medium text-[#0F172A]">
                              {p.total_rows.toLocaleString()}
                            </td>
                          ))}
                        </tr>
                        <tr className="border-b border-slate-100 hover:bg-slate-50">
                          <td className="py-3 px-4 text-sm text-[#64748B]">Total Columns</td>
                          {comparisonResult.projects.map((p) => (
                            <td key={p.project_id} className="py-3 px-4 text-center font-medium text-[#0F172A]">
                              {p.total_columns}
                            </td>
                          ))}
                        </tr>
                        <tr className="border-b border-slate-100 hover:bg-slate-50">
                          <td className="py-3 px-4 text-sm text-[#64748B]">Missing Values %</td>
                          {comparisonResult.projects.map((p) => (
                            <td key={p.project_id} className="py-3 px-4 text-center font-medium text-[#0F172A]">
                              {p.missing_percentage}%
                            </td>
                          ))}
                        </tr>
                        <tr className="border-b border-slate-100 hover:bg-slate-50">
                          <td className="py-3 px-4 text-sm text-[#64748B]">Duplicate Rows</td>
                          {comparisonResult.projects.map((p) => (
                            <td key={p.project_id} className="py-3 px-4 text-center font-medium text-[#0F172A]">
                              {p.duplicate_rows}
                            </td>
                          ))}
                        </tr>
                        <tr className="border-b border-slate-100 hover:bg-slate-50">
                          <td className="py-3 px-4 text-sm text-[#64748B]">Issues Count</td>
                          {comparisonResult.projects.map((p) => (
                            <td key={p.project_id} className="py-3 px-4 text-center font-medium text-[#0F172A]">
                              <span className={p.issues_count > 0 ? 'text-amber-500' : 'text-emerald-500'}>
                                {p.issues_count}
                              </span>
                            </td>
                          ))}
                        </tr>
                        <tr className="hover:bg-slate-50">
                          <td className="py-3 px-4 text-sm text-[#64748B]">Completeness</td>
                          {comparisonResult.projects.map((p) => (
                            <td key={p.project_id} className="py-3 px-4 text-center font-medium text-[#0F172A]">
                              {p.completeness}%
                            </td>
                          ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </Card>
              </div>
            )}

            {/* Charts Tab */}
            {activeTab === 'charts' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6" data-testid="charts-tab">
                {/* Radar Chart */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold text-[#0F172A] mb-4">Data Health Radar</h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart data={comparisonResult.radar_data}>
                        <PolarGrid stroke="#E2E8F0" />
                        <PolarAngleAxis dataKey="metric" tick={{ fontSize: 12, fill: '#64748B' }} />
                        <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
                        {comparisonResult.projects.map((p, i) => (
                          <Radar
                            key={p.project_id}
                            name={p.project_name}
                            dataKey={p.project_name}
                            stroke={COLORS[i]}
                            fill={COLORS[i]}
                            fillOpacity={0.2}
                          />
                        ))}
                        <Legend />
                        <Tooltip />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </Card>

                {/* Quality Score Bar Chart */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold text-[#0F172A] mb-4">Quality Score Comparison</h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={comparisonResult.bar_chart_data.quality}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                        <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <Bar dataKey="value" name="Quality Score" radius={[4, 4, 0, 0]}>
                          {comparisonResult.bar_chart_data.quality.map((entry, index) => (
                            <Bar key={index} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </Card>

                {/* Row Count Bar Chart */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold text-[#0F172A] mb-4">Row Count Comparison</h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={comparisonResult.bar_chart_data.rows}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                        <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                        <YAxis />
                        <Tooltip formatter={(value) => value.toLocaleString()} />
                        <Bar dataKey="value" name="Rows" fill="#14B8A6" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </Card>

                {/* Issues Count Bar Chart */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold text-[#0F172A] mb-4">Issues Count Comparison</h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={comparisonResult.bar_chart_data.issues}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                        <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" name="Issues" fill="#F59E0B" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </Card>
              </div>
            )}

            {/* Details Tab */}
            {activeTab === 'details' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6" data-testid="details-tab">
                {comparisonResult.projects.map((p, i) => (
                  <Card key={p.project_id} className={`p-6 border-2 ${getQualityBg(p.quality_score)}`}>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: COLORS[i] }} />
                      <h3 className="text-lg font-bold text-[#0F172A]">{p.project_name}</h3>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-[#64748B]">Quality Score</span>
                        <span className={`text-2xl font-bold ${getQualityColor(p.quality_score)}`}>
                          {p.quality_score}%
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-white/50 rounded-lg p-3">
                          <p className="text-xs text-[#64748B]">Rows</p>
                          <p className="text-lg font-semibold text-[#0F172A]">{p.total_rows.toLocaleString()}</p>
                        </div>
                        <div className="bg-white/50 rounded-lg p-3">
                          <p className="text-xs text-[#64748B]">Columns</p>
                          <p className="text-lg font-semibold text-[#0F172A]">{p.total_columns}</p>
                        </div>
                        <div className="bg-white/50 rounded-lg p-3">
                          <p className="text-xs text-[#64748B]">Numeric</p>
                          <p className="text-lg font-semibold text-[#6366F1]">{p.numeric_columns}</p>
                        </div>
                        <div className="bg-white/50 rounded-lg p-3">
                          <p className="text-xs text-[#64748B]">Categorical</p>
                          <p className="text-lg font-semibold text-[#14B8A6]">{p.categorical_columns}</p>
                        </div>
                      </div>
                      
                      <div className="border-t border-slate-200 pt-4">
                        <div className="flex justify-between text-sm mb-2">
                          <span className="text-[#64748B]">Missing Values</span>
                          <span className="font-medium">{p.missing_percentage}%</span>
                        </div>
                        <div className="flex justify-between text-sm mb-2">
                          <span className="text-[#64748B]">Duplicates</span>
                          <span className="font-medium">{p.duplicate_rows}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-[#64748B]">Issues</span>
                          <span className="font-medium">
                            {p.critical_issues > 0 && (
                              <span className="text-red-500 mr-2">{p.critical_issues} critical</span>
                            )}
                            {p.warning_issues > 0 && (
                              <span className="text-amber-500">{p.warning_issues} warnings</span>
                            )}
                            {p.issues_count === 0 && (
                              <span className="text-emerald-500">No issues</span>
                            )}
                          </span>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default CompareProjects;
