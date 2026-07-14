# Cron + systemctl --user: Silent False-Positive Pattern

## Problem

User-crontab scriptlerinde `systemctl --user is-active <service>` her zaman "inactive"
dondurur — oysa servis calisiyordur. Bu, cron ortaminda `XDG_RUNTIME_DIR` ve
`DBUS_SESSION_BUS_ADDRESS` set edilmedigi icin olur.

## Affected Script

`auth_monitor.sh` — her 6 saatte bir calisir, servisleri kontrol eder, false-positive
"DOWN" alarmlari uretir. Cozum: script basina envar exportlari ekle.

```
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
```

Ayni cozum `watchdog.sh`'da zaten vardi (dogru ornek).

## Ayrica: Container Yoksa "DOWN" Alarmi

`daily_health.sh`'deki Docker container kontrolu de false positive uretiyordu —
container yokken "DOWN" raporlaniyordu. Cozum: once container var mi kontrol et, yoksa
"N/A" olarak isaretle.
