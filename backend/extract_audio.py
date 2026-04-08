"""Extract audio from video clip for TRIBE v2 audio-only prediction."""
from moviepy import VideoFileClip
from pathlib import Path

VIDEO = Path("./test_video_30s.mp4")
OUTPUT = Path("./data/videos/big_buck_bunny_30s.wav")
OUTPUT.parent.mkdir(exist_ok=True)

clip = VideoFileClip(str(VIDEO))
clip.audio.write_audiofile(str(OUTPUT))
clip.close()
print(f"Saved: {OUTPUT}")