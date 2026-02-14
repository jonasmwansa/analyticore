import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Database, Shield, Lock, Smartphone, Key, History, AlertTriangle,
  CheckCircle, XCircle, Eye, EyeOff, ArrowLeft, Bell, Mail
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card } from '../components/ui/card';
import api from '../api';

function SecuritySettings({ user }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [securitySettings, setSecuritySettings] = useState(null);
  const [auditLog, setAuditLog] = useState([]);
  
  // Password change state
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [passwordValidation, setPasswordValidation] = useState(null);
  const [passwordLoading, setPasswordLoading] = useState(false);
  
  // 2FA state
  const [show2FASetup, setShow2FASetup] = useState(false);
  const [otpId, setOtpId] = useState(null);
  const [otpCode, setOtpCode] = useState('');
  const [twoFALoading, setTwoFALoading] = useState(false);
  const [disablePassword, setDisablePassword] = useState('');

  useEffect(() => {
    loadSecurityData();
  }, []);

  useEffect(() => {
    if (newPassword) {
      validatePassword(newPassword);
    } else {
      setPasswordValidation(null);
    }
  }, [newPassword]);

  const loadSecurityData = async () => {
    try {
      const [settingsRes, logRes] = await Promise.all([
        api.get('/auth/security/settings'),
        api.get('/auth/security/audit-log?limit=10')
      ]);
      setSecuritySettings(settingsRes.data);
      setAuditLog(logRes.data.logs || []);
    } catch (error) {
      toast.error('Failed to load security settings');
    } finally {
      setLoading(false);
    }
  };

  const validatePassword = async (pwd) => {
    try {
      const response = await api.post('/auth/password/validate', { password: pwd });
      setPasswordValidation(response.data);
    } catch (error) {
      console.error('Password validation error:', error);
    }
  };

  const handleUpdatePassword = async (e) => {
    e.preventDefault();
    
    if (!passwordValidation?.valid) {
      toast.error('Password does not meet requirements');
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setPasswordLoading(true);
    try {
      await api.post('/auth/password/update', {
        current_password: currentPassword,
        new_password: newPassword
      });
      toast.success('Password updated successfully');
      setShowPasswordForm(false);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      loadSecurityData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update password');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleEnable2FA = async () => {
    setTwoFALoading(true);
    try {
      const response = await api.post('/auth/2fa/enable', { method: 'email' });
      setOtpId(response.data.otp_id);
      setShow2FASetup(true);
      toast.success('Verification code sent to your email');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to initiate 2FA setup');
    } finally {
      setTwoFALoading(false);
    }
  };

  const handleVerify2FA = async () => {
    if (!otpCode || otpCode.length !== 6) {
      toast.error('Please enter a 6-digit code');
      return;
    }

    setTwoFALoading(true);
    try {
      await api.post('/auth/2fa/verify-enable', { otp_id: otpId, code: otpCode });
      toast.success('Two-factor authentication enabled!');
      setShow2FASetup(false);
      setOtpCode('');
      loadSecurityData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Invalid verification code');
    } finally {
      setTwoFALoading(false);
    }
  };

  const handleDisable2FA = async () => {
    if (!disablePassword) {
      toast.error('Please enter your password');
      return;
    }

    setTwoFALoading(true);
    try {
      await api.post('/auth/2fa/disable', { password: disablePassword });
      toast.success('Two-factor authentication disabled');
      setDisablePassword('');
      loadSecurityData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to disable 2FA');
    } finally {
      setTwoFALoading(false);
    }
  };

  const formatEventType = (type) => {
    const map = {
      'login_success': 'Successful Login',
      'login_failed': 'Failed Login',
      'logout': 'Logout',
      'password_change': 'Password Changed',
      'password_reset_request': 'Password Reset Requested',
      'password_reset_complete': 'Password Reset Completed',
      '2fa_enabled': '2FA Enabled',
      '2fa_disabled': '2FA Disabled',
      '2fa_success': '2FA Verification Success',
      '2fa_failed': '2FA Verification Failed',
      'account_locked': 'Account Locked',
      'settings_changed': 'Settings Changed'
    };
    return map[type] || type;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-slate-400 hover:text-white"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
              <Shield className="w-6 h-6 text-indigo-400" />
              <h1 className="text-xl font-bold text-white">Security Settings</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {/* Two-Factor Authentication */}
        <Card className="bg-slate-800 border-slate-700 p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-indigo-500/20 rounded-xl flex items-center justify-center">
                <Smartphone className="w-6 h-6 text-indigo-400" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Two-Factor Authentication</h2>
                <p className="text-slate-400 text-sm mt-1">
                  Add an extra layer of security with email OTP verification
                </p>
                <div className="mt-3">
                  {securitySettings?.two_factor_enabled ? (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-500/20 text-emerald-400 text-sm rounded-full">
                      <CheckCircle className="w-4 h-4" /> Enabled (Email)
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-amber-500/20 text-amber-400 text-sm rounded-full">
                      <AlertTriangle className="w-4 h-4" /> Not Enabled
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            {!securitySettings?.two_factor_enabled ? (
              <Button
                onClick={handleEnable2FA}
                disabled={twoFALoading}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                {twoFALoading ? 'Sending...' : 'Enable 2FA'}
              </Button>
            ) : (
              <div className="flex gap-2">
                <Input
                  type="password"
                  value={disablePassword}
                  onChange={(e) => setDisablePassword(e.target.value)}
                  placeholder="Enter password"
                  className="w-40 bg-slate-700 border-slate-600 text-white text-sm"
                />
                <Button
                  onClick={handleDisable2FA}
                  disabled={twoFALoading}
                  variant="outline"
                  className="border-red-500/50 text-red-400 hover:bg-red-500/20"
                >
                  Disable
                </Button>
              </div>
            )}
          </div>

          {/* 2FA Setup Modal */}
          {show2FASetup && (
            <div className="mt-6 bg-slate-700/50 rounded-lg p-6 border border-slate-600">
              <h3 className="text-white font-medium mb-4">Enter Verification Code</h3>
              <p className="text-slate-400 text-sm mb-4">
                We've sent a 6-digit code to your email. Enter it below to complete 2FA setup.
              </p>
              <div className="flex gap-3">
                <Input
                  type="text"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="000000"
                  className="w-32 bg-slate-700 border-slate-600 text-white text-center text-xl tracking-widest"
                  maxLength={6}
                />
                <Button
                  onClick={handleVerify2FA}
                  disabled={twoFALoading || otpCode.length !== 6}
                  className="bg-emerald-600 hover:bg-emerald-700"
                >
                  {twoFALoading ? 'Verifying...' : 'Verify & Enable'}
                </Button>
                <Button
                  onClick={() => setShow2FASetup(false)}
                  variant="ghost"
                  className="text-slate-400"
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </Card>

        {/* Password */}
        <Card className="bg-slate-800 border-slate-700 p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center">
                <Lock className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Password</h2>
                <p className="text-slate-400 text-sm mt-1">
                  Your password must be at least 12 characters with mixed case, numbers, and symbols
                </p>
                {securitySettings?.password_expires_at && (
                  <p className="text-slate-500 text-xs mt-2">
                    Expires: {new Date(securitySettings.password_expires_at).toLocaleDateString()}
                    {securitySettings.password_expired && (
                      <span className="text-red-400 ml-2">Password expired!</span>
                    )}
                  </p>
                )}
              </div>
            </div>
            <Button
              onClick={() => setShowPasswordForm(!showPasswordForm)}
              variant="outline"
              className="border-slate-600 text-slate-300 hover:bg-slate-700"
            >
              {showPasswordForm ? 'Cancel' : 'Change Password'}
            </Button>
          </div>

          {showPasswordForm && (
            <form onSubmit={handleUpdatePassword} className="mt-6 space-y-4 border-t border-slate-700 pt-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Current Password</label>
                <Input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">New Password</label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="bg-slate-700 border-slate-600 text-white pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              {passwordValidation && (
                <div className="bg-slate-700/50 rounded-lg p-4 space-y-2">
                  {Object.entries(passwordValidation.requirements || {}).map(([key, req]) => (
                    <div key={key} className="flex items-center gap-2 text-sm">
                      {req.met ? (
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-400" />
                      )}
                      <span className={req.met ? 'text-emerald-400' : 'text-slate-400'}>{req.message}</span>
                    </div>
                  ))}
                  <div className="mt-3">
                    <div className="h-2 bg-slate-600 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          passwordValidation.strength === 100 ? 'bg-emerald-500' :
                          passwordValidation.strength >= 60 ? 'bg-amber-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${passwordValidation.strength}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Confirm New Password</label>
                <Input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white"
                  required
                />
                {confirmPassword && newPassword !== confirmPassword && (
                  <p className="text-red-400 text-sm mt-1">Passwords do not match</p>
                )}
              </div>

              <Button
                type="submit"
                disabled={passwordLoading || !passwordValidation?.valid || newPassword !== confirmPassword}
                className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
              >
                {passwordLoading ? 'Updating...' : 'Update Password'}
              </Button>
            </form>
          )}
        </Card>

        {/* Security Audit Log */}
        <Card className="bg-slate-800 border-slate-700 p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 bg-amber-500/20 rounded-xl flex items-center justify-center">
              <History className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Security Activity</h2>
              <p className="text-slate-400 text-sm">Recent security events on your account</p>
            </div>
          </div>

          <div className="space-y-3">
            {auditLog.length === 0 ? (
              <p className="text-slate-500 text-center py-8">No security events recorded</p>
            ) : (
              auditLog.map((log, idx) => (
                <div key={idx} className="flex items-center justify-between py-3 border-b border-slate-700 last:border-0">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      log.event_type.includes('success') || log.event_type === 'login_success' ? 'bg-emerald-500/20' :
                      log.event_type.includes('failed') ? 'bg-red-500/20' : 'bg-slate-700'
                    }`}>
                      {log.event_type.includes('success') || log.event_type === 'login_success' ? (
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                      ) : log.event_type.includes('failed') ? (
                        <XCircle className="w-4 h-4 text-red-400" />
                      ) : (
                        <Shield className="w-4 h-4 text-slate-400" />
                      )}
                    </div>
                    <div>
                      <p className="text-sm text-white">{formatEventType(log.event_type)}</p>
                      {log.ip_address && (
                        <p className="text-xs text-slate-500">IP: {log.ip_address}</p>
                      )}
                    </div>
                  </div>
                  <span className="text-xs text-slate-500">
                    {new Date(log.created_at).toLocaleString()}
                  </span>
                </div>
              ))
            )}
          </div>
        </Card>
      </main>
    </div>
  );
}

export default SecuritySettings;
