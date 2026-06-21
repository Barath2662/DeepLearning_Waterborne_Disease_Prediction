function FormField({ label, id, children }) {
  return (
    <div>
      <label htmlFor={id} className="label-text">{label}</label>
      {children}
    </div>
  )
}

function NumberInput({ id, value, onChange, min, max, step = 0.1 }) {
  return (
    <input
      id={id}
      type="number"
      className="input-field"
      value={value}
      min={min}
      max={max}
      step={step}
      onChange={e => onChange(parseFloat(e.target.value) || 0)}
    />
  )
}

function SelectInput({ id, value, onChange, options }) {
  return (
    <select
      id={id}
      className="input-field"
      value={value}
      onChange={e => onChange(e.target.value)}
    >
      {options.map(opt => (
        <option key={opt} value={opt} className="bg-gray-900">{opt}</option>
      ))}
    </select>
  )
}

export default function InputPanel({ formData, setFormData, onPredict, onReset, loading, error }) {
  const set = (key) => (val) => setFormData(prev => ({ ...prev, [key]: val }))

  return (
    <div className="glass-card p-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="section-title mb-0">
            <span className="text-2xl">🔬</span> Water Quality Parameters
          </h2>
          <p className="text-xs text-gray-400 mt-0.5">Enter environmental and water quality data for risk assessment</p>
        </div>
        <button
          id="btn-reset-params"
          onClick={onReset}
          className="text-xs text-gray-400 hover:text-white border border-white/10 hover:border-white/30 px-3 py-1.5 rounded-lg transition-all"
        >
          ↺ Reset
        </button>
      </div>

      {/* Fields Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        <FormField label="Water pH" id="ph">
          <NumberInput id="ph" value={formData.ph} onChange={set('ph')} min={0} max={14} step={0.1} />
        </FormField>
        <FormField label="Turbidity (NTU)" id="turbidity">
          <NumberInput id="turbidity" value={formData.turbidity} onChange={set('turbidity')} min={0} max={1000} step={0.5} />
        </FormField>
        <FormField label="Dissolved O₂ (mg/L)" id="dissolved_oxygen">
          <NumberInput id="dissolved_oxygen" value={formData.dissolved_oxygen} onChange={set('dissolved_oxygen')} min={0} max={20} step={0.1} />
        </FormField>
        <FormField label="Temperature (°C)" id="temperature">
          <NumberInput id="temperature" value={formData.temperature} onChange={set('temperature')} min={0} max={60} step={0.5} />
        </FormField>
        <FormField label="Rainfall (mm)" id="rainfall">
          <NumberInput id="rainfall" value={formData.rainfall} onChange={set('rainfall')} min={0} max={1000} step={1} />
        </FormField>
        <FormField label="Humidity (%)" id="humidity">
          <NumberInput id="humidity" value={formData.humidity} onChange={set('humidity')} min={0} max={100} step={0.5} />
        </FormField>
        <FormField label="Population Density" id="population_density">
          <NumberInput id="population_density" value={formData.population_density} onChange={set('population_density')} min={0} max={50000} step={10} />
        </FormField>
        <FormField label="Sanitation Index" id="sanitation_index">
          <NumberInput id="sanitation_index" value={formData.sanitation_index} onChange={set('sanitation_index')} min={0} max={100} step={1} />
        </FormField>
        <FormField label="Bacterial Count (CFU/mL)" id="bacterial_count">
          <NumberInput id="bacterial_count" value={formData.bacterial_count} onChange={set('bacterial_count')} min={0} max={10000} step={1} />
        </FormField>
        <FormField label="E.coli Count (CFU/100mL)" id="ecoli_count">
          <NumberInput id="ecoli_count" value={formData.ecoli_count} onChange={set('ecoli_count')} min={0} max={1000} step={1} />
        </FormField>
        <FormField label="Chlorine Level (mg/L)" id="chlorine_level">
          <NumberInput id="chlorine_level" value={formData.chlorine_level} onChange={set('chlorine_level')} min={0} max={10} step={0.05} />
        </FormField>
        <FormField label="Previous Cases" id="previous_cases">
          <NumberInput id="previous_cases" value={formData.previous_cases} onChange={set('previous_cases')} min={0} max={500} step={1} />
        </FormField>
        <FormField label="Water Source" id="water_source">
          <SelectInput id="water_source" value={formData.water_source} onChange={set('water_source')}
            options={['River', 'Lake', 'Groundwater', 'Tap', 'Well', 'Pond']} />
        </FormField>
        <FormField label="Region Type" id="region_type">
          <SelectInput id="region_type" value={formData.region_type} onChange={set('region_type')}
            options={['Urban', 'Rural', 'Semi-Urban', 'Coastal', 'Hilly']} />
        </FormField>
        <FormField label="Season" id="season">
          <SelectInput id="season" value={formData.season} onChange={set('season')}
            options={['Summer', 'Monsoon', 'Winter', 'Spring']} />
        </FormField>
      </div>

      {/* Error */}
      {error && (
        <div className="mt-4 px-4 py-3 rounded-xl border border-red-500/30 bg-red-500/10 text-red-400 text-sm flex items-start gap-2">
          <span className="mt-0.5">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-3 mt-6">
        <button
          id="btn-predict"
          onClick={onPredict}
          disabled={loading}
          className="btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Analyzing…
            </>
          ) : (
            <>🔍 Predict Disease Risk</>
          )}
        </button>
      </div>

      {/* Quick Scenario Buttons */}
      <div className="mt-4 flex flex-wrap gap-2">
        <p className="text-xs text-gray-500 w-full">Quick Scenarios:</p>
        <button
          id="btn-scenario-low"
          className="text-xs px-3 py-1.5 rounded-lg border border-green-500/30 text-green-400 hover:bg-green-500/10 transition-all"
          onClick={() => setFormData({
            ph:7.2, turbidity:2, dissolved_oxygen:9, temperature:20, rainfall:30,
            humidity:50, population_density:400, sanitation_index:90, bacterial_count:50,
            ecoli_count:5, chlorine_level:1.8, water_source:'Tap', region_type:'Urban',
            season:'Winter', previous_cases:1
          })}
        >✅ Low Risk Sample</button>
        <button
          id="btn-scenario-medium"
          className="text-xs px-3 py-1.5 rounded-lg border border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/10 transition-all"
          onClick={() => setFormData({
            ph:6.8, turbidity:12, dissolved_oxygen:6, temperature:28, rainfall:150,
            humidity:68, population_density:1500, sanitation_index:55, bacterial_count:400,
            ecoli_count:45, chlorine_level:0.7, water_source:'River', region_type:'Semi-Urban',
            season:'Summer', previous_cases:18
          })}
        >⚡ Medium Risk Sample</button>
        <button
          id="btn-scenario-high"
          className="text-xs px-3 py-1.5 rounded-lg border border-red-500/30 text-red-400 hover:bg-red-500/10 transition-all"
          onClick={() => setFormData({
            ph:5.2, turbidity:80, dissolved_oxygen:3, temperature:36, rainfall:400,
            humidity:85, population_density:6000, sanitation_index:20, bacterial_count:2000,
            ecoli_count:200, chlorine_level:0.05, water_source:'Pond', region_type:'Rural',
            season:'Monsoon', previous_cases:60
          })}
        >🔴 High Risk Sample</button>
      </div>
    </div>
  )
}
