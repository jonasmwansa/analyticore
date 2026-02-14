import React, { useEffect, useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

function ProtectedRoute({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(location.state?.user ? true : null);
  const [user, setUser] = useState(location.state?.user || null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (location.state?.user) {
      return;
    }

    const checkAuth = async () => {
      try {
        const response = await axios.get(`${API_URL}/auth/me`, {
          withCredentials: true
        });
        setUser(response.data);
        setIsAuthenticated(true);
      } catch (error) {
        setIsAuthenticated(false);
      }
    };

    checkAuth();
  }, [location.state]);

  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[#6366F1] border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-[#64748B]">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/signin" replace />;
  }

  return <>{React.cloneElement(children, { user })}</>;
}

export default ProtectedRoute;