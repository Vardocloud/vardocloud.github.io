#!/usr/bin/env python3
"""
Hermes Config Restore v2 — Update Resilience System
Restores critical customizations after Hermes updates using golden_config.yaml.

Modes:
  --check:       Dry-run, show diff, exit 0=OK 1=needs restore
  --sync:        Read current config, add new entries to golden_config.yaml
  --restore:     Sync first, then apply golden values to config
  --post-update: Full pipeline: snapshot -> sync -> restore -> restart -> verify
  --force:       (with --restore) Also overwrite _config_version

Design:
  - Uses ruamel.yaml to preserve comments and ordering
  - golden_config.yaml is the SINGLE SOURCE OF TRUTH
  - When you add new providers/models in config, --sync detects and adds them to golden
  - When Hermes update resets config, --restore reapplies golden values
  - _config_version is NEVER overwritten (let Hermes migrate)
  - SOUL.md/AGENTS.md: section merge (preserve user sections, keep new Hermes content)
"""

import sys, os, subprocess, re, shutil, copy
from pathlib import Path
from datetime import datetime

try:
    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
except ImportError:
    print("ERROR: ruamel.yaml required. Install: pip install --user --break-system-packages ruamel.yaml")
    sys.exit(99)

HOME = Path.home()
HERMES_HOME = HOME / ".hermes"
CONFIG_PATH = HERMES_HOME / "config.yaml"
GOLDEN_PATH = HERMES_HOME / "scripts" / "golden_config.yaml"
SOUL_PATH = HERMES_HOME / "SOUL.md"
AGENTS_PATH = HERMES_HOME / "AGENTS.md"
GATEWAY_SERVICE = "hermes-gateway.service"
GOLDEN_DIR = HERMES_HOME / "golden"
GOLDEN_JOBS = GOLDEN_DIR / "jobs.json"
GOLDEN_SCRIPTS = GOLDEN_DIR / "scripts"
CRON_JOBS_PATH = HERMES_HOME / "cron" / "jobs.json"
SCRIPTS_DIR = HERMES_HOME / "scripts"
SKILLS_DIR = HERMES_HOME / "skills"

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")

def load_yaml(path):
    if not path.exists():
        return None
    with open(path, 'r') as f:
        return yaml.load(f)

def save_yaml(path, data):
    with open(path, 'w') as f:
        yaml.dump(data, f)

def load_golden():
    if not GOLDEN_PATH.exists():
        log(f"Golden config not found: {GOLDEN_PATH}", "ERROR")
        sys.exit(1)
    return load_yaml(GOLDEN_PATH)

# ─── Golden Sync: detect new entries from config ─────────────────

# List-type keys in golden where items are identified by a 'name' field
NAMED_LIST_KEYS = {'custom_providers'}

# Dict-type keys in golden where sub-keys are individual entries
DICT_ENTRY_KEYS = {'model_aliases', 'mcp_servers', 'platform_toolsets'}

