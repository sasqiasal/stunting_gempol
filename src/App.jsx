import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import PengukuranPage from './pages/PengukuranPage';
import BalitaPage from './pages/BalitaPage';
import PosyanduPage from './pages/PosyanduPage';
import EvaluasiModelPage from './pages/EvaluasiModelPage';
import EvaluasiGlobalPage from './pages/EvaluasiGlobalPage';
import AkunPage from './pages/AkunPage';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const user = useAuthStore((state) => state.user);
  
  console.log('ProtectedRoute check:', { isAuthenticated, user });
  
  if (!isAuthenticated) {
    console.log('Not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }
  
  console.log('Authenticated, rendering protected content');
  return children;
};

// Admin Only Route
const AdminRoute = ({ children }) => {
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  if (user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

function App() {
  const initialize = useAuthStore((state) => state.initialize);
  
  useEffect(() => {
    // Initialize auth state from localStorage on mount
    initialize();
  }, [initialize]);
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<LoginPage />} />
        
        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/pengukuran"
          element={
            <ProtectedRoute>
              <PengukuranPage />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/balita"
          element={
            <ProtectedRoute>
              <BalitaPage />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/evaluasi-model"
          element={
            <ProtectedRoute>
              <EvaluasiModelPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/evaluasi-global"
          element={
            <AdminRoute>
              <EvaluasiGlobalPage />
            </AdminRoute>
          }
        />
        
        <Route
          path="/akun"
          element={
            <AdminRoute>
              <AkunPage />
            </AdminRoute>
          }
        />
        
        <Route
          path="/posyandu"
          element={
            <AdminRoute>
              <PosyanduPage />
            </AdminRoute>
          }
        />
        
        {/* Default Route */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        
        {/* 404 Route */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  );
}

export default App;
