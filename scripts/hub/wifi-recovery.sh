#!/bin/bash
# Re-join the YachtArion wifi if the hub has had no wifi connection for a while.
# Why: after a power-up the hub can boot before the router, and the router's wifi can refuse
# associations for several minutes at a time (seen 2026-10-11). NetworkManager normally keeps
# retrying; this is a backstop for when it stops (e.g. autoconnect blocked after "no-secrets").
#
# Conservative by design, so it never fights NetworkManager or a working connection:
#   - does nothing while wlan0 is connected
#   - does nothing while NetworkManager is itself mid-attempt (connecting/configuring/etc.)
#   - only acts once wlan0 has been disconnected/failed for GRACE seconds, then at most once
#     per GRACE period
#   - only acts when the YachtArion SSID is in range
set -u
DEV=wlan0
CON=YachtArion
GRACE=180
STAMP=/run/wifi-recovery.down-since

state=$(nmcli -g GENERAL.STATE device show "$DEV" 2>/dev/null)
code=${state%% *}

case "$code" in
    100) rm -f "$STAMP"; exit 0 ;;        # connected: nothing to do
    30|120) ;;                            # disconnected / failed: candidate
    "")  logger -t wifi-recovery "no device $DEV"; exit 0 ;;
    *)   exit 0 ;;                        # NM is mid-attempt (or device unavailable): leave it
esac

now=$(date +%s)
if [ ! -f "$STAMP" ]; then
    echo "$now" > "$STAMP"
    exit 0
fi
since=$(cat "$STAMP" 2>/dev/null || echo "$now")
[ $((now - since)) -ge "$GRACE" ] || exit 0

# Only try when the SSID is visible; otherwise stay quiet and try again next run.
if ! nmcli -t -f SSID device wifi list ifname "$DEV" 2>/dev/null | grep -qx "$CON"; then
    exit 0
fi

echo "$now" > "$STAMP"                    # next attempt no sooner than GRACE from now
logger -t wifi-recovery "$DEV down ${GRACE}s+ (state '$state'), $CON in range: running nmcli con up"
if timeout 60 nmcli con up "$CON" ifname "$DEV" >/dev/null 2>&1; then
    logger -t wifi-recovery "joined $CON"
else
    logger -t wifi-recovery "nmcli con up $CON failed; will retry in ${GRACE}s"
fi
