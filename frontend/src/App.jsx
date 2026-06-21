import { useState, useEffect, useCallback } from 'react'
import { predictRisk, getAnalytics } from './api'
import Header from './components/Header'
import StatCards from './components/StatCards'
import InputPanel from './components/InputPanel'
import PredictionResult from './components/PredictionResult'
import RiskDistributionChart from './components/charts/RiskDistributionChart'
import WaterQualityChart from './components/charts/WaterQualityChart'
import ModelAccuracyChart from './components/charts/ModelAccuracyChart'
import FeatureImportanceChart from './components/charts/FeatureImportanceChart'

const defaultFormData = {
  ph: 7.2,
  turbidity: 5.0,
  dissolved_oxygen: 6.5,
  temperature: 28.0,
  rainfall: 150.0,
  humidity: 70.0,
  population_density: 1200.0,
  sanitation_index: 65.0,
  bacterial_count: 350.0,
  ecoli_count: 40.0,
  chlorine_level: 1.2,
  water_source: 'River',
  region_type: 'Urban',
  season: 'Monsoon',
  previous_cases: 20,
}

export default function App() {
  const [formData, setFormData] = useState(defaultFormData)
  const [prediction, setPrediction] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(false)
  const [analyticsLoading, setAnalyticsLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchAnalytics = useCallback(async () => {
    try {
      setAnalyticsLoading(true)
      const data = await getAnalytics()
      setAnalytics(data)
    } catch (err) {
      console.error('Analytics fetch error:', err)
    } finally {
      setAnalyticsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAnalytics()
  }, [fetchAnalytics])

  const handlePredict = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await predictRisk(formData)
      setPrediction(result)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to connect to backend. Ensure the FastAPI server is running on port 8000.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setFormData(defaultFormData)
    setPrediction(null)
    setError(null)
  }

  return (
    <div className="min-h-screen">
      <Header backendOnline={!!analytics} />

      <main className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Stats Row */}
        <StatCards analytics={analytics} loading={analyticsLoading} />

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Input Panel (left 2/3 on XL) */}
          <div className="xl:col-span-2 space-y-6">
            <InputPanel
              formData={formData}
              setFormData={setFormData}
              onPredict={handlePredict}
              onReset={handleReset}
              loading={loading}
              error={error}
            />
            {prediction && (
              <PredictionResult prediction={prediction} />
            )}
          </div>

          {/* Charts Column (right 1/3 on XL) */}
          <div className="space-y-6">
            <RiskDistributionChart analytics={analytics} loading={analyticsLoading} />
            <ModelAccuracyChart analytics={analytics} loading={analyticsLoading} />
          </div>
        </div>

        {/* Bottom Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <WaterQualityChart analytics={analytics} loading={analyticsLoading} />
          <FeatureImportanceChart />
        </div>
      </main>

      <footer className="text-center py-6 text-gray-500 text-sm border-t border-white/5 mt-8">
        <p>WaterGuard AI – Deep Learning Based Early Warning System for Water-Borne Disease Prediction</p>
        <p className="mt-1 text-xs text-gray-600">Powered by TensorFlow · FastAPI · React · Open Source Stack</p>
      </footer>
    </div>
  )
}
