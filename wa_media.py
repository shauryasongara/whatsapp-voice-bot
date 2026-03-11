import os
import uuid
import requests

GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v20.0")


def download_media(media_id, token):
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{media_id}"
    headers = {"Authorization": f"Bearer {token}"}

    meta_response = requests.get(url, headers=headers, timeout=30)
    meta_response.raise_for_status()

    meta_json = meta_response.json()
    media_url = meta_json.get("url")
    if not media_url:
        raise ValueError(f"No media URL returned from WhatsApp: {meta_json}")

    media_response = requests.get(media_url, headers=headers, timeout=60)
    media_response.raise_for_status()

    local_path = f"{uuid.uuid4()}.ogg"
    with open(local_path, "wb") as f:
        f.write(media_response.content)

    return local_path


def upload_media(file_path, token, phone_number_id):
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{phone_number_id}/media"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"messaging_product": "whatsapp"}

    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, headers=headers, files=files, data=data, timeout=60)

    response.raise_for_status()

    response_json = response.json()
    media_id = response_json.get("id")
    if not media_id:
        raise ValueError(f"No media ID returned from WhatsApp: {response_json}")

    return media_id
