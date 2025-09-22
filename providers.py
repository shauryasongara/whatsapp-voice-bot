import openai
import os
import uuid

openai.api_key = os.getenv("OPENAI_API_KEY")

def transcribe_audio(wav_path):
    with open(wav_path, "rb") as f:
        transcript = openai.audio.transcriptions.create(model="whisper-1", file=f)
    return transcript.text

def gpt_reply(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def tts_generate(text):
    wav_path = f"{uuid.uuid4()}.wav"
    response = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )
    with open(wav_path, "wb") as f:
        f.write(response.content)
    return wav_path
