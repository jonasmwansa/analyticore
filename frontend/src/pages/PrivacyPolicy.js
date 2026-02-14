import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, ArrowLeft, Shield, Lock, Eye, Server, UserCheck, Bell, Trash2 } from 'lucide-react';
import { Button } from '../components/ui/button';

function PrivacyPolicy() {
  const navigate = useNavigate();
  const lastUpdated = "February 14, 2026";

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation */}
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
            <Database className="w-8 h-8 text-indigo-600" />
            <span className="text-2xl font-bold text-slate-900">AnalytiCore</span>
          </div>
          <Button
            variant="ghost"
            onClick={() => navigate(-1)}
            className="text-slate-600 hover:text-indigo-600"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> Back
          </Button>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 py-12">
        <div className="bg-white rounded-2xl shadow-lg p-8 md:p-12">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="w-16 h-16 bg-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Shield className="w-8 h-8 text-indigo-600" />
            </div>
            <h1 className="text-4xl font-bold text-slate-900 mb-4">Privacy Policy</h1>
            <p className="text-slate-500">Last updated: {lastUpdated}</p>
          </div>

          {/* Introduction */}
          <section className="mb-10">
            <p className="text-slate-600 leading-relaxed text-lg">
              At AnalytiCore, we take your privacy seriously. This Privacy Policy explains how we collect, 
              use, disclose, and safeguard your information when you use our data analytics platform. 
              We are committed to protecting your data with government-grade security standards.
            </p>
          </section>

          {/* Section 1 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Eye className="w-5 h-5 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">1. Information We Collect</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <h3 className="font-semibold text-slate-800">Personal Information</h3>
              <ul className="list-disc ml-6 space-y-2">
                <li>Email address (for account creation and communication)</li>
                <li>Name (for personalization)</li>
                <li>Password (stored securely using industry-standard hashing)</li>
                <li>Profile picture (optional, if provided)</li>
              </ul>
              
              <h3 className="font-semibold text-slate-800 mt-6">Data You Upload</h3>
              <ul className="list-disc ml-6 space-y-2">
                <li>CSV, Excel, and other data files you upload for analysis</li>
                <li>Database connection credentials (encrypted at rest)</li>
                <li>Google Sheets access tokens (stored securely)</li>
              </ul>
              
              <h3 className="font-semibold text-slate-800 mt-6">Automatically Collected Information</h3>
              <ul className="list-disc ml-6 space-y-2">
                <li>IP address (for security and fraud prevention)</li>
                <li>Browser type and version</li>
                <li>Device information</li>
                <li>Usage patterns and feature interactions</li>
                <li>Login timestamps and session data</li>
              </ul>
            </div>
          </section>

          {/* Section 2 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <Server className="w-5 h-5 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">2. How We Use Your Data</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <ul className="list-disc ml-6 space-y-2">
                <li><strong>To provide our services:</strong> Process and analyze your uploaded data, generate visualizations, and run machine learning models</li>
                <li><strong>To improve our platform:</strong> Analyze usage patterns to enhance features and user experience</li>
                <li><strong>To communicate with you:</strong> Send service updates, security alerts, and (if opted-in) marketing communications</li>
                <li><strong>To ensure security:</strong> Monitor for suspicious activity, prevent fraud, and protect against unauthorized access</li>
                <li><strong>To comply with legal obligations:</strong> Meet regulatory requirements and respond to legal requests</li>
              </ul>
              
              <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 mt-6">
                <p className="text-emerald-800 font-medium">
                  We do NOT sell your personal information or uploaded data to third parties.
                </p>
              </div>
            </div>
          </section>

          {/* Section 3 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <Lock className="w-5 h-5 text-purple-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">3. Data Security</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <p>We implement government-grade security measures to protect your data:</p>
              <ul className="list-disc ml-6 space-y-2">
                <li><strong>Encryption at Rest:</strong> All stored data is encrypted using AES-256 encryption</li>
                <li><strong>Encryption in Transit:</strong> All data transfers use TLS 1.3</li>
                <li><strong>Two-Factor Authentication:</strong> Available for all accounts (email OTP)</li>
                <li><strong>Password Policy:</strong> Enforced strong passwords (12+ characters, mixed case, numbers, special characters)</li>
                <li><strong>Password Expiry:</strong> 90-day password rotation policy</li>
                <li><strong>Account Lockout:</strong> Automatic lockout after 5 failed login attempts</li>
                <li><strong>Audit Logging:</strong> Complete audit trail of all security events</li>
                <li><strong>Regular Security Assessments:</strong> Periodic penetration testing and vulnerability scans</li>
              </ul>
            </div>
          </section>

          {/* Section 4 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                <UserCheck className="w-5 h-5 text-amber-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">4. Your Rights</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <p>You have the following rights regarding your personal data:</p>
              <ul className="list-disc ml-6 space-y-2">
                <li><strong>Access:</strong> Request a copy of all personal data we hold about you</li>
                <li><strong>Rectification:</strong> Request correction of inaccurate personal data</li>
                <li><strong>Erasure:</strong> Request deletion of your personal data ("right to be forgotten")</li>
                <li><strong>Portability:</strong> Request your data in a machine-readable format</li>
                <li><strong>Objection:</strong> Object to processing of your personal data</li>
                <li><strong>Withdraw Consent:</strong> Withdraw consent at any time for consent-based processing</li>
              </ul>
              <p className="mt-4">To exercise these rights, contact us at <a href="mailto:privacy@analyticore.com" className="text-indigo-600 hover:underline">privacy@analyticore.com</a></p>
            </div>
          </section>

          {/* Section 5 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <Trash2 className="w-5 h-5 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">5. Data Retention</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <ul className="list-disc ml-6 space-y-2">
                <li><strong>Account Data:</strong> Retained while your account is active, deleted within 30 days of account closure</li>
                <li><strong>Uploaded Files:</strong> Retained until you delete them or close your account</li>
                <li><strong>Analysis Results:</strong> Retained with associated project data</li>
                <li><strong>Security Logs:</strong> Retained for 2 years for compliance and security purposes</li>
                <li><strong>Backup Data:</strong> Deleted from backups within 90 days of primary deletion</li>
              </ul>
            </div>
          </section>

          {/* Section 6 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                <Bell className="w-5 h-5 text-indigo-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">6. Updates to This Policy</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <p>
                We may update this Privacy Policy from time to time. We will notify you of any material 
                changes by email and/or a prominent notice on our platform. We encourage you to review 
                this Privacy Policy periodically.
              </p>
            </div>
          </section>

          {/* Contact */}
          <section className="bg-slate-50 rounded-xl p-6 mt-12">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Contact Us</h2>
            <p className="text-slate-600">
              If you have questions about this Privacy Policy or our data practices, please contact us:
            </p>
            <ul className="mt-4 text-slate-600 space-y-2">
              <li>Email: <a href="mailto:privacy@analyticore.com" className="text-indigo-600 hover:underline">privacy@analyticore.com</a></li>
              <li>Data Protection Officer: <a href="mailto:dpo@analyticore.com" className="text-indigo-600 hover:underline">dpo@analyticore.com</a></li>
            </ul>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-8 mt-12">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-slate-500">&copy; 2026 AnalytiCore. All rights reserved.</p>
          <div className="flex gap-6">
            <button onClick={() => navigate('/privacy')} className="text-slate-500 hover:text-indigo-600">Privacy Policy</button>
            <button onClick={() => navigate('/terms')} className="text-slate-500 hover:text-indigo-600">Terms of Service</button>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default PrivacyPolicy;
