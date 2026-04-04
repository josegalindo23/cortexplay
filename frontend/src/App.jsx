/**
 * CortexPlay — Main Application Component
 * 
 * Root component that orchestrates the brain visualizer layout.
 * Renders the 3D brain viewer synchronized with video playback.
 */

import { useState, useEffect, useCallback } from 'react'
import BrainViewer from './components/BrainViewer/BrainViewer'

const API = 'http://localhost:8000/api'
const CLIP_ID = 'big_buck_bunny_30s' // Example video ID, replace with actual
const HEMODYNAMIC_LAG = 5 // seconds — typical delay between neural activity and fMRI signal, from TRIBE v2 paper

function App() {
  const [surfaceData, setSurfaceData]     = useState(null)
  const [activations, setActivations]     = useState(null)
  const [currentTime, setCurrentTime]     = useState(0)
  const [nTimesteps, setNTimesteps]       = useState(30)
  const [loading, setLoading]             = useState(true)
  const [error, setError]                 = useState(null)

  useEffect(() => {
    // Load brain surface geometry once
    fetch(`${API}/brain/surface`)
      .then(res => res.json())
      .then(data => {
        setSurfaceData(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  // Load activations whenever currentTime changes
  // Apply hemodynamic lag: brain response lags stimulus by 5s
  const fetchActivations = useCallback((t) => {
    const laggedT = Math.max(0, t - HEMODYNAMIC_LAG)
    fetch(`${API}/brain/activation?clip_id=${CLIP_ID}&t=${laggedT}`)
      .then(res => res.json())
      .then(data => {
        setActivations(new Float32Array(data.activations))
        setNTimesteps(data.n_timesteps)
      })
      .catch(err => console.error('Activation fetch error:', err))
  }, [])

  // Fetch activations on mount
  useEffect(() => {
    if (!loading) fetchActivations(0)
  }, [loading, fetchActivations])

  // Auto-advance time every second (simulates video playback)
  useEffect(() => {
    if (loading) return
    const interval = setInterval(() => {
      setCurrentTime(t => {
        const next = (t + 1) % nTimesteps
        fetchActivations(next)
        return next
      })
    }, 1000)
    return () => clearInterval(interval)
  }, [loading, nTimesteps, fetchActivations])

  if (loading) return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        <div className="text-2xl mb-2">🧠</div>
        <p className="text-gray-400">Loading brain geometry...</p>
      </div>
    </div>
  )

  if (error) return (
    <div className="min-h-screen bg-black text-red-400 flex items-center justify-center">
      <p>Error: {error}</p>
    </div>
  )

  // return (
  //   <div className="h-screen w-screen bg-black text-white flex flex-col overflow-hidden">
  //     {/* Header */}
  //     <header className="flex-none p-3 border-b border-gray-800 flex items-center gap-3">
  //       <h1 className="text-lg font-bold">🧠 CortexPlay</h1>
  //       <span className="text-gray-600 text-xs">
  //         Powered by TRIBE v2 — d'Ascoli et al., 2026, Meta FAIR
  //       </span>
  //     </header>

  //     {/* Brain Viewer — takes all remaining space */}
  //     <main className="flex-1 min-h-0">
  //       <BrainViewer surfaceData={surfaceData} />
  //     </main>
  //   </div>
  //   )

  return (<div className="h-screen w-screen bg-black text-white flex flex-col overflow-hidden">
      {/* Header */}
      <header className="flex-none p-3 border-b border-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-bold">🧠 CortexPlay</h1>
          <span className="text-gray-600 text-xs hidden md:block">
            Powered by TRIBE v2 — d'Ascoli et al., 2026, Meta FAIR
          </span>
        </div>
        {/* Time indicator */}
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span>t = {currentTime}s</span>
          <span className="text-gray-700">|</span>
          <span className="text-orange-500">
            brain = {Math.max(0, currentTime - HEMODYNAMIC_LAG)}s
          </span>
          <span className="text-gray-700 text-xs" title="Hemodynamic lag">
            +{HEMODYNAMIC_LAG}s lag
          </span>
        </div>
      </header>

      {/* Brain Viewer */}
      <main className="flex-1 min-h-0">
        <BrainViewer
          surfaceData={surfaceData}
          activations={activations}
        />
      </main>

      {/* Timeline bar */}
      <footer className="flex-none p-3 border-t border-gray-800">
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-600 w-8">0s</span>
          <div className="flex-1 h-1 bg-gray-800 rounded-full relative">
            <div
              className="h-1 bg-orange-500 rounded-full transition-all duration-300"
              style={{ width: `${(currentTime / (nTimesteps - 1)) * 100}%` }}
            />
          </div>
          <span className="text-xs text-gray-600 w-8">{nTimesteps}s</span>
        </div>
      </footer>
    </div>
  )

}

export default App