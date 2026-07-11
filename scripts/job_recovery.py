#!/usr/bin/env python3
"""
Job Recovery — Gateway crash sonrası geciken job'ları kurtarır.
Her gateway restart'ta + cron-health-check'te çalışır.
Strateji: last_run_at >= 24h ise ve schedule atlanmışsa next_run_at = now yapılır.
"""
import json, datetime, os, sys, re, logging, shutil

JOBS_PATH = os.path.expanduser('~/.hermes/cron/jobs.json')
BACKUP_PATH = JOBS_PATH + '.recovery_bak'
LOG_PATH = os.path.expanduser('~/.hermes/logs/job_recovery.log')

logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def parse_cron_interval(expr):
    """Cron ifadesinden yaklaşık interval (saat) hesapla"""
    parts = expr.strip().split()
    if len(parts) < 5:
        return None
    minute, hour, dom, month, dow = parts
    # Her saat: */N → N saat
    if hour.startswith('*/'):
        try: return int(hour[2:])
        except: return None
    # Sabit saat: 0 8,18 → günde 2 kere → 12 saat
    if ',' in hour:
        times = [int(h) for h in hour.split(',') if h.isdigit()]
        if len(times) >= 2:
            return min(times[i+1] - times[i] for i in range(len(times)-1))
    # Tek saat: 0 8 * * * → 24 saat
    if hour.isdigit() and '*' in (dom + month + dow):
        return 24
    # Haftalık: 0 6 * * 0 → 168 saat
    if dow.isdigit() or dow == '0':
        return 168
    return 48

def load_jobs():
    with open(JOBS_PATH) as f:
        return json.load(f)

def save_jobs(data):
    shutil.copy2(JOBS_PATH, BACKUP_PATH)
    with open(JOBS_PATH, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def recover():
    now = datetime.datetime.now(datetime.timezone.utc)
    data = load_jobs()
    jobs = data.get('jobs', [])
    fixed_running = 0
    rescheduled = []
    skipped = []

    for j in jobs:
        name = j.get('name', '?')
        
        # 1. Orphan running → scheduled
        if j.get('state') == 'running':
            j['state'] = 'scheduled'
            fixed_running += 1
            logging.info(f'Running→scheduled: {name}')

        # 2. Stuck jobs: enabled, scheduled, has last_run_at
        if not j.get('enabled'): continue
        if j.get('state') != 'scheduled': continue
        lr = j.get('last_run_at')
        if not lr: continue
        
        try:
            last_dt = datetime.datetime.fromisoformat(lr.replace('Z','+00:00'))
            hours_idle = (now - last_dt).total_seconds() / 3600
        except:
            continue

        # Cron interval hesapla
        sch = j.get('schedule', {})
        if sch.get('kind') == 'interval':
            expected_hours = sch.get('minutes', 1440) / 60
        elif sch.get('kind') == 'cron':
            expected = parse_cron_interval(sch.get('expr', ''))
            if not expected: continue
            expected_hours = expected
        else:
            continue

        # Eğer beklenen interval'in 2 katından fazla idiyse → gecikmiş
        if hours_idle > expected_hours * 2 and hours_idle >= 24:
            j['next_run_at'] = now.isoformat()
            rescheduled.append(f'{name} ({hours_idle:.0f}h idle, expected {expected_hours}h)')
            logging.info(f'Rescheduled: {name} idle={hours_idle:.0f}h expected={expected_hours}h')
        
        # 3. next_run_at geçmişte kalmışsa da düzelt (scheduler bug koruması)
        nxt = j.get('next_run_at')
        if nxt:
            try:
                nxt_dt = datetime.datetime.fromisoformat(nxt.replace('Z','+00:00'))
                if nxt_dt < now - datetime.timedelta(hours=1):
                    j['next_run_at'] = now.isoformat()
                    if name not in [r.split(' (')[0] for r in rescheduled]:
                        rescheduled.append(f'{name} (past next_run_at)')
                        logging.info(f'Fixed past next_run_at: {name}')
            except:
                pass

    data['jobs'] = jobs
    save_jobs(data)
    
    result = {
        'running_fixed': fixed_running,
        'rescheduled': len([r for r in rescheduled if 'past' not in r]),
        'past_nxt_fixed': len([r for r in rescheduled if 'past' in r]),
        'details': rescheduled[:20]
    }
    logging.info(f'Recovery: {json.dumps(result)}')
    return result

if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else 'recover'
    if action == 'recover':
        r = recover()
        print(f'Running-state fixed: {r["running_fixed"]}')
        print(f'Rescheduled (idle): {r["rescheduled"]}')
        print(f'Past next_run_at fixed: {r["past_nxt_fixed"]}')
        for d in r['details'][:15]:
            print(f'  {d}')
    elif action == 'status':
        data = load_jobs()
        for j in data.get('jobs', []):
            lr = j.get('last_run_at','?')[:16] if j.get('last_run_at') else 'never'
            nx = j.get('next_run_at','?')[:16] if j.get('next_run_at') else 'N/A'
            st = j.get('state','?')
            en = 'Y' if j.get('enabled') else 'N'
            err = '!' if j.get('last_status') == 'error' else ' '
            print(f'{err}{st[0].upper():1s} {en:1s} {lr} -> {nx}  {j.get("name","?")[:50]}')
