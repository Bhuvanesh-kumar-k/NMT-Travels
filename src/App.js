import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import ChangePassword from './pages/ChangePassword';
import ForgotPassword from './pages/ForgotPassword';
import ResetDriverPassword from './pages/ResetDriverPassword';
import AdminDashboard from './pages/AdminDashboard';
import DriverDashboard from './pages/DriverDashboard';
import TripForm from './pages/TripForm';
import AdminTripsPage from './pages/AdminTripsPage';
import AdminDriversPage from './pages/AdminDriversPage';
import AdminSalaryPage from './pages/AdminSalaryPage';
import AdminDriverForm from './pages/AdminDriverForm';

const ProtectedRoute = ({ children, allowedRole }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  // Admins can access all routes, drivers can only access driver routes
  if (allowedRole === 'driver' && user.role !== 'admin' && user.role !== 'driver') {
    return <Navigate to={user.role === 'admin' ? '/admin/dashboard' : '/driver/dashboard'} />;
  }
  
  if (allowedRole === 'admin' && user.role !== 'admin') {
    return <Navigate to='/driver/dashboard' />;
  }
  
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/change-password" element={<ChangePassword />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          
          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute allowedRole="admin">
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/admin/reset-driver-password"
            element={
              <ProtectedRoute allowedRole="admin">
                <ResetDriverPassword />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/admin/trips"
            element={
              <ProtectedRoute allowedRole="admin">
                <AdminTripsPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/admin/drivers"
            element={
              <ProtectedRoute allowedRole="admin">
                <AdminDriversPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/admin/drivers/new"
            element={
              <ProtectedRoute allowedRole="admin">
                <AdminDriverForm />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/admin/drivers/:id"
            element={
              <ProtectedRoute allowedRole="admin">
                <AdminDriverForm />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/admin/salary"
            element={
              <ProtectedRoute allowedRole="admin">
                <AdminSalaryPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/driver/dashboard"
            element={
              <ProtectedRoute allowedRole="driver">
                <DriverDashboard />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/driver/trips/new"
            element={
              <ProtectedRoute allowedRole="driver">
                <TripForm />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/admin/trips/new"
            element={
              <ProtectedRoute allowedRole="admin">
                <TripForm />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/driver/trips/:id"
            element={
              <ProtectedRoute allowedRole="driver">
                <TripForm />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/admin/trips/:id"
            element={
              <ProtectedRoute allowedRole="admin">
                <TripForm />
              </ProtectedRoute>
            }
          />
          
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
