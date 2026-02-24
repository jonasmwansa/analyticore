import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'sonner';
import { Database, Mail, Lock, User, Eye, EyeOff } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { authAPI } from '../api';

function SignUp() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await authAPI.register(formData);
      toast.success('Registration successful! Please check your email to verify your account.');
      navigate('/signin');
    } catch (error) {
      toast.error(error.response?.data?.detail || 
                  error.response?.data?.email?.[0] || 
                  'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      <div className="flex-1 flex items-center justify-center px-6 py-12 bg-[#F8FAFC]">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <Link 
              to="/" 
              className="flex items-center justify-center gap-2 mb-4 hover:opacity-80 transition"
            >
              <Database className="w-10 h-10 text-[#6366F1]" />
              <span className="text-3xl font-bold text-[#0F172A]">AnalytiCore</span>
            </Link>
            <h1 className="text-3xl font-bold text-[#0F172A] mb-2">Create your account</h1>
            <p className="text-[#64748B]">Start cleaning your data with AI</p>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-8">
            {/* Email/Password Sign Up Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="name" className="text-[#0F172A] font-medium mb-2 block">
                  Full Name
                </Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#94A3B8]" />
                  <Input
                    id="name"
                    type="text"
                    placeholder="John Doe"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    data-testid="signup-name-input"
                    className="pl-10 h-11 bg-white border-slate-200 rounded-lg"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="email" className="text-[#0F172A] font-medium mb-2 block">
                  Email
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#94A3B8]" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                    data-testid="signup-email-input"
                    className="pl-10 h-11 bg-white border-slate-200 rounded-lg"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="password" className="text-[#0F172A] font-medium mb-2 block">
                  Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#94A3B8]" />
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                    data-testid="signup-password-input"
                    className="pl-10 pr-10 h-11 bg-white border-slate-200 rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[#94A3B8] hover:text-[#64748B]"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                data-testid="signup-submit-btn"
                className="w-full bg-[#6366F1] hover:bg-[#4F46E5] text-white rounded-lg h-11 font-semibold shadow-md shadow-indigo-500/20"
              >
                {loading ? 'Creating account...' : 'Create Account'}
              </Button>
            </form>

            <p className="mt-6 text-center text-[#64748B]">
              Already have an account?{' '}
              <Link to="/signin" className="text-[#6366F1] hover:underline font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>

      <div className="hidden lg:flex flex-1 items-center justify-center p-12 hero-gradient">
        <div className="max-w-lg">
          <img
            src="https://images.unsplash.com/photo-1686625689084-7498ab1c017b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxODF8MHwxfHNlYXJjaHwyfHxhYnN0cmFjdCUyMGNvbG9yZnVsJTIwM2QlMjBnZW9tZXRyaWMlMjBzaGFwZXMlMjBkYXRhJTIwZmxvd3xlbnwwfHx8fDE3NzEwNzM3NDh8MA&ixlib=rb-4.1.0&q=85"
            alt="Visualization"
            className="rounded-2xl shadow-2xl"
          />
        </div>
      </div>
    </div>
  );
}

export default SignUp;