def sync_golden_from_config(config, golden):
    """Read current config and add any new entries to golden.
    Returns list of additions made to golden."""
    additions = []

    for key in NAMED_LIST_KEYS:
        config_list = config.get(key, [])
        golden_list = golden.get(key, [])
        if not isinstance(config_list, list) or not isinstance(golden_list, list):
            continue
        golden_names = {item.get('name') for item in golden_list if isinstance(item, dict)}
        for item in config_list:
            if isinstance(item, dict) and item.get('name') not in golden_names:
                golden_list.append(copy.deepcopy(item))
                golden_names.add(item.get('name'))
                additions.append(f"  + {key}: {item.get('name')}")
        golden[key] = golden_list

    for key in DICT_ENTRY_KEYS:
        config_dict = config.get(key, {})
        golden_dict = golden.get(key, {})
        if not isinstance(config_dict, dict) or not isinstance(golden_dict, dict):
            continue
        for sub_key, sub_val in config_dict.items():
            if sub_key not in golden_dict:
                golden_dict[sub_key] = copy.deepcopy(sub_val)
                additions.append(f"  + {key}.{sub_key}")

    # auxiliary: detect new sub-sections and new fields within existing sub-sections
    config_aux = config.get('auxiliary', {})
    golden_aux = golden.get('auxiliary', {})
    if isinstance(config_aux, dict) and isinstance(golden_aux, dict):
        for sub_key, sub_val in config_aux.items():
            if sub_key not in golden_aux:
                golden_aux[sub_key] = copy.deepcopy(sub_val)
                additions.append(f"  + auxiliary.{sub_key}")
            elif isinstance(sub_val, dict) and isinstance(golden_aux.get(sub_key), dict):
                for field_key, field_val in sub_val.items():
                    if field_key not in golden_aux[sub_key]:
                        golden_aux[sub_key][field_key] = copy.deepcopy(field_val)
                        additions.append(f"  + auxiliary.{sub_key}.{field_key}")

    # plugins.enabled: merge new entries
    config_plugins = config.get('plugins', {})
    golden_plugins = golden.get('plugins', {})
    if isinstance(config_plugins, dict) and isinstance(golden_plugins, dict):
        for pk, pv in config_plugins.items():
            if pk not in golden_plugins:
                golden_plugins[pk] = copy.deepcopy(pv)
                additions.append(f"  + plugins.{pk}")
            elif isinstance(pv, list) and isinstance(golden_plugins.get(pk), list):
                for item in pv:
                    if item not in golden_plugins[pk]:
                        golden_plugins[pk].append(item)
                        additions.append(f"  + plugins.{pk}: {item}")

    # toolsets: merge if string representation differs
    config_ts = config.get('toolsets', '')
    golden_ts = golden.get('toolsets', '')
    if config_ts and golden_ts:
        try:
            import json
            config_set = set(json.loads(config_ts)) if isinstance(config_ts, str) else set(config_ts)
            golden_set = set(json.loads(golden_ts)) if isinstance(golden_ts, str) else set(golden_ts)
            new_items = config_set - golden_set
            if new_items:
                merged = sorted(golden_set | config_set)
                golden['toolsets'] = json.dumps(merged)
                additions.append(f"  + toolsets: {new_items}")
        except (json.JSONDecodeError, TypeError):
            pass

    # fallback_providers: merge new entries
    config_fb = config.get('fallback_providers', [])
    golden_fb = golden.get('fallback_providers', [])
    if isinstance(config_fb, list) and isinstance(golden_fb, list):
        golden_fb_keys = {(item.get('provider'), item.get('model')) for item in golden_fb if isinstance(item, dict)}
        for item in config_fb:
            if isinstance(item, dict):
                key = (item.get('provider'), item.get('model'))
                if key not in golden_fb_keys:
                    golden_fb.append(copy.deepcopy(item))
                    additions.append(f"  + fallback_providers: {key}")

    return additions

# ─── Config Merge ───────────────────────────────────────────────

REPLACE_KEYS = {
    'custom_providers', 'model_aliases', 'fallback_providers',
    'platform_toolsets', 'mcp_servers', 'toolsets',
}

AUX_REPLACE = {
    'vision', 'web_extract', 'compression', 'skills_hub', 'approval',
    'mcp', 'title_generation', 'triage_specifier', 'kanban_decomposer',
    'profile_describer', 'curator', 'session_search',
}

def merge_config(config, golden):
    """Merge golden values into config. Returns list of changes."""
    changes = []
    config_version = config.get('_config_version')

    for key, golden_val in golden.items():
        if key == '_config_version':
            continue

        if key in REPLACE_KEYS:
            if config.get(key) != golden_val:
                changes.append(f"  {key}: REPLACE (full list)")
                config[key] = golden_val
            continue

        if key == 'auxiliary':
            if 'auxiliary' not in config:
                config['auxiliary'] = {}
            aux = config['auxiliary']
            if isinstance(golden_val, dict):
                for sub_key, sub_val in golden_val.items():
                    if sub_key in AUX_REPLACE:
                        if aux.get(sub_key) != sub_val:
                            changes.append(f"  auxiliary.{sub_key}: REPLACE")
                            aux[sub_key] = sub_val
                    else:
                        if aux.get(sub_key) != sub_val:
                            changes.append(f"  auxiliary.{sub_key}: MERGE")
                            if isinstance(sub_val, dict) and isinstance(aux.get(sub_key), dict):
                                aux[sub_key].update(sub_val)
                            else:
                                aux[sub_key] = sub_val
            continue

        if key == 'plugins':
            if 'plugins' not in config:
                config['plugins'] = {}
            config_plugins = config['plugins']
            if isinstance(golden_val, dict):
                for pk, pv in golden_val.items():
                    if config_plugins.get(pk) != pv:
                        changes.append(f"  plugins.{pk}: SET")
                        config_plugins[pk] = pv
            continue

        if isinstance(golden_val, dict) and key in config and isinstance(config.get(key), dict):
            for dk, dv in golden_val.items():
                if config[key].get(dk) != dv:
                    changes.append(f"  {key}.{dk}: {config[key].get(dk)!r} -> {dv!r}")
                    config[key][dk] = dv
        else:
            if config.get(key) != golden_val:
                old_val = config.get(key)
                if isinstance(old_val, (dict, list)) or isinstance(golden_val, (dict, list)):
                    changes.append(f"  {key}: REPLACE")
                else:
                    changes.append(f"  {key}: {old_val!r} -> {golden_val!r}")
                config[key] = golden_val

    if config_version is not None:
        config['_config_version'] = config_version

    return changes

