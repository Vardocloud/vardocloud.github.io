#!/usr/bin/env python3
"""
temp_cleanup.py — Retention-based temporary file cleanup.

Usage:
  python3 temp_cleanup.py [--dry-run] [--older-than DAYS]
  python3 temp_cleanup.py --report          # just show what's taking space

Retention Policy:
  /tmp/ pip-unpack-* chatterbox_test  → 7 days (build artifacts)
  /tmp/ reel_*.mp4, hermes-results/   → 7 days
  /tmp/ *.wav, *.deb                  → 14 days (downloads)
  ~/.hermes/audio_cache/              → 30 days (voice messages)
  ~/.hermes/cron/output/              → 30 days (logs)
  ~/.hermes/image_cache/              → 30 days (screenshots)

SAFE LIST (never touched):
  Scripts: ~/*.py, ~/*.sh
  Config: ~/.hermes/  (except cache/cron/output)
  Code repos: ~/hermes-agent/
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

HOME = Path.home()
HERMES = HOME / ".hermes"
NOW = datetime.now(timezone.utc)

# ── Retention rules ──────────────────────────────────────────────────
# Each rule: (path, min_age_days, description, glob_pattern, is_dir)
# is_dir=True means delete the whole directory, not just contents

# ── Always-clean patterns (build artifacts, zero retention) ─────────
BUILD_ARTIFACTS = [
    ("/tmp", "pip-unpack-*", False),       # pip partial downloads
    ("/tmp", "pip-metadata-*", False),     # pip metadata leftovers
    ("/tmp", "chatterbox_test*", False),   # disposable test environments
    ("/tmp", "markitdown-mcp", True),      # test repos
    ("/tmp", "vision_test", True),         # vision test screenshots
    ("/tmp", "hermes-results/*", False),   # subagent results
    ("/tmp", "tmp*", False),               # unnamed temp files (tmpXXXXXX)
    ("/tmp", "hermes-snap-*.sh", False),   # snap scripts
    ("/tmp", "hermes-cwd-*.txt", False),   # cwd markers
    ("/tmp", "glaido_*.txt", False),       # temp text files
    ("/tmp", "karusel_*.pdf", False),      # temporary PDFs
]

# ── Retention-based rules (age matters) ─────────────────────────────
RETENTION_RULES = [
    # Hermes caches
    (str(HERMES / "audio_cache"), 30, "audio cache (voice messages)"),
    (str(HERMES / "image_cache"), 30, "image cache (screenshots)"),

    # Cron output (each job has its own subdir)
    (str(HERMES / "cron" / "output"), 30, "cron output logs"),

    # /tmp/ media
    ("/tmp", 14, "downloaded audio (wav)"),
    ("/tmp", 7, "downloaded videos (mp4)"),
    ("/tmp", 14, "deb packages"),
    ("/tmp", 14, "temp shell scripts"),
    ("/tmp", 14, "temp pulseaudio files"),
]

# ── SAFE DIRS (never cleaned) ────────────────────────────────────────
SAFE_PREFIXES = [
    str(HERMES / "skills"),
    str(HERMES / "plugins"),
    str(HERMES / "config.yaml"),
    str(HERMES / ".env"),
    str(HERMES / "google_token.json"),
    str(HERMES / "scripts"),
    str(HERMES / "cron" / "jobs.json"),
    str(HERMES / "golden"),
]


def parse_args():
    dry_run = "--dry-run" in sys.argv
    report_only = "--report" in sys.argv
    older_than = 7
    for i, a in enumerate(sys.argv):
        if a == "--older-than" and i + 1 < len(sys.argv):
            older_than = int(sys.argv[i + 1])
    return {"dry_run": dry_run, "report_only": report_only, "older_than": older_than}


def human_size(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def get_size(path):
    if path.is_file() or path.is_symlink():
        return path.stat().st_size
    total = 0
    try:
        for p in path.rglob("*"):
            if p.is_file():
                total += p.stat().st_size
    except PermissionError:
        pass
    return total


def should_skip(path, base_path):
    """Check if file/dir is in safe zone."""
    p = str(path.resolve())
    for safe in SAFE_PREFIXES:
        if p.startswith(safe):
            return True
    return False


def find_matching(base, pattern, is_dir):
    """Find items matching a pattern under base."""
    base = Path(base)
    if not base.exists():
        return []

    if is_dir and pattern is None:
        # All subdirectories directly under base
        return [d for d in base.iterdir() if d.is_dir() and not d.name.startswith(".")]

    if is_dir:
        return list(base.glob(pattern))

    # For file patterns
    if "*" in pattern or "?" in pattern:
        if "/" in pattern:
            # Pattern with subdirectory (hermes-results/*)
            parts = pattern.split("/", 1)
            parent = base / parts[0]
            if parent.is_dir():
                return list(parent.glob(parts[1]))
        return list(base.glob(pattern))

    return []


def age_in_days(path):
    """Return file age in days."""
    try:
        mtime = path.stat().st_mtime
        return (time.time() - mtime) / 86400
    except (OSError, PermissionError):
        return 0


def get_build_artifacts():
    """Find build artifacts regardless of age."""
    items = []
    for base_path, pattern, is_dir in BUILD_ARTIFACTS:
        found = find_matching(base_path, pattern, is_dir)
        for item in found:
            if should_skip(item, base_path):
                continue
            desc = f"build artifact ({pattern})"
            size = get_size(item)
            items.append((item, desc, size))
    return items


def get_retention_candidates(args):
    """Find files/dirs that match retention rules and are old enough."""
    candidates = []
    for base_path, min_days, desc in RETENTION_RULES:
        if os.path.isdir(base_path) and min_days >= 7:
            # Clean subdirectories in cron/output
            base = Path(base_path)
            if base.name == "output" and base.parent.name == "cron":
                for d in base.iterdir():
                    if d.is_dir() and not d.name.startswith("."):
                        days = age_in_days(d)
                        if days >= min_days:
                            size = get_size(d)
                            candidates.append((d, desc, size))
            else:
                # Clean files in cache dirs
                for f in base.iterdir():
                    if f.is_file() and not f.name.startswith("."):
                        days = age_in_days(f)
                        if days >= min_days:
                            candidates.append((f, desc, f.stat().st_size))
        elif base_path == "/tmp":
            # Handle /tmp/ rules: find matching files
            for entry in Path("/tmp").iterdir():
                if not entry.is_file():
                    continue
                if entry.name.startswith("."):
                    continue
                # Check if it matches retention rules
                for rule_base, rule_days, rule_desc in RETENTION_RULES:
                    if rule_base != "/tmp":
                        continue
                    # Match by extension/pattern
                    if rule_desc.startswith("downloaded audio") and entry.suffix.lower() in (".wav",):
                        days = age_in_days(entry)
                        if days >= rule_days:
                            candidates.append((entry, rule_desc, get_size(entry)))
                            break
                    elif rule_desc.startswith("downloaded videos") and entry.suffix.lower() in (".mp4", ".webm", ".mov"):
                        days = age_in_days(entry)
                        if days >= rule_days:
                            candidates.append((entry, rule_desc, get_size(entry)))
                            break
                    elif rule_desc.startswith("deb packages") and entry.suffix.lower() in (".deb",):
                        days = age_in_days(entry)
                        if days >= rule_days:
                            candidates.append((entry, rule_desc, get_size(entry)))
                            break
                    elif rule_desc.startswith("temp shell scripts") and entry.suffix.lower() in (".sh",):
                        days = age_in_days(entry)
                        if days >= rule_days:
                            candidates.append((entry, rule_desc, get_size(entry)))
                            break
                    elif rule_desc.startswith("temp pulseaudio") and "pulse" in entry.name.lower():
                        days = age_in_days(entry)
                        if days >= rule_days:
                            candidates.append((entry, rule_desc, get_size(entry)))
                            break

    return candidates

    # Sort by size (biggest first)
    candidates.sort(key=lambda x: -x[2])
    return candidates


def perform_cleanup(candidates, dry_run=False):
    """Delete the candidates."""
    total_freed = 0
    deleted = []

    for path, desc, size in candidates:
        try:
            if dry_run:
                print(f"  [DRY-RUN] would delete: {path} ({human_size(size)}) — {desc}")
            else:
                if path.is_dir() and not path.is_symlink():
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)

                if not path.exists():
                    total_freed += size
                    deleted.append((path, desc, size))
                    print(f"  ✅ Deleted: {path} ({human_size(size)}) — {desc}")
                else:
                    print(f"  ⚠️  Could not delete: {path}")
        except Exception as e:
            print(f"  ❌ Error deleting {path}: {e}")

    return total_freed, deleted


def report_disk_usage():
    """Show current disk usage summary."""
    dirs = [
        ("audio_cache", HERMES / "audio_cache"),
        ("image_cache", HERMES / "image_cache"),
        ("cron/output", HERMES / "cron" / "output"),
        ("/tmp/hermes-results", Path("/tmp/hermes-results")),
        ("/tmp (user only)", Path("/tmp")),
    ]

    print("\n📊 Disk Usage Report")
    print("━" * 50)
    total = 0
    for name, path in dirs:
        if path.exists():
            s = get_size(path)
            total += s
            print(f"  {name:25s} → {human_size(s)}")
    print(f"  {'TOTAL':25s} → {human_size(total)}")

    # Top files in /tmp
    print("\n📁 Largest files in /tmp (>50MB):")
    try:
        result = subprocess.run(
            ["find", "/tmp", "-type", "f", "-size", "+50M", "-exec", "ls", "-lh", "{}", "+"],
            capture_output=True, text=True, timeout=15
        )
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                print(f"  {line}")
    except Exception:
        pass

    return total


def main():
    args = parse_args()

    if args["report_only"]:
        report_disk_usage()
        return

    print(f"🔍 Scanning for cleanup...")
    build_candidates = get_build_artifacts()
    retention_candidates = get_retention_candidates(args)
    candidates = build_candidates + retention_candidates
    candidates.sort(key=lambda x: -x[2])

    if not candidates:
        print("✨ Nothing to clean up!")
        return

    # Separate build artifacts and retention items for display
    build_paths = set(str(c[0]) for c in build_candidates)
    build_items = [c for c in candidates if str(c[0]) in build_paths]
    retention_items = [c for c in candidates if str(c[0]) not in build_paths]

    print(f"\n📋 Found {len(candidates)} item(s) to clean:")
    total_waste = sum(c[2] for c in candidates)

    if build_items:
        print(f"\n  🔧 Build artifacts (always clean):")
        for path, desc, size in build_items:
            print(f"     • {path.name} ({human_size(size)})")

    if retention_items:
        print(f"\n  ⏳ Retention-based (age threshold):")
        for path, desc, size in retention_items:
            days = age_in_days(path)
            print(f"     • {path.name} ({human_size(size)}, {days:.0f}d old) — {desc}")

    print(f"\n  Total reclaimable: {human_size(total_waste)}")

    if args["dry_run"]:
        print("\n🚩 Dry-run mode — no files deleted.")
        return

    # Ask for confirmation unless --force
    if "--force" not in sys.argv:
        print("\n⚠️  Pass --force to actually delete, or --dry-run to preview.")
        return

    print("\n🗑️  Cleaning up...")
    freed, deleted = perform_cleanup(candidates)

    print(f"\n✅ Done! Freed {human_size(freed)}, deleted {len(deleted)} items.")
    print(f"   Remaining in /tmp: ", end="")
    try:
        result = subprocess.run(["du", "-sh", "/tmp"], capture_output=True, text=True, timeout=5)
        print(result.stdout.strip())
    except Exception:
        print("?")


if __name__ == "__main__":
    main()
