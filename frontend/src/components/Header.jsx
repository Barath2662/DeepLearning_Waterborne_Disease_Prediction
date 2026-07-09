export default function Header({ backendOnline }) {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 backdrop-blur-xl" style={{ background: 'rgba(15,23,36,0.85)' }}>
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-xl"
              style={{ background: 'linear-gradient(135deg,#2196f3,#1565c0)' }}>
              💧
            </div>
            <div>
              <h1 className="font-bold text-white text-sm sm:text-base leading-tight">WaterGuard AI</h1>
              <p className="text-xs text-blue-400 hidden sm:block">Early Warning System · Water-Borne Disease Prediction</p>
            </div>
          </div>

          {/* Status */}
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border ${
              backendOnline
                ? 'border-green-500/30 text-green-400 bg-green-500/10'
                : 'border-red-500/30 text-red-400 bg-red-500/10'
            }`}>
              <span className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
              {backendOnline ? 'Backend Online' : 'Backend Offline'}
            </div>
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border border-blue-500/30 text-blue-400 bg-blue-500/10">
              <span>🧠</span>
              Random Forest · XGBoost
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
