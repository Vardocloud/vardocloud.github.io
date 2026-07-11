#!/usr/bin/env python3
"""Talim Alani Interactive - Challenge Cards with inline keyboard"""
import os, sys, json, asyncio, logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = "-1003917030255"
THREAD_ID = 10996

async def send_card(day_num, title, badge, description, steps, hint, buttons=None):
    """Send an interactive challenge card"""
    bot = Bot(token=TOKEN)
    
    # Build card
    steps_text = ""
    for i, (step, detail) in enumerate(steps, 1):
        steps_text += f"\n│\n├ {i}️⃣ **{step}**\n│   {detail}"
    
    text = (
        f"╔══════════════════════════╗\n"
        f"║  {badge}  **GÜN {day_num}**  ║\n"
        f"╚══════════════════════════╝\n\n"
        f"### 🎯 {title}\n\n"
        f"{description}\n\n"
        f"📋 **ROTA:**{steps_text}\n\n"
        f"💡 **İpucu:** {hint}\n\n"
        f"**⬇️ Hadi başla — aşağıya yaz ☕️**"
    )
    
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    
    try:
        msg = await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text=text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        logging.info(f"Card sent: msg_id={msg.message_id}")
        return msg
    except TelegramError as e:
        logging.error(f"Failed: {e}")
        return None

async def day1():
    """Seviye 1: Sadece konu"""
    buttons = [
        [InlineKeyboardButton("🎯 Bana Konu Ver", callback_data="d1_topic"),
         InlineKeyboardButton("👀 Örnek Gör", callback_data="d1_example")],
        [InlineKeyboardButton("✅ Başlıyorum →", callback_data="d1_start")]
    ]
    await send_card(
        day_num=1,
        title="Bağlamın Gücü",
        badge="🟢",
        description=(
            "**Hedef:** Bağlam olmadan çıktının ne kadar "
            "vasat olduğunu görmek.\n\n"
            "🔴 **Kural:** Sadece konu adı söyle. "
            "Kitle, amaç, ton — hiçbirini ekleme.\n\n"
            "Çıktıyı görünce şaşıracaksın. "
            "Bu farkındalık, bağlamın gücünü öğrenmenin ilk adımı."
        ),
        steps=[
            ("Konu Seç", "Aklına gelen bir psikoloji konusu"),
            ("Ham Çıktı", "Ben vasat bir metin üreteceğim"),
            ("Sorgula", "Neden bu kadar genel olduğunu düşün"),
            ("İterasyon", "'Şunu düzelt' de, hızlı revizeyi gör")
        ],
        hint="Psikolojiyle ilgili herhangi bir konu olabilir. "
             "Örnek: 'bilişsel çarpıtmalar', 'bağlanma teorisi', "
             "'narsisizm'... Sadece 2-3 kelime yeter.",
        buttons=buttons
    )

async def main():
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set")
        sys.exit(1)
    await day1()

if __name__ == "__main__":
    asyncio.run(main())
