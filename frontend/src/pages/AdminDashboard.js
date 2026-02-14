import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { 
  Database, Users, FolderKanban, Activity, TrendingUp, 
  ArrowLeft, BarChart3, PieChart, Calendar 
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { adminAPI, authAPI } from '../api';

function AdminDashboard({ user }) {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('overview');

  useEffect(() => {
    if (!user?.is_staff) {
      toast.error('Access denied: Admin only');
      navigate('/dashboard');
      return;
    }
    fetchDashboardData();
  }, [user, navigate]);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, usersRes, projectsRes] = await Promise.all([
        adminAPI.getDashboard(),
        adminAPI.getUsers(),
        adminAPI.getProjects()
      ]);
      
      setStats(statsRes.data);
      setUsers(usersRes.data.users);
      setProjects(projectsRes.data.projects);
    } catch (error) {
      toast.error('Failed to load admin data');
    } finally {
      setLoading(false);
    }
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

  if (loading) {
    return (
      <div className=\"min-h-screen flex items-center justify-center bg-[#F8FAFC]\">
        <div className=\"text-center\">
          <div className=\"w-16 h-16 border-4 border-[#6366F1] border-t-transparent rounded-full animate-spin mx-auto mb-4\"></div>
          <p className=\"text-[#64748B]\">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className=\"min-h-screen bg-[#F8FAFC]\">
      <nav className=\"bg-white border-b border-slate-200 sticky top-0 z-50\">
        <div className=\"max-w-7xl mx-auto px-6 py-4 flex justify-between items-center\">
          <div className=\"flex items-center gap-4\">
            <Database className=\"w-8 h-8 text-[#6366F1]\" />
            <span className=\"text-2xl font-bold text-[#0F172A]\">AnalytiCore Admin</span>
            <span className=\"px-3 py-1 bg-[#EEF2FF] text-[#6366F1] text-sm font-semibold rounded-full\">Admin</span>
          </div>
          <div className=\"flex items-center gap-4\">
            <Button
              variant=\"ghost\"
              onClick={() => navigate('/dashboard')}
              className=\"text-slate-700\"
            >
              <ArrowLeft className=\"w-5 h-5 mr-2\" />
              Back to Client Dashboard
            </Button>
            <Button
              variant=\"ghost\"
              onClick={handleLogout}
              className=\"text-slate-700\"
            >
              Logout
            </Button>
          </div>
        </div>
      </nav>

      <main className=\"max-w-7xl mx-auto px-6 py-8\">
        <div className=\"mb-8\">
          <h1 className=\"text-4xl font-bold text-[#0F172A] mb-2\">SaaS Administration</h1>
          <p className=\"text-lg text-[#64748B]\">Monitor users, projects, and platform analytics</p>
        </div>

        <div className=\"flex gap-4 mb-8\">
          <Button
            onClick={() => setActiveView('overview')}
            className={activeView === 'overview' ? 'bg-[#6366F1] text-white' : 'bg-white text-slate-700 border border-slate-200'}
          >
            <BarChart3 className=\"w-5 h-5 mr-2\" />
            Overview
          </Button>
          <Button
            onClick={() => setActiveView('users')}
            className={activeView === 'users' ? 'bg-[#6366F1] text-white' : 'bg-white text-slate-700 border border-slate-200'}
          >
            <Users className=\"w-5 h-5 mr-2\" />
            Users
          </Button>
          <Button
            onClick={() => setActiveView('projects')}
            className={activeView === 'projects' ? 'bg-[#6366F1] text-white' : 'bg-white text-slate-700 border border-slate-200'}
          >
            <FolderKanban className=\"w-5 h-5 mr-2\" />
            Projects
          </Button>
        </div>

        {activeView === 'overview' && stats && (
          <div>
            <div className=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8\">
              <Card className=\"stat-card bg-white border border-slate-200 rounded-xl p-6 shadow-sm\">
                <div className=\"flex items-center gap-3\">
                  <div className=\"w-12 h-12 bg-[#EEF2FF] rounded-lg flex items-center justify-center\">
                    <Users className=\"w-6 h-6 text-[#6366F1]\" />
                  </div>
                  <div>
                    <p className=\"text-sm text-[#94A3B8]\">Total Users</p>
                    <p className=\"text-2xl font-bold text-[#0F172A]\">{stats.overview.total_users}</p>
                    <p className=\"text-xs text-[#14B8A6]\">+{stats.overview.new_users_30d} this month</p>
                  </div>
                </div>
              </Card>

              <Card className=\"stat-card bg-white border border-slate-200 rounded-xl p-6 shadow-sm\">
                <div className=\"flex items-center gap-3\">
                  <div className=\"w-12 h-12 bg-[#F0FDFA] rounded-lg flex items-center justify-center\">
                    <CheckCircle2 className=\"w-6 h-6 text-[#14B8A6]\" />
                  </div>
                  <div>
                    <p className=\"text-sm text-[#94A3B8]\">Verified Users</p>
                    <p className=\"text-2xl font-bold text-[#0F172A]\">{stats.overview.verified_users}</p>
                    <p className=\"text-xs text-[#64748B]\">{Math.round((stats.overview.verified_users / stats.overview.total_users) * 100)}% verified</p>
                  </div>
                </div>
              </Card>

              <Card className=\"stat-card bg-white border border-slate-200 rounded-xl p-6 shadow-sm\">
                <div className=\"flex items-center gap-3\">
                  <div className=\"w-12 h-12 bg-[#FEF3F2] rounded-lg flex items-center justify-center\">
                    <FolderKanban className=\"w-6 h-6 text-[#F59E0B]\" />
                  </div>
                  <div>
                    <p className=\"text-sm text-[#94A3B8]\">Total Projects</p>
                    <p className=\"text-2xl font-bold text-[#0F172A]\">{stats.overview.total_projects}</p>
                    <p className=\"text-xs text-[#F59E0B]\">+{stats.overview.new_projects_30d} this month</p>
                  </div>
                </div>
              </Card>

              <Card className=\"stat-card bg-white border border-slate-200 rounded-xl p-6 shadow-sm\">
                <div className=\"flex items-center gap-3\">
                  <div className=\"w-12 h-12 bg-[#F3F4F6] rounded-lg flex items-center justify-center\">
                    <TrendingUp className=\"w-6 h-6 text-[#8B5CF6]\" />
                  </div>
                  <div>
                    <p className=\"text-sm text-[#94A3B8]\">Avg Projects/User</p>
                    <p className=\"text-2xl font-bold text-[#0F172A]\">{(stats.overview.total_projects / stats.overview.total_users).toFixed(1)}</p>
                  </div>
                </div>
              </Card>
            </div>

            <div className=\"grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8\">
              <Card className=\"bg-white border border-slate-200 rounded-xl p-6 shadow-sm\">
                <h3 className=\"text-lg font-bold text-[#0F172A] mb-4\">Subscription Breakdown</h3>
                <div className=\"space-y-3\">
                  {stats.subscriptions.map((sub, idx) => (
                    <div key={idx} className=\"flex items-center justify-between\">
                      <span className=\"text-[#64748B] font-medium capitalize\">{sub.plan}</span>
                      <span className=\"text-[#0F172A] font-bold\">{sub.count} users</span>
                    </div>
                  ))}
                </div>
              </Card>

              <Card className=\"bg-white border border-slate-200 rounded-xl p-6 shadow-sm\">
                <h3 className=\"text-lg font-bold text-[#0F172A] mb-4\">Project Status</h3>
                <div className=\"space-y-3\">
                  {stats.project_statuses.map((status, idx) => (
                    <div key={idx} className=\"flex items-center justify-between\">
                      <span className=\"text-[#64748B] font-medium capitalize\">{status.status}</span>
                      <span className=\"text-[#0F172A] font-bold\">{status.count}</span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            <Card className=\"bg-white border border-slate-200 rounded-xl p-6 shadow-sm\">
              <h3 className=\"text-lg font-bold text-[#0F172A] mb-4\">Top Users by Project Count</h3>
              <div className=\"overflow-x-auto\">
                <table className=\"w-full\">
                  <thead>
                    <tr className=\"border-b border-slate-200\">
                      <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Email</th>
                      <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Name</th>
                      <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Projects</th>
                      <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Joined</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.top_users.map((user, idx) => (
                      <tr key={idx} className=\"border-b border-slate-100 hover:bg-slate-50\">
                        <td className=\"py-3 px-4 text-sm text-[#0F172A]\">{user.email}</td>
                        <td className=\"py-3 px-4 text-sm text-[#64748B]\">{user.name}</td>
                        <td className=\"py-3 px-4 text-sm font-bold text-[#6366F1]\">{user.project_count}</td>
                        <td className=\"py-3 px-4 text-sm text-[#64748B]\">{new Date(user.date_joined).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        )}

        {activeView === 'users' && (
          <Card className=\"bg-white border border-slate-200 rounded-xl p-6 shadow-sm\">
            <h3 className=\"text-lg font-bold text-[#0F172A] mb-4\">All Users ({users.length})</h3>
            <div className=\"overflow-x-auto\">
              <table className=\"w-full\">
                <thead>
                  <tr className=\"border-b border-slate-200\">
                    <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Email</th>
                    <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Name</th>
                    <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Status</th>
                    <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Projects</th>
                    <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Subscription</th>
                    <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Joined</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user, idx) => (
                    <tr key={idx} className=\"border-b border-slate-100 hover:bg-slate-50\">
                      <td className=\"py-3 px-4 text-sm text-[#0F172A]\">{user.email}</td>
                      <td className=\"py-3 px-4 text-sm text-[#64748B]\">{user.name}</td>
                      <td className=\"py-3 px-4\">
                        {user.is_verified ? (
                          <span className=\"px-2 py-1 bg-[#DCFCE7] text-[#14B8A6] text-xs rounded-full font-semibold\">Verified</span>
                        ) : (
                          <span className=\"px-2 py-1 bg-[#FEE2E2] text-[#F43F5E] text-xs rounded-full font-semibold\">Unverified</span>
                        )}
                      </td>
                      <td className=\"py-3 px-4 text-sm font-bold text-[#6366F1]\">{user.project_count}</td>
                      <td className=\"py-3 px-4 text-sm text-[#64748B] capitalize\">{user.subscription}</td>
                      <td className=\"py-3 px-4 text-sm text-[#64748B]\">{new Date(user.date_joined).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {activeView === 'projects' && (
          <Card className=\"bg-white border border-slate-200 rounded-xl p-6 shadow-sm\">
            <h3 className=\"text-lg font-bold text-[#0F172A] mb-4\">All Projects ({projects.length})</h3>
            <div className=\"overflow-x-auto\">
              <table className=\"w-full\">
                <thead>
                  <tr className=\"border-b border-slate-200\">
                    <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Project Name</th>
                    <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">User</th>
                    <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Source Type</th>
                    <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Status</th>
                    <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Rows</th>
                    <th className=\"text-left py-3 px-4 text-sm font-semibold text-[#64748B]\">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {projects.map((project, idx) => (
                    <tr key={idx} className=\"border-b border-slate-100 hover:bg-slate-50\">
                      <td className=\"py-3 px-4 text-sm font-medium text-[#0F172A]\">{project.name}</td>
                      <td className=\"py-3 px-4 text-sm text-[#64748B]\">{project.user_email}</td>
                      <td className=\"py-3 px-4 text-sm text-[#64748B] capitalize\">{project.source_type.replace('_', ' ')}</td>
                      <td className=\"py-3 px-4\">
                        <span className=\"px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full font-semibold capitalize\">{project.status}</span>
                      </td>
                      <td className=\"py-3 px-4 text-sm text-[#64748B]\">{project.row_count?.toLocaleString() || '-'}</td>
                      <td className=\"py-3 px-4 text-sm text-[#64748B]\">{new Date(project.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </main>
    </div>
  );
}

export default AdminDashboard;
