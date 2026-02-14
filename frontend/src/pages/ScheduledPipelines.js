import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { 
  Clock, Play, Pause, Trash2, Plus, 
  CheckCircle2, XCircle, AlertCircle, Calendar,
  BarChart3, Settings, Loader2
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { pipelinesAPI, projectsAPI } from '../api';
import DashboardLayout from '../components/DashboardLayout';

function ScheduledPipelines({ user }) {
  const navigate = useNavigate();
  const [schedules, setSchedules] = useState([]);
  const [stats, setStats] = useState(null);
  const [runs, setRuns] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('schedules');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [creating, setCreating] = useState(false);
  
  // Create form state
  const [newSchedule, setNewSchedule] = useState({
    project_id: '',
    name: '',
    description: '',
    schedule_type: 'daily',
    hour: 0,
    minute: 0,
    day_of_week: '1',
    day_of_month: '1',
    action_type: 'run_analysis',
    is_active: true
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [schedulesRes, statsRes, runsRes, projectsRes] = await Promise.all([
        pipelinesAPI.listSchedules(),
        pipelinesAPI.getStats(),
        pipelinesAPI.listRuns(),
        projectsAPI.list()
      ]);
      setSchedules(schedulesRes.data.schedules || []);
      setStats(statsRes.data);
      setRuns(runsRes.data.runs || []);
      setProjects(projectsRes.data.results || projectsRes.data || []);
    } catch (error) {
      console.error('Failed to load data:', error);
      toast.error('Failed to load scheduled pipelines');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSchedule = async () => {
    if (!newSchedule.project_id || !newSchedule.name) {
      toast.error('Please select a project and enter a name');
      return;
    }
    
    setCreating(true);
    try {
      await pipelinesAPI.createSchedule(newSchedule);
      toast.success('Schedule created successfully!');
      setShowCreateDialog(false);
      setNewSchedule({
        project_id: '',
        name: '',
        description: '',
        schedule_type: 'daily',
        hour: 0,
        minute: 0,
        day_of_week: '1',
        day_of_month: '1',
        action_type: 'run_analysis',
        is_active: true
      });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create schedule');
    } finally {
      setCreating(false);
    }
  };

  const handleToggle = async (scheduleId) => {
    try {
      const res = await pipelinesAPI.toggleSchedule(scheduleId);
      toast.success(res.data.message);
      fetchData();
    } catch (error) {
      toast.error('Failed to toggle schedule');
    }
  };

  const handleRunNow = async (scheduleId) => {
    try {
      const res = await pipelinesAPI.runNow(scheduleId);
      toast.success('Pipeline run queued!');
      fetchData();
    } catch (error) {
      toast.error('Failed to run pipeline');
    }
  };

  const handleDelete = async (scheduleId) => {
    if (!window.confirm('Are you sure you want to delete this schedule?')) return;
    
    try {
      await pipelinesAPI.deleteSchedule(scheduleId);
      toast.success('Schedule deleted');
      fetchData();
    } catch (error) {
      toast.error('Failed to delete schedule');
    }
  };

  const getStatusBadge = (status, isActive) => {
    if (!isActive) {
      return <Badge className="bg-slate-100 text-slate-600">Paused</Badge>;
    }
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-700">Active</Badge>;
      case 'failed':
        return <Badge className="bg-red-100 text-red-700">Failed</Badge>;
      default:
        return <Badge className="bg-slate-100 text-slate-600">{status}</Badge>;
    }
  };

  const getRunStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'running':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      default:
        return <AlertCircle className="w-4 h-4 text-slate-400" />;
    }
  };

  if (loading) {
    return (
      <DashboardLayout user={user}>
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-[#6366F1] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-[#64748B]">Loading schedules...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout user={user}>
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Page Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-[#0F172A] mb-1">Scheduled Pipelines</h1>
            <p className="text-[#64748B]">Automate your data transformation workflows</p>
          </div>
          
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button 
                className="bg-[#6366F1] hover:bg-[#4F46E5] text-white"
                data-testid="create-schedule-btn"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Schedule
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-white max-w-lg">
              <DialogHeader>
                <DialogTitle className="text-xl font-bold text-[#0F172A]">Create Scheduled Pipeline</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label>Project</Label>
                  <Select 
                    value={newSchedule.project_id} 
                    onValueChange={(v) => setNewSchedule({...newSchedule, project_id: v})}
                  >
                    <SelectTrigger data-testid="project-select" className="bg-white">
                      <SelectValue placeholder="Select a project..." />
                    </SelectTrigger>
                    <SelectContent className="bg-white">
                      {projects.map((p) => (
                        <SelectItem key={p.project_id} value={p.project_id}>
                          {p.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>Schedule Name</Label>
                  <Input
                    value={newSchedule.name}
                    onChange={(e) => setNewSchedule({...newSchedule, name: e.target.value})}
                    placeholder="Daily Sales Report"
                    data-testid="schedule-name-input"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Schedule Type</Label>
                    <Select 
                      value={newSchedule.schedule_type} 
                      onValueChange={(v) => setNewSchedule({...newSchedule, schedule_type: v})}
                    >
                      <SelectTrigger className="bg-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-white">
                        <SelectItem value="hourly">Hourly</SelectItem>
                        <SelectItem value="daily">Daily</SelectItem>
                        <SelectItem value="weekly">Weekly</SelectItem>
                        <SelectItem value="monthly">Monthly</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Action Type</Label>
                    <Select 
                      value={newSchedule.action_type} 
                      onValueChange={(v) => setNewSchedule({...newSchedule, action_type: v})}
                    >
                      <SelectTrigger className="bg-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-white">
                        <SelectItem value="refresh_data">Refresh Data</SelectItem>
                        <SelectItem value="run_analysis">Run Analysis</SelectItem>
                        <SelectItem value="apply_cleaning">Apply Cleaning</SelectItem>
                        <SelectItem value="export_data">Export Data</SelectItem>
                        <SelectItem value="full_pipeline">Full Pipeline</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Hour (0-23)</Label>
                    <Input
                      type="number"
                      min="0"
                      max="23"
                      value={newSchedule.hour}
                      onChange={(e) => setNewSchedule({...newSchedule, hour: parseInt(e.target.value) || 0})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Minute (0-59)</Label>
                    <Input
                      type="number"
                      min="0"
                      max="59"
                      value={newSchedule.minute}
                      onChange={(e) => setNewSchedule({...newSchedule, minute: parseInt(e.target.value) || 0})}
                    />
                  </div>
                </div>
                
                {newSchedule.schedule_type === 'weekly' && (
                  <div className="space-y-2">
                    <Label>Day of Week</Label>
                    <Select 
                      value={newSchedule.day_of_week} 
                      onValueChange={(v) => setNewSchedule({...newSchedule, day_of_week: v})}
                    >
                      <SelectTrigger className="bg-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-white">
                        <SelectItem value="0">Sunday</SelectItem>
                        <SelectItem value="1">Monday</SelectItem>
                        <SelectItem value="2">Tuesday</SelectItem>
                        <SelectItem value="3">Wednesday</SelectItem>
                        <SelectItem value="4">Thursday</SelectItem>
                        <SelectItem value="5">Friday</SelectItem>
                        <SelectItem value="6">Saturday</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}
                
                {newSchedule.schedule_type === 'monthly' && (
                  <div className="space-y-2">
                    <Label>Day of Month</Label>
                    <Input
                      type="number"
                      min="1"
                      max="31"
                      value={newSchedule.day_of_month}
                      onChange={(e) => setNewSchedule({...newSchedule, day_of_month: e.target.value})}
                    />
                  </div>
                )}
                
                <Button
                  onClick={handleCreateSchedule}
                  disabled={creating}
                  className="w-full bg-[#6366F1] hover:bg-[#4F46E5] text-white"
                  data-testid="submit-schedule-btn"
                >
                  {creating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create Schedule'
                  )}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-[#EEF2FF] rounded-lg flex items-center justify-center">
                  <Clock className="w-6 h-6 text-[#6366F1]" />
                </div>
                <div>
                  <p className="text-sm text-[#64748B]">Total Schedules</p>
                  <p className="text-2xl font-bold text-[#0F172A]">{stats.total_schedules}</p>
                </div>
              </div>
            </Card>
            
            <Card className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <CheckCircle2 className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-[#64748B]">Active</p>
                  <p className="text-2xl font-bold text-[#0F172A]">{stats.active_schedules}</p>
                </div>
              </div>
            </Card>
            
            <Card className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-[#64748B]">Runs (7 days)</p>
                  <p className="text-2xl font-bold text-[#0F172A]">{stats.runs_last_7_days?.total || 0}</p>
                </div>
              </div>
            </Card>
            
            <Card className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center">
                  <span className="text-xl font-bold text-emerald-600">
                    {stats.runs_last_7_days?.success_rate || 0}%
                  </span>
                </div>
                <div>
                  <p className="text-sm text-[#64748B]">Success Rate</p>
                  <p className="text-sm text-[#0F172A]">
                    {stats.runs_last_7_days?.successful || 0} / {stats.runs_last_7_days?.total || 0}
                  </p>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-white border border-slate-200 p-1 rounded-lg mb-6">
            <TabsTrigger 
              value="schedules"
              className="data-[state=active]:bg-[#6366F1] data-[state=active]:text-white rounded-md"
            >
              <Clock className="w-4 h-4 mr-2" />
              Schedules
            </TabsTrigger>
            <TabsTrigger 
              value="history"
              className="data-[state=active]:bg-[#6366F1] data-[state=active]:text-white rounded-md"
            >
              <Calendar className="w-4 h-4 mr-2" />
              Run History
            </TabsTrigger>
          </TabsList>

          {/* Schedules Tab */}
          <TabsContent value="schedules">
            {schedules.length === 0 ? (
              <Card className="bg-white border border-slate-200 rounded-xl p-12 text-center">
                <Clock className="w-16 h-16 text-[#94A3B8] mx-auto mb-4" />
                <h3 className="text-xl font-bold text-[#0F172A] mb-2">No Scheduled Pipelines</h3>
                <p className="text-[#64748B] mb-6">
                  Create a schedule to automate your data pipelines
                </p>
                <Button
                  onClick={() => setShowCreateDialog(true)}
                  className="bg-[#6366F1] hover:bg-[#4F46E5] text-white"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Schedule
                </Button>
              </Card>
            ) : (
              <div className="space-y-4">
                {schedules.map((schedule) => (
                  <Card
                    key={schedule.schedule_id}
                    className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm"
                    data-testid={`schedule-${schedule.schedule_id}`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-[#0F172A]">{schedule.name}</h3>
                          {getStatusBadge(schedule.status, schedule.is_active)}
                        </div>
                        <p className="text-sm text-[#64748B] mb-2">
                          Project: <span className="font-medium">{schedule.project.name}</span>
                        </p>
                        <div className="flex items-center gap-4 text-sm text-[#64748B]">
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {schedule.schedule_display}
                          </span>
                          <span className="flex items-center gap-1">
                            <Settings className="w-4 h-4" />
                            {schedule.action_type.replace('_', ' ')}
                          </span>
                          {schedule.next_run && (
                            <span className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              Next: {new Date(schedule.next_run).toLocaleString()}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleRunNow(schedule.schedule_id)}
                          data-testid={`run-now-${schedule.schedule_id}`}
                        >
                          <Play className="w-4 h-4 mr-1" />
                          Run Now
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleToggle(schedule.schedule_id)}
                          data-testid={`toggle-${schedule.schedule_id}`}
                        >
                          {schedule.is_active ? (
                            <><Pause className="w-4 h-4 mr-1" /> Pause</>
                          ) : (
                            <><Play className="w-4 h-4 mr-1" /> Activate</>
                          )}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(schedule.schedule_id)}
                          className="text-red-600 hover:text-red-700"
                          data-testid={`delete-${schedule.schedule_id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    
                    {/* Recent Runs */}
                    {schedule.recent_runs?.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-slate-100">
                        <p className="text-sm font-medium text-[#64748B] mb-2">Recent Runs</p>
                        <div className="flex gap-2">
                          {schedule.recent_runs.slice(0, 5).map((run) => (
                            <div
                              key={run.run_id}
                              className="flex items-center gap-1 text-xs bg-slate-50 px-2 py-1 rounded"
                              title={`${run.status} - ${new Date(run.started_at).toLocaleString()}`}
                            >
                              {getRunStatusIcon(run.status)}
                              <span>{run.duration_seconds ? `${run.duration_seconds}s` : '-'}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history">
            {runs.length === 0 ? (
              <Card className="bg-white border border-slate-200 rounded-xl p-12 text-center">
                <Calendar className="w-16 h-16 text-[#94A3B8] mx-auto mb-4" />
                <h3 className="text-xl font-bold text-[#0F172A] mb-2">No Run History</h3>
                <p className="text-[#64748B]">Pipeline runs will appear here</p>
              </Card>
            ) : (
              <Card className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
                <table className="w-full">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200">
                      <th className="text-left py-3 px-4 text-xs uppercase tracking-wider text-slate-500 font-semibold">Schedule</th>
                      <th className="text-left py-3 px-4 text-xs uppercase tracking-wider text-slate-500 font-semibold">Project</th>
                      <th className="text-left py-3 px-4 text-xs uppercase tracking-wider text-slate-500 font-semibold">Status</th>
                      <th className="text-left py-3 px-4 text-xs uppercase tracking-wider text-slate-500 font-semibold">Trigger</th>
                      <th className="text-left py-3 px-4 text-xs uppercase tracking-wider text-slate-500 font-semibold">Started</th>
                      <th className="text-left py-3 px-4 text-xs uppercase tracking-wider text-slate-500 font-semibold">Duration</th>
                      <th className="text-left py-3 px-4 text-xs uppercase tracking-wider text-slate-500 font-semibold">Rows</th>
                    </tr>
                  </thead>
                  <tbody>
                    {runs.map((run) => (
                      <tr key={run.run_id} className="border-b border-slate-100 hover:bg-slate-50">
                        <td className="py-3 px-4 font-medium text-[#0F172A]">{run.schedule.name}</td>
                        <td className="py-3 px-4 text-[#64748B]">{run.project_name}</td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            {getRunStatusIcon(run.status)}
                            <span className="capitalize">{run.status}</span>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <Badge variant="outline" className="capitalize">{run.trigger}</Badge>
                        </td>
                        <td className="py-3 px-4 text-[#64748B]">
                          {new Date(run.started_at).toLocaleString()}
                        </td>
                        <td className="py-3 px-4 text-[#64748B]">
                          {run.duration_seconds ? `${run.duration_seconds}s` : '-'}
                        </td>
                        <td className="py-3 px-4 text-[#64748B]">
                          {run.rows_processed.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

export default ScheduledPipelines;
