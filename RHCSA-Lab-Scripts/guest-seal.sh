#!/bin/bash
# Final step in golden; shuts down. Do not boot golden again before cloning.
set -euo pipefail
[[ $(id -u) == 0 && $(uname -m) == aarch64 ]] || exit 1
[[ $(cat /etc/rhcsa-fusion-golden) == jconwell-fusion-golden-v2 ]] || { echo 'Run v2 bootstrap first'; exit 1; }
[[ ! -f /etc/rhcsa-fusion-seeded ]] || { echo 'Exam clone refused'; exit 1; }
[[ -z ${SSH_CONNECTION:-} ]] || { echo 'Use console'; exit 1; }
# Clone first boot gets new IDs and SSH host keys. No live machine-ID reinitialisation.
mkdir -p /var/lib/rhcsa-fusion /var/lib/dbus
if [[ -s /etc/machine-id ]]; then
 cp /etc/machine-id /var/lib/rhcsa-fusion/golden-machine-id
elif [[ ! -s /var/lib/rhcsa-fusion/golden-machine-id ]]; then
 echo "No saved original machine ID; stop" >&2; exit 1
fi
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub | awk '{print $2}' > /var/lib/rhcsa-fusion/golden-hostkey-fingerprint
: > /etc/machine-id
rm -f /var/lib/dbus/machine-id
ln -s /etc/machine-id /var/lib/dbus/machine-id
rm -f /etc/ssh/ssh_host_*key /etc/ssh/ssh_host_*key.pub
sync
systemctl poweroff
