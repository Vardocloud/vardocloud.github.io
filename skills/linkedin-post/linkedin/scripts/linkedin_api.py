#!/usr/bin/env python3
"""
LinkedIn API istemcisi — token yönetimi ve post oluşturma.
Bardo Psychology için Edel'in LinkedIn hesabı.
"""
import json
import os
import sys
import requests
from datetime import datetime, timedelta

CONFIG_DIR = os.path.expanduser("~/.hermes/secrets")
TOKEN_FILE = os.path.join(CONFIG_DIR, "linkedin_token.json")
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "linkedin.env")

API_BASE = "https://api.linkedin.com/v2"


def _load_credentials():
    """Read credentials from linkedin.env only — no hardcoded fallback."""
    if not os.path.exists(CREDENTIALS_FILE):
        raise RuntimeError(
            f"linkedin.env bulunamadı: {CREDENTIALS_FILE}. "
            "Kopyalamak için: cp ~/.hermes/secrets/linkedin.env.example "
            "~/.hermes/secrets/linkedin.env"
        )
    creds = {}
    with open(CREDENTIALS_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                creds[k.strip()] = v.strip()
    cid = creds.get("LINKEDIN_CLIENT_ID")
    csec = creds.get("LINKEDIN_CLIENT_SECRET")
    if not cid or not csec:
        raise RuntimeError("linkedin.env'de LINKEDIN_CLIENT_ID veya LINKEDIN_CLIENT_SECRET eksik")
    return cid, csec


def _load_token() -> dict | None:
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return None


def _save_token(data: dict):
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    data["_refreshed_at"] = datetime.now().isoformat()
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(TOKEN_FILE, 0o600)


def refresh_access_token() -> str:
    token_data = _load_token()
    if not token_data or "refresh_token" not in token_data:
        raise ValueError("Refresh token bulunamadı. Manuel OAuth gerekli.")
    cid, csec = _load_credentials()
    resp = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "refresh_token",
            "refresh_token": token_data["refresh_token"],
            "client_id": cid,
            "client_secret": csec,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Token yenileme başarısız ({resp.status_code}): {resp.text}")
    new_data = resp.json()
    if "refresh_token" not in new_data:
        new_data["refresh_token"] = token_data["refresh_token"]
    new_data["person_urn"] = token_data.get("person_urn")
    new_data["name"] = token_data.get("name")
    _save_token(new_data)
    return new_data["access_token"]


def get_access_token() -> str:
    token_data = _load_token()
    if not token_data:
        raise ValueError("Token bulunamadı.")
    refreshed_at = token_data.get("_refreshed_at")
    if refreshed_at:
        last = datetime.fromisoformat(refreshed_at)
        if datetime.now() - last > timedelta(days=50):
            return refresh_access_token()
    test_resp = requests.get(
        f"{API_BASE}/userinfo",
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
        timeout=10,
    )
    if test_resp.status_code == 401:
        return refresh_access_token()
    return token_data["access_token"]


def create_post(text: str, visibility: str = "PUBLIC") -> dict:
    token_data = _load_token()
    if not token_data or "person_urn" not in token_data:
        raise ValueError("Person URN bulunamadı.")
    access_token = get_access_token()
    person_urn = token_data["person_urn"]
    body = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": visibility,
        },
    }
    resp = requests.post(
        f"{API_BASE}/ugcPosts",
        json=body,
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202505",
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    if resp.status_code == 201:
        post_id = resp.headers.get("X-RestLi-Id") or resp.json().get("id", "unknown")
        return {"success": True, "id": post_id, "text": text[:100] + "..."}
    else:
        return {"success": False, "status": resp.status_code, "error": resp.text[:300]}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python3 linkedin_api.py <post|refresh|status> [post metni]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "refresh":
        token = refresh_access_token()
        print(f"✅ Token yenilendi: {token[:30]}...")
    elif cmd == "status":
        token_data = _load_token()
        if token_data:
            print(f"✅ Token mevcut")
            print(f"   Person: {token_data.get('name', 'Bilinmiyor')}")
            print(f"   URN: {token_data.get('person_urn', '?')}")
            print(f"   Scope: {token_data.get('scope', '?')}")
            print(f"   expires_in: {token_data.get('expires_in', '?')}s")
            print(f"   Son yenileme: {token_data.get('_refreshed_at', '?')}")
        else:
            print("❌ Token yok.")
    elif cmd == "post":
        # --image opsiyonunu ayıkla
        image_path = None
        text_parts = []
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--image" and i + 1 < len(args):
                image_path = args[i + 1]
                i += 2
            else:
                text_parts.append(args[i])
                i += 1
        text = " ".join(text_parts) if text_parts else "Test post from Bardo API 🤖"
        result = create_post(text, image_path=image_path)
        if result["success"]:
            print(f"✅ Post atıldı: {result['id']}")
        else:
            print(f"❌ Hata: {result}")
            sys.exit(1)
    else:
        print(f"Bilinmeyen komut: {cmd}")
        sys.exit(1)
