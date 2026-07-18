import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { tripAPI } from '../services/api';
import { Car, Plus, Clock, CheckCircle, LogOut } from 'lucide-react';

const DriverDashboard = () => {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchTrips();
  }, []);

  const fetchTrips = async () => {
    try {
      const response = await tripAPI.list();
      setTrips(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch trips:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'draft':
        return <Clock className="w-4 h-4" />;
      case 'in_progress':
        return <Clock className="w-4 h-4" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const activeTrip = trips.find(t => t.status === 'in_progress');
  const draftTrips = trips.filter(t => t.status === 'draft');
  const completedTrips = trips.filter(t => t.status === 'completed');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Driver Dashboard</h1>
              <p className="text-sm text-gray-600">Welcome, {user?.first_name} {user?.last_name}</p>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg"
            >
              <LogOut className="w-5 h-5" />
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <button
            onClick={() => navigate('/driver/trips/new')}
            className="bg-blue-600 text-white rounded-xl shadow-sm p-6 hover:bg-blue-700 transition-colors flex items-center gap-4"
          >
            <div className="bg-blue-500 p-3 rounded-full">
              <Plus className="w-6 h-6" />
            </div>
            <div className="text-left">
              <p className="font-semibold">Start New Trip</p>
              <p className="text-sm text-blue-100">Create a new trip entry</p>
            </div>
          </button>

          {activeTrip && (
            <button
              onClick={() => navigate(`/driver/trips/${activeTrip.id}`)}
              className="bg-yellow-500 text-white rounded-xl shadow-sm p-6 hover:bg-yellow-600 transition-colors flex items-center gap-4"
            >
              <div className="bg-yellow-400 p-3 rounded-full">
                <Car className="w-6 h-6" />
              </div>
              <div className="text-left">
                <p className="font-semibold">Continue Active Trip</p>
                <p className="text-sm text-yellow-100">Trip Code: {activeTrip.trip_code}</p>
              </div>
            </button>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Trip</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {activeTrip ? activeTrip.trip_code : 'None'}
                </p>
              </div>
              <div className="bg-yellow-100 p-3 rounded-full">
                <Clock className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Draft Trips</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {draftTrips.length}
                </p>
              </div>
              <div className="bg-gray-100 p-3 rounded-full">
                <Clock className="w-6 h-6 text-gray-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Completed Trips</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {completedTrips.length}
                </p>
              </div>
              <div className="bg-green-100 p-3 rounded-full">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Recent Trips */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Recent Trips</h2>
            <button
              onClick={() => navigate('/driver/trips')}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              View All
            </button>
          </div>

          <div className="space-y-4">
            {trips.slice(0, 5).map((trip) => (
              <div
                key={trip.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                onClick={() => navigate(`/driver/trips/${trip.id}`)}
              >
                <div className="flex items-center gap-4">
                  <div className={`p-2 rounded-full ${getStatusColor(trip.status)}`}>
                    {getStatusIcon(trip.status)}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{trip.trip_code}</p>
                    <p className="text-sm text-gray-600">
                      {trip.pickup_place} → {trip.drop_place}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium text-gray-900">{trip.date}</p>
                  <p className="text-sm text-gray-600 capitalize">{trip.status.replace('_', ' ')}</p>
                </div>
              </div>
            ))}

            {trips.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Car className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No trips yet. Start your first trip!</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default DriverDashboard;