def check_mcp_paths(config):
    """Verify MCP server binary paths exist."""
    issues = []
    mcp = config.get('mcp_servers', {})
    if not isinstance(mcp, dict):
        return issues
    for name, srv in mcp.items():
        if isinstance(srv, dict):
            cmd = srv.get('command', '')
            if cmd and not cmd.startswith('$'):
                if '/' in cmd:
                    expanded = cmd.replace('$HOME', str(HOME)).replace('~', str(HOME))
                    if not Path(expanded).exists():
                        issues.append(f"  MCP {name}: command not found: {cmd}")
    return issues

# ─── SOUL.md / AGENTS.md Section Merge ──────────────────────────

def parse_sections(content):
    sections = {}
    current_header = "_preamble"
    current_lines = []
    for line in content.split('\n'):
        if re.match(r'^#{1,3}\s+', line):
            if current_lines:
                sections[current_header] = '\n'.join(current_lines)
            current_header = line.strip()
            current_lines = [line]
        else:
            current_lines.append(line)
    if current_lines:
        sections[current_header] = '\n'.join(current_lines)
    return sections

def merge_sections(old_content, new_content):
    old_sections = parse_sections(old_content)
    new_sections = parse_sections(new_content)
    result = new_content
    new_headers = set(new_sections.keys())
    appended = []
    for header, content in old_sections.items():
        if header not in new_headers and header != "_preamble":
            appended.append(content.strip())
    if appended:
        result += "\n\n" + "\n\n".join(appended)
    return result, len(appended)

def restore_file_section_merge(filepath):
    snapshot_dirs = sorted((HERMES_HOME / "backups" / "snapshots").glob("*"))
    if not snapshot_dirs:
        log(f"  {filepath.name}: no snapshots available")
        return False
    latest = snapshot_dirs[-1]
    backup_file = latest / filepath.name
    if not backup_file.exists():
        log(f"  {filepath.name}: not in latest snapshot")
        return False
    if not filepath.exists():
        shutil.copy2(backup_file, filepath)
        log(f"  {filepath.name}: restored from snapshot (file was deleted)")
        return True
    old_content = backup_file.read_text()
    new_content = filepath.read_text()
    if old_content == new_content:
        log(f"  {filepath.name}: unchanged")
        return False
    merged, n_appended = merge_sections(old_content, new_content)
    if n_appended > 0:
        filepath.write_text(merged)
        log(f"  {filepath.name}: merged {n_appended} preserved sections")
        return True
    else:
        log(f"  {filepath.name}: all sections present in new version")
        return False

# ─── Symlink Verification ────────────────────────────────────────

def verify_symlinks():
    issues = []
    expected_links = {
        'notebooklm-mcp': '/usr/local/bin/notebooklm-mcp',
    }
    local_bin = HOME / '.local/bin'
    for name, expected_target in expected_links.items():
        link_path = local_bin / name
        if link_path.is_symlink():
            actual = os.readlink(str(link_path))
            resolved = str(Path(actual).resolve()) if not Path(actual).is_absolute() else actual
            if resolved != expected_target and actual != expected_target:
                issues.append(f"  Symlink {name}: points to {actual}, expected {expected_target}")
        elif link_path.exists():
            issues.append(f"  {name}: exists but is not a symlink")
        else:
            issues.append(f"  {name}: missing, creating symlink")
            try:
                local_bin.mkdir(parents=True, exist_ok=True)
                link_path.symlink_to(expected_target)
                log(f"  Created symlink: {name} -> {expected_target}")
            except OSError as e:
                issues.append(f"  {name}: failed to create symlink: {e}")
    return issues

# ─── Main Actions ────────────────────────────────────────────────

