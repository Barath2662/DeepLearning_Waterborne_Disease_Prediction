function StatCard({ icon, label, value, sub, color, loading }) {
  return (
    <div className="glass-card p-5 flex items-center gap-4 animate-fade-in">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl flex-shrink-0`}
        style={{ background: color }}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-xs text-gray-400 uppercase tracking-wider font-medium">{label}</p>
        {loading ? (
          <div className="h-7 w-24 mt-1 rounded shimmer" />
        ) : (
          <p className="text-2xl font-bold text-white mt-0.5">{value}</p>
        )}
        {sub && <p className="text-xs text-gray-500 mt-0.5 truncate">{sub}</p>}
      </div>
    </div>
  )
}

export default function StatCards({ analytics, loading }) {
  const totalRecords = analytics?.total_records ?? '—'
  const classDistrib = analytics?.class_distribution ?? {}
  const highRisk = classDistrib['High'] ?? '—'
  const modelAcc = analytics?.model_accuracy ?? {}
  const dnnAcc = modelAcc['Deep Neural Network'] != null
    ? `${(modelAcc['Deep Neural Network'] * 100).toFixed(1)}%`
    : '—'

  // compute avg water quality
  const stats = analytics?.dataset_stats ?? {}
  let avgQuality = '—'
  if (stats.ph) {
    // composite score: pH nearness to 7, chlorine, DO
    const ph = stats.ph.mean ?? 7
    const cl = stats.chlorine_level?.mean ?? 1
    const doVal = stats.dissolved_oxygen?.mean ?? 7
    const score = Math.min(100, (
      (1 - Math.abs(ph - 7) / 7) * 40 +
      Math.min(cl / 2, 1) * 30 +
      (doVal / 14) * 30
    )).toFixed(1)
    avgQuality = score
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard icon="📊" label="Total Records" value={loading ? '—' : totalRecords.toLocaleString()}
        sub="Dataset size" color="linear-gradient(135deg,#2196f3,#1565c0)" loading={loading} />
      <StatCard icon="🧠" label="DNN Accuracy" value={loading ? '—' : dnnAcc}
        sub="Test set performance" color="linear-gradient(135deg,#9c27b0,#6a1b9a)" loading={loading} />
      <StatCard icon="⚠️" label="High Risk Cases" value={loading ? '—' : (highRisk !== '—' ? highRisk.toLocaleString() : '—')}
        sub="In dataset" color="linear-gradient(135deg,#f44336,#b71c1c)" loading={loading} />
      <StatCard icon="💧" label="Avg Water Quality" value={loading ? '—' : avgQuality}
        sub="Composite score /100" color="linear-gradient(135deg,#4caf50,#2e7d32)" loading={loading} />
    </div>
  )
}
