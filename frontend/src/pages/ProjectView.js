import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { toast } from 'sonner';
import { Database, FileSpreadsheet, Wand2, BarChart3, Zap, History, Sparkles } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { projectsAPI, exportsAPI, analysisAPI } from '../api';
import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel } from '../components/ui/alert-dialog';
import { Button } from '../components/ui/button';
import AnalysisDashboard from '../components/analysis/AnalysisDashboard';
import AutomatedPipelineReport from '../components/project/AutomatedPipelineReport';
import AutomatedPipeline from '../components/analysis/AutomatedPipeline';
import TransformationHistory from '../components/project/TransformationHistory';
import DataSourcePicker from '../components/data/DataSourcePicker';
import DashboardLayout from '../components/DashboardLayout';
import { DataPreviewSection, RecommendationsSection, ProjectHeader } from '../components/project';

function ProjectView({ user }) {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [transforming, setTransforming] = useState(false);
  const [oneClickCleaning, setOneClickCleaning] = useState(false);
  const [showCleanConfirm, setShowCleanConfirm] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [dataPreview, setDataPreview] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedRules, setSelectedRules] = useState([]);
  const [activeTab, setActiveTab] = useState('upload');

  useEffect(() => {
    fetchProject();
    
    // Check for Google Sheets callback params
    const params = new URLSearchParams(location.search);
    if (params.get('sheets_connected') === 'true') {
      toast.success('Google Sheets connected successfully!');
      navigate(location.pathname, { replace: true });
    } else if (params.get('sheets_error')) {
      toast.error(`Google Sheets error: ${params.get('sheets_error')}`);
      navigate(location.pathname, { replace: true });
    }
  }, [projectId]);

  const fetchProject = async () => {
    try {
      const response = await projectsAPI.get(projectId);
      setProject(response.data);
      
      if (['uploaded', 'profiled', 'analyzed', 'transformed', 'completed'].includes(response.data.status)) {
        setActiveTab('pipeline');
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

  const analyzeData = async () => {
    setAnalyzing(true);
    try {
      const response = await analysisAPI.runAutomation(projectId);
      setRecommendations(response.data.recommendations);
      await fetchProject();
      await fetchDataPreview();
      setActiveTab('pipeline');
      toast.success('Automated pipeline complete!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Automation failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const runOneClickClean = async () => {
    if (!project) return;
    setOneClickCleaning(true);
    try {
      const analysisResp = await analysisAPI.runMagicAnalysis(projectId);
      const result = analysisResp.data;

      const suggestions = result.cleaning_suggestions || [];
      if (suggestions.length === 0) {
        toast('No cleaning suggestions found');
        return;
      }

      // Build actions choosing recommended option for each suggestion
      const actions = suggestions.map(s => {
        const option = (s.options || []).find(o => o.recommended) || (s.options && s.options[0]) || {};
        return {
          column: s.column,
          issue: s.issue || s.type || 'missing_values',
          strategy: option.strategy || option.strategy_name || null,
          value: option.value || null
        };
      }).filter(a => a.strategy);

      if (actions.length === 0) {
        toast('No actionable cleaning strategies found');
        return;
      }

      await analysisAPI.applyMagicCleaning(projectId, actions);
      toast.success('Cleaning applied — refreshing preview');
      await fetchProject();
      await fetchDataPreview();
      setActiveTab('preview');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'One-click clean failed');
    } finally {
      setOneClickCleaning(false);
    }
  };

  const openCleanConfirm = () => setShowCleanConfirm(true);
  const closeCleanConfirm = () => setShowCleanConfirm(false);

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

  const handleRollback = async (entry) => {
    if (!project) return;
    setTransforming(true);
    try {
      await analysisAPI.rollback(projectId);
      toast.success('Rollback applied');
      await fetchProject();
      await fetchDataPreview();
      setActiveTab('preview');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Rollback failed');
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

  const handleImportComplete = async (data) => {
    if (data.file) {
      setUploading(true);
      try {
        await projectsAPI.uploadFile(projectId, data.file);
        toast.success('File uploaded successfully!');
        await fetchProject();
        setActiveTab('pipeline');
        await fetchDataPreview();
      } catch (error) {
        toast.error(error.response?.data?.detail || 'Upload failed');
      } finally {
        setUploading(false);
      }
    } else if (data.statistics) {
      await fetchProject();
      setActiveTab('pipeline');
      await fetchDataPreview();
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
    <DashboardLayout user={user}>
      <div className="min-h-full bg-[#F8FAFC]" data-testid="project-view">
        <ProjectHeader 
          project={project} 
          exporting={exporting} 
          onExport={handleExport} 
        />

        <main className="max-w-7xl mx-auto px-6 py-8">
          <AlertDialog open={showCleanConfirm} onOpenChange={setShowCleanConfirm}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Apply Cleaning Suggestions?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will apply recommended cleaning operations to your dataset. This action can modify or remove rows. Do you want to continue?
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel onClick={closeCleanConfirm}>Cancel</AlertDialogCancel>
                <Button
                  onClick={async () => {
                    closeCleanConfirm();
                    await runOneClickClean();
                  }}
                >
                  Apply Cleaning
                </Button>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="bg-white border border-slate-200 p-1 rounded-lg">
              <TabsTrigger 
                value="upload" 
                data-testid="tab-upload"
                className="data-[state=active]:bg-[#6366F1] data-[state=active]:text-white rounded-md"
              >
                <Database className="w-4 h-4 mr-2" />
                Data Sources
              </TabsTrigger>
              <TabsTrigger 
                value="pipeline" 
                data-testid="tab-pipeline"
                disabled={!project?.file_path}
                className="data-[state=active]:bg-[#6366F1] data-[state=active]:text-white rounded-md disabled:opacity-50"
              >
                <Zap className="w-4 h-4 mr-2" />
                Pipeline
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
                Recommendations
              </TabsTrigger>
              <TabsTrigger 
                value="history" 
                data-testid="tab-history"
                disabled={!project?.file_path}
                className="data-[state=active]:bg-[#6366F1] data-[state=active]:text-white rounded-md disabled:opacity-50"
              >
                <History className="w-4 h-4 mr-2" />
                History
              </TabsTrigger>
            </TabsList>

            <TabsContent value="upload" data-testid="upload-tab-content">
              <DataSourcePicker 
                projectId={projectId}
                onImportComplete={handleImportComplete}
              />
            </TabsContent>

            <TabsContent value="pipeline" data-testid="pipeline-tab-content">
              <AutomatedPipeline 
                projectId={projectId}
                projectName={project?.name}
                onComplete={(results) => {
                  fetchProject();
                  fetchDataPreview();
                  toast.success('Automated analysis complete!');
                }}
              />
              {project?.statistics?.automation && (
                <div className="mt-6">
                  <AutomatedPipelineReport project={project} />
                </div>
              )}
            </TabsContent>

            <TabsContent value="preview" data-testid="preview-tab-content">
              <DataPreviewSection
                project={project}
                dataPreview={dataPreview}
                analyzing={analyzing}
                onAnalyzeData={analyzeData}
                onViewAnalysis={() => setActiveTab('analysis')}
                onOneClickClean={openCleanConfirm}
                oneClickCleaning={oneClickCleaning}
              />
            </TabsContent>

            <TabsContent value="analysis" data-testid="analysis-tab-content">
              <AnalysisDashboard projectId={projectId} />
            </TabsContent>

            <TabsContent value="recommendations" data-testid="recommendations-tab-content">
              <div className="space-y-6">
                <RecommendationsSection
                  recommendations={recommendations}
                  selectedRules={selectedRules}
                  transforming={transforming}
                  onToggleRecommendation={toggleRecommendation}
                  onApplyTransformations={applyTransformations}
                  onGoToAnalyze={() => {
                    setActiveTab('pipeline');
                    setTimeout(analyzeData, 100);
                  }}
                  isRecommendationSelected={isRecommendationSelected}
                />
              </div>
            </TabsContent>

            <TabsContent value="history" data-testid="history-tab-content">
              {project?.statistics?.automation?.stages?.length > 0 || project?.applied_transformations?.length > 0 ? (
                <TransformationHistory project={project} onRollback={handleRollback} />
              ) : (
                <div className="rounded-xl border border-slate-200 bg-white p-12 text-center shadow-sm">
                  <p className="text-lg font-semibold text-slate-900">No pipeline history yet</p>
                  <p className="mt-2 text-sm text-slate-500">Upload data and run the pipeline to populate the execution history.</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </DashboardLayout>
  );
}

export default ProjectView;
