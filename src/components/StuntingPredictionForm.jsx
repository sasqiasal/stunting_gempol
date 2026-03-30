import React, { useState, useEffect } from 'react';
import {
  stuntingPredictionAPI,
  formatPredictionResult,
  validatePredictionInput,
} from '../services/stuntingPredictionAPI';

export const StuntingPredictionForm = () => {
  const [formData, setFormData] = useState({
    jenis_kelamin: 1,
    usia_bulan: 24,
    berat_badan: 12.5,
    tinggi_badan: 89.0,
    lingkar_lengan: 18.0,
    lingkar_kepala: 53.0,
  });

  const [result, setResult] = useState(null);
  const [neighbors, setNeighbors] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showNeighbors, setShowNeighbors] = useState(false);
  const [modelInfo, setModelInfo] = useState(null);

  // Load model info on mount
  useEffect(() => {
    try {
      stuntingPredictionAPI.getModelInfo().then(setModelInfo);
    } catch (err) {
      console.error('Failed to load model info:', err);
    }
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'jenis_kelamin' ? parseInt(value) : parseFloat(value),
    }));
  };

  const handlePredictClick = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setNeighbors(null);

    try {
      // Validate input
      const validation = validatePredictionInput(formData);
      if (!validation.valid) {
        setError('Validasi gagal: ' + validation.errors.join(', '));
        setLoading(false);
        return;
      }

      // Get prediction
      const response = await stuntingPredictionAPI.predictStunting(formData);
      const formattedResult = formatPredictionResult(response);
      setResult(formattedResult);
    } catch (err) {
      setError(err.message || 'Terjadi kesalahan saat prediksi');
    } finally {
      setLoading(false);
    }
  };

  const handleGetNeighbors = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await stuntingPredictionAPI.getNeighbors(formData);
      setNeighbors(response);
      setShowNeighbors(true);
    } catch (err) {
      setError(err.message || 'Terjadi kesalahan saat mengambil neighbors');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🏥 Prediksi Stunting KNN
          </h1>
          <p className="text-gray-600">
            Model K-Nearest Neighbors untuk deteksi status gizi anak balita
          </p>

          {modelInfo && (
            <div className="mt-4 inline-block bg-white rounded-lg shadow p-4 text-sm">
              <p className="text-gray-700">
                📊 Akurasi Model: <span className="font-bold text-green-600">95.05%</span> |
                K-value: <span className="font-bold">5</span> |
                Test samples: <span className="font-bold">101</span>
              </p>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Form Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Data Balita</h2>

              <form onSubmit={handlePredictClick} className="space-y-4">
                {/* Jenis Kelamin */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Jenis Kelamin
                  </label>
                  <select
                    name="jenis_kelamin"
                    value={formData.jenis_kelamin}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  >
                    <option value={0}>👧 Perempuan</option>
                    <option value={1}>👦 Laki-laki</option>
                  </select>
                </div>

                {/* Usia Bulan */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Usia (bulan)
                  </label>
                  <input
                    type="number"
                    name="usia_bulan"
                    value={formData.usia_bulan}
                    onChange={handleInputChange}
                    min="0"
                    max="60"
                    step="1"
                    className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  />
                  <small className="text-gray-500">(0-60 bulan)</small>
                </div>

                {/* Berat Badan */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Berat Badan (kg)
                  </label>
                  <input
                    type="number"
                    name="berat_badan"
                    value={formData.berat_badan}
                    onChange={handleInputChange}
                    step="0.1"
                    min="0"
                    className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  />
                </div>

                {/* Tinggi Badan */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Tinggi Badan (cm)
                  </label>
                  <input
                    type="number"
                    name="tinggi_badan"
                    value={formData.tinggi_badan}
                    onChange={handleInputChange}
                    step="0.1"
                    min="0"
                    className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  />
                </div>

                {/* Lingkar Lengan */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Lingkar Lengan (cm)
                  </label>
                  <input
                    type="number"
                    name="lingkar_lengan"
                    value={formData.lingkar_lengan}
                    onChange={handleInputChange}
                    step="0.1"
                    min="0"
                    className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  />
                </div>

                {/* Lingkar Kepala */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Lingkar Kepala (cm)
                  </label>
                  <input
                    type="number"
                    name="lingkar_kepala"
                    value={formData.lingkar_kepala}
                    onChange={handleInputChange}
                    step="0.1"
                    min="0"
                    className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  />
                </div>

                {/* Buttons */}
                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded-lg transition duration-200"
                  >
                    {loading ? '⏳ Prediksi...' : '🔍 Prediksi'}
                  </button>
                  <button
                    type="button"
                    onClick={handleGetNeighbors}
                    disabled={loading}
                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded-lg transition duration-200"
                  >
                    {loading ? '⏳ Loading...' : '👥 Neighbors'}
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Result Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
                <p className="text-red-700 font-semibold">❌ Error</p>
                <p className="text-red-600">{error}</p>
              </div>
            )}

            {/* Prediction Result */}
            {result && (
              <div
                className="rounded-lg shadow-lg p-6"
                style={{ backgroundColor: result.isStunting ? '#FFF3F3' : '#F3FFF3' }}
              >
                <div className="flex items-center gap-4 mb-4">
                  <div
                    className="w-16 h-16 rounded-full flex items-center justify-center text-3xl"
                    style={{ backgroundColor: result.color }}
                  >
                    {result.isStunting ? '⚠️' : '✅'}
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-800">{result.status}</h3>
                    <p className="text-gray-600">{result.label}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="bg-white rounded p-3">
                    <p className="text-sm text-gray-600">Predicted Class</p>
                    <p className="text-2xl font-bold text-blue-600">{result.class}</p>
                  </div>
                  <div className="bg-white rounded p-3">
                    <p className="text-sm text-gray-600">Confidence Score</p>
                    <p className="text-2xl font-bold text-green-600">{result.confidence}</p>
                  </div>
                </div>

                <div className="bg-white rounded p-4 border-l-4" style={{ borderColor: result.color }}>
                  <p className="text-sm font-semibold text-gray-700 mb-2">Rekomendasi:</p>
                  <p className="text-gray-700 leading-relaxed">{result.recommendation}</p>
                </div>
              </div>
            )}

            {/* Neighbors Info */}
            {showNeighbors && neighbors && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">
                  👥 K-Nearest Neighbors (K=5)
                </h3>

                {neighbors.success && neighbors.data ? (
                  <div className="space-y-2">
                    <p className="text-sm text-gray-600 mb-3">
                      Predicted Class: <span className="font-bold">{neighbors.data.predicted_class}</span>
                    </p>

                    {neighbors.data.neighbors && (
                      <div>
                        <p className="text-sm font-semibold text-gray-700 mb-2">
                          Distance ke Neighbors:
                        </p>
                        <div className="space-y-1">
                          {neighbors.data.neighbors.map((neighbor, idx) => (
                            <div
                              key={idx}
                              className="flex justify-between items-center bg-gray-50 p-3 rounded"
                            >
                              <span className="font-semibold text-gray-700">
                                Neighbor {idx + 1}
                              </span>
                              <span className="text-blue-600 font-mono">
                                {neighbor.distance.toFixed(4)}
                              </span>
                            </div>
                          ))}
                        </div>

                        {neighbors.data.neighbors.length > 0 && (
                          <div className="mt-4 p-3 bg-blue-50 rounded border-l-4 border-blue-400">
                            <p className="text-sm text-gray-700">
                              <span className="font-semibold">Avg Distance:</span>{' '}
                              {(
                                neighbors.data.neighbors.reduce((sum, n) => sum + n.distance, 0) /
                                neighbors.data.neighbors.length
                              ).toFixed(4)}
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-red-600">Gagal mengambil neighbors info</p>
                )}
              </div>
            )}

            {/* Initial State */}
            {!result && !error && (
              <div className="bg-gray-50 rounded-lg p-8 text-center">
                <p className="text-gray-500 text-lg">
                  📝 Masukkan data balita dan klik "Prediksi" untuk melihat hasil
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StuntingPredictionForm;
