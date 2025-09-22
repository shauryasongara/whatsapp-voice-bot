import subprocess
import uuid

def ogg_to_wav(ogg_path):
    wav_path = f"{uuid.uuid4()}.wav"
    subprocess.run(["ffmpeg", "-y", "-i", ogg_path, wav_path], check=True)
    return wav_path

def wav_to_ogg(wav_path):
    ogg_path = f"{uuid.uuid4()}.ogg"
    subprocess.run(["ffmpeg", "-y", "-i", wav_path, "-c:a", "libopus", ogg_path], check=True)
    return ogg_path
