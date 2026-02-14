import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { 
  Database, ArrowLeft, Upload, FileSpreadsheet, Wand2, Check, 
  X, Download, Play, AlertCircle, CheckCircle2, Activity, BarChart3
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import { projectsAPI, exportsAPI } from '../api';
import AnalysisDashboard from '../components/analysis/AnalysisDashboard';

function ProjectView({ user }) {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [transforming, setTransforming] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [dataPreview, setDataPreview] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedRules, setSelectedRules] = useState([]);
  const [activeTab, setActiveTab] = useState('upload');

  useEffect(() => {
    fetchProject();
  }, [projectId]);

  const fetchProject = async () => {
    try {
      const response = await projectsAPI.get(projectId);
      setProject(response.data);
      
      if (response.data.status === 'uploaded' || response.data.status === 'transformed' || response.data.status === 'analyzed') {
        setActiveTab('preview');
        fetchDataPreview();
      }
      
      if (response.data.ai_recommendations && response.data.ai_recommendations.length > 0) {
        setRecommendations(response.data.ai_recommendations);
      }
    } catch (error) {
      toast.error('Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  const fetchDataPreview = async () => {
    try {
      const response = await projectsAPI.getData(projectId);
      setDataPreview(response.data);
    } catch (error) {
      console.error('Failed to load data preview');
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      await projectsAPI.uploadFile(projectId, file);
      toast.success('File uploaded successfully!');
      await fetchProject();
      setActiveTab('preview');
      await fetchDataPreview();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const analyzeData = async () => {
    setAnalyzing(true);
    try {
      const response = await projectsAPI.analyze(projectId);
      setRecommendations(response.data.recommendations);
      setActiveTab('recommendations');
      toast.success('AI analysis complete!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const toggleRecommendation = (index) => {
    const rec = recommendations[index];
    const ruleExists = selectedRules.find(r => r.column === rec.column && r.action === rec.action_type);
    
    if (ruleExists) {
      setSelectedRules(selectedRules.filter(r => !(r.column === rec.column && r.action === rec.action_type)));
    } else {
      setSelectedRules([...selectedRules, {
        column: rec.column,
        action: rec.action_type,
        parameters: rec.parameters || {}
      }]);
    }
  };

  const applyTransformations = async () => {
    if (selectedRules.length === 0) {
      toast.error('Please select at least one transformation');
      return;
    }

    setTransforming(true);
    try {
      await projectsAPI.transform(projectId, selectedRules);
      toast.success('Transformations applied successfully!');
      await fetchProject();
      await fetchDataPreview();
      setActiveTab('preview');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Transformation failed');
    } finally {
      setTransforming(false);
    }
  };

  const handleExport = async (format) => {
    setExporting(true);
    try {
      const response = await exportsAPI.exportData(projectId, format);
      const blob = new Blob([response.data], { 
        type: format === 'csv' ? 'text/csv' : 
              format === 'xlsx' ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' :
              'application/json'
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${project.name}_export.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success(`Data exported as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('Export failed');
    } finally {
      setExporting(false);
    }
  };

  const isRecommendationSelected = (index) => {
    const rec = recommendations[index];
    return selectedRules.some(r => r.column === rec.column && r.action === rec.action_type);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[#6366F1] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#64748B]">Loading project...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              onClick={() => navigate('/dashboard')}
              data-testid="back-to-dashboard-btn"
              className="text-slate-700 hover:text-[#6366F1]"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back
            </Button>
            <div className="h-8 w-px bg-slate-200"></div>
            <div className="flex items-center gap-2">
              <Database className="w-6 h-6 text-[#6366F1]" />
              <span className="text-xl font-bold text-[#0F172A]">{project?.name}</span>
            </div>
          </div>
          
          {project?.file_path && (
            <div className="flex items-center gap-2">
              <Select onValueChange={handleExport} disabled={exporting}>
                <SelectTrigger className="w-40 bg-white" data-testid="export-select">
                  <SelectValue placeholder={exporting ? "Exporting..." : "Export Data"} />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="csv">Export CSV</SelectItem>
                  <SelectItem value="xlsx">Export Excel</SelectItem>
                  <SelectItem value="json">Export JSON</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-white border border-slate-200 p-1 rounded-lg">
            <TabsTrigger 
              value="upload" 
              data-testid="tab-upload"
              className="data-[state=active]:bg-[#6366F1] data-[state=active]:text-white rounded-md"
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload Data
            </TabsTrigger>
            <TabsTrigger 
              value="preview" 
              data-testid="tab-preview"
              disabled={!project?.file_path}
              className="data-[state=active]:bg-[#6366F1] data-[state=active]:text-white rounded-md disabled:opacity-50"
            >
              <FileSpreadsheet className="w-4 h-4 mr-2" />
              Data Preview
            </TabsTrigger>
            <TabsTrigger 
              value="analysis" 
              data-testid="tab-analysis"
              disabled={!project?.file_path}
              className="data-[state=active]:bg-[#6366F1] data-[state=active]:text-white rounded-md disabled:opacity-50"
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Analysis
            </TabsTrigger>
            <TabsTrigger 
              value="recommendations" 
              data-testid="tab-recommendations"
              disabled={!project?.file_path}
              className="data-[state=active]:bg-[#6366F1] data-[state=active]:text-white rounded-md disabled:opacity-50"
            >
              <Wand2 className="w-4 h-4 mr-2" />
              AI Cleaning
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload" data-testid="upload-tab-content">
            <Card className="bg-white border border-slate-200 rounded-xl p-8 shadow-sm">
              <div className="text-center py-12">
                <div className="w-20 h-20 bg-[#EEF2FF] rounded-full flex items-center justify-center mx-auto mb-6">
                  <Upload className="w-10 h-10 text-[#6366F1]" />
                </div>
                <h2 className="text-2xl font-bold text-[#0F172A] mb-3">Upload Your Data</h2>
                <p className="text-[#64748B] mb-6">Supported formats: CSV, Excel (.xlsx, .xls), JSON</p>
                
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls,.json"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  id="file-upload"
                  data-testid="file-upload-input"
                  className="hidden"
                />
                <label htmlFor="file-upload">
                  <Button
                    as="span"
                    disabled={uploading}
                    data-testid="upload-file-btn"
                    className="bg-[#6366F1] hover:bg-[#4F46E5] text-white rounded-lg h-12 px-8 font-semibold shadow-md shadow-indigo-500/20 cursor-pointer"
                  >
                    {uploading ? 'Uploading...' : 'Choose File'}
                  </Button>
                </label>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="preview" data-testid="preview-tab-content">
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
                        onClick={analyzeData}
                        disabled={analyzing}
                        data-testid="analyze-data-btn"
                        className="flex-1 bg-[#8B5CF6] hover:bg-[#7C3AED] text-white rounded-lg h-12 font-semibold shadow-md shadow-violet-500/20"
                      >
                        {analyzing ? (
                          <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                            Analyzing...
                          </>
                        ) : (
                          <>
                            <Wand2 className="w-5 h-5 mr-2" />
                            AI Insights
                          </>
                        )}
                      </Button>
                      <Button
                        onClick={() => setActiveTab('analysis')}
                        data-testid="view-analysis-btn"
                        variant="outline"
                        className="h-12 px-4"
                      >
                        <BarChart3 className="w-5 h-5" />
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
          </TabsContent>

          <TabsContent value="analysis" data-testid="analysis-tab-content">
            <AnalysisDashboard projectId={projectId} />
          </TabsContent>

          <TabsContent value="recommendations" data-testid="recommendations-tab-content">
            <div className="space-y-6">
              {recommendations.length === 0 ? (
                <Card className="bg-white border border-slate-200 rounded-xl p-12 shadow-sm text-center">
                  <Wand2 className="w-16 h-16 text-[#94A3B8] mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-[#0F172A] mb-2">No Recommendations Yet</h3>
                  <p className="text-[#64748B] mb-6">Click "AI Insights" in the Data Preview tab to analyze your data</p>
                  <Button
                    onClick={() => {
                      setActiveTab('preview');
                      setTimeout(analyzeData, 100);
                    }}
                    data-testid="goto-analyze-btn"
                    className="bg-[#8B5CF6] hover:bg-[#7C3AED] text-white rounded-lg h-11 px-6 font-semibold shadow-md shadow-violet-500/20"
                  >
                    Analyze Data Now
                  </Button>
                </Card>
              ) : (
                <>
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="text-2xl font-bold text-[#0F172A] mb-1">AI Cleaning Recommendations</h3>
                      <p className="text-[#64748B]">Select transformations to apply to your data</p>
                    </div>
                    <Button
                      onClick={applyTransformations}
                      disabled={selectedRules.length === 0 || transforming}
                      data-testid="apply-transformations-btn"
                      className="bg-[#6366F1] hover:bg-[#4F46E5] text-white rounded-lg h-11 px-6 font-semibold shadow-md shadow-indigo-500/20 disabled:opacity-50"
                    >
                      {transforming ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                          Applying...
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4 mr-2" />
                          Apply Selected ({selectedRules.length})
                        </>
                      )}
                    </Button>
                  </div>

                  <div className="space-y-3">
                    {recommendations.map((rec, index) => (
                      <Card
                        key={index}
                        data-testid={`recommendation-${index}`}
                        className={`recommendation-item bg-white border rounded-xl p-5 shadow-sm cursor-pointer ${
                          isRecommendationSelected(index) ? 'border-[#6366F1] ring-2 ring-[#6366F1] ring-opacity-20' : 'border-slate-200'
                        }`}
                        onClick={() => toggleRecommendation(index)}
                      >
                        <div className="flex items-start gap-4">
                          <Checkbox
                            checked={isRecommendationSelected(index)}
                            onCheckedChange={() => toggleRecommendation(index)}
                            data-testid={`recommendation-checkbox-${index}`}
                            className="mt-1"
                          />
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <Badge className="bg-[#EEF2FF] text-[#6366F1] hover:bg-[#EEF2FF] font-semibold">
                                {rec.column}
                              </Badge>
                              <Badge className="bg-slate-100 text-slate-700 hover:bg-slate-100 font-medium">
                                {rec.action_type.replace('_', ' ').toUpperCase()}
                              </Badge>
                            </div>
                            <p className="text-sm text-[#F59E0B] font-medium mb-1">
                              <AlertCircle className="w-4 h-4 inline mr-1" />
                              {rec.issue}
                            </p>
                            <p className="text-sm text-[#0F172A]">{rec.recommendation}</p>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                </>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

export default ProjectView;
