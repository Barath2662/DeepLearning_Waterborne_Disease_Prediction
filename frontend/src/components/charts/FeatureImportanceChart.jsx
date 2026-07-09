import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  BarElement, Title, Tooltip, Legend
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

// Fallback feature importance used if backend analytics are unavailable
const IMPORTANCE = [
  { feature: 'Bacterial Count', importance: 0.195 },
  { feature: 'E.coli Count', importance: 0.175 },
  { feature: 'Sanitation Index', importance: 0.145 },
  { feature: 'Chlorine Level', importance: 0.115 },
  { feature: 'Turbidity', importance: 0.098 },
  { feature: 'Dissolved Oxygen', importance: 0.085 },
  { feature: 'Rainfall', importance: 0.062 },
  { feature: 'pH', importance: 0.048 },
  { feature: 'Temperature', importance: 0.038 },
  { feature: 'Previous Cases', importance: 0.039 },
]

export default function FeatureImportanceChart({ analytics, loading }) {
  const backendImportance = analytics?.feature_importance ?? []
  const source = backendImportance.length > 0
    ? backendImportance.map(row => ({
        feature: row.feature ?? row.index ?? row.name,
        importance: row.importance ?? row.value ?? 0,
      }))
    : IMPORTANCE

  const sorted = [...source].filter(item => item.feature).sort((a, b) => a.importance - b.importance)

  const data = {
    labels: sorted.map(d => d.feature),
    datasets: [{
      label: 'Feature Importance',
      data: sorted.map(d => +(d.importance * 100).toFixed(1)),
      backgroundColor: sorted.map((_, i) => {
        const t = i / sorted.length
        const r = Math.round(33 + t * (244 - 33))
        const g = Math.round(150 + t * (67 - 150))
        const b = Math.round(243 + t * (54 - 243))
        return `rgba(${r},${g},${b},0.8)`
      }),
      borderColor: '#2196f3',
      borderWidth: 0,
      borderRadius: 4,
    }]
  }

  const options = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        ticks: {
          color: '#9ca3af',
          font: { size: 10, family: 'Inter' },
          callback: v => `${v}%`,
        },
        grid: { color: 'rgba(255,255,255,0.06)' },
      },
      y: {
        ticks: { color: '#9ca3af', font: { size: 10, family: 'Inter' } },
        grid: { display: false },
      }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: { label: ctx => `  Importance: ${ctx.parsed.x}%` },
        backgroundColor: 'rgba(15,23,36,0.9)',
        titleColor: '#fff',
        bodyColor: '#9ca3af',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
      }
    }
  }

  return (
    <div className="glass-card p-5 animate-fade-in">
      <h3 className="section-title">
        <span>🔬</span> Feature Importance
      </h3>
      <p className="text-xs text-gray-400 -mt-2 mb-4">Key factors influencing disease risk prediction</p>
      {loading ? (
        <div className="h-64 shimmer rounded-xl" />
      ) : (
        <div className="h-64">
          <Bar data={data} options={options} />
        </div>
      )}
    </div>
  )
}
