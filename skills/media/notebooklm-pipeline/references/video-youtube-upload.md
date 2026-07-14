# NotebookLM Video → YouTube Upload Pipeline

## Akış

```
NotebookLM studio_create(video) → poll → download_artifact → YouTube Data API v3 upload
```

## Ön Koşul: YouTube OAuth Scope

NotebookLM videosunu YouTube'a yüklemek için Google OAuth token'ında `https://www.googleapis.com/auth/youtube.upload` scope'u OLMASI ZORUNLUDUR. Gmail/Calendar/Drive için alınan token'da bu scope YOKTUR — ayrıca eklenmesi gerekir.

**Kontrol:**
```bash
python3 -c "import json; d=json.load(open('$HOME/.hermes/google_token.json')); print('youtube.upload' in d.get('scope',''))"
```

False dönüyorsa → Google Cloud Console'da YouTube Data API v3'ü enable et → `$GSETUP --revoke` → yeniden OAuth (scope'a manuel `youtube.upload` ekle).

## Adım Adım

### 1. Video Artifact Oluştur
```python
studio_create(
    notebook_id=notebook_id,
    artifact_type="video",
    video_format="explainer",  # explainer | brief | cinematic
    language="tr",
    focus_prompt="Bu videoyu oluştururken: ...",
    confirm=True
)
```

### 2. Poll ve İndir
```python
# Video deep_dive ~15-25 dk sürebilir
studio_status(notebook_id)  # completed olunca

download_artifact(
    notebook_id=notebook_id,
    artifact_type="video",
    output_path="/home/ubuntu/.hermes/video_cache/bardo_video.mp4",
    artifact_id="..."
)
```

### 3. YouTube'a Yükle
```python
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

TOKEN = json.load(open(os.path.expanduser('~/.hermes/google_token.json')))
creds = Credentials.from_authorized_user_info(TOKEN, ['https://www.googleapis.com/auth/youtube.upload'])
youtube = build('youtube', 'v3', credentials=creds)

body = {
    'snippet': {
        'title': 'Video Title',
        'description': 'Bardo Psikoloji — AI ile backlink stratejisi',
        'tags': ['psikoloji', 'SEO'],
        'categoryId': '27'  # Education
    },
    'status': {'privacyStatus': 'unlisted'}
}

media = MediaFileUpload('/home/ubuntu/.hermes/video_cache/bardo_video.mp4', chunksize=-1, resumable=True)
request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
response = request.execute()
print(f"Uploaded: https://youtube.com/watch?v={response['id']}")
```

## Pitfalls

- **Token scope yoksa 403:** OAuth sırasında YouTube Data API v3 scope'u istenmemişse yükleme başarısız olur. Token'ı revoke edip yeniden auth al.
- **Scope yenilemeyle EKLENMEZ (1 Haz 2026):** refresh_google_token.sh sadece access token'ı yeniler, scope'u DEĞİŞTİRMEZ. İlk OAuth onayında hangi scope'lar verildiyse onlar kalır. youtube.upload yoksa → GSETUP --revoke → sıfırdan OAuth (scope'a manuel youtube.upload ekleyerek). Refresh sonrası scope hala boşsa sorun refresh'te değil, ilk OAuth'tadır.
- **Scope boş görünüyorsa:** Token JSON'ında scope alanı boş string olabilir — bu tüm scope'ların eksik olduğu anlamına gelir. Çözüm: GSETUP --revoke + yeniden OAuth.
- **ALL_PROXY kuralı:** Google API çağrılarında ALL_PROXY="" zorunlu — WARP SOCKS5 Google'ı bloklar.
- **Video dosyası büyükse:** chunksize=-1 + resumable=True ile parçalı yükleme.
- **Kategori ID:** 27 = Education, 22 = People & Blogs. Tam liste: youtube.videoCategories().list(part='snippet', regionCode='TR').execute()
- **Privacy:** unlisted → sadece linki olanlar görür. Backlink için ideal.
