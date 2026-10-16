#!/bin/bash
# Run ONLY in the Fusion console of the golden guest. May be repeated.
set -euo pipefail
[[ $(id -u) == 0 && $(uname -m) == aarch64 ]] || { echo 'Root on ARM Linux required'; exit 1; }
[[ -z ${SSH_CONNECTION:-} ]] || { echo 'Use Fusion console: network configuration changes'; exit 1; }
[[ ! -f /etc/rhcsa-fusion-seeded ]] || { echo 'This is an exam clone, not golden'; exit 1; }
[[ $(lsblk -dnr -o NAME,TYPE | awk '$2=="disk" && $1 !~ /^zram[0-9]+$/ {n++} END {print n+0}') == 1 ]] || { echo 'Golden must have one disk'; exit 1; }
[[ $(getenforce) == Enforcing ]] || { echo 'Enable SELinux enforcing and reboot first'; exit 1; }
dnf install -y open-vm-tools NetworkManager firewalld openssh-server python3 \
 parted util-linux lvm2 xfsprogs e2fsprogs dosfstools nfs-utils autofs chrony \
 cronie at rsyslog rsync tar gzip bzip2 zip unzip acl bash-completion \
 policycoreutils-python-utils tuned bind-utils dnf-plugins-core \
 openssl psmisc sysstat cpio man-db man-pages info coreutils-common audit logrotate
systemctl enable --now vmtoolsd NetworkManager sshd firewalld
systemctl set-default multi-user.target
ip -br link
read -r -p 'NAT interface (match mac0 in host state): ' NAT_IF
read -r -p 'Host-only interface (match mac1): ' LAB_IF
[[ $NAT_IF != "$LAB_IF" && $NAT_IF != lo && $LAB_IF != lo && -e /sys/class/net/$NAT_IF/address && -e /sys/class/net/$LAB_IF/address ]] || exit 1
for profile in fusion-nat fusion-lab; do
 if ! nmcli -g UUID con show "$profile" >/dev/null 2>&1; then
  nmcli con add type ethernet ifname '*' con-name "$profile" ipv4.method disabled ipv6.method disabled
 fi
done
nmcli con mod fusion-nat connection.interface-name '' 802-3-ethernet.mac-address "$(cat /sys/class/net/"$NAT_IF"/address)" ipv4.method auto ipv6.method auto connection.autoconnect yes
nmcli con mod fusion-lab connection.interface-name '' 802-3-ethernet.mac-address "$(cat /sys/class/net/"$LAB_IF"/address)" ipv4.method disabled ipv6.method disabled connection.autoconnect yes connection.zone public
# Disable competing installer Ethernet profiles only after replacements exist.
while IFS= read -r uuid; do
 type=$(nmcli -g connection.type con show "$uuid")
 name=$(nmcli -g connection.id con show "$uuid")
 if [[ $type == 802-3-ethernet && $name != fusion-nat && $name != fusion-lab ]]; then
  nmcli con mod "$uuid" connection.autoconnect no
 fi
done < <(nmcli -g UUID con show)
nmcli con up fusion-nat
nmcli con up fusion-lab
hostnamectl set-hostname rhel10-golden
id student >/dev/null 2>&1 || useradd -m student
if id -nG student | tr ' ' '\n' | grep -qx wheel; then gpasswd -d student wheel; fi
# sudo list mode may return 0 even when root lists a denied user.
# Accept only an explicit English denial; errors or grants stop preparation.
sudo_denied() {
 local report
 report=$(LC_ALL=C sudo -l -U "$1" 2>&1) || true
 printf '%s\n' "$report" | grep -Eq "^User $1 is not allowed to run sudo on .+\.$"
}
# Do not remove arbitrary sudoers entries. Stop and name the account to inspect.
if ! sudo_denied student; then
 echo 'student still has sudo rights. Inspect sudo -l -U student; remove only its explicit lab grants, then rerun.' >&2
 exit 1
fi
while IFS=: read -r account password uid gid gecos home shell; do
 if [[ $uid -ge 1000 && $uid -lt 65534 && $account != student ]] && ! sudo_denied "$account"; then
  echo "STOP: installation account $account still has sudo rights. Read BESTAANDE-VMS.md; remove only its lab grants on this new golden copy." >&2
  exit 1
 fi
done < /etc/passwd
for account in alice bob carol dave emma frank gina henry noah oscar; do
 if id "$account" >/dev/null 2>&1; then echo "Golden contains task account $account; use an unworked golden" >&2; exit 1; fi
done
for package in httpd tmux nano zsh; do
 if rpm -q "$package" >/dev/null 2>&1; then echo "Golden contains exercise package $package; remove it only from the new golden copy, then rerun" >&2; exit 1; fi
done
passwd student
vmware-toolbox-cmd timesync disable
printf '%s\n' 'jconwell-fusion-golden-v2' > /etc/rhcsa-fusion-golden
sync
echo 'Bootstrap complete. Read START-HIER.md: seal before cloning.'
