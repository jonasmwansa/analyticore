import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  LineChart, Line, BarChart, Bar, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import { 
  Brain, Play, Loader2, Trash2, TrendingUp, Target, Layers,
  Zap, BarChart3, CircleDot, RefreshCw, Award, AlertCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Checkbox } from '../ui/checkbox';
import { mlAPI } from '../../api';

const COLORS = ['#6366F1', '#EC4899', '#10B981', '#F59E0B', '#8B5CF6', '#EF4444', '#14B8A6', '#F97316'];

export default function MLDashboard({ projectId }) {
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [mlInfo, setMLInfo] = useState(null);
  const [trainedModels, setTrainedModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [activeTab, setActiveTab] = useState('train');
  
  // Training form state
  const [modelType, setModelType] = useState('regression');
  const [algorithm, setAlgorithm] = useState('');
  const [targetColumn, setTargetColumn] = useState('');
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  
  // Clustering state
  const [clusteringResult, setClusteringResult] = useState(null);
  const [optimalK, setOptimalK] = useState(null);
  const [nClusters, setNClusters] = useState(3);
  const [runningClustering, setRunningClustering] = useState(false);
  
  // Auto-ML state
  const [autoMLResult, setAutoMLResult] = useState(null);
  const [runningAutoML, setRunningAutoML] = useState(false);

  useEffect(() => {
    if (projectId) {
      loadMLInfo();
      loadModels();
    }
  }, [projectId]);

  const loadMLInfo = async () => {
    try {
      const response = await mlAPI.getMLInfo(projectId);
      setMLInfo(response.data);
      
      // Set default target
      if (response.data.potential_regression_targets?.length > 0) {
        setTargetColumn(response.data.potential_regression_targets[0]);
      }
      
      // Set default features (all numeric except target)
      if (response.data.numeric_columns?.length > 0) {
        setSelectedFeatures(response.data.numeric_columns.filter(c => c !== targetColumn));
      }
    } catch (error) {
      toast.error('Failed to load ML info');
    } finally {
      setLoading(false);
    }
  };

  const loadModels = async () => {
    try {
      const response = await mlAPI.listModels(projectId);
      setTrainedModels(response.data.models || []);
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  };

  const handleTrainModel = async () => {
    if (!algorithm || !targetColumn) {
      toast.error('Please select algorithm and target column');
      return;
    }
    
    setTraining(true);
    try {
      const response = await mlAPI.trainModel(projectId, {
        model_type: modelType,
        algorithm: algorithm,
        target: targetColumn,
        features: selectedFeatures.length > 0 ? selectedFeatures : null
      });
      
      setSelectedModel(response.data);
      toast.success(`Model trained! ${modelType === 'regression' ? `R² = ${response.data.metrics.r2_score}` : `Accuracy = ${response.data.metrics.accuracy}`}`);
      loadModels();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Training failed');
    } finally {
      setTraining(false);
    }
  };

  const handleRunAutoML = async () => {
    if (!targetColumn) {
      toast.error('Please select a target column');
      return;
    }
    
    setRunningAutoML(true);
    try {
      const response = await mlAPI.autoML(projectId, {
        model_type: modelType,
        target: targetColumn,
        features: selectedFeatures.length > 0 ? selectedFeatures : null
      });
      
      setAutoMLResult(response.data);
      toast.success('Auto-ML complete! Best model found.');
      loadModels();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Auto-ML failed');
    } finally {
      setRunningAutoML(false);
    }
  };

  const handleFindOptimalK = async () => {
    setRunningClustering(true);
    try {
      const response = await mlAPI.findOptimalClusters(projectId, selectedFeatures, 10);
      setOptimalK(response.data);
      setNClusters(response.data.recommended_k);
    } catch (error) {
      toast.error('Failed to find optimal clusters');
    } finally {
      setRunningClustering(false);
    }
  };

  const handleRunClustering = async () => {
    setRunningClustering(true);
    try {
      const response = await mlAPI.runClustering(projectId, {
        algorithm: 'kmeans',
        n_clusters: nClusters,
        features: selectedFeatures.length > 0 ? selectedFeatures : null
      });
      setClusteringResult(response.data);
      toast.success(`Clustering complete! Silhouette score: ${response.data.silhouette_score}`);
    } catch (error) {
      toast.error('Clustering failed');
    } finally {
      setRunningClustering(false);
    }
  };

  const handleDeleteModel = async (modelId) => {
    try {
      await mlAPI.deleteModel(projectId, modelId);
      toast.success('Model deleted');
      loadModels();
      if (selectedModel?.model_id === modelId) {
        setSelectedModel(null);
      }
    } catch (error) {
      toast.error('Failed to delete model');
    }
  };

  const toggleFeature = (feature) => {
    setSelectedFeatures(prev => 
      prev.includes(feature) 
        ? prev.filter(f => f !== feature)
        : [...prev, feature]
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-indigo-500 animate-spin mx-auto mb-4" />
          <p className="text-slate-500">Loading ML capabilities...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="ml-dashboard">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="bg-white border border-slate-200 p-1 rounded-lg">
          <TabsTrigger value="train" className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-md">
            <Brain className="w-4 h-4 mr-2" />
            Train Model
          </TabsTrigger>
          <TabsTrigger value="automl" className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-md">
            <Zap className="w-4 h-4 mr-2" />
            Auto-ML
          </TabsTrigger>
          <TabsTrigger value="clustering" className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-md">
            <CircleDot className="w-4 h-4 mr-2" />
            Clustering
          </TabsTrigger>
          <TabsTrigger value="models" className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white rounded-md">
            <Layers className="w-4 h-4 mr-2" />
            My Models ({trainedModels.length})
          </TabsTrigger>
        </TabsList>

        {/* Train Model Tab */}
        <TabsContent value="train">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Configuration */}
            <Card className="bg-white border border-slate-200 shadow-sm">
              <CardHeader className="border-b border-slate-100 pb-4">
                <CardTitle className="text-lg">Model Configuration</CardTitle>
                <CardDescription>Configure and train your ML model</CardDescription>
              </CardHeader>
              <CardContent className="p-6 space-y-4">
                {/* Model Type */}
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Model Type</label>
                  <Select value={modelType} onValueChange={setModelType}>
                    <SelectTrigger className="bg-white" data-testid="model-type-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-white">
                      <SelectItem value="regression">Regression (Predict Numbers)</SelectItem>
                      <SelectItem value="classification">Classification (Predict Categories)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Algorithm */}
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Algorithm</label>
                  <Select value={algorithm} onValueChange={setAlgorithm}>
                    <SelectTrigger className="bg-white" data-testid="algorithm-select">
                      <SelectValue placeholder="Select algorithm" />
                    </SelectTrigger>
                    <SelectContent className="bg-white">
                      {mlInfo?.available_algorithms?.[modelType]?.map(algo => (
                        <SelectItem key={algo.id} value={algo.id}>
                          {algo.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Target Column */}
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Target Column (What to Predict)</label>
                  <Select value={targetColumn} onValueChange={setTargetColumn}>
                    <SelectTrigger className="bg-white" data-testid="target-select">
                      <SelectValue placeholder="Select target" />
                    </SelectTrigger>
                    <SelectContent className="bg-white">
                      {(modelType === 'regression' 
                        ? mlInfo?.potential_regression_targets 
                        : mlInfo?.potential_classification_targets
                      )?.map(col => (
                        <SelectItem key={col} value={col}>{col}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Feature Selection */}
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">
                    Features (Input Columns)
                  </label>
                  <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto p-2 bg-slate-50 rounded-lg">
                    {mlInfo?.numeric_columns?.filter(c => c !== targetColumn).map(col => (
                      <div key={col} className="flex items-center gap-2">
                        <Checkbox
                          id={`feature-${col}`}
                          checked={selectedFeatures.includes(col)}
                          onCheckedChange={() => toggleFeature(col)}
                        />
                        <label htmlFor={`feature-${col}`} className="text-sm text-slate-600 cursor-pointer">
                          {col}
                        </label>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    {selectedFeatures.length} features selected
                  </p>
                </div>

                <Button
                  onClick={handleTrainModel}
                  disabled={training || !algorithm || !targetColumn}
                  className="w-full bg-indigo-500 hover:bg-indigo-600"
                  data-testid="train-model-btn"
                >
                  {training ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Training...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Train Model
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Results */}
            <Card className="bg-white border border-slate-200 shadow-sm">
              <CardHeader className="border-b border-slate-100 pb-4">
                <CardTitle className="text-lg">Training Results</CardTitle>
                <CardDescription>Model performance metrics</CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                {selectedModel ? (
                  <div className="space-y-4">
                    {/* Model Info */}
                    <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                      <Award className="w-6 h-6 text-green-600" />
                      <div>
                        <p className="font-medium text-green-800">{selectedModel.algorithm.replace('_', ' ')}</p>
                        <p className="text-sm text-green-600">Target: {selectedModel.target}</p>
                      </div>
                    </div>

                    {/* Metrics */}
                    <div className="grid grid-cols-2 gap-3">
                      {selectedModel.model_type === 'regression' ? (
                        <>
                          <div className="p-3 bg-slate-50 rounded-lg text-center">
                            <p className="text-2xl font-bold text-indigo-600">{selectedModel.metrics.r2_score}</p>
                            <p className="text-xs text-slate-500">R² Score</p>
                          </div>
                          <div className="p-3 bg-slate-50 rounded-lg text-center">
                            <p className="text-2xl font-bold text-purple-600">{selectedModel.metrics.rmse}</p>
                            <p className="text-xs text-slate-500">RMSE</p>
                          </div>
                          <div className="p-3 bg-slate-50 rounded-lg text-center">
                            <p className="text-2xl font-bold text-blue-600">{selectedModel.metrics.mae}</p>
                            <p className="text-xs text-slate-500">MAE</p>
                          </div>
                          <div className="p-3 bg-slate-50 rounded-lg text-center">
                            <p className="text-2xl font-bold text-green-600">{selectedModel.metrics.cv_score_mean}</p>
                            <p className="text-xs text-slate-500">CV Score</p>
                          </div>
                        </>
                      ) : (
                        <>
                          <div className="p-3 bg-slate-50 rounded-lg text-center">
                            <p className="text-2xl font-bold text-indigo-600">{(selectedModel.metrics.accuracy * 100).toFixed(1)}%</p>
                            <p className="text-xs text-slate-500">Accuracy</p>
                          </div>
                          <div className="p-3 bg-slate-50 rounded-lg text-center">
                            <p className="text-2xl font-bold text-purple-600">{(selectedModel.metrics.precision * 100).toFixed(1)}%</p>
                            <p className="text-xs text-slate-500">Precision</p>
                          </div>
                          <div className="p-3 bg-slate-50 rounded-lg text-center">
                            <p className="text-2xl font-bold text-blue-600">{(selectedModel.metrics.recall * 100).toFixed(1)}%</p>
                            <p className="text-xs text-slate-500">Recall</p>
                          </div>
                          <div className="p-3 bg-slate-50 rounded-lg text-center">
                            <p className="text-2xl font-bold text-green-600">{(selectedModel.metrics.f1_score * 100).toFixed(1)}%</p>
                            <p className="text-xs text-slate-500">F1 Score</p>
                          </div>
                        </>
                      )}
                    </div>

                    {/* Feature Importance */}
                    {selectedModel.feature_importance?.length > 0 && (
                      <div>
                        <h4 className="text-sm font-semibold text-slate-700 mb-2">Feature Importance</h4>
                        <ResponsiveContainer width="100%" height={200}>
                          <BarChart data={selectedModel.feature_importance.slice(0, 8)} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis type="number" tick={{ fontSize: 11 }} />
                            <YAxis dataKey="feature" type="category" width={100} tick={{ fontSize: 11 }} />
                            <Tooltip />
                            <Bar dataKey="importance" fill="#6366F1" radius={[0, 4, 4, 0]}>
                              {selectedModel.feature_importance.slice(0, 8).map((_, idx) => (
                                <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-400">
                    <Brain className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Train a model to see results</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Auto-ML Tab */}
        <TabsContent value="automl">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-white border border-slate-200 shadow-sm">
              <CardHeader className="border-b border-slate-100 pb-4">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Zap className="w-5 h-5 text-yellow-500" />
                  Auto-ML
                </CardTitle>
                <CardDescription>Automatically find the best model for your data</CardDescription>
              </CardHeader>
              <CardContent className="p-6 space-y-4">
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Problem Type</label>
                  <Select value={modelType} onValueChange={setModelType}>
                    <SelectTrigger className="bg-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-white">
                      <SelectItem value="regression">Regression</SelectItem>
                      <SelectItem value="classification">Classification</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Target Column</label>
                  <Select value={targetColumn} onValueChange={setTargetColumn}>
                    <SelectTrigger className="bg-white">
                      <SelectValue placeholder="Select target" />
                    </SelectTrigger>
                    <SelectContent className="bg-white">
                      {(modelType === 'regression' 
                        ? mlInfo?.potential_regression_targets 
                        : mlInfo?.potential_classification_targets
                      )?.map(col => (
                        <SelectItem key={col} value={col}>{col}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <Button
                  onClick={handleRunAutoML}
                  disabled={runningAutoML || !targetColumn}
                  className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600"
                  data-testid="auto-ml-btn"
                >
                  {runningAutoML ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Finding Best Model...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4 mr-2" />
                      Run Auto-ML
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Auto-ML Results */}
            <Card className="bg-white border border-slate-200 shadow-sm">
              <CardHeader className="border-b border-slate-100 pb-4">
                <CardTitle className="text-lg">Auto-ML Results</CardTitle>
                <CardDescription>Comparison of all tested algorithms</CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                {autoMLResult ? (
                  <div className="space-y-4">
                    {/* Best Model Highlight */}
                    {autoMLResult.best_model && (
                      <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
                        <div className="flex items-center gap-2 mb-2">
                          <Award className="w-5 h-5 text-green-600" />
                          <span className="font-semibold text-green-800">Best Model</span>
                        </div>
                        <p className="text-lg font-bold text-green-900">
                          {autoMLResult.best_model.algorithm.replace(/_/g, ' ')}
                        </p>
                        <p className="text-sm text-green-700">
                          {autoMLResult.comparison_metric}: {
                            autoMLResult.comparison_metric === 'r2_score' 
                              ? autoMLResult.best_model.metrics.r2_score 
                              : (autoMLResult.best_model.metrics.accuracy * 100).toFixed(1) + '%'
                          }
                        </p>
                      </div>
                    )}

                    {/* All Results */}
                    <div>
                      <h4 className="text-sm font-semibold text-slate-700 mb-2">All Results</h4>
                      <div className="space-y-2">
                        {autoMLResult.all_results?.map((result, idx) => (
                          <div key={idx} className="flex items-center justify-between p-2 bg-slate-50 rounded">
                            <span className="text-sm font-medium text-slate-700">
                              {result.algorithm.replace(/_/g, ' ')}
                            </span>
                            {result.error ? (
                              <Badge variant="destructive">Error</Badge>
                            ) : (
                              <span className="text-sm font-mono text-indigo-600">
                                {autoMLResult.comparison_metric === 'r2_score' 
                                  ? result.score.toFixed(4)
                                  : (result.score * 100).toFixed(1) + '%'
                                }
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-400">
                    <Zap className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Run Auto-ML to compare algorithms</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Clustering Tab */}
        <TabsContent value="clustering">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-white border border-slate-200 shadow-sm">
              <CardHeader className="border-b border-slate-100 pb-4">
                <CardTitle className="text-lg">K-Means Clustering</CardTitle>
                <CardDescription>Group similar data points together</CardDescription>
              </CardHeader>
              <CardContent className="p-6 space-y-4">
                <Button
                  onClick={handleFindOptimalK}
                  disabled={runningClustering}
                  variant="outline"
                  className="w-full"
                >
                  {runningClustering ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Target className="w-4 h-4 mr-2" />
                  )}
                  Find Optimal Clusters
                </Button>

                {optimalK && (
                  <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-sm text-blue-800">
                      Recommended: <strong>{optimalK.recommended_k} clusters</strong>
                    </p>
                    <p className="text-xs text-blue-600">
                      Best silhouette score at k={optimalK.best_silhouette_k}
                    </p>
                  </div>
                )}

                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">
                    Number of Clusters: {nClusters}
                  </label>
                  <input
                    type="range"
                    min="2"
                    max="10"
                    value={nClusters}
                    onChange={(e) => setNClusters(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>

                <Button
                  onClick={handleRunClustering}
                  disabled={runningClustering}
                  className="w-full bg-indigo-500 hover:bg-indigo-600"
                  data-testid="run-clustering-btn"
                >
                  {runningClustering ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <CircleDot className="w-4 h-4 mr-2" />
                  )}
                  Run Clustering
                </Button>
              </CardContent>
            </Card>

            {/* Clustering Results */}
            <Card className="bg-white border border-slate-200 shadow-sm">
              <CardHeader className="border-b border-slate-100 pb-4">
                <CardTitle className="text-lg">Clustering Results</CardTitle>
                <CardDescription>Cluster visualization and statistics</CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                {clusteringResult ? (
                  <div className="space-y-4">
                    {/* Metrics */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 bg-slate-50 rounded-lg text-center">
                        <p className="text-2xl font-bold text-indigo-600">{clusteringResult.n_clusters}</p>
                        <p className="text-xs text-slate-500">Clusters</p>
                      </div>
                      <div className="p-3 bg-slate-50 rounded-lg text-center">
                        <p className="text-2xl font-bold text-purple-600">{clusteringResult.silhouette_score}</p>
                        <p className="text-xs text-slate-500">Silhouette Score</p>
                      </div>
                    </div>

                    {/* Scatter Plot */}
                    <div>
                      <h4 className="text-sm font-semibold text-slate-700 mb-2">Cluster Visualization (PCA)</h4>
                      <ResponsiveContainer width="100%" height={250}>
                        <ScatterChart>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                          <XAxis dataKey="x" name="PC1" tick={{ fontSize: 11 }} />
                          <YAxis dataKey="y" name="PC2" tick={{ fontSize: 11 }} />
                          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                          <Scatter data={clusteringResult.scatter_data} fill="#6366F1">
                            {clusteringResult.scatter_data.map((entry, idx) => (
                              <Cell key={idx} fill={COLORS[entry.cluster % COLORS.length]} />
                            ))}
                          </Scatter>
                        </ScatterChart>
                      </ResponsiveContainer>
                    </div>

                    {/* Cluster Stats */}
                    <div>
                      <h4 className="text-sm font-semibold text-slate-700 mb-2">Cluster Sizes</h4>
                      <div className="flex gap-2 flex-wrap">
                        {clusteringResult.cluster_stats?.map((stat, idx) => (
                          <Badge 
                            key={idx} 
                            style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                            className="text-white"
                          >
                            Cluster {stat.cluster}: {stat.size} ({stat.percentage}%)
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-400">
                    <CircleDot className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Run clustering to see results</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Elbow Chart */}
          {optimalK && (
            <Card className="bg-white border border-slate-200 shadow-sm mt-6">
              <CardHeader className="border-b border-slate-100 pb-4">
                <CardTitle className="text-lg">Elbow Method Analysis</CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={optimalK.k_range.map((k, i) => ({
                    k,
                    inertia: optimalK.inertias[i],
                    silhouette: optimalK.silhouette_scores[i]
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="k" tick={{ fontSize: 11 }} label={{ value: 'Number of Clusters', position: 'bottom', fontSize: 12 }} />
                    <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
                    <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend />
                    <Line yAxisId="left" type="monotone" dataKey="inertia" stroke="#6366F1" name="Inertia" strokeWidth={2} />
                    <Line yAxisId="right" type="monotone" dataKey="silhouette" stroke="#10B981" name="Silhouette" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Trained Models Tab */}
        <TabsContent value="models">
          <Card className="bg-white border border-slate-200 shadow-sm">
            <CardHeader className="border-b border-slate-100 pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Trained Models</CardTitle>
                  <CardDescription>Manage your saved models</CardDescription>
                </div>
                <Button variant="outline" size="sm" onClick={loadModels}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              {trainedModels.length > 0 ? (
                <div className="space-y-3">
                  {trainedModels.map((model) => (
                    <div 
                      key={model.model_id}
                      className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-200"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
                          <Brain className="w-5 h-5 text-indigo-600" />
                        </div>
                        <div>
                          <p className="font-medium text-slate-800">
                            {model.algorithm.replace(/_/g, ' ')}
                          </p>
                          <p className="text-sm text-slate-500">
                            Target: {model.target} | {model.features?.length || 0} features
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge>{model.model_type}</Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteModel(model.model_id)}
                          className="text-red-500 hover:text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-slate-400">
                  <Layers className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>No trained models yet</p>
                  <p className="text-sm">Train a model to see it here</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
