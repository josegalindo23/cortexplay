/**
 * RGBMap — multimodal integration visualization
 * Reproduces Figure 7 from d'Ascoli et al., 2026
 * R = video response, G = audio response, B = text response
 */
export default function RGBMap({ activations }) {
  if (!activations) return (
    <p className="text-gray-600 text-xs">Waiting for activation data...</p>
  )

  // Approximate modality zones based on cortical anatomy
  const n = activations.length
  const visual  = activations.slice(0, Math.floor(n * 0.15))
  const auditory = activations.slice(Math.floor(n * 0.22), Math.floor(n * 0.30))
  const language = activations.slice(Math.floor(n * 0.30), Math.floor(n * 0.40))

  const mean = arr => arr.reduce((a, b) => a + b, 0) / arr.length
  const norm = v => Math.min(1, Math.max(0, (v + 1.2) / 2.4))

  const r = norm(mean(Array.from(visual)))
  const g = norm(mean(Array.from(auditory)))
  const b = norm(mean(Array.from(language)))

  const toHex = v => Math.round(v * 255).toString(16).padStart(2, '0')
  const color = `#${toHex(r)}${toHex(g)}${toHex(b)}`

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded" style={{ background: color }} />
        <div className="text-xs text-gray-500">
          <p>integrated response</p>
          <p className="font-mono text-gray-400">{color}</p>
        </div>
      </div>
      <div className="space-y-1">
        {[
          { label: 'R  video',  value: r, color: 'bg-red-500'   },
          { label: 'G  audio',  value: g, color: 'bg-green-500' },
          { label: 'B  text',   value: b, color: 'bg-blue-500'  },
        ].map(({ label, value, color: bc }) => (
          <div key={label} className="flex items-center gap-2">
            <span className="text-xs text-gray-600 w-14 font-mono">{label}</span>
            <div className="flex-1 h-1.5 bg-gray-800 rounded-full">
              <div className={`h-1.5 rounded-full ${bc}`} style={{ width: `${value * 100}%` }} />
            </div>
            <span className="text-xs text-gray-600 w-8 text-right">{Math.round(value * 100)}%</span>
          </div>
        ))}
      </div>
      <p className="text-gray-700 text-xs">Fig. 7 — d'Ascoli et al., 2026</p>
    </div>
  )
}