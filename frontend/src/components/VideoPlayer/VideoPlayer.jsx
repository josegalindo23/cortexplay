/**
 * VideoPlayer — synchronized video player component
 * Emits current time to parent for brain synchronization
 */
import { useRef, useEffect } from 'react'

export default function VideoPlayer({ onTimeUpdate, onDurationChange }) {
  const videoRef = useRef()

  useEffect(() => {
    const video = videoRef.current
    if (!video) return
    const handleTime = () => onTimeUpdate?.(Math.floor(video.currentTime))
    const handleDuration = () => onDurationChange?.(Math.floor(video.duration))
    video.addEventListener('timeupdate', handleTime)
    video.addEventListener('loadedmetadata', handleDuration)
    return () => {
      video.removeEventListener('timeupdate', handleTime)
      video.removeEventListener('loadedmetadata', handleDuration)
    }
  }, [onTimeUpdate, onDurationChange])

  return (
    <video
      ref={videoRef}
      src="http://localhost:8000/videos/big_buck_bunny_30s_video.mp4"
      controls
      autoPlay
      loop
      className="w-full h-full object-contain"
    />
  )
}