#!/bin/bash
# Answer helper; run when the networking TASK requests it, in Fusion console.
set -euo pipefail
[[ $(id -u) == 0 && -z ${SSH_CONNECTION:-} ]] || { echo 'Root Fusion console required'; exit 1; }
case $(hostname -s) in
 *alpha*) ADDRESS=192.168.100.10; V6=fd00::10; PROFILE=lab-static ;;
 *bravo*) ADDRESS=192.168.100.20; V6=fd00::20; PROFILE=lab-static ;;
 *charlie*) ADDRESS=10.20.30.11; V6=fd42::11; PROFILE=lab-static ;;
 *delta*) ADDRESS=10.20.30.12; V6=fd42::12; PROFILE=lab-static ;;
 *echo*) ADDRESS=172.16.40.21; V6=fd10::21; PROFILE=lab3-static ;;
 *foxtrot*) ADDRESS=172.16.40.22; V6=fd10::22; PROFILE=lab3-static ;;
 *) echo 'Unknown node'; exit 1 ;;
esac
nmcli -f NAME,UUID,DEVICE con show
read -r -p 'UUID of the host-only connection (match manifest MAC): ' UUID
nmcli con show "$UUID" >/dev/null
nmcli con mod "$UUID" connection.id "$PROFILE" ipv4.method manual \
 ipv4.addresses "$ADDRESS/24" ipv4.gateway '' ipv4.dns '' ipv4.never-default yes \
 ipv6.method manual ipv6.addresses "$V6/64" ipv6.gateway '' ipv6.dns '' ipv6.never-default yes connection.autoconnect yes
# Deliberately preserve zone; exam 2 sets labzone itself.
nmcli con up "$UUID"
