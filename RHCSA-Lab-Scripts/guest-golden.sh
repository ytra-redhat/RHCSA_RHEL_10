#!/bin/bash
# Run inside the newly installed golden guest, never on macOS.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo 'Run as root'; exit 1; }
[ "$(uname -m)" = aarch64 ] || { echo 'ARM64 Linux required'; exit 1; }
[ ! -f /etc/rhcsa-fusion-seeded ] || { echo 'Use a fresh golden, not an exam clone'; exit 1; }
[ ! -f /etc/rhcsa-fusion-golden ] || { echo 'Golden already prepared'; exit 1; }
[ "$(lsblk -dn -o TYPE | grep -cx disk)" = 1 ] || { echo 'Golden must have only the system disk'; exit 1; }
dnf install -y open-vm-tools NetworkManager firewalld openssh-server python3 \
  parted gdisk lvm2 xfsprogs e2fsprogs dosfstools nfs-utils autofs chrony \
  cronie at rsyslog rsync tar gzip bzip2 zip unzip acl bash-completion \
  policycoreutils-python-utils tuned bind-utils dnf-plugins-core flatpak
systemctl enable --now vmtoolsd NetworkManager sshd firewalld
systemctl set-default multi-user.target
[ "$(getenforce)" = Enforcing ] || { echo 'Set SELinux enforcing and reboot before bootstrap'; exit 1; }
sed -i 's/^GRUB_TIMEOUT=.*/GRUB_TIMEOUT=10/' /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg
# Identify NICs via the freshly generated Fusion template; two NICs are required.
mapfile -t NICS < <(find /sys/class/net -mindepth 1 -maxdepth 1 -type l -printf '%f\n' | grep -v '^lo$' | sort)
[ "${#NICS[@]}" = 2 ] || { echo 'Expected NAT + host-only NICs'; exit 1; }
echo 'Match NIC MACs with golden fusion-state.json on the Mac.'
ip -br link
read -r -p 'NAT interface name: ' NAT_IF
read -r -p 'Host-only interface name: ' LAB_IF
[ "$NAT_IF" != "$LAB_IF" ] && [[ " ${NICS[*]} " == *" $NAT_IF "* ]] && [[ " ${NICS[*]} " == *" $LAB_IF "* ]] || exit 1
# Golden is explicitly disposable. Remove its initial installer-generated Ethernet
# profiles to avoid competing autoconnect profiles in clones. Preserve other types.
while IFS= read -r id; do
 [ -n "$id" ] || continue
 [ "$(nmcli -g connection.type con show "$id")" != '802-3-ethernet' ] || nmcli con delete "$id"
done < <(nmcli -g UUID con show)
nmcli con add type ethernet ifname "$NAT_IF" con-name fusion-nat \
 ipv4.method auto ipv6.method auto connection.autoconnect yes
nmcli con add type ethernet ifname "$LAB_IF" con-name fusion-lab \
 ipv4.method disabled ipv6.method disabled connection.autoconnect yes
nmcli con mod fusion-lab connection.zone public
nmcli con up fusion-nat
nmcli con up fusion-lab
hostnamectl set-hostname rhel10-golden
# A normal non-sudo account is useful for SSH tests; root password stays known.
if ! id student >/dev/null 2>&1; then useradd -m student; fi
if id -nG student | tr ' ' '\n' | grep -qx wheel; then gpasswd -d student wheel; fi
passwd student
rm -f /etc/machine-id
systemd-machine-id-setup
printf '%s\n' 'jconwell-fusion-golden-v1' > /etc/rhcsa-fusion-golden
sync
echo 'Golden prepared. Shut down with systemctl poweroff, then create exam clones on the Mac.'
