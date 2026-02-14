import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Toaster } from './components/ui/sonner';
import LandingPage from './pages/LandingPage';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';
import VerifyEmail from './pages/VerifyEmail';
import Dashboard from './pages/Dashboard';
import ProjectView from './pages/ProjectView';
import AuthCallback from './pages/AuthCallback';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function AppRouter() {
  const location = useLocation();
  
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }
  
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/signin" element={<SignIn />} />
      <Route path="/signup" element={<SignUp />} />
      <Route path="/verify-email" element={<VerifyEmail />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects/:projectId"
        element={
          <ProtectedRoute>
            <ProjectView />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AppRouter />
        <Toaster richColors position="top-right" />
      </BrowserRouter>
    </div>
  );
}

export default App;