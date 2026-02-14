import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { 
  Database, Users, FolderKanban, Activity, TrendingUp, TrendingDown,
  ArrowLeft, BarChart3, PieChart, Calendar, CheckCircle2, XCircle,
  Settings, Bell, Clock, Zap, Target, RefreshCw, ChevronDown, ChevronRight,
  Home, LineChart, Filter, Gauge, AlertTriangle, Server, Cpu, HardDrive,
  UserPlus, UserCheck, UserMinus, Layers, Play, Pause, Timer, Loader2
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { adminAPI, authAPI } from '../api';
import {
  LineChart as ReLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart as RePieChart,
  Pie, Cell, Legend, Funnel, FunnelChart, LabelList
} from 'recharts';

const COLORS = ['#6366F1', '#14B8A6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#10B981', '#3B82F6'];

function AdminDashboard({ user }) {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Data states
  const [summary, setSummary] = useState(null);
  const [userMetrics, setUserMetrics] = useState(null);
  const [userGrowth, setUserGrowth] = useState([]);
  const [activity, setActivity] = useState(null);
  const [projectAnalytics, setProjectAnalytics] = useState(null);
  const [pipelineAnalytics, setPipelineAnalytics] = useState(null);
  const [subscriptions, setSubscriptions] = useState(null);
  const [retention, setRetention] = useState(null);
  const [funnel, setFunnel] = useState(null);
  const [activityFeed, setActivityFeed] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    if (!user?.is_staff) {
      toast.error('Access denied: Admin only');
      navigate('/dashboard');
      return;
    }
    loadAllData();
  }, [user, navigate]);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        adminAPI.getSummary(),
        adminAPI.getUserMetrics(),
        adminAPI.getUserGrowth(30),
        adminAPI.getActivityAnalytics(30),
        adminAPI.getProjectAnalytics(30),
        adminAPI.getPipelineAnalytics(30),
        adminAPI.getSubscriptionAnalytics(),
        adminAPI.getRetentionAnalytics(),
        adminAPI.getFunnelAnalytics(),
        adminAPI.getActivityFeed(50),
        adminAPI.getSystemHealth(),
        adminAPI.getUsers(),
        adminAPI.getProjects()
      ]);
      
      if (results[0].status === 'fulfilled') setSummary(results[0].value.data);
      if (results[1].status === 'fulfilled') setUserMetrics(results[1].value.data);
      if (results[2].status === 'fulfilled') setUserGrowth(results[2].value.data.data || []);
      if (results[3].status === 'fulfilled') setActivity(results[3].value.data);
      if (results[4].status === 'fulfilled') setProjectAnalytics(results[4].value.data);
      if (results[5].status === 'fulfilled') setPipelineAnalytics(results[5].value.data);
      if (results[6].status === 'fulfilled') setSubscriptions(results[6].value.data);
      if (results[7].status === 'fulfilled') setRetention(results[7].value.data);
      if (results[8].status === 'fulfilled') setFunnel(results[8].value.data);
      if (results[9].status === 'fulfilled') setActivityFeed(results[9].value.data.activities || []);
      if (results[10].status === 'fulfilled') setSystemHealth(results[10].value.data);
      if (results[11].status === 'fulfilled') setUsers(results[11].value.data.users || []);
      if (results[12].status === 'fulfilled') setProjects(results[12].value.data.projects || []);
    } catch (error) {
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    await loadAllData();
    setRefreshing(false);
    toast.success('Data refreshed');
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      localStorage.removeItem('auth_token');
      toast.success('Logged out successfully');
      navigate('/signin');
    } catch (error) {
      toast.error('Logout failed');
    }
  };

  const menuItems = [
    { id: 'overview', label: 'Overview', icon: Home },
    { id: 'users', label: 'User Metrics', icon: Users },
    { id: 'activity', label: 'Activity Analytics', icon: Activity },
    { id: 'projects', label: 'Project Analytics', icon: FolderKanban },
    { id: 'pipelines', label: 'Pipeline Analytics', icon: Zap },
    { id: 'retention', label: 'Retention & Funnels', icon: Target },
    { id: 'system', label: 'System Health', icon: Server },
    { id: 'users-list', label: 'All Users', icon: UserCheck },
    { id: 'projects-list', label: 'All Projects', icon: Layers },
    { id: 'feed', label: 'Activity Feed', icon: Bell },
    { id: 'settings', label: 'Alert Settings', icon: Settings },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <Loader2 className="w-16 h-16 text-indigo-500 animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading analytics dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 flex" data-testid="admin-dashboard">
      {/* Sidebar */}
      <aside 
        className={`bg-slate-800 border-r border-slate-700 transition-all duration-300 ${
          sidebarCollapsed ? 'w-16' : 'w-64'
        } flex flex-col`}
        data-testid="admin-sidebar"
      >
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2">
              <Database className="w-7 h-7 text-indigo-500" />
              <span className="text-lg font-bold text-white">AnalytiCore</span>
            </div>
          )}
          <button 
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-2 rounded-lg hover:bg-slate-700 text-slate-400"
          >
            {sidebarCollapsed ? <ChevronRight size={18} /> : <ChevronDown size={18} />}
          </button>
        </div>
        
        <nav className="flex-1 py-4 overflow-y-auto">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveSection(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors ${
                activeSection === item.id 
                  ? 'bg-indigo-600/20 text-indigo-400 border-r-2 border-indigo-500' 
                  : 'text-slate-400 hover:bg-slate-700/50 hover:text-white'
              }`}
              data-testid={`nav-${item.id}`}
            >
              <item.icon size={20} />
              {!sidebarCollapsed && <span className="text-sm font-medium">{item.label}</span>}
            </button>
          ))}
        </nav>
        
        <div className="p-4 border-t border-slate-700">
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full flex items-center gap-2 px-3 py-2 text-slate-400 hover:text-white text-sm rounded-lg hover:bg-slate-700"
          >
            <ArrowLeft size={18} />
            {!sidebarCollapsed && <span>Client Dashboard</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700 sticky top-0 z-40 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">Admin Analytics</h1>
              <p className="text-sm text-slate-400">Monitor users, projects, and platform performance</p>
            </div>
            <div className="flex items-center gap-3">
              <Button
                onClick={refreshData}
                variant="outline"
                className="border-slate-600 text-slate-300 hover:bg-slate-700"
                disabled={refreshing}
                data-testid="refresh-btn"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button
                onClick={handleLogout}
                variant="ghost"
                className="text-slate-400 hover:text-white"
              >
                Logout
              </Button>
            </div>
          </div>
        </header>

        <div className="p-6">
          {activeSection === 'overview' && <OverviewSection summary={summary} userMetrics={userMetrics} userGrowth={userGrowth} systemHealth={systemHealth} />}
          {activeSection === 'users' && <UserMetricsSection userMetrics={userMetrics} userGrowth={userGrowth} />}
          {activeSection === 'activity' && <ActivitySection activity={activity} />}
          {activeSection === 'projects' && <ProjectsSection projectAnalytics={projectAnalytics} />}
          {activeSection === 'pipelines' && <PipelinesSection pipelineAnalytics={pipelineAnalytics} />}
          {activeSection === 'retention' && <RetentionSection retention={retention} funnel={funnel} />}
          {activeSection === 'system' && <SystemSection systemHealth={systemHealth} />}
          {activeSection === 'users-list' && <UsersListSection users={users} />}
          {activeSection === 'projects-list' && <ProjectsListSection projects={projects} />}
          {activeSection === 'feed' && <ActivityFeedSection activityFeed={activityFeed} />}
        </div>
      </main>
    </div>
  );
}

// Overview Section
function OverviewSection({ summary, userMetrics, userGrowth, systemHealth }) {
  if (!summary) return null;
  
  return (
    <div className="space-y-6" data-testid="overview-section">
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="Total Users" 
          value={summary.users?.total || 0}
          subtext={`+${summary.users?.new_today || 0} today`}
          icon={Users}
          trend="up"
          color="indigo"
        />
        <MetricCard 
          title="Active Today (DAU)" 
          value={userMetrics?.dau || 0}
          subtext={`${userMetrics?.stickiness || 0}% stickiness`}
          icon={UserCheck}
          color="emerald"
        />
        <MetricCard 
          title="Total Projects" 
          value={summary.projects?.total || 0}
          subtext={`+${summary.projects?.new_today || 0} today`}
          icon={FolderKanban}
          color="amber"
        />
        <MetricCard 
          title="Pipeline Runs Today" 
          value={summary.pipelines?.runs_today || 0}
          subtext={`${summary.pipelines?.successful || 0} successful`}
          icon={Zap}
          color="purple"
        />
      </div>

      {/* User Growth Chart */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">User Growth (Last 30 Days)</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={userGrowth}>
              <defs>
                <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#6366F1" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" tick={{ fontSize: 11 }} />
              <YAxis stroke="#9CA3AF" tick={{ fontSize: 11 }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                labelStyle={{ color: '#9CA3AF' }}
              />
              <Area type="monotone" dataKey="total_users" stroke="#6366F1" fillOpacity={1} fill="url(#colorUsers)" name="Total Users" />
              <Line type="monotone" dataKey="new_users" stroke="#14B8A6" strokeWidth={2} name="New Users" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* System Health & Subscriptions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health Card */}
        <Card className="bg-slate-800 border-slate-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">System Health</h3>
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
              systemHealth?.status === 'healthy' ? 'bg-emerald-500/20 text-emerald-400' :
              systemHealth?.status === 'warning' ? 'bg-amber-500/20 text-amber-400' :
              'bg-red-500/20 text-red-400'
            }`}>
              {systemHealth?.status?.toUpperCase() || 'UNKNOWN'}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-700/50 rounded-lg p-4">
              <p className="text-slate-400 text-sm">DB Response</p>
              <p className="text-2xl font-bold text-white">{systemHealth?.db_response_ms || 0}ms</p>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4">
              <p className="text-slate-400 text-sm">Error Rate (24h)</p>
              <p className="text-2xl font-bold text-white">{systemHealth?.error_rate || 0}%</p>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4">
              <p className="text-slate-400 text-sm">Errors (24h)</p>
              <p className="text-2xl font-bold text-red-400">{systemHealth?.errors_24h || 0}</p>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-4">
              <p className="text-slate-400 text-sm">Operations (24h)</p>
              <p className="text-2xl font-bold text-emerald-400">{systemHealth?.total_operations_24h || 0}</p>
            </div>
          </div>
        </Card>

        {/* Subscription Breakdown */}
        <Card className="bg-slate-800 border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Subscription Breakdown</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <RePieChart>
                <Pie
                  data={summary.subscriptions || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  dataKey="count"
                  nameKey="plan"
                  label={({ plan, count }) => `${plan}: ${count}`}
                >
                  {(summary.subscriptions || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
              </RePieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
}

// User Metrics Section
function UserMetricsSection({ userMetrics, userGrowth }) {
  if (!userMetrics) return <p className="text-slate-400">Loading user metrics...</p>;
  
  return (
    <div className="space-y-6" data-testid="user-metrics-section">
      <h2 className="text-xl font-bold text-white">User Metrics</h2>
      
      {/* Core Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <MetricCard title="Total Users" value={userMetrics.total_users} icon={Users} color="indigo" />
        <MetricCard title="DAU" value={userMetrics.dau} subtext="Active Today" icon={UserCheck} color="emerald" />
        <MetricCard title="WAU" value={userMetrics.wau} subtext="Active This Week" icon={Calendar} color="blue" />
        <MetricCard title="MAU" value={userMetrics.mau} subtext="Active This Month" icon={TrendingUp} color="purple" />
        <MetricCard title="Stickiness" value={`${userMetrics.stickiness}%`} subtext="DAU/MAU" icon={Target} color="amber" />
      </div>

      {/* Growth & Churn */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="New Today" 
          value={userMetrics.new_users_today} 
          icon={UserPlus} 
          color="emerald" 
        />
        <MetricCard 
          title="Growth Rate" 
          value={`${userMetrics.growth_rate > 0 ? '+' : ''}${userMetrics.growth_rate}%`} 
          subtext="Week over Week"
          icon={userMetrics.growth_rate >= 0 ? TrendingUp : TrendingDown} 
          color={userMetrics.growth_rate >= 0 ? 'emerald' : 'red'} 
        />
        <MetricCard 
          title="Churned Users" 
          value={userMetrics.churned_users} 
          subtext="Inactive 30+ days"
          icon={UserMinus} 
          color="red" 
        />
        <MetricCard 
          title="Returning" 
          value={userMetrics.returning_users} 
          subtext="Active today & before"
          icon={RefreshCw} 
          color="blue" 
        />
      </div>

      {/* Verification Stats */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Email Verification</h3>
        <div className="flex items-center gap-8">
          <div>
            <p className="text-4xl font-bold text-emerald-400">{userMetrics.verified_users}</p>
            <p className="text-slate-400">Verified Users</p>
          </div>
          <div className="flex-1 bg-slate-700 rounded-full h-4 overflow-hidden">
            <div 
              className="bg-emerald-500 h-full rounded-full transition-all"
              style={{ width: `${userMetrics.verification_rate}%` }}
            />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{userMetrics.verification_rate}%</p>
            <p className="text-slate-400">Verification Rate</p>
          </div>
        </div>
      </Card>

      {/* User Growth Chart */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">User Growth Trend</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={userGrowth.slice(-14)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" tick={{ fontSize: 10 }} />
              <YAxis stroke="#9CA3AF" />
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
              <Bar dataKey="new_users" fill="#6366F1" name="New Users" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}

// Activity Section
function ActivitySection({ activity }) {
  if (!activity) return <p className="text-slate-400">Loading activity data...</p>;
  
  return (
    <div className="space-y-6" data-testid="activity-section">
      <h2 className="text-xl font-bold text-white">Activity Analytics</h2>

      {/* Top Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-slate-800 border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Top Actions</h3>
          <div className="space-y-3">
            {activity.top_actions?.slice(0, 8).map((action, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-slate-300 capitalize">{action.action?.replace(/_/g, ' ')}</span>
                <span className="text-indigo-400 font-semibold">{action.count}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card className="bg-slate-800 border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Resource Types</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <RePieChart>
                <Pie
                  data={activity.resource_types || []}
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  dataKey="count"
                  nameKey="resource_type"
                  label={({ resource_type }) => resource_type}
                >
                  {(activity.resource_types || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
              </RePieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Hourly Distribution */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Activity by Hour of Day</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={activity.hour_distribution || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="hour" stroke="#9CA3AF" tickFormatter={(h) => `${h}:00`} />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} 
                labelFormatter={(h) => `${h}:00`}
              />
              <Bar dataKey="count" fill="#14B8A6" name="Actions" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Power Users */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Power Users (Top 10)</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">User</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Name</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {activity.power_users?.map((user, idx) => (
                <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-3 px-4 text-sm text-white">{user.user__email}</td>
                  <td className="py-3 px-4 text-sm text-slate-400">{user.user__name}</td>
                  <td className="py-3 px-4 text-sm font-bold text-indigo-400 text-right">{user.action_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

// Projects Section
function ProjectsSection({ projectAnalytics }) {
  if (!projectAnalytics) return <p className="text-slate-400">Loading project data...</p>;
  
  return (
    <div className="space-y-6" data-testid="projects-section">
      <h2 className="text-xl font-bold text-white">Project Analytics</h2>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard title="Total Projects" value={projectAnalytics.total_projects} icon={FolderKanban} color="indigo" />
        <MetricCard title="This Period" value={projectAnalytics.projects_this_period} subtext="Last 30 days" icon={Calendar} color="emerald" />
        <MetricCard title="Total Rows" value={(projectAnalytics.total_rows_processed || 0).toLocaleString()} icon={Database} color="blue" />
        <MetricCard title="Avg Rows/Project" value={(projectAnalytics.avg_rows_per_project || 0).toLocaleString()} icon={BarChart3} color="purple" />
      </div>

      {/* Analysis Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard title="Total Analyses" value={projectAnalytics.total_analyses} icon={LineChart} color="amber" />
        <MetricCard title="Analyses (30d)" value={projectAnalytics.analyses_this_period} icon={Activity} color="emerald" />
        <MetricCard title="Transformations" value={projectAnalytics.total_transformations} icon={RefreshCw} color="purple" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Breakdown */}
        <Card className="bg-slate-800 border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Project Status</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <RePieChart>
                <Pie
                  data={projectAnalytics.status_breakdown || []}
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  dataKey="count"
                  nameKey="status"
                  label={({ status, count }) => `${status}: ${count}`}
                >
                  {(projectAnalytics.status_breakdown || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
              </RePieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Source Breakdown */}
        <Card className="bg-slate-800 border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Data Sources</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={projectAnalytics.source_breakdown || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" stroke="#9CA3AF" />
                <YAxis type="category" dataKey="source_type" stroke="#9CA3AF" width={100} />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
                <Bar dataKey="count" fill="#6366F1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Common Transformations */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Most Common Transformations</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {projectAnalytics.common_actions?.slice(0, 10).map((action, idx) => (
            <div key={idx} className="bg-slate-700/50 rounded-lg p-3 text-center">
              <p className="text-lg font-bold text-indigo-400">{action.count}</p>
              <p className="text-xs text-slate-400 capitalize">{action.action?.replace(/_/g, ' ')}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

// Pipelines Section
function PipelinesSection({ pipelineAnalytics }) {
  if (!pipelineAnalytics) return <p className="text-slate-400">Loading pipeline data...</p>;
  
  return (
    <div className="space-y-6" data-testid="pipelines-section">
      <h2 className="text-xl font-bold text-white">Pipeline Analytics</h2>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard title="Total Pipelines" value={pipelineAnalytics.total_pipelines} icon={Zap} color="indigo" />
        <MetricCard title="Active" value={pipelineAnalytics.active_pipelines} icon={Play} color="emerald" />
        <MetricCard title="Paused" value={pipelineAnalytics.paused_pipelines} icon={Pause} color="amber" />
        <MetricCard 
          title="Success Rate" 
          value={`${pipelineAnalytics.success_rate}%`} 
          icon={CheckCircle2} 
          color={pipelineAnalytics.success_rate >= 90 ? 'emerald' : pipelineAnalytics.success_rate >= 70 ? 'amber' : 'red'} 
        />
      </div>

      {/* Run Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard title="Total Runs" value={pipelineAnalytics.total_runs} icon={RefreshCw} color="blue" />
        <MetricCard title="Runs (30d)" value={pipelineAnalytics.runs_this_period} icon={Calendar} color="purple" />
        <MetricCard title="Avg Duration" value={`${pipelineAnalytics.avg_duration_seconds}s`} icon={Timer} color="amber" />
      </div>

      {/* Run Status Chart */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Run Status (Last 30 Days)</h3>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <RePieChart>
              <Pie
                data={pipelineAnalytics.run_status || []}
                cx="50%"
                cy="50%"
                outerRadius={70}
                dataKey="count"
                nameKey="status"
                label={({ status, count }) => `${status}: ${count}`}
              >
                {(pipelineAnalytics.run_status || []).map((entry, index) => {
                  const colors = { completed: '#10B981', failed: '#EF4444', running: '#6366F1', pending: '#F59E0B' };
                  return <Cell key={`cell-${index}`} fill={colors[entry.status] || COLORS[index]} />;
                })}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
            </RePieChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Top Pipelines */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Most Active Pipelines</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Pipeline</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Project</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Schedule</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Status</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Runs</th>
              </tr>
            </thead>
            <tbody>
              {pipelineAnalytics.top_pipelines?.map((pipeline, idx) => (
                <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-3 px-4 text-sm text-white">{pipeline.name}</td>
                  <td className="py-3 px-4 text-sm text-slate-400">{pipeline.project}</td>
                  <td className="py-3 px-4 text-sm text-slate-400 capitalize">{pipeline.schedule_type}</td>
                  <td className="py-3 px-4">
                    {pipeline.is_active ? (
                      <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded-full">Active</span>
                    ) : (
                      <span className="px-2 py-1 bg-amber-500/20 text-amber-400 text-xs rounded-full">Paused</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-sm font-bold text-indigo-400 text-right">{pipeline.run_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

// Retention Section
function RetentionSection({ retention, funnel }) {
  return (
    <div className="space-y-6" data-testid="retention-section">
      <h2 className="text-xl font-bold text-white">Retention & Funnel Analytics</h2>
      
      {/* Retention Metrics */}
      {retention && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <MetricCard title="Day 1 Retention" value={`${retention.day1_retention}%`} icon={Clock} color="indigo" />
            <MetricCard title="Day 7 Retention" value={`${retention.day7_retention}%`} icon={Calendar} color="emerald" />
            <MetricCard title="Day 30 Retention" value={`${retention.day30_retention}%`} icon={Target} color="purple" />
          </div>

          {/* Cohort Table */}
          <Card className="bg-slate-800 border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Cohort Retention</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Cohort</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Users</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Month 1</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Month 2</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-slate-400">Month 3</th>
                  </tr>
                </thead>
                <tbody>
                  {retention.cohort_retention?.map((cohort, idx) => (
                    <tr key={idx} className="border-b border-slate-700/50">
                      <td className="py-3 px-4 text-sm text-white">{cohort.cohort}</td>
                      <td className="py-3 px-4 text-sm text-slate-400 text-right">{cohort.total}</td>
                      <td className="py-3 px-4 text-sm text-right">
                        {cohort.month_1 !== undefined ? (
                          <span className={cohort.month_1 > 30 ? 'text-emerald-400' : 'text-amber-400'}>{cohort.month_1}%</span>
                        ) : '-'}
                      </td>
                      <td className="py-3 px-4 text-sm text-right">
                        {cohort.month_2 !== undefined ? (
                          <span className={cohort.month_2 > 20 ? 'text-emerald-400' : 'text-amber-400'}>{cohort.month_2}%</span>
                        ) : '-'}
                      </td>
                      <td className="py-3 px-4 text-sm text-right">
                        {cohort.month_3 !== undefined ? (
                          <span className={cohort.month_3 > 15 ? 'text-emerald-400' : 'text-amber-400'}>{cohort.month_3}%</span>
                        ) : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}

      {/* User Journey Funnel */}
      {funnel && (
        <Card className="bg-slate-800 border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">User Journey Funnel</h3>
          <div className="space-y-3">
            {funnel.funnel?.map((stage, idx) => (
              <div key={idx} className="flex items-center gap-4">
                <div className="w-32 text-sm text-slate-400">{stage.stage}</div>
                <div className="flex-1 bg-slate-700 rounded-full h-8 overflow-hidden relative">
                  <div 
                    className="h-full rounded-full transition-all bg-gradient-to-r from-indigo-600 to-indigo-400"
                    style={{ width: `${stage.rate}%` }}
                  />
                  <span className="absolute inset-0 flex items-center justify-center text-sm font-medium text-white">
                    {stage.count} ({stage.rate}%)
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}

// System Health Section
function SystemSection({ systemHealth }) {
  if (!systemHealth) return <p className="text-slate-400">Loading system data...</p>;
  
  return (
    <div className="space-y-6" data-testid="system-section">
      <h2 className="text-xl font-bold text-white">System Health</h2>
      
      {/* Status Banner */}
      <Card className={`p-6 border ${
        systemHealth.status === 'healthy' ? 'bg-emerald-500/10 border-emerald-500/30' :
        systemHealth.status === 'warning' ? 'bg-amber-500/10 border-amber-500/30' :
        'bg-red-500/10 border-red-500/30'
      }`}>
        <div className="flex items-center gap-4">
          {systemHealth.status === 'healthy' ? (
            <CheckCircle2 className="w-12 h-12 text-emerald-400" />
          ) : systemHealth.status === 'warning' ? (
            <AlertTriangle className="w-12 h-12 text-amber-400" />
          ) : (
            <XCircle className="w-12 h-12 text-red-400" />
          )}
          <div>
            <h3 className="text-2xl font-bold text-white">System Status: {systemHealth.status?.toUpperCase()}</h3>
            <p className="text-slate-400">
              {systemHealth.status === 'healthy' ? 'All systems operational' : 
               systemHealth.status === 'warning' ? 'Some issues detected' : 
               'Critical issues require attention'}
            </p>
          </div>
        </div>
      </Card>

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard 
          title="Database Response" 
          value={`${systemHealth.db_response_ms}ms`} 
          icon={Database}
          color={systemHealth.db_response_ms < 100 ? 'emerald' : systemHealth.db_response_ms < 500 ? 'amber' : 'red'}
        />
        <MetricCard 
          title="Error Rate" 
          value={`${systemHealth.error_rate}%`} 
          icon={AlertTriangle}
          color={systemHealth.error_rate < 1 ? 'emerald' : systemHealth.error_rate < 5 ? 'amber' : 'red'}
        />
        <MetricCard 
          title="Errors (24h)" 
          value={systemHealth.errors_24h} 
          icon={XCircle}
          color={systemHealth.errors_24h === 0 ? 'emerald' : systemHealth.errors_24h < 10 ? 'amber' : 'red'}
        />
        <MetricCard 
          title="Operations (24h)" 
          value={systemHealth.total_operations_24h} 
          icon={Activity}
          color="blue"
        />
      </div>

      {/* Database Stats */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Database Statistics</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-700/50 rounded-lg p-4">
            <p className="text-slate-400 text-sm">Total Users in DB</p>
            <p className="text-3xl font-bold text-white">{systemHealth.total_users}</p>
          </div>
          <div className="bg-slate-700/50 rounded-lg p-4">
            <p className="text-slate-400 text-sm">Total Projects in DB</p>
            <p className="text-3xl font-bold text-white">{systemHealth.total_projects}</p>
          </div>
        </div>
      </Card>
    </div>
  );
}

// Users List Section
function UsersListSection({ users }) {
  return (
    <div className="space-y-6" data-testid="users-list-section">
      <h2 className="text-xl font-bold text-white">All Users ({users.length})</h2>
      
      <Card className="bg-slate-800 border-slate-700 p-6">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Email</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Name</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Status</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Projects</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Plan</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user, idx) => (
                <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-3 px-4 text-sm text-white">{user.email}</td>
                  <td className="py-3 px-4 text-sm text-slate-400">{user.name}</td>
                  <td className="py-3 px-4">
                    {user.is_verified ? (
                      <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded-full">Verified</span>
                    ) : (
                      <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded-full">Unverified</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-sm font-bold text-indigo-400">{user.project_count}</td>
                  <td className="py-3 px-4 text-sm text-slate-400 capitalize">{user.subscription}</td>
                  <td className="py-3 px-4 text-sm text-slate-400">{new Date(user.date_joined).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

// Projects List Section
function ProjectsListSection({ projects }) {
  return (
    <div className="space-y-6" data-testid="projects-list-section">
      <h2 className="text-xl font-bold text-white">All Projects ({projects.length})</h2>
      
      <Card className="bg-slate-800 border-slate-700 p-6">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Project</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">User</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Source</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Status</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Rows</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Created</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((project, idx) => (
                <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-3 px-4 text-sm font-medium text-white">{project.name}</td>
                  <td className="py-3 px-4 text-sm text-slate-400">{project.user_email}</td>
                  <td className="py-3 px-4 text-sm text-slate-400 capitalize">{project.source_type?.replace('_', ' ')}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full capitalize">{project.status}</span>
                  </td>
                  <td className="py-3 px-4 text-sm text-slate-400">{project.row_count?.toLocaleString() || '-'}</td>
                  <td className="py-3 px-4 text-sm text-slate-400">{new Date(project.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

// Activity Feed Section
function ActivityFeedSection({ activityFeed }) {
  return (
    <div className="space-y-6" data-testid="feed-section">
      <h2 className="text-xl font-bold text-white">Real-time Activity Feed</h2>
      
      <Card className="bg-slate-800 border-slate-700 p-6">
        <div className="space-y-3 max-h-[600px] overflow-y-auto">
          {activityFeed.map((activity, idx) => (
            <div key={idx} className="flex items-start gap-4 p-3 bg-slate-700/30 rounded-lg hover:bg-slate-700/50 transition-colors">
              <div className="w-10 h-10 bg-indigo-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                <Activity className="w-5 h-5 text-indigo-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-white">{activity.user_name || activity.user_email}</span>
                  <span className="text-xs text-slate-500">{new Date(activity.timestamp).toLocaleString()}</span>
                </div>
                <p className="text-sm text-slate-400 mt-1">
                  <span className="text-indigo-400 capitalize">{activity.action?.replace(/_/g, ' ')}</span>
                  {' on '}
                  <span className="text-slate-300">{activity.resource_type}</span>
                </p>
              </div>
            </div>
          ))}
          {activityFeed.length === 0 && (
            <p className="text-slate-400 text-center py-8">No recent activity</p>
          )}
        </div>
      </Card>
    </div>
  );
}

// Reusable Metric Card Component
function MetricCard({ title, value, subtext, icon: Icon, trend, color = 'indigo' }) {
  const colorClasses = {
    indigo: 'bg-indigo-500/20 text-indigo-400',
    emerald: 'bg-emerald-500/20 text-emerald-400',
    amber: 'bg-amber-500/20 text-amber-400',
    red: 'bg-red-500/20 text-red-400',
    purple: 'bg-purple-500/20 text-purple-400',
    blue: 'bg-blue-500/20 text-blue-400',
  };
  
  return (
    <Card className="bg-slate-800 border-slate-700 p-4">
      <div className="flex items-start gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colorClasses[color]}`}>
          <Icon size={20} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs text-slate-400 truncate">{title}</p>
          <p className="text-xl font-bold text-white">{value}</p>
          {subtext && <p className="text-xs text-slate-500 truncate">{subtext}</p>}
        </div>
      </div>
    </Card>
  );
}

export default AdminDashboard;
