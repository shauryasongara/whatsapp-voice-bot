import os
import requests
from flask import Flask, request
from dotenv import load_dotenv
from wa_media import download_media, upload_media
from audio import ogg_to_wav, wav_to_ogg
from providers import transcribe_audio, gpt_reply, tts_generate

load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v20.0")

app = Flask(__name__)

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming:", data)

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]

        if "text" in message:
            text_in = message["text"]["body"]
            send_text(from_number, f"You said: {text_in}")

        elif message["type"] == "audio":
            media_id = message["audio"]["id"]
            local_ogg = download_media(media_id, WHATSAPP_TOKEN)
            wav_path = ogg_to_wav(local_ogg)

            transcript = transcribe_audio(wav_path)
            print("Transcript:", transcript)

            llm_reply = gpt_reply(transcript)
            wav_reply = tts_generate(llm_reply)
            ogg_reply = wav_to_ogg(wav_reply)
            media_id = upload_media(ogg_reply, WHATSAPP_TOKEN, PHONE_NUMBER_ID)

            send_audio(from_number, media_id)
            send_text(from_number, f"(Transcript: {transcript})")
    except Exception as e:
        print("Error:", e)

    return "ok", 200

def send_text(to, body):
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}",
               "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body[:1000]}
    }
    r = requests.post(url, headers=headers, json=payload)
    print("Text status:", r.status_code, r.text)

def send_audio(to, media_id):
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}",
               "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "audio",
        "audio": {"id": media_id}
    }
    r = requests.post(url, headers=headers, json=payload)
    print("Audio status:", r.status_code, r.text)

if __name__ == "__main__":
    app.run(port=8000, debug=True)
