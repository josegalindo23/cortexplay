/**
 * StimulusPanel — displays the stimulus corresponding to each modality
 * Video: video player
 * Audio: audio player with waveform indicator
 * Text: word-by-word display synchronized with timestep
 */
import VideoPlayer from '../VideoPlayer/VideoPlayer'

const API = 'http://localhost:8000'

export default function StimulusPanel({ modality, onTimeUpdate, onDurationChange, currentTime }) {
  if (modality === 'video' || modality === 'multimodal') {
    return (
      <div className="w-full h-full">
        <VideoPlayer
          src={`${API}/videos/big_buck_bunny_30s_video.mp4`}
          onTimeUpdate={onTimeUpdate}
          onDurationChange={onDurationChange}
        />
      </div>
    )
  }

  if (modality === 'audio') {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-black p-4 gap-4">
        <p className="text-gray-500 text-xs uppercase tracking-wider">Audio stimulus</p>
        <audio
          controls
          autoPlay
          loop
          className="w-full"
          onTimeUpdate={(e) => onTimeUpdate?.(Math.floor(e.target.currentTime))}
          onLoadedMetadata={(e) => onDurationChange?.(Math.floor(e.target.duration))}
        >
          <source src={`${API}/videos/big_buck_bunny_30s_audio.wav`} type="audio/wav" />
        </audio>
        {/* Waveform visualization */}
        <div className="flex items-end gap-0.5 h-12 w-full">
          {Array.from({length: 60}, (_, i) => (
            <div
              key={i}
              className="flex-1 rounded-sm transition-all duration-100"
              style={{
                height: `${20 + Math.sin(i * 0.5 + currentTime) * 15 + Math.random() * 10}%`,
                background: i / 60 < currentTime / 30 ? '#f97316' : '#374151'
              }}
            />
          ))}
        </div>
        <p className="text-gray-600 text-xs">{currentTime}s / 30s</p>
      </div>
    )
  }

  if (modality === 'text') {
    const sentences = [
      "A large rabbit emerges from a burrow",
      "in a meadow surrounded by tall trees.",
      "The rabbit looks around curiously",
      "at birds flying overhead.",
      "A squirrel watches from a nearby branch",
      "as butterflies flutter past.",
      "The rabbit stretches and yawns",
      "in the warm morning sunlight.",
      "Suddenly, three small creatures appear",
      "and begin to torment the rabbit.",
      "The rabbit devises a plan for revenge.",
    ]
    const currentSentence = sentences[Math.min(
      Math.floor(currentTime / (19 / sentences.length)),
      sentences.length - 1
    )]

    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-black p-6 gap-4">
        <p className="text-gray-500 text-xs uppercase tracking-wider">Text stimulus</p>
        <div className="rounded border border-gray-800 p-4 w-full min-h-16 flex items-center justify-center">
          <p className="text-white text-sm text-center leading-relaxed">
            {currentSentence}
          </p>
        </div>
        <div className="flex gap-1 w-full">
          {sentences.map((_, i) => (
            <div
              key={i}
              className="flex-1 h-1 rounded-full"
              style={{
                background: i <= Math.floor(currentTime / (19 / sentences.length))
                  ? '#f97316' : '#374151'
              }}
            />
          ))}
        </div>
        <p className="text-gray-600 text-xs">{currentTime}s / 19s</p>
      </div>
    )
  }

  return null
}