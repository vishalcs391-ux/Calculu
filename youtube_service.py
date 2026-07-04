"""
YouTube -> transcript extraction. Uses the public transcript API (no API key
needed for captions). Falls back to raising a clear error if no captions exist.
"""
import re
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Could not parse a YouTube video ID from that URL.")


def extract_transcript(url: str) -> str:
    video_id = extract_video_id(url)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        raise ValueError(f"No transcript/captions available for this video: {e}")
    return " ".join(chunk["text"] for chunk in transcript)
