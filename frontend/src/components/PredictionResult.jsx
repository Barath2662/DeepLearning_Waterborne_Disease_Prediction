export default function PredictionResult({ prediction }) {
  const { risk, confidence, recommendation, probabilities, diseases } = prediction

  const riskConfig = {
    Low: {
      badge: 'risk-badge-low',
      icon: '✅',
      emoji: '💚',
      color: '#4caf50',
      glow: 'rgba(76,175,80,0.3)',
      bg: 'linear-gradient(135deg, rgba(76,175,80,0.12), rgba(46,125,50,0.06))',
      border: 'border-green-500/25',
    },
    Medium: {
      badge: 'risk-badge-medium',
      icon: '⚡',
      emoji: '🟡',
      color: '#ff9800',
      glow: 'rgba(255,152,0,0.3)',
      bg: 'linear-gradient(135deg, rgba(255,152,0,0.12), rgba(230,81,0,0.06))',
      border: 'border-yellow-500/25',
    },
    High: {
      badge: 'risk-badge-high',
      icon: '🚨',
      emoji: '🔴',
      color: '#f44336',
      glow: 'rgba(244,67,54,0.3)',
      bg: 'linear-gradient(135deg, rgba(244,67,54,0.15), rgba(183,28,28,0.08))',
      border: 'border-red-500/25',
    },
  }

  const cfg = riskConfig[risk] || riskConfig.Low
  const confVal = parseFloat(confidence)

  return (
    <div
      className={`rounded-2xl border ${cfg.border} p-6 animate-slide-up`}
      style={{ background: cfg.bg, boxShadow: `0 8px 32px ${cfg.glow}` }}
    >
      {/* Title Row */}
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <span className="text-2xl">{cfg.icon}</span> Prediction Result
        </h3>
        <span className="text-xs text-gray-400 font-mono">
          {new Date().toLocaleTimeString()}
        </span>
      </div>

      {/* Main Result */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 mb-6">
        {/* Risk Level */}
        <div className="flex flex-col gap-2">
          <p className="text-xs text-gray-400 uppercase tracking-wider">Disease Risk Level</p>
          <div className={cfg.badge} style={{ fontSize: '1.1rem', padding: '0.6rem 1.2rem' }}>
            <span className="text-xl">{cfg.emoji}</span>
            <span>{risk} Risk</span>
          </div>
        </div>

        {/* Confidence Gauge */}
        <div className="flex-1">
          <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">
            Model Confidence: <span className="text-white font-bold ml-1">{confidence}</span>
          </p>
          <div className="h-3 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-1000"
              style={{
                width: `${confVal}%`,
                background: `linear-gradient(90deg, ${cfg.color}99, ${cfg.color})`,
                boxShadow: `0 0 8px ${cfg.glow}`,
              }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0%</span><span>50%</span><span>100%</span>
          </div>
        </div>
      </div>

      {/* Probability Breakdown */}
      {probabilities && (
        <div className="mb-5">
          <p className="text-xs text-gray-400 uppercase tracking-wider mb-3">Class Probabilities</p>
          <div className="grid grid-cols-3 gap-3">
            {Object.entries(probabilities).map(([cls, prob]) => {
              const colors = { Low: '#4caf50', Medium: '#ff9800', High: '#f44336' }
              const clr = colors[cls] || '#2196f3'
              return (
                <div key={cls} className="glass-card p-3 text-center">
                  <p className="text-xs text-gray-400 mb-1">{cls}</p>
                  <p className="text-xl font-bold" style={{ color: clr }}>{prob.toFixed(1)}%</p>
                  <div className="h-1 bg-white/10 rounded-full mt-2 overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${prob}%`, background: clr }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Waterborne Diseases */}
      {diseases && diseases.length > 0 && (
        <div className="mb-5">
          <p className="text-xs text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <span>🦠</span> Potential Waterborne Diseases at Risk
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {diseases.map((disease, idx) => (
              <div
                key={idx}
                className="rounded-lg p-3 border transition-all"
                style={{
                  background: `rgba(255,255,255,0.05)`,
                  borderColor: cfg.color + '40',
                  boxShadow: `0 0 12px ${cfg.glow}`,
                }}
              >
                <p className="text-sm font-semibold text-white">{disease}</p>
                <p className="text-xs text-gray-400 mt-1">
                  {risk === 'Low' && 'No risk - water is safe'}
                  {risk === 'Medium' && 'Moderate risk - elevated caution'}
                  {risk === 'High' && 'High risk - immediate concern'}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendation */}
      <div className="rounded-xl p-4 border border-white/8" style={{ background: 'rgba(255,255,255,0.04)' }}>
        <p className="text-xs text-gray-400 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
          <span>📋</span> Recommendation
        </p>
        <p className="text-sm text-gray-200 leading-relaxed">{recommendation}</p>
      </div>
    </div>
  )
}
