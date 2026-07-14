#!/usr/bin/env python3
"""
Vanitas Podcast Fabrikası — AI Podcast Üretim Aracı

Konu + Hedef Kitle + Süre → Podcast paketi (plan + diyalog)

Kullanım:
  python3 podcast_fabrikasi.py --konu "Bilinç Akışı" --hedef-kitle "üniversite öğrencileri" --sure 8
  python3 podcast_fabrikasi.py --konu "Sibernetik Bilinç" --hedef-kitle "teknoloji meraklıları" --sure 10 --output-dir ./cikti
  python3 podcast_fabrikasi.py --help
"""

import argparse
import json
import os
import sys
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path


# ─── Constants ────────────────────────────────────────────────────────────────

ZEN_API_URL = "https://opencode.ai/zen/v1/chat/completions"
ZEN_MODEL = "mimo-v2.5-free"

POLLINATIONS_API_URL = "http://127.0.0.1:19999/v1/chat/completions"
POLLINATIONS_MODEL = "gpt-5.4-mini"

DEFAULT_OUTPUT_DIR = "output"

# ─── Helpers ──────────────────────────────────────────────────────────────────


def eprint(*args, **kwargs):
    """Print to stderr for status messages."""
    print(*args, file=sys.stderr, **kwargs)


def run_jq_curl(
    api_url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> dict:
    """
    Build a JSON payload via jq (Turkish-safe) and send via curl.
    Returns parsed JSON response.
    """
    # Build the jq payload inline
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens

    # Write payload to temp file for curl -d @-
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f, ensure_ascii=False)
        tmp_path = f.name

    try:
        cmd = [
            "curl", "-s", "-X", "POST",
            api_url,
            "-H", "Content-Type: application/json",
            "-d", f"@{tmp_path}",
        ]
        eprint(f"  🔄 API çağrısı: {api_url} (model: {model})")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            raise RuntimeError(f"curl failed (exit {result.returncode}): {result.stderr}")

        response = json.loads(result.stdout)

        # Check for API-level errors
        if "error" in response:
            raise RuntimeError(f"API error: {response['error']}")

        return response
    finally:
        os.unlink(tmp_path)


def extract_content(response: dict) -> str:
    """Extract message content from OpenAI-compatible response."""
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Beklenmeyen API yanıt formatı: {e}\nYanıt: {json.dumps(response, indent=2, ensure_ascii=False)[:500]}")


def safe_filename(text: str, max_len: int = 60) -> str:
    """Convert text to safe filename."""
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in text)
    safe = safe.strip().replace(" ", "_")
    return safe[:max_len]


# ─── Stage 1: İçerik Planlayıcı ──────────────────────────────────────────────


def stage1_plan(konu: str, hedef_kitle: str, sure_dk: int) -> dict:
    """
    Aşama 1: Zen API (mimo-v2.5-free) ile podcast akış planı al.
    Returns parsed JSON plan.
    """
    eprint(f"\n📋 AŞAMA 1: İçerik Planlayıcı")
    eprint(f"   Konu: {konu}")
    eprint(f"   Hedef Kitle: {hedef_kitle}")
    eprint(f"   Hedef Süre: {sure_dk} dk")

    system_prompt = (
        "Sen bir podcast yapımcısısın. Verilen konu için JSON formatında "
        "podcast akış planı çıkar. Sadece JSON dön, açıklama ekleme."
    )

    user_prompt = (
        f"KONU: {konu}\n"
        f"HEDEF KİTLE: {hedef_kitle}\n"
        f"HEDEF SÜRE: {sure_dk} dakika\n\n"
        f"JSON formatında dön: "
        f'{{"podcast_adi", "host1": {{"isim", "rol", "ton"}}, '
        f'"host2": {{"isim", "rol", "ton"}}, '
        f'"ortam", '
        f'"bolumler": [{{"baslik", "sure_dk", "ana_noktalar": []}}]}}'
    )

    response = run_jq_curl(
        api_url=ZEN_API_URL,
        model=ZEN_MODEL,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.7,
    )

    content = extract_content(response)

    # Try to parse JSON from the response
    # The model might wrap JSON in markdown code blocks
    content_stripped = content.strip()
    if "```json" in content_stripped:
        content_stripped = content_stripped.split("```json", 1)[1]
        if "```" in content_stripped:
            content_stripped = content_stripped.split("```", 1)[0]
    elif "```" in content_stripped:
        content_stripped = content_stripped.split("```", 1)[1]
        if "```" in content_stripped:
            content_stripped = content_stripped.split("```", 1)[0]

    content_stripped = content_stripped.strip()

    try:
        plan = json.loads(content_stripped)
    except json.JSONDecodeError:
        eprint("  ⚠️ JSON parse hatası, ham yanıt kaydediliyor.")
        plan = {"raw_response": content_stripped}

    eprint(f"  ✅ Plan alındı: {plan.get('podcast_adi', 'İsimsiz Podcast')}")
    return plan


