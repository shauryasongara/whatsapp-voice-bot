import subprocess
import uuid


def ogg_to_wav(ogg_path):
    wav_path = f"{uuid.uuid4()}.wav"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", ogg_path, wav_path],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg ogg_to_wav failed: {e.stderr}") from e
    return wav_path


def wav_to_ogg(wav_path):
    ogg_path = f"{uuid.uuid4()}.ogg"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", wav_path, "-c:a", "libopus", ogg_path],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg wav_to_ogg failed: {e.stderr}") from e
    return ogg_path
