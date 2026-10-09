#!/bin/bash
# Records connect/disconnect events of the wind node's rtl_433 MQTT client so
# unclean reboots of arion-wx (locked overlay, no local logs) are visible here.
LOG=/var/log/arion/zero-mqtt-events.log
PAT='rtl_433-[0-9a-f]+.*(New client connected|disconnected|exceeded timeout|taken over)|New client connected from 192\.168\.20\.102.*rtl_433'
tail -Fn0 /var/log/mosquitto/mosquitto.log | grep -a --line-buffered -E "$PAT" | while IFS= read -r l; do
  ts=${l%%:*}
  [[ $ts =~ ^[0-9]+$ ]] && echo "$(date -d @"$ts" -Is) ${l#*: }" >> "$LOG" || echo "$l" >> "$LOG"
done
