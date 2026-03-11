import os
import logging
from flask import Flask, request, jsonify
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    data = request.get_json(silent=True) or {}
    logger.info("Incoming webhook received")

    try:
        entries = data.get("entry", [])

        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])

                for message in messages:
                    process_message(message)

    except Exception:
        logger.exception("Unexpected error while processing webhook")

    return "ok", 200


def process_message(message):
    from_number = message.get("from")
    msg_type = message.get("type")

    if not from_number:
        logger.warning("Skipping message with no sender: %s", message)
        return

    logger.info("Processing message from %s of type %s", from_number, msg_type)

    try:
        if msg_type == "text":
            handle_text_message(from_number, message)

        elif msg_type == "audio":
            handle_audio_message(from_number, message)

        else:
            logger.info("Unsupported message type: %s", msg_type)
            send_text(from_number, f"Sorry, I don't support '{msg_type}' messages yet.")

    except Exception:
        logger.exception("Failed to process message from %s", from_number)
        send_text(from_number, "Sorry, something went wrong while processing your message.")


def handle_text_message(from_number, message):
    text_obj = message.get("text", {})
    text_in = text_obj.get("body", "").strip()

    if not text_in:
        send_text(from_number, "I received an empty text message.")
        return

    # For now: AI reply instead of echo
    reply = gpt_reply(text_in)
    send_text(from_number, reply)


def handle_audio_message(from_number, message):
    audio_obj = message.get("audio", {})
    media_id = audio_obj.get("id")

    if not media_id:
        raise ValueError("Audio message missing media ID")

    local_ogg = None
    wav_input = None
    wav_reply = None
    ogg_reply = None

    try:
        local_ogg = download_media(media_id, WHATSAPP_TOKEN)
        wav_input = ogg_to_wav(local_ogg)

        transcript = transcribe_audio(wav_input)
        logger.info("Transcript: %s", transcript)

        llm_reply = gpt_reply(transcript)
        wav_reply = tts_generate(llm_reply)
        ogg_reply = wav_to_ogg(wav_reply)

        uploaded_media_id = upload_media(ogg_reply, WHATSAPP_TOKEN, PHONE_NUMBER_ID)

        send_audio(from_number, uploaded_media_id)
        send_text(from_number, f"(Transcript: {transcript})")

    finally:
        cleanup_files(local_ogg, wav_input, wav_reply, ogg_reply)


def cleanup_files(*paths):
    for path in paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
                logger.info("Deleted temp file: %s", path)
            except Exception:
                logger.exception("Failed to delete temp file: %s", path)


def send_text(to, body):
    import requests

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body[:1000]}
    }

    r = requests.post(url, headers=headers, json=payload, timeout=30)
    try:
        r.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to send text. Response: %s", r.text)
        raise

    logger.info("Text status: %s %s", r.status_code, r.text)


def send_audio(to, media_id):
    import requests

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "audio",
        "audio": {"id": media_id}
    }

    r = requests.post(url, headers=headers, json=payload, timeout=30)
    try:
        r.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to send audio. Response: %s", r.text)
        raise

    logger.info("Audio status: %s %s", r.status_code, r.text)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
