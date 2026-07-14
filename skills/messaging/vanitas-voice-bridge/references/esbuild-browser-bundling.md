# esbuild ile NPM Paketlerini Browser Bundle'a Çevirme

## Ne Zaman Kullanılır

Bir NPM paketini vanilla HTML/JS frontend'inde kullanmak istediğinde ama:
- Paketin **UMD build'i yok** (sadece ESM/CJS)
- CDN'den yüklemek çalışmıyor (404, global değişken bulunamadı)
- `type="module"` import'u çalışmıyor veya uygun değil

## Workflow

### 1. Wrapper Dosyası Oluştur

```javascript
// wrapper.js — import et + global'e ata
import { SonioxClient } from '@soniox/client';
window.SonioxClient = SonioxClient;
```

### 2. esbuild ile Bundle

```bash
npx esbuild wrapper.js --bundle --outfile=public/soniox-bundle.js
```

- `--bundle`: tüm bağımlılıkları tek dosyaya toplar
- `--outfile`: çıktı dosyası
- İsteğe bağlı: `--minify` (production için)
- İsteğe bağlı: `--sourcemap` (debug için)

### 3. HTML'e Ekle

```html
<script src="soniox-bundle.js"></script>
```

Bundle sonrası `window.SonioxClient` global'de kullanılabilir.

## Neden CDN Çalışmaz

Bazı NPM paketleri (`@soniox/client`, `@anthropic-ai/sdk` gibi) sadece Node.js/bundler hedeflidir:

| Format | Açıklama | Browser'da? |
|--------|----------|-------------|
| ESM (`.mjs`) | ES Module import/export | `type="module"` ile çalışır ama paket bağımlılıkları yoksa kırılır |
| CJS (`.cjs`) | CommonJS require/module.exports | ❌ Tarayıcıda çalışmaz |
| UMD (`.umd.js`) | Universal Module Definition | ✅ CDN script tag ile çalışır |

Bu paketlerin `package.json`'ında `"unpkg"` veya `"jsdelivr"` alanı yoksa, CDN'den UMD gelmez.

## Proje Yapısı

```
vanitas-web/
├── public/
│   ├── index.html
│   └── soniox-bundle.js    ← build çıktısı (gitignore)
├── node_modules/            ← npm install
├── wrapper.js               ← esbuild giriş noktası
├── server.mjs
└── package.json
```

## Notlar

- Bundle boyutu: `@soniox/client` için ~74KB
- esbuild çok hızlı (~7ms), CI/CD'de veya development'ta rahatça kullanılabilir
- Build'i tekrarlamak için `npm run build` script'i eklenebilir
- Herhangi bir NPM paketi için aynı yöntem geçerli