# ─── Stage 2: Diyalog Yazarı ────────────────────────────────────────────────


def stage2_dialog(plan: dict, sure_dk: int) -> str:
    """
    Aşama 2: Pollinations (gpt-5.4-mini) ile doğal Türkçe diyalog yaz.
    Returns dialog text.
    """
    eprint(f"\n✍️  AŞAMA 2: Diyalog Yazarı")
    eprint(f"   Hedef Süre: {sure_dk} dk")

    plan_json = json.dumps(plan, ensure_ascii=False, indent=2)

    # Estimate word count: ~125 words per minute for Turkish podcast
    kelime_sayisi = sure_dk * 125

    system_prompt = (
        "Sen bir podcast diyalog yazarısın. Verilen podcast planını kullanarak "
        "doğal, akıcı bir Türkçe karşılıklı konuşma metni yaz."
    )

    user_prompt = (
        f"PODCAST PLANI:\n{plan_json}\n\n"
        f"YAZIM KURALLARI:\n"
        f"- Her hostun ayrı ses tonu ve karakteri olmalı\n"
        f"- Doğal geçişler, espriler, \"aa gerçekten mi?\" anları ekle\n"
        f"- Hedef süre: ~{sure_dk} dakika (yaklaşık {kelime_sayisi} kelime)\n"
        f"- Akademik kavramları günlük dille açıkla\n"
        f"- Host1 (uzman): derinlemesine bilgi verir, sakin ve açıklayıcı\n"
        f"- Host2 (meraklı): sorular sorar, şaşırır, basitleştirilmesini ister\n\n"
        f"FORMAT:\n"
        f"Her satır \"Host1:\" veya \"Host2:\" ile başlasın.\n"
        f"Konuşma akışı: Giriş selamı → 3 bölüm → Kapanış"
    )

    response = run_jq_curl(
        api_url=POLLINATIONS_API_URL,
        model=POLLINATIONS_MODEL,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.8,
        max_tokens=2048,
    )

    content = extract_content(response)
    eprint(f"  ✅ Diyalog yazıldı ({len(content.split())} kelime)")
    return content


# ─── Output ───────────────────────────────────────────────────────────────────