def restore_from_golden():
    """Restore jobs.json, scripts, and skills from golden/ directory."""
    restored = []

    # Restore jobs.json
    if GOLDEN_JOBS.exists() and CRON_JOBS_PATH.exists():
        golden_jobs = GOLDEN_JOBS.read_bytes()
        current_jobs = CRON_JOBS_PATH.read_bytes()
        if golden_jobs != current_jobs:
            CRON_JOBS_PATH.write_bytes(golden_jobs)
            restored.append("jobs.json")
            log(f"  Restored jobs.json from golden/ ({len(golden_jobs)} bytes)")
        else:
            log("  jobs.json already in sync with golden/")
    elif GOLDEN_JOBS.exists():
        CRON_JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN_JOBS.write_bytes(golden_jobs) if False else None
        # Actually copy it properly
        import shutil
        shutil.copy2(str(GOLDEN_JOBS), str(CRON_JOBS_PATH))
        restored.append("jobs.json")
        log(f"  Restored jobs.json from golden/ (file was missing)")

    # Restore scripts from golden/scripts/
    if GOLDEN_SCRIPTS.exists():
        for script_file in sorted(GOLDEN_SCRIPTS.iterdir()):
            if script_file.is_file():
                dest = SCRIPTS_DIR / script_file.name
                if not dest.exists() or dest.read_bytes() != script_file.read_bytes():
                    import shutil
                    shutil.copy2(str(script_file), str(dest))
                    restored.append(f"scripts/{script_file.name}")
                    log(f"  Restored scripts/{script_file.name}")
        if not restored:
            # Check if any files exist in golden/scripts that are in scripts/
            golden_files = {f.name for f in GOLDEN_SCRIPTS.iterdir() if f.is_file()}
            script_files = {f.name for f in SCRIPTS_DIR.iterdir() if f.is_file()}
            if golden_files.issubset(script_files):
                log("  All golden/scripts/ files already in sync")
    else:
        log("  No golden/scripts/ directory found, skipping script restore")

    return restored

def do_sync():
    """Sync: read current config, add new entries to golden_config.yaml."""
    config = load_yaml(CONFIG_PATH)
    golden = load_golden()
    if config is None or golden is None:
        log("Cannot load config or golden", "ERROR")
        sys.exit(1)

    log("Syncing golden_config.yaml with current config...")
    additions = sync_golden_from_config(config, golden)

    if additions:
        save_yaml(GOLDEN_PATH, golden)
        log(f"Golden config updated: {len(additions)} new entries added")
        for a in additions:
            log(a)
    else:
        log("Golden config already up to date (no new entries found)")
    
    return len(additions) > 0

def do_check():
    """Dry-run: show what would be restored + any untracked entries."""
    config = load_yaml(CONFIG_PATH)
    golden = load_golden()
    if config is None or golden is None:
        log("Cannot load config or golden", "ERROR")
        sys.exit(1)

    # Check for untracked entries first
    additions = sync_golden_from_config(config, copy.deepcopy(golden))
    if additions:
        log("New entries in config not yet in golden (run --sync to add):")
        for a in additions:
            log(a)
    else:
        log("All config entries are tracked in golden")

    # Show restore diff
    config_copy = copy.deepcopy(dict(config)) if isinstance(config, dict) else dict(config)
    changes = merge_config(config_copy, golden)

    log("Config diff (what would be restored):")
    if changes:
        for c in changes:
            log(c)
    else:
        log("  Config is already aligned with golden values")

    mcp_issues = check_mcp_paths(config)
    if mcp_issues:
        log("MCP path issues:")
        for m in mcp_issues:
            log(m)

    symlink_issues = verify_symlinks()
    if symlink_issues:
        log("Symlink issues:")
        for s in symlink_issues:
            log(s)

    return len(changes) > 0 or len(mcp_issues) > 0 or len(symlink_issues) > 0 or len(additions) > 0

