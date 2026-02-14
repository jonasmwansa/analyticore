import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, ArrowLeft, FileText, CheckCircle, XCircle, AlertTriangle, Scale } from 'lucide-react';
import { Button } from '../components/ui/button';

function TermsOfService() {
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
              <FileText className="w-8 h-8 text-indigo-600" />
            </div>
            <h1 className="text-4xl font-bold text-slate-900 mb-4">Terms of Service</h1>
            <p className="text-slate-500">Last updated: {lastUpdated}</p>
          </div>

          {/* Introduction */}
          <section className="mb-10">
            <p className="text-slate-600 leading-relaxed text-lg">
              Welcome to AnalytiCore. These Terms of Service ("Terms") govern your use of our data analytics 
              platform and services. By accessing or using AnalytiCore, you agree to be bound by these Terms.
            </p>
          </section>

          {/* Section 1 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-emerald-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">1. Acceptance of Terms</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <p>By creating an account or using our services, you acknowledge that you have read, understood, and agree to be bound by:</p>
              <ul className="list-disc ml-6 space-y-2">
                <li>These Terms of Service</li>
                <li>Our Privacy Policy</li>
                <li>Any additional guidelines or rules applicable to specific services</li>
              </ul>
              <p>If you do not agree to these Terms, please do not use our services.</p>
            </div>
          </section>

          {/* Section 2 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Scale className="w-5 h-5 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">2. Description of Services</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <p>AnalytiCore provides a comprehensive data analytics platform that includes:</p>
              <ul className="list-disc ml-6 space-y-2">
                <li><strong>Data Ingestion:</strong> Upload and import data from files (CSV, Excel), Google Sheets, and databases</li>
                <li><strong>Data Profiling:</strong> Automatic analysis of data quality and characteristics</li>
                <li><strong>Data Cleaning:</strong> Rule-based and AI-powered data transformation tools</li>
                <li><strong>Data Analysis:</strong> Statistical analysis, correlation, and distribution analysis</li>
                <li><strong>Machine Learning:</strong> Automated ML model training, clustering, and predictions</li>
                <li><strong>Visualization:</strong> Interactive charts and dashboards</li>
                <li><strong>Scheduled Pipelines:</strong> Automated recurring analysis jobs</li>
                <li><strong>Data Export:</strong> Export results in various formats</li>
              </ul>
            </div>
          </section>

          {/* Section 3 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-purple-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">3. User Responsibilities</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <p>As a user of AnalytiCore, you agree to:</p>
              <ul className="list-disc ml-6 space-y-2">
                <li>Provide accurate and complete information when creating your account</li>
                <li>Maintain the security of your account credentials</li>
                <li>Enable two-factor authentication for enhanced security (recommended for sensitive data)</li>
                <li>Notify us immediately of any unauthorized access to your account</li>
                <li>Use the services only for lawful purposes</li>
                <li>Not upload data that you do not have the right to process</li>
                <li>Comply with all applicable laws and regulations regarding data processing</li>
                <li>Not attempt to gain unauthorized access to our systems</li>
              </ul>
            </div>
          </section>

          {/* Section 4 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <XCircle className="w-5 h-5 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">4. Prohibited Uses</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <p>You may not use AnalytiCore to:</p>
              <ul className="list-disc ml-6 space-y-2">
                <li>Process data containing personally identifiable information (PII) without proper consent</li>
                <li>Store or transmit any malicious code or malware</li>
                <li>Engage in any activity that interferes with or disrupts our services</li>
                <li>Attempt to reverse engineer, decompile, or disassemble our software</li>
                <li>Use automated means to access or scrape our services without permission</li>
                <li>Violate any applicable laws or regulations</li>
                <li>Infringe on the intellectual property rights of others</li>
                <li>Process data related to illegal activities</li>
              </ul>
            </div>
          </section>

          {/* Section 5 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">5. Data Ownership and Rights</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <h3 className="font-semibold text-slate-800">Your Data</h3>
              <ul className="list-disc ml-6 space-y-2">
                <li>You retain all ownership rights to the data you upload</li>
                <li>You grant us a limited license to process your data solely to provide our services</li>
                <li>We will not access your data except as necessary to provide services or as required by law</li>
              </ul>
              
              <h3 className="font-semibold text-slate-800 mt-6">Our Services</h3>
              <ul className="list-disc ml-6 space-y-2">
                <li>AnalytiCore retains all rights to our platform, software, and algorithms</li>
                <li>Analysis results and visualizations generated from your data belong to you</li>
                <li>We may use anonymized, aggregated data to improve our services</li>
              </ul>
            </div>
          </section>

          {/* Section 6 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                <Scale className="w-5 h-5 text-indigo-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">6. Limitation of Liability</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <p>
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, ANALYTICORE SHALL NOT BE LIABLE FOR ANY INDIRECT, 
                INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS 
                OF PROFITS, DATA, USE, OR OTHER INTANGIBLE LOSSES.
              </p>
              <p>
                Our total liability for any claims arising out of or relating to these Terms or our services 
                shall not exceed the amount you paid us in the twelve (12) months preceding the claim.
              </p>
            </div>
          </section>

          {/* Section 7 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-slate-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">7. Termination</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <p>
                We reserve the right to suspend or terminate your account at any time for violation of these 
                Terms or for any other reason at our discretion. Upon termination:
              </p>
              <ul className="list-disc ml-6 space-y-2">
                <li>Your right to use our services will cease immediately</li>
                <li>You may request export of your data within 30 days</li>
                <li>We will delete your data in accordance with our data retention policy</li>
              </ul>
            </div>
          </section>

          {/* Section 8 */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">8. Changes to Terms</h2>
            </div>
            
            <div className="space-y-4 text-slate-600 ml-13">
              <p>
                We may modify these Terms at any time. We will provide notice of material changes via email 
                or through our platform. Your continued use of our services after such changes constitutes 
                acceptance of the modified Terms.
              </p>
            </div>
          </section>

          {/* Contact */}
          <section className="bg-slate-50 rounded-xl p-6 mt-12">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Contact Us</h2>
            <p className="text-slate-600">
              If you have questions about these Terms of Service, please contact us:
            </p>
            <ul className="mt-4 text-slate-600 space-y-2">
              <li>Email: <a href="mailto:legal@analyticore.com" className="text-indigo-600 hover:underline">legal@analyticore.com</a></li>
              <li>Support: <a href="mailto:support@analyticore.com" className="text-indigo-600 hover:underline">support@analyticore.com</a></li>
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

export default TermsOfService;
