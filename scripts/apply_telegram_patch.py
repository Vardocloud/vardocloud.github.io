#!/usr/bin/env python3
"""Apply the Telegram callback handler patch to telegram.py if not already applied.

Protects against Docker image rebuilds — the patch is re-applied on every
container start if missing. Checks for the "feedback_delivered" marker.

Patch: fix_telegram_model_picker_callback
- Silently answers callback before model switch (prevents BadRequest crash)
- Separates model switch from UI feedback
- Falls back to send_message if edit_message fails
"""
import sys

TARGET = "/home/ubuntu/hermes-agent/gateway/platforms/telegram.py"
MARKER = "feedback_delivered"

OLD_BLOCK = """            model_id = model_list[idx]
            provider_slug = state.get("selected_provider", "")
            callback = state.get("on_model_selected")

            if not callback:
                await query.answer(text="Picker expired.")
                return

            try:
                result_text = await callback(chat_id, model_id, provider_slug)
            except Exception as exc:
                logger.error("Model picker switch failed: %s", exc)
                result_text = f"Error switching model: {exc}"

            # Edit message to show confirmation, remove buttons
            try:
                await query.edit_message_text(
                    text=self.format_message(result_text),
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=None,
                )
            except Exception:
                # Markdown parse failure — retry as plain text
                try:
                    await query.edit_message_text(
                        text=result_text,
                        parse_mode=None,
                        reply_markup=None,
                    )
                except Exception:
                    pass
            await query.answer(text="Model switched!")"""

NEW_BLOCK = """            model_id = model_list[idx]
            provider_slug = state.get("selected_provider", "")
            callback_fn = state.get("on_model_selected")

            if not callback_fn:
                await query.answer(text="Picker expired.")
                return

            # Acknowledge callback silently FIRST — dismisses loading spinner
            # before the model switch. Even if expired, we continue.
            try:
                await query.answer()
            except Exception:
                pass

            # Perform model switch (config update + agent hot-swap)
            try:
                result_text = await callback_fn(chat_id, model_id, provider_slug)
            except Exception as exc:
                logger.error("Model picker switch failed: %s", exc)
                result_text = f"Error switching model: {exc}"

            # Health check: quick ping to verify provider responds
            try:
                import aiohttp
                providers_list = state.get("providers", [])
                prov = next((p for p in providers_list if p.get("slug") == provider_slug), None)
                if prov and prov.get("base_url"):
                    base = prov["base_url"].rstrip("/")
                    async with aiohttp.ClientSession() as s:
                        async with s.get(f"{base}/models", timeout=aiohttp.ClientTimeout(total=2)) as r:
                            if r.status >= 500:
                                result_text += "\\n\\n⚠️ Warning: This provider returned HTTP %s. Response might be slow until it recovers." % r.status
                elif prov and not prov.get("base_url"):
                    pass
            except Exception:
                result_text += "\\n\\n⚠️ Warning: This provider is not responding right now. Model switch succeeded, but requests may fail until the provider recovers."

            # Show confirmation by editing the message (works even when
            # callback query is expired — it uses message ID, not callback).
            # Fallback: send a new message if editing fails.
            feedback_delivered = False
            try:
                await query.edit_message_text(
                    text=self.format_message(result_text),
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=None,
                )
                feedback_delivered = True
            except Exception:
                try:
                    await query.edit_message_text(
                        text=result_text,
                        parse_mode=None,
                        reply_markup=None,
                    )
                    feedback_delivered = True
                except Exception:
                    pass
            if not feedback_delivered:
                try:
                    await self._send_message_with_thread_fallback(
                        chat_id=int(chat_id),
                        text=result_text,
                    )
                except Exception:
                    pass

            # Clean up state
            self._model_picker_state.pop(chat_id, None)"""


def main():
    print(f"[patch-telegram] Checking {TARGET}...")

    try:
        with open(TARGET, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[patch-telegram] File not found, skipping: {TARGET}")
        return 0

    if MARKER in content:
        print(f"[patch-telegram] Patch already applied (found '{MARKER}').")
        return 0

    if OLD_BLOCK not in content:
        # Check for the critical line that identifies the old code
        if 'await query.answer(text="Model switched!")' not in content:
            print("[patch-telegram] Old block not found — already patched or code changed. Skipping.")
            return 0
        print("[patch-telegram] WARNING: Found 'Model switched!' but old block does not match exactly.")
        print("[patch-telegram] File may have been modified. Not applying patch to avoid corruption.")
        return 1

    content = content.replace(OLD_BLOCK, NEW_BLOCK, 1)
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[patch-telegram] Patch applied successfully ({len(content)} bytes).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
