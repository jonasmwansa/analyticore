import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Database,
  Upload,
  Brain,
  Wand2,
  BarChart3,
  Share2,
  ArrowRight,
  Menu,
  X,
  Shield,
  ChevronRight,
  Rocket,
  Cloud,
  PieChart,
  ArrowUp, // Added for go to top
} from "lucide-react";
import { Button } from "../components/ui/button";

function LandingPage() {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [showGoToTop, setShowGoToTop] = useState(false); // New state

  /* ===== Scroll Effects ===== */
  useEffect(() => {
    const handleScroll = () => {
      // For navbar background
      setScrolled(window.scrollY > 20);
      
      // Show go to top button after scrolling past 500px
      setShowGoToTop(window.scrollY > 500);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  /* ===== Go to Top Function ===== */
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  };

  /* ===== Reveal Animation ===== */
  useEffect(() => {
    const elements = document.querySelectorAll(".reveal");
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("active");
          }
        });
      },
      { threshold: 0.15 }
    );
    elements.forEach((el) => observer.observe(el));
  }, []);

  // Close mobile menu when clicking a link
  const handleMobileNavClick = () => {
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-white text-slate-900 overflow-x-hidden">
      {/* ================= FIXED NAVIGATION ================= */}
      <nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
          scrolled
            ? "bg-white/80 backdrop-blur-xl shadow-lg border-b border-slate-200"
            : "bg-white/50 backdrop-blur-md"
        }`}
      >
        {/* ... (navbar content unchanged) ... */}
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">

          <div
            onClick={() => navigate("/")}
            className="flex items-center gap-2 cursor-pointer group"
          >
            <Database className="w-8 h-8 text-indigo-600 transition-all group-hover:scale-110 group-hover:rotate-6" />
            <span className="text-2xl font-bold bg-gradient-to-r from-slate-900 to-indigo-600 bg-clip-text text-transparent">
              AnalytiCore
            </span>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#features" className="hover:text-indigo-600 transition">
              Features
            </a>
            <a href="#how" className="hover:text-indigo-600 transition">
              How It Works
            </a>
          </div>

          <div className="hidden md:flex items-center gap-3">
            <Button variant="ghost" onClick={() => navigate("/signin")}>
              Sign In
            </Button>
            <Button
              onClick={() => navigate("/signup")}
              className="relative overflow-hidden bg-indigo-600 text-white px-6 py-2 shadow-xl hover:-translate-y-1 transition-all group"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-indigo-400 to-purple-500 opacity-0 group-hover:opacity-20 blur-xl transition-all"></span>
              Start Free
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-slate-600 hover:text-indigo-600 transition"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu Dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-16 left-0 right-0 bg-white/95 backdrop-blur-xl border-b border-slate-200 shadow-xl animate-slideDown">
            <div className="max-w-7xl mx-auto px-6 py-6 flex flex-col gap-4">
              
              <a
                href="#features"
                onClick={handleMobileNavClick}
                className="text-lg font-medium text-slate-600 hover:text-indigo-600 transition py-3 px-4 rounded-lg hover:bg-indigo-50"
              >
                Features
              </a>
              
              <a
                href="#how"
                onClick={handleMobileNavClick}
                className="text-lg font-medium text-slate-600 hover:text-indigo-600 transition py-3 px-4 rounded-lg hover:bg-indigo-50"
              >
                How It Works
              </a>

              <div className="h-px bg-slate-200 my-2"></div>

              <Button
                variant="ghost"
                onClick={() => {
                  navigate("/signin");
                  setMobileMenuOpen(false);
                }}
                className="w-full justify-start text-lg py-6 px-4 hover:bg-indigo-50"
              >
                Sign In
              </Button>

              <Button
                onClick={() => {
                  navigate("/signup");
                  setMobileMenuOpen(false);
                }}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-6 text-lg"
              >
                Start Free <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </div>
          </div>
        )}
      </nav>

      {/* ================= GO TO TOP BUTTON ================= */}
      {showGoToTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 z-50 p-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 hover:scale-110 group animate-fadeIn"
          aria-label="Go to top"
        >
          <ArrowUp className="w-6 h-6 group-hover:-translate-y-1 transition-transform" />
        </button>
      )}

      {/* ================= MAIN CONTENT ================= */}
      <main className="pt-16">
        {/* HERO SECTION */}
        <section className="relative py-32 overflow-hidden">
          {/* Background glow */}
          <div className="absolute inset-0 opacity-[0.03] bg-[radial-gradient(#6366f1_1px,transparent_1px)] [background-size:40px_40px]" />
          <div className="absolute -top-20 -left-20 w-[500px] h-[500px] bg-indigo-200 rounded-full blur-3xl opacity-30 animate-blob" />
          <div className="absolute -bottom-20 -right-20 w-[500px] h-[500px] bg-purple-200 rounded-full blur-3xl opacity-30 animate-blob animation-delay-2000" />

          <div className="relative max-w-4xl mx-auto px-6 text-center reveal">

            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/70 backdrop-blur-xl border border-slate-200 rounded-full text-sm mb-10 shadow-sm">
              <Shield className="w-4 h-4 text-indigo-600" />
              Decision Intelligence Infrastructure
            </div>

            <h1 className="text-5xl md:text-6xl font-extrabold leading-tight mb-8">
              From raw data to
              <span className="block bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent animate-gradient">
                confident action
              </span>
            </h1>

            <p className="text-xl text-slate-600 mb-12 leading-relaxed">
              AnalytiCore automatically structures, analyzes, and interprets
              your data — delivering prioritized insights with recommended next
              steps in clear business language.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                onClick={() => navigate("/signup")}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 h-14 shadow-2xl hover:-translate-y-1 transition-all group"
              >
                Start Your First Analysis
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>
          </div>
        </section>

        {/* FEATURES SECTION */}
        <section id="features" className="py-28 bg-slate-50">
          <div className="max-w-7xl mx-auto px-6">

            <div className="text-center max-w-3xl mx-auto mb-20 reveal">
              <h2 className="text-4xl font-bold mb-6">
                Intelligence embedded across the pipeline
              </h2>
              <p className="text-lg text-slate-600">
                Automated. Structured. Outcome-driven.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-10">

              {[
                { icon: <Upload />, title: "Data Structuring", desc: "Automatic schema detection and column classification." },
                { icon: <Wand2 />, title: "Anomaly Detection", desc: "Surface inconsistencies, risk, and outliers instantly." },
                { icon: <Brain />, title: "Driver Analysis", desc: "Reveal what influences your key metrics." },
                { icon: <BarChart3 />, title: "Insight Visualization", desc: "Contextual visuals designed for clarity." },
                { icon: <Share2 />, title: "Business Summaries", desc: "Insights written in decision-ready language." },
                { icon: <Cloud />, title: "Unified Workspace", desc: "Files, databases, APIs — one environment." }
              ].map((item, i) => (
                <div
                  key={i}
                  className="reveal group relative p-[1px] rounded-2xl bg-gradient-to-r from-indigo-200 via-purple-200 to-indigo-200 transition-all duration-500 hover:shadow-[0_0_40px_rgba(99,102,241,0.25)]"
                >
                  <div className="bg-white p-8 rounded-2xl h-full group-hover:-translate-y-2 transition-all duration-300 shadow-md group-hover:shadow-2xl">
                    <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition">
                      {item.icon}
                    </div>
                    <h3 className="text-xl font-bold mb-3">{item.title}</h3>
                    <p className="text-slate-600 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              ))}

            </div>
          </div>
        </section>

        {/* CTA SECTION */}
        <section className="py-28 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-center reveal">
          <div className="max-w-3xl mx-auto px-6">
            <h2 className="text-4xl font-bold mb-6">
              Your data already holds the answers.
            </h2>
            <p className="text-lg mb-10 text-indigo-100">
              Let AnalytiCore reveal them clearly — and help you act confidently.
            </p>

            <Button
              size="lg"
              onClick={() => navigate("/signup")}
              className="bg-white text-indigo-600 hover:bg-indigo-50 shadow-2xl hover:-translate-y-1 transition-all duration-300"
            >
              Get Started Free <Rocket className="ml-2 w-5 h-5" />
            </Button>
          </div>
        </section>

        {/* FOOTER */}
        <footer className="bg-slate-900 text-slate-400 py-14">
          <div className="max-w-6xl mx-auto px-6 text-center">

            <div className="h-px w-full bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-40 mb-10"></div>

            <Database className="mx-auto text-indigo-500 mb-4" />
            <p className="text-white font-semibold mb-6 text-lg">
              AnalytiCore
            </p>

            <div className="flex justify-center gap-8 text-sm mb-8">
              <button
                onClick={() => navigate("/privacy")}
                className="hover:text-white transition"
              >
                Privacy Policy
              </button>
              <button
                onClick={() => navigate("/terms")}
                className="hover:text-white transition"
              >
                Terms of Service
              </button>
            </div>

            <p className="text-xs text-slate-500">
              © {new Date().getFullYear()} AnalytiCore. All rights reserved.
            </p>

          </div>
        </footer>
      </main>

      {/* ================= ANIMATIONS ================= */}
      <style jsx>{`
        @keyframes blob {
          0% { transform: translate(0,0) scale(1); }
          33% { transform: translate(30px,-40px) scale(1.1); }
          66% { transform: translate(-20px,20px) scale(0.9); }
          100% { transform: translate(0,0) scale(1); }
        }
        .animate-blob {
          animation: blob 8s infinite ease-in-out;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .reveal {
          opacity: 0;
          transform: translateY(40px);
          transition: all 0.8s ease;
        }
        .reveal.active {
          opacity: 1;
          transform: translateY(0);
        }
        .animate-gradient {
          background-size: 200% 200%;
          animation: gradientShift 6s ease infinite;
        }
        @keyframes gradientShift {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        
        /* Mobile menu animation */
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slideDown {
          animation: slideDown 0.3s ease-out;
        }

        /* Go to top button animation */
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: scale(0.8);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>

    </div>
  );
}

export default LandingPage;