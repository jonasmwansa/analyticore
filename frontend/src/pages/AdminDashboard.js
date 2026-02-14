import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { 
  Database, Users, FolderKanban, Activity, ArrowLeft, Home, Bell, Settings,
  Server, UserCheck, Layers, Zap, Target, ChevronDown, ChevronRight, RefreshCw, Loader2
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { adminAPI, authAPI } from '../api';

// Import all admin section components
import {
  OverviewSection,
  UserMetricsSection,
  ActivitySection,
  ProjectsSection,
  PipelinesSection,
  RetentionSection,
  SystemSection,
  UsersListSection,
  ProjectsListSection,
  ActivityFeedSection,
  AlertSettingsSection
} from '../components/admin';

const MENU_ITEMS = [
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

  const renderSection = () => {
    switch (activeSection) {
      case 'overview':
        return <OverviewSection summary={summary} userMetrics={userMetrics} userGrowth={userGrowth} systemHealth={systemHealth} />;
      case 'users':
        return <UserMetricsSection userMetrics={userMetrics} userGrowth={userGrowth} />;
      case 'activity':
        return <ActivitySection activity={activity} />;
      case 'projects':
        return <ProjectsSection projectAnalytics={projectAnalytics} />;
      case 'pipelines':
        return <PipelinesSection pipelineAnalytics={pipelineAnalytics} />;
      case 'retention':
        return <RetentionSection retention={retention} funnel={funnel} />;
      case 'system':
        return <SystemSection systemHealth={systemHealth} />;
      case 'users-list':
        return <UsersListSection users={users} />;
      case 'projects-list':
        return <ProjectsListSection projects={projects} />;
      case 'feed':
        return <ActivityFeedSection activityFeed={activityFeed} />;
      case 'settings':
        return <AlertSettingsSection />;
      default:
        return <OverviewSection summary={summary} userMetrics={userMetrics} userGrowth={userGrowth} systemHealth={systemHealth} />;
    }
  };

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
            data-testid="toggle-admin-sidebar-btn"
          >
            {sidebarCollapsed ? <ChevronRight size={18} /> : <ChevronDown size={18} />}
          </button>
        </div>
        
        <nav className="flex-1 py-4 overflow-y-auto">
          {MENU_ITEMS.map((item) => (
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
            data-testid="back-to-client-dashboard-btn"
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
                data-testid="logout-btn"
              >
                Logout
              </Button>
            </div>
          </div>
        </header>

        <div className="p-6">
          {renderSection()}
        </div>
      </main>
    </div>
  );
}

export default AdminDashboard;
