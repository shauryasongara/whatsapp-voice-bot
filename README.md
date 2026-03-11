# WhatsApp Voice AI Bot

A Flask-based WhatsApp bot that can receive **text and voice messages**, process them with **OpenAI models**, and respond with **AI-generated audio replies**.

The bot integrates with the **WhatsApp Cloud API** through a webhook. When a user sends a voice message, the system transcribes the audio, generates a response using a language model, converts the response back into speech, and sends the audio reply to the user.

---

# Features

* Receive messages from WhatsApp via webhook
* Support for **text messages**
* Support for **voice messages**
* Speech-to-text transcription using OpenAI Whisper
* AI-generated responses using a language model
* Text-to-speech generation for audio replies
* Automatic conversion between audio formats (OGG ↔ WAV)
* Temporary file cleanup after processing
* Improved error handling and logging

---

# How It Works

## Text Message Flow

1. A user sends a text message to the WhatsApp number.
2. WhatsApp sends a webhook event to the server.
3. The server extracts the message text.
4. The text is sent to the AI model.
5. The AI response is returned as a text message.

---

## Voice Message Flow

1. A user sends a voice message to WhatsApp.
2. WhatsApp sends a webhook event containing the audio media ID.
3. The bot downloads the audio file from WhatsApp.
4. The audio is converted from **OGG → WAV** using FFmpeg.
5. OpenAI Whisper transcribes the speech to text.
6. The transcript is sent to an AI model to generate a reply.
7. The reply text is converted into speech using OpenAI TTS.
8. The generated speech is converted from **WAV → OGG**.
9. The audio file is uploaded back to WhatsApp.
10. The bot sends the audio reply to the user.
11. The transcript is optionally sent as a text message.

---

# Project Structure

```
project/
│
├── app.py
├── audio.py
├── providers.py
├── wa_media.py
├── .env
└── README.md
```

## `app.py`

Main Flask application that:

* Handles WhatsApp webhook verification
* Receives incoming messages
* Routes messages to the correct processing logic
* Sends replies back to WhatsApp

---

## `audio.py`

Handles audio conversion using **FFmpeg**.

Functions:

* `ogg_to_wav()` – converts WhatsApp audio to WAV
* `wav_to_ogg()` – converts generated audio back to OGG

These conversions are required because transcription and TTS services typically operate on WAV files.

---

## `providers.py`

Handles all interactions with **OpenAI services**.

Functions:

* `transcribe_audio()` – speech-to-text using Whisper
* `gpt_reply()` – generates AI responses
* `tts_generate()` – converts text responses into speech

---

## `wa_media.py`

Handles media interactions with the **WhatsApp Cloud API**.

Functions:

* `download_media()` – downloads audio from WhatsApp
* `upload_media()` – uploads generated audio files

---

# Requirements

## Python

Python **3.9+** recommended.

Required packages:

```
flask
requests
python-dotenv
openai
```

Install them with:

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```
flask
requests
python-dotenv
openai
```

---

## FFmpeg

The project requires **FFmpeg** for audio conversion.

Install:

Mac:

```
brew install ffmpeg
```

Ubuntu:

```
sudo apt install ffmpeg
```

Windows:
Download from:
https://ffmpeg.org/download.html

---

# Environment Variables

Create a `.env` file in the project root.

Example:

```
VERIFY_TOKEN=your_verify_token
WHATSAPP_TOKEN=your_whatsapp_cloud_api_token
PHONE_NUMBER_ID=your_whatsapp_phone_number_id
GRAPH_API_VERSION=v20.0
OPENAI_API_KEY=your_openai_api_key
```

### Variables Explained

| Variable          | Description                      |
| ----------------- | -------------------------------- |
| VERIFY_TOKEN      | Token used to verify the webhook |
| WHATSAPP_TOKEN    | WhatsApp Cloud API access token  |
| PHONE_NUMBER_ID   | WhatsApp phone number ID         |
| GRAPH_API_VERSION | Meta Graph API version           |
| OPENAI_API_KEY    | API key for OpenAI services      |

---

# Running the Server

Start the Flask server:

```bash
python app.py
```

The server will start on:

```
http://localhost:8000
```

---

# Webhook Setup

Configure your WhatsApp Cloud API webhook to point to:

```
https://your-server-domain/webhook
```

Verification will be performed using the `VERIFY_TOKEN`.

---

# Error Handling Improvements

The application includes improved robustness:

* Safe handling of webhook payloads
* Logging for debugging
* Network timeouts for API calls
* Validation of API responses
* Automatic cleanup of temporary audio files

---

# Summary

This project demonstrates how to build a **WhatsApp voice assistant** by combining:

* WhatsApp Cloud API
* OpenAI speech and language models
* Flask webhooks
* Audio processing with FFmpeg

It provides a simple foundation for building more advanced conversational AI systems on messaging platforms.
