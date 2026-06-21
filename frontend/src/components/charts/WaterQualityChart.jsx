import { Radar } from 'react-chartjs-2'
import {
  Chart as ChartJS, RadialLinearScale, PointElement,
  LineElement, Filler, Tooltip, Legend
} from 'chart.js'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

export default function WaterQualityChart({ analytics, loading }) {
  const stats = analytics?.dataset_stats ?? {}

  // Normalize each indicator to 0-100 scale for radar
  const normalize = (val, min, max) => Math.min(100, Math.max(0, ((val - min) / (max - min)) * 100))

  const phMean    = stats.ph?.mean ?? 7
  const doMean    = stats.dissolved_oxygen?.mean ?? 7
  const clMean    = stats.chlorine_level?.mean ?? 1
  const sanMean   = stats.sanitation_index?.mean ?? 60
  const turbMean  = stats.turbidity?.mean ?? 10
  const tempMean  = stats.temperature?.mean ?? 25

  // For radar: higher = better quality
  const phScore    = normalize(Math.abs(phMean - 7), 0, 3) * -1 + 100   // closer to 7 = better
  const doScore    = normalize(doMean, 0, 14)
  const clScore    = normalize(clMean, 0, 3) * 60 + 40                   // 0-3 mg/L
  const sanScore   = sanMean
  const turbScore  = normalize(turbMean, 0, 100) * -1 + 100              // lower turbidity = better
  const tempScore  = normalize(Math.abs(tempMean - 22), 0, 20) * -1 + 100

  const data = {
    labels: ['pH Quality', 'Dissolved O₂', 'Chlorination', 'Sanitation', 'Clarity', 'Temperature'],
    datasets: [{
      label: 'Water Quality Score',
      data: [
        +phScore.toFixed(1),
        +doScore.toFixed(1),
        +Math.min(100, clScore).toFixed(1),
        +sanScore.toFixed(1),
        +turbScore.toFixed(1),
        +tempScore.toFixed(1),
      ],
      backgroundColor: 'rgba(33,150,243,0.15)',
      borderColor: '#2196f3',
      borderWidth: 2,
      pointBackgroundColor: '#2196f3',
      pointBorderColor: '#fff',
      pointBorderWidth: 1.5,
      pointRadius: 4,
    }]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: {
          color: '#6b7280',
          font: { size: 9 },
          stepSize: 25,
          backdropColor: 'transparent',
        },
        grid: { color: 'rgba(255,255,255,0.06)' },
        angleLines: { color: 'rgba(255,255,255,0.08)' },
        pointLabels: {
          color: '#9ca3af',
          font: { size: 10, family: 'Inter' },
        }
      }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: { label: ctx => `  ${ctx.label}: ${ctx.parsed.r.toFixed(1)}/100` },
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
        <span>🕸️</span> Water Quality Indicators
      </h3>
      <p className="text-xs text-gray-400 -mt-2 mb-4">Dataset average values normalized to quality scores (0–100)</p>
      {loading ? (
        <div className="h-64 shimmer rounded-xl" />
      ) : (
        <div className="h-64">
          <Radar data={data} options={options} />
        </div>
      )}
    </div>
  )
}
