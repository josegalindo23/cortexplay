/**
 * ModalityToggle — switches between stimulus modalities
 * Changes which brain regions are highlighted
 */
const MODALITIES = [
  { id: 'video',      label: 'Video',      color: 'text-orange-400' },
  { id: 'audio',      label: 'Audio',      color: 'text-blue-400'   },
  { id: 'text',       label: 'Text',       color: 'text-green-400'  },
  { id: 'multimodal', label: 'Multimodal', color: 'text-purple-400' },
]

export default function ModalityToggle({ value, onChange }) {
  return (
    <div className="flex gap-1">
      {MODALITIES.map(m => (
        <button
          key={m.id}
          onClick={() => onChange(m.id)}
          className={`px-3 py-1 text-xs rounded border transition-all ${
            value === m.id
              ? `border-gray-500 bg-gray-800 ${m.color}`
              : 'border-gray-800 text-gray-600 hover:text-gray-400'
          }`}
        >
          {m.label}
        </button>
      ))}
    </div>
  )
}