def save_output(output_dir: Path, plan: dict, dialog: str, konu: str):
    """Save all output files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    konu_slug = safe_filename(konu)

    # Create output directories
    output_dir = Path(output_dir)
    paket_dir = output_dir / "podcast_paketi"
    output_dir.mkdir(parents=True, exist_ok=True)
    paket_dir.mkdir(parents=True, exist_ok=True)

    # Save plan
    plan_file = output_dir / "plan.json"
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    eprint(f"  📄 Plan kaydedildi: {plan_file}")

    # Save dialog
    dialog_file = output_dir / "diyalog.txt"
    with open(dialog_file, "w", encoding="utf-8") as f:
        f.write(dialog)
    eprint(f"  📄 Diyalog kaydedildi: {dialog_file}")

    # Save timestamped package
    paket_plan = paket_dir / f"plan_{timestamp}_{konu_slug}.json"
    paket_dialog = paket_dir / f"diyalog_{timestamp}_{konu_slug}.txt"

    # Copy or symlink
    with open(paket_plan, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    with open(paket_dialog, "w", encoding="utf-8") as f:
        f.write(dialog)

    eprint(f"  📦 Paket: {paket_dir}/")

    # Summary
    podcast_adi = plan.get("podcast_adi", konu)
    host1 = plan.get("host1", {}).get("isim", "Host1")
    host2 = plan.get("host2", {}).get("isim", "Host2")

    print("\n" + "=" * 60)
    print(f"🎙️  PODCAST HAZIR!")
    print(f"   Adı: {podcast_adi}")
    print(f"   Hostlar: {host1} & {host2}")
    print(f"   Ortam: {plan.get('ortam', 'Belirtilmemiş')}")
    if "bolumler" in plan:
        print(f"   Bölümler:")
        for b in plan["bolumler"]:
            print(f"     • {b.get('baslik', '?')} ({b.get('sure_dk', '?')} dk)")
    print(f"   Çıktılar:")
    print(f"     • Plan: {plan_file}")
    print(f"     • Diyalog: {dialog_file}")
    print(f"     • Paket: {paket_dir}/")
    print("=" * 60)


# ─── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Vanitas Podcast Fabrikası — AI Podcast Üretim Aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnek kullanım:
  python3 %(prog)s --konu "Bilinç Akışı" --hedef-kitle "üniversite öğrencileri" --sure 8
  python3 %(prog)s --konu "Sibernetik Bilinç" --sure 10 --output-dir ./cikti
  python3 %(prog)s --plan-only --konu "Yapay Zeka ve Etik" --hedef-kitle "geliştiriciler"
        """,
    )

    parser.add_argument(
        "--konu",
        type=str,
        default="Bilinç Akışı ve Yaratıcılık",
        help="Podcast konusu (varsayılan: Bilinç Akışı ve Yaratıcılık)",
    )
    parser.add_argument(
        "--hedef-kitle",
        "--kitle",
        type=str,
        default="üniversite öğrencileri",
        help="Hedef kitle (varsayılan: üniversite öğrencileri)",
    )
    parser.add_argument(
        "--sure",
        type=int,
        default=8,
        help="Hedef süre dakika (varsayılan: 8)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Çıktı dizini (varsayılan: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Sadece Aşama 1 (plan) çalıştır, diyalog yazma",
    )
    parser.add_argument(
        "--plan-file",
        type=str,
        help="Mevcut bir plan.json dosyasını kullan (Aşama 1'i atla)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Detaylı çıktı",
    )

    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════╗
║   🎙️  Vanitas Podcast Fabrikası         ║
║   AI Podcast Üretim Aracı               ║
╚══════════════════════════════════════════╝
""")
    print(f"   Konu: {args.konu}")
    print(f"   Hedef Kitle: {args.hedef_kitle}")
    print(f"   Hedef Süre: {args.sure} dk")

    # ── Load or create plan ──
    plan = None

    if args.plan_file:
        eprint(f"\n📂 Mevcut plan yükleniyor: {args.plan_file}")
        with open(args.plan_file, "r", encoding="utf-8") as f:
            plan = json.load(f)
        eprint(f"   ✅ Plan yüklendi: {plan.get('podcast_adi', 'İsimsiz')}")
    else:
        try:
            plan = stage1_plan(args.konu, args.hedef_kitle, args.sure)
        except Exception as e:
            eprint(f"\n❌ Aşama 1 hatası: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)

    if args.plan_only:
        eprint("\n⏹️  Plan-only modu, çıktı kaydediliyor...")
        save_output(Path(args.output_dir), plan, "", args.konu)
        return

    # ── Generate dialog ──
    dialog = ""
    try:
        dialog = stage2_dialog(plan, args.sure)
    except Exception as e:
        eprint(f"\n❌ Aşama 2 hatası: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        eprint("⚠️  Diyalog oluşturulamadı, plan kaydediliyor...")
        dialog = f"[DİYALOG OLUŞTURULAMADI: {e}]"

    # ── Save everything ──
    save_output(Path(args.output_dir), plan, dialog, args.konu)


if __name__ == "__main__":
    main()
