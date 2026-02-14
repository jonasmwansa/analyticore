import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Database, Home, FolderKanban, Clock, Shield, Settings, LogOut,
  ChevronLeft, ChevronRight, Bell, User, BarChart3, Menu, X
} from 'lucide-react';
import { Button } from './ui/button';
import { authAPI } from '../api';
import NotificationBell from './NotificationBell';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';

const MENU_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: Home, path: '/dashboard' },
  { id: 'schedules', label: 'Schedules', icon: Clock, path: '/schedules' },
  { id: 'security', label: 'Security', icon: Shield, path: '/settings/security' },
  { id: 'notifications', label: 'Notifications', icon: Bell, path: '/settings/notifications' },
];

const ADMIN_MENU_ITEMS = [
  { id: 'admin', label: 'Admin Dashboard', icon: BarChart3, path: '/admin', adminOnly: true },
];

export default function DashboardLayout({ children, user }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Close mobile menu when route changes
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Check for saved sidebar state
  useEffect(() => {
    const saved = localStorage.getItem('sidebar_collapsed');
    if (saved !== null) {
      setSidebarCollapsed(JSON.parse(saved));
    }
  }, []);

  const toggleSidebar = () => {
    const newState = !sidebarCollapsed;
    setSidebarCollapsed(newState);
    localStorage.setItem('sidebar_collapsed', JSON.stringify(newState));
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

  const isActive = (path) => {
    if (path === '/dashboard') {
      return location.pathname === '/dashboard' || location.pathname.startsWith('/projects/');
    }
    return location.pathname === path || location.pathname.startsWith(path);
  };

  const allMenuItems = [
    ...MENU_ITEMS,
    ...(user?.is_staff ? ADMIN_MENU_ITEMS : [])
  ];

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex">
      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 bg-white border-r border-slate-200 flex flex-col transition-all duration-300 
          ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          ${sidebarCollapsed ? 'lg:w-20' : 'lg:w-64'} w-64`}
        data-testid="dashboard-sidebar"
      >
        {/* Logo Header */}
        <div className={`h-16 border-b border-slate-200 flex items-center ${sidebarCollapsed ? 'justify-center px-2' : 'justify-between px-4'}`}>
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/dashboard')}>
              <Database className="w-8 h-8 text-[#6366F1]" />
              <span className="text-xl font-bold text-[#0F172A]">AnalytiCore</span>
            </div>
          )}
          {sidebarCollapsed && (
            <Database className="w-8 h-8 text-[#6366F1] cursor-pointer" onClick={() => navigate('/dashboard')} />
          )}
          <button
            onClick={toggleSidebar}
            className="hidden lg:flex p-2 rounded-lg hover:bg-slate-100 text-slate-500 transition-colors"
            data-testid="toggle-sidebar-btn"
          >
            {sidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="lg:hidden p-2 rounded-lg hover:bg-slate-100 text-slate-500"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 overflow-y-auto">
          <div className={`${sidebarCollapsed ? 'px-2' : 'px-3'}`}>
            {!sidebarCollapsed && (
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 px-3">
                Main Menu
              </p>
            )}
            <div className="space-y-1">
              {allMenuItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center gap-3 rounded-lg transition-all ${
                    sidebarCollapsed ? 'justify-center p-3' : 'px-3 py-2.5'
                  } ${
                    isActive(item.path)
                      ? 'bg-[#6366F1] text-white shadow-md shadow-indigo-500/25'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`}
                  data-testid={`nav-${item.id}`}
                  title={sidebarCollapsed ? item.label : undefined}
                >
                  <item.icon size={20} className={isActive(item.path) ? 'text-white' : ''} />
                  {!sidebarCollapsed && (
                    <span className="text-sm font-medium">{item.label}</span>
                  )}
                  {item.adminOnly && !sidebarCollapsed && (
                    <span className="ml-auto px-2 py-0.5 text-xs bg-amber-100 text-amber-700 rounded-full">
                      Admin
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        </nav>

        {/* User Section */}
        <div className={`border-t border-slate-200 p-4 ${sidebarCollapsed ? 'flex justify-center' : ''}`}>
          {sidebarCollapsed ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="w-10 h-10 rounded-full bg-[#6366F1] flex items-center justify-center text-white font-semibold">
                  {user?.name?.[0]?.toUpperCase() || 'U'}
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56 bg-white">
                <div className="px-3 py-2">
                  <p className="font-medium text-slate-900">{user?.name}</p>
                  <p className="text-sm text-slate-500">{user?.email}</p>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => navigate('/settings/security')} className="cursor-pointer">
                  <Shield className="w-4 h-4 mr-2" />
                  Security Settings
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/settings/notifications')} className="cursor-pointer">
                  <Bell className="w-4 h-4 mr-2" />
                  Notifications
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-red-600">
                  <LogOut className="w-4 h-4 mr-2" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[#6366F1] flex items-center justify-center text-white font-semibold flex-shrink-0">
                {user?.name?.[0]?.toUpperCase() || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 truncate">{user?.name}</p>
                <p className="text-xs text-slate-500 truncate">{user?.email}</p>
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="p-2 rounded-lg hover:bg-slate-100 text-slate-500">
                    <Settings size={18} />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48 bg-white">
                  <DropdownMenuItem onClick={() => navigate('/settings/security')} className="cursor-pointer">
                    <Shield className="w-4 h-4 mr-2" />
                    Security
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate('/settings/notifications')} className="cursor-pointer">
                    <Bell className="w-4 h-4 mr-2" />
                    Notifications
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-red-600">
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 lg:px-6 sticky top-0 z-30">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-slate-100 text-slate-600"
              data-testid="mobile-menu-btn"
            >
              <Menu size={24} />
            </button>
          </div>
          
          <div className="flex items-center gap-3">
            <NotificationBell />
            <div className="hidden sm:block text-right">
              <p className="text-sm font-medium text-slate-900">{user?.name}</p>
              <p className="text-xs text-slate-500">
                {user?.is_staff ? 'Administrator' : 'User'}
              </p>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
