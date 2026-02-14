import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Bell, Check, CheckCheck, Trash2, X, BarChart3, AlertTriangle, Download, Upload, FolderPlus, Settings } from 'lucide-react';
import { notificationsAPI } from '../api';
import { Button } from './ui/button';

const NOTIFICATION_ICONS = {
  analysis_complete: BarChart3,
  data_issues: AlertTriangle,
  export_ready: Download,
  upload_complete: Upload,
  project_created: FolderPlus,
  transformation_applied: Settings,
  system: Bell,
};

const NOTIFICATION_COLORS = {
  analysis_complete: 'bg-green-100 text-green-600',
  data_issues: 'bg-amber-100 text-amber-600',
  export_ready: 'bg-blue-100 text-blue-600',
  upload_complete: 'bg-indigo-100 text-indigo-600',
  project_created: 'bg-purple-100 text-purple-600',
  transformation_applied: 'bg-cyan-100 text-cyan-600',
  system: 'bg-slate-100 text-slate-600',
};

function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);

  const fetchNotifications = useCallback(async () => {
    try {
      const response = await notificationsAPI.getSummary();
      setUnreadCount(response.data.unread_count);
      setNotifications(response.data.latest_unread);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    
    // Poll for new notifications every 30 seconds
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMarkRead = async (notificationId) => {
    try {
      await notificationsAPI.markRead(notificationId);
      setNotifications(prev => prev.filter(n => n.notification_id !== notificationId));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      setLoading(true);
      await notificationsAPI.markAllRead();
      setNotifications([]);
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (notificationId, e) => {
    e.stopPropagation();
    try {
      await notificationsAPI.delete(notificationId);
      setNotifications(prev => prev.filter(n => n.notification_id !== notificationId));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
        data-testid="notification-bell"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-[#F43F5E] text-white text-xs font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-xl border border-slate-200 z-50 overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-100 flex justify-between items-center bg-slate-50">
            <h3 className="font-semibold text-slate-900">Notifications</h3>
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleMarkAllRead}
                disabled={loading}
                className="text-xs text-[#6366F1] hover:text-[#4F46E5] hover:bg-indigo-50"
                data-testid="mark-all-read-btn"
              >
                <CheckCheck className="w-4 h-4 mr-1" />
                Mark all read
              </Button>
            )}
          </div>

          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="py-12 text-center">
                <Bell className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                <p className="text-slate-500">No new notifications</p>
              </div>
            ) : (
              notifications.map((notification) => {
                const Icon = NOTIFICATION_ICONS[notification.notification_type] || Bell;
                const colorClass = NOTIFICATION_COLORS[notification.notification_type] || NOTIFICATION_COLORS.system;
                
                return (
                  <div
                    key={notification.notification_id}
                    className="px-4 py-3 hover:bg-slate-50 transition-colors cursor-pointer border-b border-slate-100 last:border-0"
                    onClick={() => handleMarkRead(notification.notification_id)}
                    data-testid={`notification-${notification.notification_id}`}
                  >
                    <div className="flex gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${colorClass}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start gap-2">
                          <h4 className="font-medium text-slate-900 text-sm truncate">{notification.title}</h4>
                          <div className="flex items-center gap-1 flex-shrink-0">
                            <span className="text-xs text-slate-400">{notification.time_ago}</span>
                            <button
                              onClick={(e) => handleDelete(notification.notification_id, e)}
                              className="p-1 rounded hover:bg-slate-200 text-slate-400 hover:text-slate-600"
                              data-testid={`delete-notification-${notification.notification_id}`}
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </div>
                        </div>
                        <p className="text-sm text-slate-500 mt-0.5 line-clamp-2">{notification.message}</p>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          <div className="px-4 py-3 border-t border-slate-100 bg-slate-50">
            <a 
              href="/settings/notifications"
              className="text-sm text-[#6366F1] hover:text-[#4F46E5] font-medium"
            >
              Notification Settings
            </a>
          </div>
        </div>
      )}
    </div>
  );
}

export default NotificationBell;
