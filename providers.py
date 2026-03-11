import os
import uuid
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def transcribe_audio(wav_path):
    try:
        with open(wav_path, "rb") as f:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        return transcript.text
    except Exception as e:
        raise RuntimeError(f"Transcription failed: {e}") from e


def gpt_reply(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Chat reply generation failed: {e}") from e


def tts_generate(text):
    wav_path = f"{uuid.uuid4()}.wav"
    try:
        response = openai.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text
        )
        with open(wav_path, "wb") as f:
            f.write(response.content)
        return wav_path
    except Exception as e:
        raise RuntimeError(f"TTS generation failed: {e}") from e