def do_restore(force=False):
    """Sync first, then apply golden values to config and merge SOUL/AGENTS."""
    # Step 0: Sync golden with current config (preserve new entries)
    log("Syncing golden_config.yaml with current config...")
    do_sync()

    log("Creating pre-restore snapshot...")
    subprocess.run(["bash", str(HERMES_HOME / "scripts" / "backup_snapshot.sh")],
                    capture_output=True, timeout=60)

    config = load_yaml(CONFIG_PATH)
    golden = load_golden()

    if config is None:
        log("config.yaml is empty or invalid!", "ERROR")
        sys.exit(1)

    config_version = config.get('_config_version')
    log(f"Current _config_version: {config_version}")

    changes = merge_config(config, golden)

    if force:
        log("FORCE mode: will overwrite _config_version")

    if config_version is not None and not force:
        config['_config_version'] = config_version
        log(f"Preserved _config_version: {config_version}")

    save_yaml(CONFIG_PATH, config)
    log(f"Config restored: {len(changes)} changes applied")

    mcp_issues = check_mcp_paths(config)
    if mcp_issues:
        log("WARNING: MCP path issues:")
        for m in mcp_issues:
            log(m)

    symlink_issues = verify_symlinks()
    if symlink_issues:
        log("Symlink issues resolved:")
        for s in symlink_issues:
            log(s)

    for filepath in [SOUL_PATH, AGENTS_PATH]:
        try:
            changed = restore_file_section_merge(filepath)
            if changed:
                log(f"  {filepath.name}: sections merged")
        except Exception as e:
            log(f"  {filepath.name}: merge failed: {e}")

    # Restore golden assets (jobs.json, scripts)
    golden_restored = restore_from_golden()
    if golden_restored:
        log(f"  Golden restore: {len(golden_restored)} items restored")
        for item in golden_restored:
            log(f"    - {item}")

    return len(changes) > 0 or len(golden_restored) > 0

def do_post_update():
    """Full post-update pipeline: sync -> snapshot -> restore -> restart -> verify."""
    log("=== Post-Update Pipeline ===")

    # Step 1: Snapshot
    log("Step 1: Creating pre-restore snapshot...")
    subprocess.run(["bash", str(HERMES_HOME / "scripts" / "backup_snapshot.sh")],
                    capture_output=True, timeout=60)

    # Step 2: Sync golden with current config (preserves any new entries before overwrite)
    log("Step 2: Syncing golden_config.yaml with current config...")
    do_sync()

    # Step 3: Restore golden assets (jobs.json, scripts)
    log("Step 3: Restoring golden assets...")
    restore_from_golden()

    # Step 4: Check what needs restoring
    log("Step 4: Checking config drift...")
    needs_restore = do_check()

    # Step 5: Restore if needed
    if needs_restore:
        log("Step 5: Restoring config...")
        changed = do_restore()
        if changed:
            log("Step 5: Config restored. Restarting gateway...")
            subprocess.run(["systemctl", "--user", "restart", GATEWAY_SERVICE],
                          capture_output=True, timeout=30)
            log("Step 5: Waiting 10s for gateway to start...")
            import time
            time.sleep(10)
    else:
        log("Step 5: No changes needed. Skipping restore.")

    # Step 6: Full verification
    log("Step 6: Running system verification...")
    result = subprocess.run(
        ["bash", str(HERMES_HOME / "scripts" / "verify_system.sh")],
        capture_output=True, text=True, timeout=120)
    log(f"Verification output:\n{result.stdout}")
    if result.returncode != 0:
        log(f"Verification warnings:\n{result.stderr}", "WARN")

    # Step 7: Telegram notification
    success = result.returncode == 0
    emoji = "OK" if success else "WARN"
    status = "SUCCESS" if success else "ISSUES DETECTED"
    msg = f"[{emoji}] Hermes post-update: {status}"
    try:
        subprocess.run([
            str(HERMES_HOME / "hermes-agent/venv/bin/python3"), "-c",
            f"import requests; requests.post('https://api.telegram.org/bot7927784182:AAHes4QI2vR6m5mTJyJFfpyFOpEgoFH7Miyk/sendMessage', json={{'chat_id': '6306976553', 'text': '{msg}'}})"
        ], capture_output=True, timeout=10)
    except Exception:
        pass

    log("=== Post-Update Pipeline Complete ===")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Hermes Config Restore v2")
    parser.add_argument('--check', action='store_true', help='Dry-run: show diff and untracked entries')
    parser.add_argument('--sync', action='store_true', help='Sync: add new config entries to golden_config.yaml')
    parser.add_argument('--restore', action='store_true', help='Sync first, then apply golden values')
    parser.add_argument('--post-update', action='store_true', help='Full post-update pipeline')
    parser.add_argument('--force', action='store_true', help='Force overwrite including _config_version')
    args = parser.parse_args()

    if args.post_update:
        do_post_update()
    elif args.sync:
        changed = do_sync()
        sys.exit(0 if changed else 1)
    elif args.restore:
        do_restore(force=args.force)
    elif args.check:
        needs = do_check()
        sys.exit(1 if needs else 0)
    else:
        parser.print_help()
        sys.exit(1)