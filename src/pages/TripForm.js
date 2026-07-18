import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { tripAPI, driverAPI, billAPI } from '../services/api';
import { Save, Send, FileText, ArrowLeft } from 'lucide-react';

const TripForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);
  const [loading, setLoading] = useState(false);
  const [drivers, setDrivers] = useState([]);
  const [tripType, setTripType] = useState('taxi');
  const [formData, setFormData] = useState({
    trip_type: 'taxi',
    date: new Date().toISOString().split('T')[0],
    day: new Date().toLocaleDateString('en-US', { weekday: 'long' }),
    driver_id: '',
    start_place: '',
    pickup_place: '',
    drop_place: '',
    end_place: '',
    start_km: '',
    end_km: '',
    time_in: '',
    time_out: '',
    cng: 0,
    petrol: 0,
    red_taxi_income: 0,
    commission: 0,
    advance: 0,
    advance_received_today: 0,
    waiting_charge: 0,
    inter_state_permit: 0,
    luggage_charges: 0,
    pet_charges: 0,
    hill_charges: 0,
    toll_charges: 0,
    base_fare: 0,
    driver_allowance: 0,
    previous_salary: 0,
    dr_adv: 0,
    salary_per_hour: 0,
    status: 'draft',
  });

  useEffect(() => {
    fetchDrivers();
    if (isEdit) {
      fetchTrip();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const fetchDrivers = async () => {
    try {
      const response = await driverAPI.list();
      setDrivers(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch drivers:', error);
    }
  };

  const fetchTrip = async () => {
    try {
      const response = await tripAPI.get(id);
      const trip = response.data;
      setFormData({
        ...trip,
        driver_id: trip.driver?.id,
        date: trip.date,
      });
      setTripType(trip.trip_type);
    } catch (error) {
      console.error('Failed to fetch trip:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleTripTypeChange = (type) => {
    setTripType(type);
    setFormData(prev => ({ ...prev, trip_type: type }));
  };

  const handleSubmit = async (e, saveAsDraft = true) => {
    e.preventDefault();
    setLoading(true);

    try {
      const data = {
        ...formData,
        status: saveAsDraft ? 'draft' : 'completed',
      };

      if (isEdit) {
        await tripAPI.update(id, data);
      } else {
        await tripAPI.create(data);
      }

      navigate('/driver/trips');
    } catch (error) {
      console.error('Failed to save trip:', error);
      alert('Failed to save trip. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateBill = async () => {
    try {
      const response = await billAPI.generatePDF(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `bill_${formData.trip_code || 'trip'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to generate bill:', error);
      alert('Failed to generate bill. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-5 h-5" />
            Back
          </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">
            {isEdit ? 'Edit Trip' : 'Create New Trip'}
          </h1>

          <form onSubmit={(e) => handleSubmit(e, true)} className="space-y-6">
            {/* Trip Type Toggle */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Trip Type
              </label>
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => handleTripTypeChange('taxi')}
                  className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
                    tripType === 'taxi'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Taxi
                </button>
                <button
                  type="button"
                  onClick={() => handleTripTypeChange('local')}
                  className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
                    tripType === 'local'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Local
                </button>
              </div>
            </div>

            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date
                </label>
                <input
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Day
                </label>
                <input
                  type="text"
                  name="day"
                  value={formData.day}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Driver
                </label>
                <select
                  name="driver_id"
                  value={formData.driver_id}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select Driver</option>
                  {drivers.map((driver) => (
                    <option key={driver.id} value={driver.id}>
                      {driver.user.first_name} {driver.user.last_name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Location Fields */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Starting Place
                </label>
                <input
                  type="text"
                  name="start_place"
                  value={formData.start_place}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Customer Pickup Place
                </label>
                <input
                  type="text"
                  name="pickup_place"
                  value={formData.pickup_place}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Customer Dropping Place
                </label>
                <input
                  type="text"
                  name="drop_place"
                  value={formData.drop_place}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ending Place
                </label>
                <input
                  type="text"
                  name="end_place"
                  value={formData.end_place}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* KM and Time */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Starting KM
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="start_km"
                  value={formData.start_km}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ending KM
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="end_km"
                  value={formData.end_km}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Time In
                </label>
                <input
                  type="time"
                  name="time_in"
                  value={formData.time_in}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Time Out
                </label>
                <input
                  type="time"
                  name="time_out"
                  value={formData.time_out}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Financial Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  CNG
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="cng"
                  value={formData.cng}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Petrol
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="petrol"
                  value={formData.petrol}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Red Taxi Income
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="red_taxi_income"
                  value={formData.red_taxi_income}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Commission
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="commission"
                  value={formData.commission}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Local Trip Specific Fields */}
            {tripType === 'local' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Waiting Charge
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="waiting_charge"
                    value={formData.waiting_charge}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Inter State Permit
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="inter_state_permit"
                    value={formData.inter_state_permit}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Luggage Charges
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="luggage_charges"
                    value={formData.luggage_charges}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Pet Charges
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="pet_charges"
                    value={formData.pet_charges}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hill Charges
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="hill_charges"
                    value={formData.hill_charges}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Toll Charges
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="toll_charges"
                    value={formData.toll_charges}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Base Fare
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="base_fare"
                    value={formData.base_fare}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Driver Allowance
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="driver_allowance"
                    value={formData.driver_allowance}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            )}

            {/* Additional Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Advance
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="advance"
                  value={formData.advance}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Advance Received Today
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="advance_received_today"
                  value={formData.advance_received_today}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Previous Salary
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="previous_salary"
                  value={formData.previous_salary}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  DR Advance
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="dr_adv"
                  value={formData.dr_adv}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Salary Per Hour
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="salary_per_hour"
                  value={formData.salary_per_hour}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Save className="w-5 h-5" />
                {loading ? 'Saving...' : 'Save Draft'}
              </button>

              <button
                type="button"
                onClick={(e) => handleSubmit(e, false)}
                disabled={loading}
                className="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Send className="w-5 h-5" />
                {loading ? 'Completing...' : 'Complete Trip'}
              </button>

              {isEdit && (
                <button
                  type="button"
                  onClick={handleGenerateBill}
                  className="flex-1 bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 flex items-center justify-center gap-2"
                >
                  <FileText className="w-5 h-5" />
                  Generate Bill
                </button>
              )}
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default TripForm;
