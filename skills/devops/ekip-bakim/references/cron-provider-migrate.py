"""
Cron job provider migrasyonu: opencode-go → opencode-zen
Tüm deepseek-v4-flash job'larını deepseek-v4-flash-free'ye taşır.
glm-5.1 job'larına dokunmaz (derin analiz işleri).
"""
import json
from pathlib import Path

JOBS_PATH = Path.home() / ".hermes/cron/jobs.json"

# --- OKU ---
with open(JOBS_PATH) as f:
    data = json.load(f)

migrated = []
skipped = []

for job in data["jobs"]:
    provider = job.get("provider") or ""
    model = job.get("model") or ""
    name = job.get("name", "?")

    if "opencode-go" in provider and model == "deepseek-v4-flash":
        job["provider"] = "opencode-zen"
        job["model"] = "deepseek-v4-flash-free"
        migrated.append(name)
    else:
        skipped.append(f"{name} ({provider}/{model})")

# --- YAZ ---
with open(JOBS_PATH, "w") as f:
    json.dump(data, f, indent=2)

print(f"Taşınan: {len(migrated)}")
for m in migrated:
    print(f"  ✅ {m}")
print(f"\nDokunulmayan: {len(skipped)}")
for s in skipped:
    print(f"  ⬜ {s}")
