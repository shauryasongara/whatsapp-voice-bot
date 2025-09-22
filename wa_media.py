import requests
import os
import uuid

GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v20.0")

def download_media(media_id, token):
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{media_id}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers).json()
    media_url = r["url"]

    r = requests.get(media_url, headers=headers)
    local_path = f"{uuid.uuid4()}.ogg"
    with open(local_path, "wb") as f:
        f.write(r.content)
    return local_path

def upload_media(file_path, token, phone_number_id):
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{phone_number_id}/media"
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": open(file_path, "rb")}
    data = {"messaging_product": "whatsapp"}
    r = requests.post(url, headers=headers, files=files, data=data).json()
    return r["id"]
