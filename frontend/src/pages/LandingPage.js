import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, Wand2, Zap, FileSpreadsheet, CheckCircle2, ArrowRight } from 'lucide-react';
import { Button } from '../components/ui/button';

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Database className="w-8 h-8 text-[#6366F1]" />
            <span className="text-2xl font-bold text-[#0F172A]" style={{ letterSpacing: '-0.02em' }}>AnalytiCore</span>
          </div>
          <div className="flex gap-3">
            <Button
              variant="ghost"
              onClick={() => navigate('/signin')}
              data-testid="nav-signin-btn"
              className="text-slate-700 hover:text-[#6366F1]"
            >
              Sign In
            </Button>
            <Button
              onClick={() => navigate('/signup')}
              data-testid="nav-signup-btn"
              className="bg-[#6366F1] hover:bg-[#4F46E5] text-white shadow-md shadow-indigo-500/20 rounded-lg px-6"
            >
              Get Started
            </Button>
          </div>
        </div>
      </nav>

      <section className="hero-gradient py-20 md:py-32">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-[#0F172A] mb-6" style={{ letterSpacing: '-0.02em', lineHeight: '1.1' }}>
                Data Cleaning
                <span className="text-[#6366F1]"> Made Simple</span>
              </h1>
              <p className="text-lg md:text-xl text-[#64748B] mb-8 leading-relaxed">
                AI-powered data pipeline that transforms messy data into analysis-ready datasets.
                No more struggles with Power BI complexity.
              </p>
              <div className="flex gap-4">
                <Button
                  size="lg"
                  onClick={() => navigate('/signup')}
                  data-testid="hero-cta-btn"
                  className="bg-[#6366F1] hover:bg-[#4F46E5] text-white shadow-lg shadow-indigo-500/30 rounded-lg px-8 h-12 text-base font-semibold"
                >
                  Start Free <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </div>
            </div>
            <div className="relative">
              <img
                src="https://images.unsplash.com/photo-1645280403333-3775178fc8c6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxODF8MHwxfHNlYXJjaHw0fHxhYnN0cmFjdCUyMGNvbG9yZnVsJTIwM2QlMjBnZW9tZXRyaWMlMjBzaGFwZXMlMjBkYXRhJTIwZmxvd3xlbnwwfHx8fDE3NzEwNzM3NDh8MA&ixlib=rb-4.1.0&q=85"
                alt="Data Flow"
                className="rounded-2xl shadow-2xl"
              />
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-[#0F172A] mb-4" style={{ letterSpacing: '-0.02em' }}>
              Powerful Features
            </h2>
            <p className="text-lg text-[#64748B]">Everything you need for perfect data preparation</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="feature-card bg-white border border-slate-200 rounded-xl p-8 shadow-sm">
              <div className="w-14 h-14 bg-[#EEF2FF] rounded-lg flex items-center justify-center mb-6">
                <FileSpreadsheet className="w-7 h-7 text-[#6366F1]" />
              </div>
              <h3 className="text-xl font-bold text-[#0F172A] mb-3">Multi-Source Ingestion</h3>
              <p className="text-[#64748B] leading-relaxed">
                Upload CSV, Excel, JSON files or connect directly to databases and APIs. One platform for all your data sources.
              </p>
            </div>

            <div className="feature-card bg-white border border-slate-200 rounded-xl p-8 shadow-sm">
              <div className="w-14 h-14 bg-[#F0FDFA] rounded-lg flex items-center justify-center mb-6">
                <Wand2 className="w-7 h-7 text-[#14B8A6]" />
              </div>
              <h3 className="text-xl font-bold text-[#0F172A] mb-3">AI Recommendations</h3>
              <p className="text-[#64748B] leading-relaxed">
                GPT-powered analysis suggests the best cleaning strategies for missing values, outliers, and data types.
              </p>
            </div>

            <div className="feature-card bg-white border border-slate-200 rounded-xl p-8 shadow-sm">
              <div className="w-14 h-14 bg-[#FEF3F2] rounded-lg flex items-center justify-center mb-6">
                <Zap className="w-7 h-7 text-[#F59E0B]" />
              </div>
              <h3 className="text-xl font-bold text-[#0F172A] mb-3">Custom Transformations</h3>
              <p className="text-[#64748B] leading-relaxed">
                Override AI suggestions with your own rules. Full control over how your data is cleaned and transformed.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-[#F8FAFC]">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-[#0F172A] mb-6" style={{ letterSpacing: '-0.02em' }}>
            Ready to transform your data?
          </h2>
          <p className="text-xl text-[#64748B] mb-8">
            Join data analysts who are saving hours on data preparation
          </p>
          <Button
            size="lg"
            onClick={() => navigate('/signup')}
            data-testid="footer-cta-btn"
            className="bg-[#6366F1] hover:bg-[#4F46E5] text-white shadow-lg shadow-indigo-500/30 rounded-lg px-10 h-14 text-lg font-semibold"
          >
            Get Started Free
          </Button>
        </div>
      </section>

      <footer className="bg-white border-t border-slate-200 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center text-[#94A3B8]">
          <p>&copy; 2026 AnalytiCore. Making data preparation effortless.</p>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;