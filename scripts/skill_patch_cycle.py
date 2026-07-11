#!/usr/bin/env python3
"""
Skill Patch Cycle — Hata anında structured değerlendirme + patch önerisi şablonu.

Bu bir OTOMATİK SCRIPT değil, bir İŞ AKIŞI ŞABLONU'dur.
Vanitas bir skill kullanırken hata aldığında bu adımları izler.

Kullanım (Vanitas için):
    from skill_patch_cycle import SkillPatchCycle
    spc = SkillPatchCycle()
    spc.evaluate(skill_name="youtube-content", error="yt-dlp not found")
    → {"score": 4, "issues": ["eksik bağımlılık"], "fix": "pip install yt-dlp"}
    
    spc.propose(skill_name, issues, fix)
    → {"prompt": "youtube-content skill'inde yt-dlp eksik, pip install ekleyelim mi?"}
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

SKILLS_DIR = Path.home() / ".hermes" / "skills"


class SkillPatchCycle:
    """
    Skill hata değerlendirme + patch önerisi döngüsü.
    
    Kullanım Senaryosu:
        1. Bir skill kullanılır, hata alınır
        2. evaluate() çağrılır → hata türü + şiddet + düzeltme önerisi çıkar
        3. propose() çağrılır → Edel'e sunulacak rapor hazırlanır
        4. Edel onaylarsa → skill_manage patch ile uygulanır
        5. Tekrar test edilir → başarılıysa kapanır
    """

    HATA_KATEGORILERI = {
        "command_not_found": {
            "type": "eksik_bağımlılık",
            "severity": "yüksek",
            "fix_type": "kurulum_adımı_ekle"
        },
        "api_timeout": {
            "type": "api_sorunu",
            "severity": "orta",
            "fix_type": "failover_adımı_ekle"
        },
        "wrong_command": {
            "type": "yanlış_komut",
            "severity": "yüksek",
            "fix_type": "komut_düzelt"
        },
        "skill_outdated": {
            "type": "güncel_değil",
            "severity": "orta",
            "fix_type": "güncelle"
        },
        "missing_step": {
            "type": "eksik_adım",
            "severity": "düşük",
            "fix_type": "adım_ekle"
        },
        "format_error": {
            "type": "çıktı_hatası",
            "severity": "düşük",
            "fix_type": "format_düzelt"
        }
    }

    def categorize_error(self, error_text):
        """Hata metnini analiz et, kategori bul."""
        error_lower = error_text.lower()
        
        if any(cmd in error_lower for cmd in ["not found", "command not found", "no such file", "cannot find"]):
            return "command_not_found"
        elif any(kw in error_lower for kw in ["timeout", "timed out", "connection refused", "500", "503"]):
            return "api_timeout"
        elif any(kw in error_lower for kw in ["invalid option", "unexpected", "syntax error", "usage:"]):
            return "wrong_command"
        elif any(kw in error_lower for kw in ["deprecated", "removed", "no longer", "version"]):
            return "skill_outdated"
        elif any(kw in error_lower for kw in ["missing", "required", "must provide", "expected"]):
            return "missing_step"
        else:
            return "format_error"

    def evaluate(self, skill_name, error, context=""):
        """
        Hata alınan skill'i değerlendir.
        
        Döndürür:
            {
                "skill": "youtube-content",
                "error": "yt-dlp not found",
                "category": "eksik_bağımlılık",
                "severity": "yüksek",
                "score": 4,          # 0-10, ne kadar acil
                "issue": "...",
                "suggested_fix": "..."
            }
        """
        category_key = self.categorize_error(error)
        category = self.HATA_KATEGORILERI.get(category_key, {
            "type": "bilinmeyen",
            "severity": "düşük",
            "fix_type": "incele"
        })
        
        # Severity'ye göre skor
        severity_scores = {"yüksek": 8, "orta": 5, "düşük": 2}
        base_score = severity_scores.get(category["severity"], 3)
        
        # Skill'in kritikliğine göre skor ajustı
        skill_path = SKILLS_DIR / skill_name
        if skill_path.exists():
            # Skill ne kadar eskiyse skor o kadar yüksek (güncellenmeli)
            mtime = skill_path.stat().st_mtime
            days_old = (datetime.now().timestamp() - mtime) / 86400
            age_penalty = min(3, int(days_old / 30))  # her 30 günde +1
        else:
            age_penalty = 0
        
        score = min(10, base_score + age_penalty)
        
        result = {
            "skill": skill_name,
            "error": error,
            "category": category["type"],
            "severity": category["severity"],
            "score": score,
            "context": context[:200] if context else "",
            "suggested_fix_type": category["fix_type"],
            "evaluated_at": datetime.now().isoformat()
        }
        
        return result

    def propose(self, evaluation_result):
        """
        Değerlendirme sonucunu Edel'e sunulacak rapora çevir.
        
        Döndürür:
            {
                "prompt": "Edel'e sorulacak soru",
                "details": "...",
                "fix_command": "..."
            }
        """
        skill = evaluation_result["skill"]
        cat = evaluation_result["category"]
        sev = evaluation_result["severity"]
        score = evaluation_result["score"]
        error = evaluation_result["error"]
        
        severity_emoji = {"yüksek": "🔴", "orta": "🟡", "düşük": "🟢"}
        emoji = severity_emoji.get(sev, "⚪")
        
        prompt = (
            f"**{skill}** skill'inde bir sorun tespit ettim.\n"
            f"{emoji} **{cat.upper()}** — Skor: {score}/10\n"
            f"Hata: `{error}`\n\n"
        )
        
        if cat == "eksik_bağımlılık":
            prompt += (
                "Öneri: Skill'in kurulum adımlarına eksik bağımlılık eklenecek.\n"
                "Onaylıyor musun?"
            )
        elif cat == "yanlış_komut":
            prompt += (
                "Öneri: Skill'deki hatalı komut güncellenecek.\n"
                "Onaylıyor musun?"
            )
        elif cat == "api_sorunu":
            prompt += (
                "Öneri: API failover adımı eklenecek (alternatif servis).\n"
                "Onaylıyor musun?"
            )
        elif cat == "eksik_adım":
            prompt += (
                "Öneri: Skill'e eksik adım eklenecek.\n"
                "Onaylıyor musun?"
            )
        else:
            prompt += (
                "Öneri: Skill incelenip güncellenecek.\n"
                "Onaylıyor musun?"
            )
        
        return {
            "prompt": prompt,
            "skill": skill,
            "score": score,
            "fix_type": evaluation_result["suggested_fix_type"],
            "severity": sev
        }


# --- CLI Test ---
if __name__ == "__main__":
    import sys
    
    spc = SkillPatchCycle()
    
    test_errors = [
        ("youtube-content", "yt-dlp: command not found"),
        ("browser-auth", "Connection timeout after 30s"),
        ("sohbet", "skill_manage: invalid option -- 'x'"),
        ("supervisor-pattern", "missing required field: 'schema'"),
        ("spotify", "Module 'spotipy' has no attribute 'new_releases'"),
    ]
    
    print("=== Skill Değerlendirme Testi ===\n")
    for skill, err in test_errors:
        result = spc.evaluate(skill, err)
        prop = spc.propose(result)
        print(f"📦 {result['skill']}")
        print(f"  Hata: {result['error']}")
        print(f"  Kategori: {result['category']} | Şiddet: {result['severity']} | Skor: {result['score']}/10")
        print(f"  Öneri: {result['suggested_fix_type']}")
        print(f"  Prompt:\n{prop['prompt']}\n")
