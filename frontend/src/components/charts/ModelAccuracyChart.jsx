import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  BarElement, Title, Tooltip, Legend
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

export default function ModelAccuracyChart({ analytics, loading }) {
  const modelAcc = analytics?.model_accuracy ?? {}

  const labels = Object.keys(modelAcc)
  const values = Object.values(modelAcc).map(v => +(v * 100).toFixed(2))

  const colors = [
    'rgba(33,150,243,0.8)',
    'rgba(76,175,80,0.8)',
    'rgba(156,39,176,0.8)',
  ]
  const borders = ['#2196f3', '#4caf50', '#9c27b0']

  const data = {
    labels: labels.length ? labels : ['Random Forest', 'XGBoost'],
    datasets: [{
      label: 'Test Accuracy (%)',
      data: values.length ? values : [0, 0, 0],
      backgroundColor: colors,
      borderColor: borders,
      borderWidth: 2,
      borderRadius: 8,
      borderSkipped: false,
    }]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        ticks: { color: '#9ca3af', font: { size: 10, family: 'Inter' } },
        grid: { color: 'rgba(255,255,255,0.04)' },
      },
      y: {
        min: 0,
        max: 100,
        ticks: {
          color: '#9ca3af',
          font: { size: 10, family: 'Inter' },
          callback: v => `${v}%`,
        },
        grid: { color: 'rgba(255,255,255,0.06)' },
      }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: { label: ctx => `  Accuracy: ${ctx.parsed.y}%` },
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
        <span>📈</span> Model Accuracy
      </h3>
      {loading ? (
        <div className="h-48 shimmer rounded-xl" />
      ) : (
        <div className="h-48">
          <Bar data={data} options={options} />
        </div>
      )}
      {!loading && Object.entries(modelAcc).length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {Object.entries(modelAcc).map(([name, acc], i) => (
            <div key={name} className="flex items-center gap-1.5 text-xs text-gray-400">
              <span className="w-2 h-2 rounded-full" style={{ background: borders[i] }} />
              {name}: <span className="text-white font-semibold ml-0.5">{(acc*100).toFixed(1)}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
