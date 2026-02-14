import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { adminAPI } from '../../api';

export function AlertSettingsSection() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [formData, setFormData] = useState({
    error_rate_threshold: 5,
    db_response_threshold_ms: 500,
    max_errors_24h: 10,
    alert_emails_enabled: true,
    daily_summary_enabled: true,
    additional_recipients: '',
    health_check_interval_minutes: 15
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await adminAPI.getAlertSettings();
      setSettings(response.data);
      setFormData(response.data);
    } catch (error) {
      toast.error('Failed to load alert settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await adminAPI.updateAlertSettings(formData);
      toast.success('Alert settings saved');
      loadSettings();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleTestEmail = async () => {
    setTesting(true);
    try {
      const response = await adminAPI.testAlertEmail();
      toast.success(`Test email sent to ${response.data.recipients?.length || 0} recipients`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send test email');
    } finally {
      setTesting(false);
    }
  };

  if (loading) return <p className="text-slate-400">Loading settings...</p>;

  return (
    <div className="space-y-6" data-testid="settings-section">
      <h2 className="text-xl font-bold text-white">Alert Settings</h2>
      
      {/* Thresholds */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-6">Alert Thresholds</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Error Rate Threshold (%)</label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.5"
              value={formData.error_rate_threshold}
              onChange={(e) => setFormData({ ...formData, error_rate_threshold: parseFloat(e.target.value) })}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
            />
            <p className="text-xs text-slate-500 mt-1">Alert when error rate exceeds this %</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">DB Response Threshold (ms)</label>
            <input
              type="number"
              min="10"
              max="10000"
              value={formData.db_response_threshold_ms}
              onChange={(e) => setFormData({ ...formData, db_response_threshold_ms: parseInt(e.target.value) })}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
            />
            <p className="text-xs text-slate-500 mt-1">Alert when DB response exceeds this</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Max Errors (24h)</label>
            <input
              type="number"
              min="1"
              max="1000"
              value={formData.max_errors_24h}
              onChange={(e) => setFormData({ ...formData, max_errors_24h: parseInt(e.target.value) })}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
            />
            <p className="text-xs text-slate-500 mt-1">Alert when errors in 24h exceed this</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Health Check Interval (minutes)</label>
            <input
              type="number"
              min="5"
              max="60"
              value={formData.health_check_interval_minutes}
              onChange={(e) => setFormData({ ...formData, health_check_interval_minutes: parseInt(e.target.value) })}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
            />
            <p className="text-xs text-slate-500 mt-1">How often to check system health</p>
          </div>
        </div>
      </Card>

      {/* Email Settings */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-6">Email Notifications</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-white">Alert Emails</p>
              <p className="text-xs text-slate-400">Send email when thresholds are exceeded</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={formData.alert_emails_enabled}
                onChange={(e) => setFormData({ ...formData, alert_emails_enabled: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-indigo-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600" />
            </label>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-white">Daily Summary</p>
              <p className="text-xs text-slate-400">Send daily health summary at 8 AM</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={formData.daily_summary_enabled}
                onChange={(e) => setFormData({ ...formData, daily_summary_enabled: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-indigo-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600" />
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Additional Recipients</label>
            <input
              type="text"
              value={formData.additional_recipients}
              onChange={(e) => setFormData({ ...formData, additional_recipients: e.target.value })}
              placeholder="email1@example.com, email2@example.com"
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500 placeholder:text-slate-500"
            />
            <p className="text-xs text-slate-500 mt-1">Comma-separated email addresses (in addition to admin users)</p>
          </div>
        </div>
      </Card>

      {/* Actions */}
      <div className="flex gap-4">
        <Button
          onClick={handleSave}
          disabled={saving}
          className="bg-indigo-600 hover:bg-indigo-700"
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
        <Button
          onClick={handleTestEmail}
          disabled={testing}
          variant="outline"
          className="border-slate-600 text-slate-300 hover:bg-slate-700"
        >
          {testing ? 'Sending...' : 'Send Test Email'}
        </Button>
      </div>

      {/* Last Updated */}
      {settings?.updated_at && (
        <p className="text-xs text-slate-500">
          Last updated: {new Date(settings.updated_at).toLocaleString()}
          {settings.updated_by && ` by ${settings.updated_by}`}
        </p>
      )}
    </div>
  );
}

export default AlertSettingsSection;
