import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogIn, Lock, User } from 'lucide-react';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [debugLogs, setDebugLogs] = useState([]);
  const { login } = useAuth();
  const navigate = useNavigate();

  const addDebugLog = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    setDebugLogs(prev => [...prev, `[${timestamp}] ${message}`]);
    console.log(message);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    setDebugLogs([]);

    addDebugLog('Starting login process');
    addDebugLog(`Username: ${username}`);
    addDebugLog(`Password length: ${password.length}`);

    try {
      addDebugLog('Calling login API');
      const { user, must_change_password } = await login(username, password);
      addDebugLog(`Login successful - User: ${JSON.stringify(user)}, must_change_password: ${must_change_password}`);
      
      if (must_change_password) {
        addDebugLog('Navigating to change-password');
        navigate('/change-password');
      } else if (user.role === 'admin') {
        addDebugLog('Navigating to admin dashboard');
        navigate('/admin/dashboard');
      } else {
        addDebugLog('Navigating to driver dashboard');
        navigate('/driver/dashboard');
      }
    } catch (err) {
      addDebugLog(`Login failed: ${err.message}`);
      addDebugLog(`Error response: ${JSON.stringify(err.response)}`);
      addDebugLog(`Error data: ${JSON.stringify(err.response?.data)}`);
      addDebugLog(`Error status: ${err.response?.status}`);
      setError(err.response?.data?.error || 'Login failed. Please try again.');
    } finally {
      addDebugLog('Setting loading to false');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">NMT Travels</h1>
          <p className="text-gray-600 mt-2">Call Taxi Management System</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="pl-10 w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your username"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="pl-10 w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your password"
                required
              />
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Signing in...
              </>
            ) : (
              <>
                <LogIn className="w-5 h-5" />
                Sign In
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <a href="/forgot-password" className="text-blue-600 hover:text-blue-700 text-sm">
            Forgot Password?
          </a>
        </div>

        {/* Debug Panel */}
        {debugLogs.length > 0 && (
          <div className="mt-6 bg-gray-900 text-green-400 p-4 rounded-lg text-xs font-mono max-h-60 overflow-y-auto">
            <div className="font-bold text-white mb-2">DEBUG LOGS:</div>
            {debugLogs.map((log, index) => (
              <div key={index} className="mb-1">{log}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Login;
