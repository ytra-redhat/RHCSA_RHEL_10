#!/bin/bash
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo 'Run as root inside the correct clone'; exit 1; }
[ "$(cat /etc/rhcsa-fusion-golden 2>/dev/null)" = jconwell-fusion-golden-v2 ] || { echo 'Golden bootstrap missing'; exit 1; }
[ "$(uname -m)" = aarch64 ] || exit 1
if [ -f /etc/rhcsa-fusion-seeded ]; then
 [ "$(cat /etc/rhcsa-fusion-seeded)" = 'c2459745e5674773b794bc092a9a2ed4' ] || exit 1
 vmtoolsd --cmd 'info-set guestinfo.rhcsa_seed c2459745e5674773b794bc092a9a2ed4'
 echo 'Completion marker republished; no guest changes'; exit 0
fi
NAT_MAC='00:50:56:13:99:df'
LAB_MAC='00:50:56:3e:62:0b'
NODE='alpha'
EXPECTED_DISKS=2
EXPECTED_SIZES=(10737418240)
# Verify identity by both VM-specific MAC addresses before any guest change.
NAT_IF=''; LAB_IF=''
[ -z "${SSH_CONNECTION:-}" ] || { echo 'Use the Fusion console; networking changes disconnect SSH'; exit 1; }
for tool in nmcli openssl wipefs vmtoolsd ssh-keygen; do
 command -v "$tool" >/dev/null || { echo "Missing tool: $tool"; exit 1; }
done
PROGRESS=/var/lib/rhcsa-fusion
mkdir -p "$PROGRESS"
trap 'echo "Seed failed at line $LINENO; inspect console and progress before retry" >&2' ERR

for path in /sys/class/net/*; do
  address=$(cat "$path/address")
  [ "$address" != "$NAT_MAC" ] || NAT_IF=${path##*/}
  [ "$address" != "$LAB_MAC" ] || LAB_IF=${path##*/}
done
[ -n "$NAT_IF" ] && [ -n "$LAB_IF" ] || { echo 'Wrong VM MACs'; exit 1; }
[ "$(lsblk -dnr -o NAME,TYPE | awk '$2=="disk" && $1 !~ /^zram[0-9]+$/ {n++} END {print n+0}')" = "$EXPECTED_DISKS" ] || { echo 'Unexpected disk count'; exit 1; }
ROOT_DISK=$(lsblk -srnp -o NAME,TYPE "$(findmnt -n -o SOURCE /)" | awk '$2=="disk" {print $1}')
[ "$ROOT_DISK" = /dev/nvme0n1 ] || { echo 'Root disk is not nvme0n1; inspect before continuing'; exit 1; }
for i in "${!EXPECTED_SIZES[@]}"; do
 device=/dev/nvme0n$((i+2))
 [ "$(blockdev --getsize64 "$device")" = "${EXPECTED_SIZES[$i]}" ] || { echo "Unexpected capacity: $device"; exit 1; }
done
for path in /sys/block/nvme0n*; do
  [ "${path##*/}" != nvme0n1 ] || continue
  [ -z "$(ls "$path" | grep -E 'p[0-9]+$' || true)" ] || { echo 'Extra disk already partitioned'; exit 1; }
  [ -z "$(wipefs -n --noheadings /dev/${path##*/})" ] || { echo 'Extra disk has signatures'; exit 1; }
done
[ -s /var/lib/rhcsa-fusion/golden-hostkey-fingerprint ] || { echo 'Hostkey seal record missing'; exit 1; }
[ -s /var/lib/rhcsa-fusion/golden-machine-id ] || { echo 'Seal record missing; stop'; exit 1; }
[ "$(cat /etc/machine-id)" != "$(cat /var/lib/rhcsa-fusion/golden-machine-id)" ] || { echo 'Golden was not sealed; identity reused'; exit 1; }
[ -s /etc/machine-id ] || { echo 'First boot identity missing'; exit 1; }
if [ ! -f "$PROGRESS/network.done" ]; then
ssh-keygen -A
[ "$(ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub | awk '{print $2}')" != "$(cat /var/lib/rhcsa-fusion/golden-hostkey-fingerprint)" ] || { echo 'SSH host key reused; stop'; exit 1; }
systemctl restart sshd
hostnamectl set-hostname rhel10-$NODE
# Remove only the template-created profiles; do not overwrite all NM config.
for name in fusion-nat fusion-lab; do
 nmcli con delete "$name" >/dev/null 2>&1 || true
done
nmcli con add type ethernet ifname '*' con-name fusion-nat \
  802-3-ethernet.mac-address "$NAT_MAC" ipv4.method auto ipv6.method auto connection.autoconnect yes
nmcli con add type ethernet ifname '*' con-name fusion-lab \
  802-3-ethernet.mac-address "$LAB_MAC" ipv4.method disabled ipv6.method disabled connection.autoconnect yes
nmcli con mod fusion-lab connection.zone public
nmcli con up fusion-nat
nmcli con up fusion-lab
systemctl set-default multi-user.target
systemctl enable --now firewalld
touch "$PROGRESS/network.done"
fi
if [ ! -f "$PROGRESS/fixtures.done" ]; then
touch /var/tmp/badperms; chmod 777 /var/tmp/badperms
python3 - <<'GRUBPY'
from pathlib import Path
import re
p=Path('/etc/default/grub');text=p.read_text()
text=re.sub(r'^GRUB_TIMEOUT=.*$', 'GRUB_TIMEOUT=3', text, flags=re.M)
text=re.sub(r'^GRUB_TIMEOUT_STYLE=.*$', 'GRUB_TIMEOUT_STYLE=menu', text, flags=re.M)
def args(m):return 'GRUB_CMDLINE_LINUX="'+' '.join(x for x in m[1].split() if x!='quiet')+'"'
text=re.sub(r'^GRUB_CMDLINE_LINUX="(.*)"$',args,text,flags=re.M)
p.write_text(text)
GRUBPY
grub2-mkconfig -o /boot/grub2/grub.cfg --update-bls-cmdline
touch "$PROGRESS/fixtures.done"
fi
printf '%s\n' 'c2459745e5674773b794bc092a9a2ed4' > /etc/rhcsa-fusion-seeded.tmp
mv /etc/rhcsa-fusion-seeded.tmp /etc/rhcsa-fusion-seeded
vmtoolsd --cmd 'info-set guestinfo.rhcsa_seed c2459745e5674773b794bc092a9a2ed4'
sync
echo 'Seed complete. Shut down; create the exam-ready snapshot before rebooting.'
