import { Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

export default function RiskDistributionChart({ analytics, loading }) {
  const dist = analytics?.class_distribution ?? {}
  const low    = dist['Low']    ?? 0
  const medium = dist['Medium'] ?? 0
  const high   = dist['High']   ?? 0
  const total  = low + medium + high

  const data = {
    labels: ['Low Risk', 'Medium Risk', 'High Risk'],
    datasets: [{
      data: [low, medium, high],
      backgroundColor: ['rgba(76,175,80,0.8)', 'rgba(255,152,0,0.8)', 'rgba(244,67,54,0.8)'],
      borderColor: ['#4caf50', '#ff9800', '#f44336'],
      borderWidth: 2,
      hoverOffset: 6,
    }]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#9ca3af',
          padding: 12,
          font: { size: 11, family: 'Inter' },
          usePointStyle: true,
          pointStyleWidth: 8,
        }
      },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : 0
            return `  ${ctx.label}: ${ctx.parsed.toLocaleString()} (${pct}%)`
          }
        },
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
        <span>🥧</span> Risk Distribution
      </h3>
      {loading ? (
        <div className="h-52 shimmer rounded-xl" />
      ) : total === 0 ? (
        <div className="h-52 flex items-center justify-center text-gray-500 text-sm">No data available</div>
      ) : (
        <>
          <div className="h-52">
            <Doughnut data={data} options={options} />
          </div>
          <div className="grid grid-cols-3 gap-2 mt-4">
            {[
              { label: 'Low', val: low, clr: '#4caf50' },
              { label: 'Medium', val: medium, clr: '#ff9800' },
              { label: 'High', val: high, clr: '#f44336' },
            ].map(({ label, val, clr }) => (
              <div key={label} className="text-center glass-card py-2 px-1">
                <p className="text-xs text-gray-400">{label}</p>
                <p className="font-bold text-sm" style={{ color: clr }}>{total > 0 ? ((val/total)*100).toFixed(0) : 0}%</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
