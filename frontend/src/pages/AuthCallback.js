import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { authAPI } from '../api';

function AuthCallback() {
  const navigate = useNavigate();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const hash = window.location.hash;
    const params = new URLSearchParams(hash.substring(1));
    const sessionId = params.get('session_id');

    if (!sessionId) {
      toast.error('Invalid authentication session');
      navigate('/signin');
      return;
    }

    const processSession = async () => {
      try {
        const response = await authAPI.googleAuthCallback(sessionId);
        localStorage.setItem('auth_token', response.data.token);
        toast.success('Successfully signed in!');
        navigate('/dashboard', { state: { user: response.data.user }, replace: true });
      } catch (error) {
        console.error('Session error:', error);
        toast.error('Authentication failed');
        navigate('/signin');
      }
    };

    processSession();
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC]">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-[#6366F1] border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="mt-4 text-[#64748B]">Completing sign in...</p>
      </div>
    </div>
  );
}

export default AuthCallback;