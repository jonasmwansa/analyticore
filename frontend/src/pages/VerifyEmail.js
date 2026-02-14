import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'sonner';
import { CheckCircle2, XCircle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { authAPI } from '../api';

function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying');
  const token = searchParams.get('token');

  useEffect(() => {
    const verifyEmail = async () => {
      if (!token) {
        setStatus('error');
        return;
      }

      try {
        await authAPI.verifyEmail(token);
        setStatus('success');
        toast.success('Email verified successfully!');
      } catch (error) {
        setStatus('error');
        toast.error(error.response?.data?.detail || error.response?.data?.token?.[0] || 'Verification failed');
      }
    };

    verifyEmail();
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC] px-6">
      <div className="max-w-md w-full bg-white border border-slate-200 rounded-xl shadow-sm p-8 text-center">
        {status === 'verifying' && (
          <>
            <div className="w-16 h-16 border-4 border-[#6366F1] border-t-transparent rounded-full animate-spin mx-auto mb-6"></div>
            <h2 className="text-2xl font-bold text-[#0F172A] mb-2">Verifying your email</h2>
            <p className="text-[#64748B]">Please wait while we verify your account...</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="w-16 h-16 bg-[#DCFCE7] rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 className="w-8 h-8 text-[#14B8A6]" />
            </div>
            <h2 className="text-2xl font-bold text-[#0F172A] mb-2">Email Verified!</h2>
            <p className="text-[#64748B] mb-6">Your account has been successfully verified. You can now sign in.</p>
            <Button
              onClick={() => navigate('/signin')}
              data-testid="goto-signin-btn"
              className="bg-[#6366F1] hover:bg-[#4F46E5] text-white rounded-lg h-11 px-8 font-semibold shadow-md shadow-indigo-500/20"
            >
              Go to Sign In
            </Button>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="w-16 h-16 bg-[#FEE2E2] rounded-full flex items-center justify-center mx-auto mb-6">
              <XCircle className="w-8 h-8 text-[#F43F5E]" />
            </div>
            <h2 className="text-2xl font-bold text-[#0F172A] mb-2">Verification Failed</h2>
            <p className="text-[#64748B] mb-6">The verification link is invalid or has expired.</p>
            <Button
              onClick={() => navigate('/signup')}
              data-testid="goto-signup-btn"
              className="bg-[#6366F1] hover:bg-[#4F46E5] text-white rounded-lg h-11 px-8 font-semibold shadow-md shadow-indigo-500/20"
            >
              Sign Up Again
            </Button>
          </>
        )}
      </div>
    </div>
  );
}

export default VerifyEmail;