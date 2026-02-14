import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { 
  Database, ArrowLeft, Bell, Mail, Smartphone, Save, 
  Loader2, CheckCircle, Settings
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { notificationsAPI } from '../api';

function NotificationSettings({ user }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [pushSupported, setPushSupported] = useState(false);
  const [pushSubscribed, setPushSubscribed] = useState(false);
  const [subscribingPush, setSubscribingPush] = useState(false);
  
  const [preferences, setPreferences] = useState({
    email_on_analysis_complete: true,
    email_on_data_issues: true,
    email_on_export_ready: true,
    email_on_upload_complete: true,
    email_digest_frequency: 'instant',
    push_enabled: false,
    push_on_analysis_complete: true,
    push_on_data_issues: true,
    push_on_export_ready: true,
    inapp_enabled: true,
  });

  useEffect(() => {
    // Check if push notifications are supported
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      setPushSupported(true);
      checkPushSubscription();
    }
    
    fetchPreferences();
  }, []);

  const checkPushSubscription = async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      setPushSubscribed(!!subscription);
    } catch (error) {
      console.error('Error checking push subscription:', error);
    }
  };

  const fetchPreferences = async () => {
    try {
      const response = await notificationsAPI.getPreferences();
      setPreferences(response.data);
    } catch (error) {
      console.error('Failed to fetch preferences:', error);
      toast.error('Failed to load notification settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await notificationsAPI.updatePreferences(preferences);
      toast.success('Notification settings saved!');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = (key) => {
    setPreferences(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handlePushSubscription = async () => {
    if (!pushSupported) {
      toast.error('Push notifications are not supported in this browser');
      return;
    }

    setSubscribingPush(true);
    
    try {
      if (pushSubscribed) {
        // Unsubscribe
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        
        if (subscription) {
          await subscription.unsubscribe();
          await notificationsAPI.unsubscribePush(subscription.endpoint);
          setPushSubscribed(false);
          setPreferences(prev => ({ ...prev, push_enabled: false }));
          toast.success('Push notifications disabled');
        }
      } else {
        // Subscribe
        // First, request permission
        const permission = await Notification.requestPermission();
        
        if (permission !== 'granted') {
          toast.error('Notification permission denied');
          return;
        }

        // Get VAPID key
        const vapidResponse = await notificationsAPI.getVapidKey();
        const vapidPublicKey = vapidResponse.data.public_key;
        
        // Register service worker if not already registered
        const registration = await navigator.serviceWorker.register('/sw.js');
        await navigator.serviceWorker.ready;
        
        // Subscribe to push
        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
        });
        
        // Send subscription to server
        const subscriptionJson = subscription.toJSON();
        await notificationsAPI.subscribePush({
          endpoint: subscriptionJson.endpoint,
          keys: subscriptionJson.keys
        });
        
        setPushSubscribed(true);
        setPreferences(prev => ({ ...prev, push_enabled: true }));
        toast.success('Push notifications enabled!');
      }
    } catch (error) {
      console.error('Push subscription error:', error);
      toast.error('Failed to update push notification settings');
    } finally {
      setSubscribingPush(false);
    }
  };

  const handleTestNotification = async () => {
    try {
      await notificationsAPI.test('system', true, pushSubscribed);
      toast.success('Test notification sent! Check your email and notifications.');
    } catch (error) {
      toast.error('Failed to send test notification');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-[#6366F1]" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              onClick={() => navigate('/dashboard')}
              className="text-slate-600 hover:text-slate-900"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-2">
              <Database className="w-8 h-8 text-[#6366F1]" />
              <span className="text-2xl font-bold text-[#0F172A]">AnalytiCore</span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-6 py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#0F172A] mb-2">Notification Settings</h1>
          <p className="text-[#64748B]">Manage how you receive notifications from AnalytiCore</p>
        </div>

        <div className="space-y-6">
          {/* In-App Notifications */}
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-[#EEF2FF] rounded-lg flex items-center justify-center">
                <Bell className="w-5 h-5 text-[#6366F1]" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-[#0F172A]">In-App Notifications</h2>
                <p className="text-sm text-[#64748B]">Notifications that appear in the app</p>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-[#0F172A] font-medium">Enable In-App Notifications</Label>
                <p className="text-sm text-[#64748B]">Show notifications in the notification bell</p>
              </div>
              <Switch
                checked={preferences.inapp_enabled}
                onCheckedChange={() => handleToggle('inapp_enabled')}
                data-testid="inapp-toggle"
              />
            </div>
          </div>

          {/* Email Notifications */}
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-[#DCFCE7] rounded-lg flex items-center justify-center">
                <Mail className="w-5 h-5 text-[#16A34A]" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-[#0F172A]">Email Notifications</h2>
                <p className="text-sm text-[#64748B]">Receive updates via email at {user?.email}</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between py-2">
                <div>
                  <Label className="text-[#0F172A] font-medium">Analysis Complete</Label>
                  <p className="text-sm text-[#64748B]">When your data analysis finishes</p>
                </div>
                <Switch
                  checked={preferences.email_on_analysis_complete}
                  onCheckedChange={() => handleToggle('email_on_analysis_complete')}
                  data-testid="email-analysis-toggle"
                />
              </div>

              <div className="flex items-center justify-between py-2">
                <div>
                  <Label className="text-[#0F172A] font-medium">Data Issues Found</Label>
                  <p className="text-sm text-[#64748B]">When problems are detected in your data</p>
                </div>
                <Switch
                  checked={preferences.email_on_data_issues}
                  onCheckedChange={() => handleToggle('email_on_data_issues')}
                  data-testid="email-issues-toggle"
                />
              </div>

              <div className="flex items-center justify-between py-2">
                <div>
                  <Label className="text-[#0F172A] font-medium">Export Ready</Label>
                  <p className="text-sm text-[#64748B]">When your data export is ready to download</p>
                </div>
                <Switch
                  checked={preferences.email_on_export_ready}
                  onCheckedChange={() => handleToggle('email_on_export_ready')}
                  data-testid="email-export-toggle"
                />
              </div>

              <div className="flex items-center justify-between py-2">
                <div>
                  <Label className="text-[#0F172A] font-medium">Upload Complete</Label>
                  <p className="text-sm text-[#64748B]">When your data upload finishes processing</p>
                </div>
                <Switch
                  checked={preferences.email_on_upload_complete}
                  onCheckedChange={() => handleToggle('email_on_upload_complete')}
                  data-testid="email-upload-toggle"
                />
              </div>

              <div className="pt-4 border-t border-slate-100">
                <Label className="text-[#0F172A] font-medium mb-2 block">Email Frequency</Label>
                <Select 
                  value={preferences.email_digest_frequency}
                  onValueChange={(value) => setPreferences(prev => ({ ...prev, email_digest_frequency: value }))}
                >
                  <SelectTrigger className="w-48" data-testid="email-frequency-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white">
                    <SelectItem value="instant">Instant</SelectItem>
                    <SelectItem value="daily">Daily Digest</SelectItem>
                    <SelectItem value="weekly">Weekly Digest</SelectItem>
                    <SelectItem value="never">Never</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Push Notifications */}
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-[#FEF3C7] rounded-lg flex items-center justify-center">
                <Smartphone className="w-5 h-5 text-[#D97706]" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-[#0F172A]">Push Notifications</h2>
                <p className="text-sm text-[#64748B]">Get instant notifications in your browser</p>
              </div>
            </div>
            
            {!pushSupported ? (
              <div className="text-center py-6 text-[#64748B]">
                <p>Push notifications are not supported in this browser.</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between py-2">
                  <div>
                    <Label className="text-[#0F172A] font-medium">
                      {pushSubscribed ? 'Push Notifications Enabled' : 'Enable Push Notifications'}
                    </Label>
                    <p className="text-sm text-[#64748B]">
                      {pushSubscribed 
                        ? 'You will receive browser notifications' 
                        : 'Receive real-time notifications in your browser'}
                    </p>
                  </div>
                  <Button
                    variant={pushSubscribed ? 'outline' : 'default'}
                    onClick={handlePushSubscription}
                    disabled={subscribingPush}
                    className={pushSubscribed 
                      ? 'border-slate-300' 
                      : 'bg-[#6366F1] hover:bg-[#4F46E5]'}
                    data-testid="push-subscribe-btn"
                  >
                    {subscribingPush ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    ) : pushSubscribed ? (
                      <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                    ) : null}
                    {pushSubscribed ? 'Disable' : 'Enable'}
                  </Button>
                </div>

                {pushSubscribed && (
                  <>
                    <div className="flex items-center justify-between py-2">
                      <div>
                        <Label className="text-[#0F172A] font-medium">Analysis Complete</Label>
                        <p className="text-sm text-[#64748B]">Push notification when analysis finishes</p>
                      </div>
                      <Switch
                        checked={preferences.push_on_analysis_complete}
                        onCheckedChange={() => handleToggle('push_on_analysis_complete')}
                        data-testid="push-analysis-toggle"
                      />
                    </div>

                    <div className="flex items-center justify-between py-2">
                      <div>
                        <Label className="text-[#0F172A] font-medium">Data Issues</Label>
                        <p className="text-sm text-[#64748B]">Push notification when issues are found</p>
                      </div>
                      <Switch
                        checked={preferences.push_on_data_issues}
                        onCheckedChange={() => handleToggle('push_on_data_issues')}
                        data-testid="push-issues-toggle"
                      />
                    </div>

                    <div className="flex items-center justify-between py-2">
                      <div>
                        <Label className="text-[#0F172A] font-medium">Export Ready</Label>
                        <p className="text-sm text-[#64748B]">Push notification when export is ready</p>
                      </div>
                      <Switch
                        checked={preferences.push_on_export_ready}
                        onCheckedChange={() => handleToggle('push_on_export_ready')}
                        data-testid="push-export-toggle"
                      />
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <Button
              onClick={handleSave}
              disabled={saving}
              className="bg-[#6366F1] hover:bg-[#4F46E5] text-white"
              data-testid="save-settings-btn"
            >
              {saving ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <Save className="w-4 h-4 mr-2" />
              )}
              Save Settings
            </Button>
            
            <Button
              variant="outline"
              onClick={handleTestNotification}
              className="border-slate-300"
              data-testid="test-notification-btn"
            >
              <Bell className="w-4 h-4 mr-2" />
              Send Test Notification
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}

// Helper function to convert VAPID key
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');
  
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export default NotificationSettings;
