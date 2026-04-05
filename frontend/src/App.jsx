import { useState, useEffect, useCallback } from 'react'
import BrainViewer from './components/BrainViewer/BrainViewer'
import VideoPlayer from './components/VideoPlayer/VideoPlayer'
import TimeSeries from './components/TimeSeries/TimeSeries'
import ModalityToggle from './components/ModalityToggle/ModalityToggle'

const API = 'http://localhost:8000/api'
const CLIP_ID = 'big_buck_bunny_30s'
const HEMODYNAMIC_LAG = 5

export default function App() {
  const [surfaceData, setSurfaceData] = useState(null)
  const [activations, setActivations] = useState(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration]       = useState(30)
  const [loading, setLoading]         = useState(true)
  const [error, setError]             = useState(null)
  const [selectedRegion, setSelectedRegion] = useState(null)
  const [timeSeriesData, setTimeSeriesData] = useState(null)
  const [modality, setModality] = useState('video')

  const handleVertexClick = useCallback((vertexId) => {
  fetch(`${API}/brain/region/${vertexId}`)
    .then(r => r.json())
    .then(setSelectedRegion)

    fetch(`${API}/brain/timeseries?clip_id=${CLIP_ID}&vertex_id=${vertexId}`)
    .then(r => r.json())
    .then(setTimeSeriesData)
}, [])

  useEffect(() => {
    fetch(`${API}/brain/surface`)
      .then(r => r.json())
      .then(d => { setSurfaceData(d); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [])

  const fetchActivations = useCallback((t, mod = modality) => {
    const laggedT = Math.max(0, t - HEMODYNAMIC_LAG)
    fetch(`${API}/brain/activation?clip_id=${CLIP_ID}&modality=${mod}&t=${laggedT}`)
      .then(r => r.json())
      .then(d => setActivations(new Float32Array(d.activations)))
      .catch(e => console.error(e))
  }, [modality])

  const handleModalityChange = (mod) => {
  setModality(mod)
  fetchActivations(currentTime, mod)
  }

  useEffect(() => {
    if (!loading) fetchActivations(0)
  }, [loading, fetchActivations])

  const handleTimeUpdate = useCallback((t) => {
    setCurrentTime(t)
    fetchActivations(t)
  }, [fetchActivations])

  if (loading) return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <p className="text-gray-400">Loading brain geometry...</p>
    </div>
  )

  if (error) return (
    <div className="min-h-screen bg-black text-red-400 flex items-center justify-center">
      <p>Error: {error}</p>
    </div>
  )

  return (
    <div className="h-screen w-screen bg-black text-white flex flex-col overflow-hidden">

      {/* Header */}
      <header className="flex-none px-4 py-2 border-b border-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-base font-bold">🧠 CortexPlay</h1>
          <span className="text-gray-600 text-xs">TRIBE v2 — d'Ascoli et al., 2026</span>
        </div>
        <div className="flex items-center gap-4">
          <ModalityToggle value={modality} onChange={handleModalityChange} />
          <div className="text-xs text-gray-500 flex gap-3">
            <span>stimulus <span className="text-white">{currentTime}s</span></span>
            <span>brain <span className="text-orange-400">{Math.max(0, currentTime - HEMODYNAMIC_LAG)}s</span></span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 min-h-0 flex">

        {/* Brain viewer — left 65% */}
        <div className="flex-1 min-w-0">
          <BrainViewer surfaceData={surfaceData} activations={activations} onVertexClick={handleVertexClick} />
        </div>

        {/* Right panel — 35% */}
        <div className="w-80 flex-none border-l border-gray-800 flex flex-col">

          {/* Video player */}
          <div className="flex-none h-48 bg-black border-b border-gray-800">
            <VideoPlayer
              onTimeUpdate={handleTimeUpdate}
              onDurationChange={setDuration}
            />
          </div>

          {/* Timeline */}
          <div className="flex-none px-3 py-2 border-b border-gray-800">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-600">0s</span>
              <div className="flex-1 h-1 bg-gray-800 rounded-full">
                <div
                  className="h-1 bg-orange-500 rounded-full transition-all duration-500"
                  style={{ width: `${(currentTime / duration) * 100}%` }}
                />
              </div>
              <span className="text-xs text-gray-600">{duration}s</span>
            </div>
          </div>

          {/* Region info placeholder */}
          <div className="flex-1 p-3">
            <p className="text-xs text-gray-600 uppercase tracking-wider mb-2">Selected Region</p>
            <div className="rounded border border-gray-800 p-3">
              {selectedRegion ? (
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-white font-medium text-sm">{selectedRegion.name}</p>
                    <span className="text-xs text-gray-600">{selectedRegion.hemisphere}</span>
                  </div>
                  <p className="text-gray-400 text-xs mb-2">{selectedRegion.full_name}</p>
                  <span className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400">
                    {selectedRegion.network}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400 ml-1">
                    {selectedRegion.brodmann}
                  </span>
                  <p className="text-gray-500 text-xs mt-2 leading-relaxed">
                    {selectedRegion.description}
                  </p>
                </div>
              ) : (
                <p className="text-gray-500 text-xs">Click on a brain region to see clinical information</p>
              )}
            </div>

            <p className="text-xs text-gray-600 uppercase tracking-wider mt-4 mb-2">Activation Over Time</p>
            <div className="rounded border border-gray-800 p-2">
              <TimeSeries data={timeSeriesData} currentTime={currentTime} />
            </div>

            

            {/* Activation stats */}
            <p className="text-xs text-gray-600 uppercase tracking-wider mt-4 mb-2">Current Frame</p>
            <div className="grid grid-cols-2 gap-2">
              <div className="rounded border border-gray-800 p-2">
                <p className="text-gray-600 text-xs">time</p>
                <p className="text-white text-sm font-mono">{currentTime}s</p>
              </div>
              <div className="rounded border border-gray-800 p-2">
                <p className="text-gray-600 text-xs">brain t</p>
                <p className="text-orange-400 text-sm font-mono">{Math.max(0, currentTime - HEMODYNAMIC_LAG)}s</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}