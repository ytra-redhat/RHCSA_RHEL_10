# Examen 2 — volledige antwoordensleutel

35 antwoordsecties. Voer deze in taakvolgorde uit; in examen 3 komt T33 vóór T16. Lees de beginvoorwaarde bij elke taak. Reeds behaalde doelen hoef je niet opnieuw te veranderen.

Korte uitvoerregels: [ZO-VOER-JE-DE-OPDRACHTEN-UIT.md](ZO-VOER-JE-DE-OPDRACHTEN-UIT.md).
Alle systeemblokken hieronder zijn bedoeld voor een **rootconsole in de genoemde Linux-VM**. Blokken voor alice/emma zijn bedoeld voor een echte login van die gebruiker. Een rootprompt is geen Mac-terminal.
Voer antwoordsecties niet automatisch als één script uit: ze bevatten herstarts, interactieve editors, verwachte fouten en netwerk/diskwijzigingen. Bestandsentries worden één keer toegevoegd; inspecteer fstab/hosts vóór herhaling.
Guest-uitvoering is nog niet end-to-end bewezen; zie VALIDATIE.md. Functionele controles in de antwoorden zijn de acceptatiecriteria.

**T1 — Root recovery**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

Open GRUB with **e**. On the `linux` line change the standalone `ro` to `rw`, remove any `rd.break`, and append `init=/bin/bash enforcing=0`. Boot with Ctrl-X.
In the resulting root Bash (PID 1), run:
```bash
mount -o remount,rw /
passwd root
touch /.autorelabel
sync
exec /sbin/init
```
Set the password specified in the question. **Do not use exit or Ctrl-D in this Bash.** Wait for SELinux relabeling; it may restart the guest. Once normal login is available, reboot normally without editing GRUB. Verify:
```bash
passwd -S root
getenforce
cat /proc/cmdline
```
Expected: password status P, Enforcing unless a later task explicitly requests Permissive, and no `init=/bin/bash` or `enforcing=0`. A black screen alone does not identify a hang; capture the last console message.

---

**T2 — Target (delta)**

**Beginvoorwaarde:** seed voltooid op delta; gebruik het rootwachtwoord van de golden-installatie. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: delta. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
systemctl set-default graphical.target
reboot
```

Na de herstart: log opnieuw in op dezelfde VM als root en voer dit nieuwe blok uit.
```bash
systemctl get-default
systemctl is-active graphical.target
runlevel
```
Verwacht `graphical.target`, `active` en runlevel 5. Deze opdracht wijzigt het target; een desktop installeren is een afzonderlijke, optionele oefening. Een tekstlogin is normaal bij deze minimal-installatie. Delta kan in rescue starten: gebruik het rootwachtwoord dat je bij de golden-installatie hebt ingesteld. T1 wijzigt uitsluitend charlie.

---

**T3 — Bootloader**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
vi /etc/default/grub    # remove rhgb quiet; add audit=1 net.ifnames=0; GRUB_TIMEOUT=5
grub2-mkconfig -o /boot/grub2/grub.cfg --update-bls-cmdline
dracut -f
reboot
```

Na de herstart: log opnieuw in op dezelfde VM als root en voer dit nieuwe blok uit.
```bash
cat /proc/cmdline
```

> `net.ifnames=0` reverts to legacy `ethX` naming — do this **before** Task 4/5, since the interface name changes.

---

**T4 — Network (both nodes)**

**Beginvoorwaarde:** T3. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: both nodes. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

De **interface** is het apparaat (`enp2s0`, `enp3s0`, of na T3 `ethX`). Het **profiel** bevat de instellingen. `fusion-nat` hoort bij Fusion NAT en verzorgt internet; `fusion-lab` hoort bij host-only en verzorgt verkeer tussen de twee examen-VM's. We wijzigen uitsluitend het labprofiel en noemen dat daarna `lab-static`. De interface verandert daardoor niet van naam.

Voer dit blok op **charlie**, als root in de Fusion-console uit. Kopieer het volledig; vul geen UUID in. Het selecteert exact één bestaand labprofiel; bij geen of meerdere treffers blijft de configuratie intact en krijg je een STOP-melding.
```bash
configure_lab() {
 local lab_uuid name uuid
 local -a matches=()
 while IFS=: read -r uuid name; do
  case "$name" in fusion-lab|lab-static) matches+=("$uuid");; esac
 done < <(nmcli -t -f UUID,NAME connection show)
 if (( ${#matches[@]} != 1 )); then
  echo 'STOP: verwacht precies één fusion-lab of lab-static; toon nmcli -f NAME,UUID,DEVICE con show' >&2
  return 1
 fi
 lab_uuid=${matches[0]}
 nmcli con mod uuid "$lab_uuid" connection.id lab-static ipv4.method manual ipv4.addresses 10.20.30.11/24 ipv4.gateway '' ipv4.dns '' ipv4.never-default yes ipv6.method manual ipv6.addresses fd42::11/64 ipv6.gateway '' ipv6.dns '' ipv6.never-default yes connection.autoconnect yes || return
 nmcli con up uuid "$lab_uuid" || return
 hostnamectl set-hostname charlie.ex200.lab || return
}
configure_lab
unset -f configure_lab
```
Bij STOP: voer de volgende blokken niet uit. Bij succes staat het labadres op de interface die bij het MAC-gebonden profiel hoort. Je hoeft de interfacenaam niet te raden.


De **interface** is het apparaat (`enp2s0`, `enp3s0`, of na T3 `ethX`). Het **profiel** bevat de instellingen. `fusion-nat` hoort bij Fusion NAT en verzorgt internet; `fusion-lab` hoort bij host-only en verzorgt verkeer tussen de twee examen-VM's. We wijzigen uitsluitend het labprofiel en noemen dat daarna `lab-static`. De interface verandert daardoor niet van naam.

Voer dit blok op **delta**, als root in de Fusion-console uit. Kopieer het volledig; vul geen UUID in. Het selecteert exact één bestaand labprofiel; bij geen of meerdere treffers blijft de configuratie intact en krijg je een STOP-melding.
```bash
configure_lab() {
 local lab_uuid name uuid
 local -a matches=()
 while IFS=: read -r uuid name; do
  case "$name" in fusion-lab|lab-static) matches+=("$uuid");; esac
 done < <(nmcli -t -f UUID,NAME connection show)
 if (( ${#matches[@]} != 1 )); then
  echo 'STOP: verwacht precies één fusion-lab of lab-static; toon nmcli -f NAME,UUID,DEVICE con show' >&2
  return 1
 fi
 lab_uuid=${matches[0]}
 nmcli con mod uuid "$lab_uuid" connection.id lab-static ipv4.method manual ipv4.addresses 10.20.30.12/24 ipv4.gateway '' ipv4.dns '' ipv4.never-default yes ipv6.method manual ipv6.addresses fd42::12/64 ipv6.gateway '' ipv6.dns '' ipv6.never-default yes connection.autoconnect yes || return
 nmcli con up uuid "$lab_uuid" || return
 hostnamectl set-hostname delta.ex200.lab || return
}
configure_lab
unset -f configure_lab
```
Bij STOP: voer de volgende blokken niet uit. Bij succes staat het labadres op de interface die bij het MAC-gebonden profiel hoort. Je hoeft de interfacenaam niet te raden.

Op **beide VM's**, na succesvolle configuratie, als root:
```bash
# Verwijder eerst eventuele eerdere labregels met dezelfde namen, om dubbelen te voorkomen.
vi /etc/hosts
printf '10.20.30.11 charlie.ex200.lab charlie\n10.20.30.12 delta.ex200.lab delta\n' >> /etc/hosts
nmcli -f NAME,UUID,DEVICE con show
ip -br address
ip route
ip -6 route
```
De default route naar internet hoort bij NAT; het labprofiel heeft geen gateway. Test pas wanneer beide VM's zijn ingesteld.

Op **charlie**:
```bash
ping -c 2 delta
ping -6 -c 2 fd42::12
```
Op **delta**:
```bash
ping -c 2 charlie
ping -6 -c 2 fd42::11
```

---

**T5 — Custom firewall (charlie)**

**Beginvoorwaarde:** T4. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
firewall-cmd --permanent --new-zone=labzone
for service in ssh https dns; do firewall-cmd --permanent --zone=labzone --add-service="$service"; done
firewall-cmd --permanent --zone=labzone --add-port=9000-9010/tcp
firewall-cmd --set-default-zone=labzone
firewall-cmd --reload
nmcli con mod lab-static connection.zone labzone
nmcli con up lab-static
firewall-cmd --zone=labzone --list-all
firewall-cmd --permanent --zone=labzone --list-all
firewall-cmd --zone=labzone --add-rich-rule='rule family="ipv4" source address="10.20.30.100" drop' --timeout=60
firewall-cmd --zone=labzone --list-rich-rules
```
Inspect immediately, then again after 60 seconds: temporary rule should disappear. Do not reload immediately after adding it. --reload and --get-default-zone are global commands: omit --zone there.

---

**T6 — Users (charlie)**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
dnf install -y zsh
groupadd -g 6000 ops
groupadd -g 6001 qateam
groupadd -r -g 6002 auditors
mkdir -p /srv/users
useradd -m -u 2100 -g ops -G qateam -d /srv/users/emma emma
useradd -m -u 2101 -g qateam -G auditors -s /bin/zsh frank
useradd -m -u 2102 -g ops -c 'Gina — DBA' gina
useradd -m -u 2103 -g auditors -s /sbin/nologin henry
semanage fcontext -a -e /home /srv/users
restorecon -Rv /srv/users
chmod 700 /srv/users/emma /home/frank /home/gina /home/henry
for u in emma frank gina henry; do getent passwd "$u"; id "$u"; done
```

---

**T7 — Password policy (charlie)**

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
printf 'emma:Init!Pass2026\nfrank:Init!Pass2026\ngina:Init!Pass2026\nhenry:Init!Pass2026\n' | chpasswd
chage -m 3 -M 45 -W 7 -I 14 emma
chage -d 0 -I 5 frank
chage -E 2027-01-01 gina
mkdir -p /etc/security/pwquality.conf.d
cat > /etc/security/pwquality.conf.d/90-lab.conf <<'EOF'
minlen = 12
dcredit = -1
ucredit = -1
ocredit = -1
EOF
authselect current
grep pam_pwquality /etc/pam.d/system-auth
chage -l emma
chage -l frank
chage -l gina
```
In a real gina login run passwd and try a weak password; do not submit a successful replacement. Root can bypass quality enforcement by default. Account-expiry and password-expiry are different conditions.

---

**T8 — Sudo (charlie)**

**Beginvoorwaarde:** T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
visudo -f /etc/sudoers.d/lab_sudo
```
```sudoers
User_Alias OPSTEAM = emma, gina
User_Alias QAUSERS = frank
Cmnd_Alias NETADMIN = /usr/bin/nmcli, /usr/sbin/ip, /usr/sbin/ss
Cmnd_Alias SVCMGMT = /usr/bin/systemctl status *, /usr/bin/systemctl restart httpd
OPSTEAM ALL=(ALL) NOPASSWD: NETADMIN
QAUSERS ALL=(ALL) SVCMGMT
%auditors ALL=(ALL) /usr/bin/cat /var/log/*
```
```bash
chmod 440 /etc/sudoers.d/lab_sudo
visudo -c
sudo -l -U emma
sudo -l -U frank
```
Confirm actual binary paths with command -v. These broad argument wildcards are a lab exercise, not a hardened policy. Test a disallowed command as emma and confirm denial.

---

**T9 — ACLs (charlie)**

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
mkdir -p /srv/project/phoenix
chown gina:ops /srv/project/phoenix
chmod 2770 /srv/project/phoenix
setfacl -m u:frank:rwx,g:auditors:rx,u:henry:---,m::rwx /srv/project/phoenix
setfacl -d -m u:frank:rwx,g:auditors:rx,u:henry:---,m::rwx /srv/project/phoenix
getfacl /srv/project/phoenix
runuser -u gina -- sh -c 'printf "project
" > /srv/project/phoenix/test.txt'
runuser -u frank -- sh -c 'printf "edit
" >> /srv/project/phoenix/test.txt'
runuser -u henry -- cat /srv/project/phoenix/test.txt
```
Henry must fail. For directories read-only access requires r-x (x for traversal); inherited regular files normally have no executable bit.

---

**T10 — Umask and links**

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: both nodes. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

On charlie root:
```bash
cat > /etc/profile.d/99-ops-umask.sh <<'EOF'
if id -nG | tr ' ' '
' | grep -qx ops; then umask 0027; fi
EOF
runuser -l gina -c 'umask'
```
On delta root:
```bash
mkdir -p /opt/data
printf 'exam data\n' > /opt/data/original.txt
ln /opt/data/original.txt /opt/data/hardlink.txt
ln -s /opt/data/original.txt /root/softlink.txt
ls -li /opt/data/original.txt /opt/data/hardlink.txt /root/softlink.txt > /root/link_notes.txt
rm /opt/data/original.txt
cat /opt/data/hardlink.txt
cat /root/softlink.txt
printf 'Hardlink shares original inode; symlink has its own inode and now points to missing path.\n' >> /root/link_notes.txt
```
The last cat is expected to fail.

---

**T11 — SSH keys and Match**

**Beginvoorwaarde:** T4, T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie ↔ delta. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

Initially on delta console allow root password login temporarily to copy keys (sshd -T must confirm it), then create ops GID 6000 and emma UID 2100 /srv/users/emma, assign Init!Pass2026 and label /srv/users like /home. On delta root console, before copying keys:
```bash
groupadd -g 6000 ops
mkdir -p /srv/users
useradd -m -u 2100 -g ops -d /srv/users/emma emma
printf 'emma:Init!Pass2026\n' | chpasswd
semanage fcontext -a -e /home /srv/users
restorecon -Rv /srv/users
```
If group/account already exists, verify its IDs and skip creation; do not silently reuse wrong IDs.
On charlie root:
```bash
ssh-keygen -t ecdsa -b 521 -N '' -f /root/.ssh/id_ecdsa
ssh-copy-id root@delta
ssh -o BatchMode=yes root@delta hostname
```
In actual emma login on charlie:
```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519
# Enter passphrase Lab#2026 interactively, twice.
ssh-copy-id emma@delta
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh -o BatchMode=yes emma@delta hostname
```
Then on delta edit effective sshd config: global settings before any Match, and the Match block at the end. Earlier Include values can win; remove/adjust only conflicting lab directives.
```sshdconfig
PermitRootLogin prohibit-password
AllowUsers root emma frank
Match User emma
    PasswordAuthentication no
    AuthenticationMethods publickey
```
```bash
sshd -t
systemctl reload sshd
sshd -T -C user=emma,host=charlie.ex200.lab,addr=10.20.30.11 | grep -E '^(passwordauthentication|authenticationmethods|permitrootlogin|allowusers) '
```
Test key login before closing the console. Root key login must still work; emma password-only login must fail.

---

**T12 — Transfer (charlie root)**

**Beginvoorwaarde:** T11. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie ↔ delta. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
rsync -a --bwlimit=500 --delete /etc/skel/ root@delta:/tmp/skel_backup/
printf 'put /etc/hostname /tmp/hostname\nbye\n' > /root/sftp_batch.txt
sftp -b /root/sftp_batch.txt root@delta
sha256sum /etc/hostname
ssh root@delta sha256sum /tmp/hostname
```
Hashes must match; filenames differ intentionally.

---

**T13 — DVD repositories (charlie)**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
mkdir -p /mnt/rhel10
printf '/dev/sr0 /mnt/rhel10 iso9660 ro,nofail 0 0\n' >> /etc/fstab
systemctl daemon-reload
mount /mnt/rhel10
ls /mnt/rhel10/BaseOS/repodata /mnt/rhel10/AppStream/repodata
```
Find the distro key first: inspect /etc/os-release, the DVD root and /etc/pki/rpm-gpg. On Rocky 10, use its installed Rocky-10 key; on RHEL use the matching Red Hat key. Do not disable gpgcheck or use an unverified filename.
```bash
cat /etc/os-release
ls /etc/pki/rpm-gpg
read -r -p 'Absolute verified signing-key path: ' KEY
[[ -f $KEY ]] || { echo 'Key missing'; exit 1; }
rpm --import "$KEY"
```
The key must actually verify a package from this DVD (rpm -K); mere key import is not proof.
```bash
for repo in baseos appstream; do
 case "$repo" in baseos) directory=BaseOS; priority=10;; appstream) directory=AppStream; priority=20;; esac
 cat > "/etc/yum.repos.d/lab-$repo.repo" <<EOF
[lab-$repo]
name=Lab $directory DVD
baseurl=file:///mnt/rhel10/$directory
enabled=1
gpgcheck=1
gpgkey=file://$KEY
metadata_expire=1h
priority=$priority
EOF
done
dnf repolist enabled
dnf --disablerepo='*' --enablerepo=lab-baseos list available
```

---

**T14 — Flatpak (charlie)**

**Beginvoorwaarde:** T13. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie, requires GUI or CLI-only ok. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
dnf install -y flatpak
flatpak --system remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak --system search gedit
flatpak --system remote-info --arch=aarch64 flathub org.gnome.gedit
flatpak --system install -y flathub org.gnome.gedit
flatpak --system list
flatpak --system uninstall -y org.gnome.gedit
flatpak --system uninstall --unused -y
```
Internet is required. If app ID/ARM build is unavailable select a listed aarch64 app and record it. If offline record this procedure in /root/flatpak_procedure.txt and mark execution NOT TESTED.

---

**T15 — RPM config restoration (charlie)**

**Beginvoorwaarde:** T13. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
dnf install -y nano
rpm -q nano
rpm -V nano
cp -a /etc/nanorc /root/nanorc.before
printf '# lab modification\n' >> /etc/nanorc
rpm -V nano
# Config(noreplace) may survive reinstall: save modified copy and remove only this file.
cp -a /etc/nanorc /root/nanorc.modified
rm /etc/nanorc
dnf reinstall -y nano
rpm -V nano
rpm -qf /etc/hosts
rpm -ql chrony
rpm -qa --last
```
Check that /etc/nanorc exists and rpm -V no longer reports it. This intentionally discards only the lab edit; never blanket-delete package configs.

---

**T16 — parted scripted**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie, `/dev/nvme0n2`. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
parted -s /dev/nvme0n2 mklabel gpt
parted -s /dev/nvme0n2 mkpart primary xfs 1MiB 2049MiB
parted -s /dev/nvme0n2 mkpart primary linux-swap 2049MiB 3073MiB
parted -s /dev/nvme0n2 mkpart primary 3073MiB 100%
parted -s /dev/nvme0n2 set 3 lvm on
```
```bash
parted /dev/nvme0n2 align-check optimal 1
partprobe /dev/nvme0n2
lsblk /dev/nvme0n2
```

---

**T17 — XFS and VFAT (charlie)**

**Beginvoorwaarde:** T16. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
mkfs.xfs -L charlieXFS /dev/nvme0n2p1
parted -s /dev/nvme0n3 mklabel gpt
parted -s /dev/nvme0n3 mkpart primary fat32 1MiB 501MiB
partprobe /dev/nvme0n3
mkfs.vfat -n USBDATA /dev/nvme0n3p1
mkdir -p /mnt/charliexfs /mnt/usbdata
printf 'UUID=%s /mnt/charliexfs xfs defaults 0 0\n' "$(blkid -s UUID -o value /dev/nvme0n2p1)" >> /etc/fstab
printf 'LABEL=USBDATA /mnt/usbdata vfat noexec,nodev,nosuid 0 0\n' >> /etc/fstab
systemctl daemon-reload
mount /mnt/charliexfs
mount /mnt/usbdata
findmnt --mountpoint /mnt/charliexfs
findmnt --mountpoint /mnt/usbdata
```
Use only the blank extra disk nvme0n3; never nvme0n1. Compare required options after reboot.

---

**T18 — Swap file (delta)**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: delta. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
mkdir -p /swap
dd if=/dev/zero of=/swap/extraswap.img bs=1M count=1024 status=progress
chmod 600 /swap/extraswap.img
mkswap /swap/extraswap.img
printf '/swap/extraswap.img none swap defaults,pri=20 0 0\n' >> /etc/fstab
swapon /swap/extraswap.img
swapon --show=NAME,SIZE,PRIO
reboot
```
After boot confirm the same file has priority 20. dd allocates real blocks; do not create a sparse swap file.

---

**T19 — Striped and linear LVM (charlie)**

**Beginvoorwaarde:** T16. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie, `/dev/nvme0n2p3` + `/dev/nvme0n4`. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
pvcreate /dev/nvme0n2p3 /dev/nvme0n4
vgcreate -s 32M vg_lab2 /dev/nvme0n2p3 /dev/nvme0n4
lvcreate --type striped -i 2 -L 1G -n lv_stripe vg_lab2
lvcreate -l 80 -n lv_home2 vg_lab2
mkfs.ext4 /dev/vg_lab2/lv_stripe
mkfs.xfs /dev/vg_lab2/lv_home2
mkdir -p /mnt/stripe /mnt/home2
printf 'UUID=%s /mnt/stripe ext4 defaults 0 0\n' "$(blkid -s UUID -o value /dev/vg_lab2/lv_stripe)" >> /etc/fstab
printf 'UUID=%s /mnt/home2 xfs defaults 0 0\n' "$(blkid -s UUID -o value /dev/vg_lab2/lv_home2)" >> /etc/fstab
systemctl daemon-reload
mount /mnt/stripe
mount /mnt/home2
pvs
vgs
lvs -a -o lv_name,segtype,stripes,devices
```

---

**T20 — Migrate PV (charlie)**

**Beginvoorwaarde:** T19. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

Normal allocation can reject placing both stripes on one PV. --alloc anywhere relaxes that constraint; it does not convert the striped segment into linear.
```bash
pvmove --alloc anywhere /dev/nvme0n4 /dev/nvme0n2p3
vgreduce vg_lab2 /dev/nvme0n4
pvremove /dev/nvme0n4
wipefs -n /dev/nvme0n4
lvextend -l +100%FREE -r /dev/vg_lab2/lv_home2
lvs -a -o lv_name,segtype,stripes,devices
df -h /mnt/home2
```
After pvremove inspect signatures; wipefs -a is only needed if unwanted signatures remain on this explicitly disposable disk. This layout must be guest-tested with its actual LVM version.

---

**T21 — NFSv4 server (delta)**

**Beginvoorwaarde:** T4. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: delta. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
dnf install -y nfs-utils
mkdir -p /srv/nfs/projects /srv/nfs/archive
groupadd -g 1500 nfsuser
useradd -u 1500 -g nfsuser -M -s /sbin/nologin nfsuser
chown nfsuser:nfsuser /srv/nfs/projects
chmod 2770 /srv/nfs/projects
cat > /etc/exports.d/lab.exports <<'EOF'
/srv/nfs/projects 10.20.30.0/24(rw,sync,sec=sys,all_squash,anonuid=1500,anongid=1500,no_subtree_check)
/srv/nfs/archive charlie.ex200.lab(ro,sync,sec=sys,root_squash,no_subtree_check)
EOF
# In /etc/nfs.conf under the existing [nfsd] section set:
# vers3=n
# vers4=y
# vers4.2=y
vi /etc/nfs.conf
systemctl enable --now nfs-server
systemctl restart nfs-server
firewall-cmd --permanent --zone=public --add-service=nfs
firewall-cmd --reload
exportfs -rav
exportfs -v
cat /proc/fs/nfsd/versions
```
Expect -3 and +4/+4.2. sec=sys is AUTH_SYS, not Kerberos. Projects writes intentionally map to 1500; archive remains read-only.

---

**T22 — NFS client (charlie)**

**Beginvoorwaarde:** T21, T4. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
dnf install -y nfs-utils
mkdir -p /mnt/projects /mnt/archive
printf 'delta:/srv/nfs/projects /mnt/projects nfs4 _netdev,nofail,rw,vers=4.2 0 0\ndelta:/srv/nfs/archive /mnt/archive nfs4 _netdev,nofail,ro,vers=4.2 0 0\n' >> /etc/fstab
systemctl daemon-reload
mount /mnt/projects
mount /mnt/archive
touch /mnt/projects/root-test
touch /mnt/archive/should-fail
```
Second touch must fail with read-only filesystem. Confirm /srv/nfs/projects/root-test on delta with UID 1500.

---

**T23 — Autofs home**

**Beginvoorwaarde:** T11, T21, T22. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

On delta root create ops GID 6000, emma UID 2100 if not already created by T11. Use /srv/nfs/homes/emma as the server directory, owned 2100:6000, mode 700. Keep any SSH login home from T11 intact.
```bash
mkdir -p /srv/nfs/homes/emma
chown 2100:6000 /srv/nfs/homes/emma
chmod 700 /srv/nfs/homes/emma
semanage fcontext -a -e /home /srv/nfs/homes
restorecon -Rv /srv/nfs/homes
printf '/srv/nfs/homes 10.20.30.0/24(rw,sync,root_squash,no_subtree_check)\n' > /etc/exports.d/homes.exports
exportfs -rav
```
On charlie root: emma must be logged out before changing her home. Preserve the old home as backup; do not copy it onto an unmounted remote path.
```bash
dnf install -y autofs
printf '/net/homes /etc/auto.labhome --timeout=60 --ghost\n' > /etc/auto.master.d/labhome.autofs
printf '* -fstype=nfs4,rw,hard delta.ex200.lab:/srv/nfs/homes/&\n' > /etc/auto.labhome
cp -a /srv/users/emma /root/emma-home-before-autofs
usermod -d /net/homes/emma emma
setsebool -P use_nfs_home_dirs on
systemctl enable --now autofs
su - emma
```
In emma shell: pwd; cp -a /srv/users/emma/. "$HOME/"; touch ~/home-test; exit. The original home remains readable by emma; /root/emma-home-before-autofs is a private backup only. Leave the mount idle and do not repeatedly ls it. After at least one expiry interval inspect findmnt without accessing the path. Move desired existing home content as emma onto the mounted home, preserving her SSH keys if they are needed later.

---

**T24 — Permissions (charlie)**

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
chown gina:ops /opt/finance
chmod 2750 /opt/finance
chown gina:ops /opt/finance/reports /opt/finance/bin /opt/finance/bin/run_report.sh /opt/finance/private
chmod 2750 /opt/finance/reports
chmod 755 /opt/finance/bin
chmod 4754 /opt/finance/bin/run_report.sh
chmod 700 /opt/finance/private
find /usr/bin -type f -perm -4000 > /root/suid_list.txt
stat -c '%a %U:%G %n' /opt/finance /opt/finance/reports /opt/finance/private /opt/finance/bin/run_report.sh
```
SUID on a shell script does not elevate privilege on Linux. This step demonstrates the permission bit only.

---

**T25 — Chrony server/client**

**Beginvoorwaarde:** T4. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: both nodes. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

On delta root keep valid upstream sources and add allow 10.20.30.0/24. In an offline lab local stratum 10 can supply unsynchronised lab time; record this limitation.
```bash
printf 'allow 10.20.30.0/24\n' >> /etc/chrony.conf
# Alleen zonder bereikbare upstream: voeg local stratum 10 toe via vi.
vi /etc/chrony.conf
systemctl enable --now chronyd
systemctl restart chronyd
firewall-cmd --permanent --zone=public --add-service=ntp
firewall-cmd --reload
timedatectl set-timezone Asia/Tokyo
```
On charlie root:
```bash
sed -i 's/^pool /#pool /; s/^server /#server /' /etc/chrony.conf
printf 'server delta.ex200.lab iburst\n' >> /etc/chrony.conf
systemctl enable --now chronyd
systemctl restart chronyd
timedatectl set-timezone Europe/London
chronyc sources -v
chronyc tracking
```
Wait for a selected ^* source; ^+ is a candidate, not the selected source.

---

**T26 — TuneD (charlie)**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
dnf install -y tuned
mkdir -p /etc/tuned/lab-highio
cat > /etc/tuned/lab-highio/tuned.conf <<'EOF'
[main]
include=throughput-performance
[sysctl]
vm.dirty_ratio=40
vm.swappiness=10
[cpu]
governor=performance
EOF
systemctl enable --now tuned
tuned-adm profile lab-highio
tuned-adm active
sysctl vm.dirty_ratio vm.swappiness
ls /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```
No cpufreq paths means governor result N/A on this VM. Verify the profile and sysctl values after reboot; inspect tuned-ppd only if actually installed.

---

**T27 — Process management**

**Beginvoorwaarde:** T13. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
openssl speed -multi 2 &
dd if=/dev/zero of=/dev/shm/memtest bs=1M count=800 &
MEM_PID=$!
wait "$MEM_PID"
free -h
rm -f /dev/shm/memtest
free -h

ps -eo pid,pri,ni,pcpu,comm --sort=-pcpu | head
read -r -p "PID from the process list: " PID
renice -n 19 -p "$PID"
systemd-run --scope -p CPUQuota=20% timeout 30s openssl speed
pkill -f stress-ng
pkill -f openssl
systemctl restart chronyd
journalctl -u chronyd -n 20
```

---

**T28 — Journal and logrotate (charlie)**

**Beginvoorwaarde:** T7, T8. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
mkdir -p /var/log/journal /etc/systemd/journald.conf.d
printf '[Journal]\nStorage=persistent\nSystemMaxUse=500M\nForwardToSyslog=yes\n' > /etc/systemd/journald.conf.d/90-lab.conf
systemd-tmpfiles --create --prefix /var/log/journal
systemctl restart systemd-journald
journalctl --flush
printf 'authpriv.* /var/log/secure.lab\n' > /etc/rsyslog.d/90-lab.conf
rsyslogd -N1
systemctl enable --now rsyslog
systemctl restart rsyslog
cat > /etc/logrotate.d/secure.lab <<'EOF'
/var/log/secure.lab {
 weekly
 rotate 8
 missingok
 notifempty
 compress
 delaycompress
 create 0600 root root
 sharedscripts
 postrotate
  /usr/bin/systemctl kill -s HUP rsyslog.service >/dev/null 2>&1 || true
 endscript
}
EOF
logger -p authpriv.notice 'lab before rotation'
logrotate -d /etc/logrotate.d/secure.lab
logrotate -f /etc/logrotate.d/secure.lab
logger -p authpriv.notice 'lab after rotation'
journalctl _COMM=sudo
grep 'lab after rotation' /var/log/secure.lab
journalctl --rotate --vacuum-time=7d
```
As frank attempt a disallowed sudo command and record its journal and secure.lab events. Check actual syslog input configuration; forwarding plus imjournal can duplicate messages on some installations.

---

**T29 — Scheduling (charlie)**

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
systemctl enable --now atd crond
printf 'echo "at-fired $(date)" >> /var/log/at_lab.log\n' | at now + 3 minutes
atq
# Add with crontab -e -u emma:
# 15 7 * * 1-5 df -h > ~/disk_report.log
cat > /usr/local/bin/labhealth.sh <<'EOF'
#!/bin/bash
set -euo pipefail
{ uptime; free -m; df -h /; } >> /var/log/labhealth.log
EOF
chmod 755 /usr/local/bin/labhealth.sh
cat > /etc/systemd/system/labhealth.service <<'EOF'
[Service]
Type=oneshot
ExecStart=/usr/local/bin/labhealth.sh
EOF
cat > /etc/systemd/system/labhealth.timer <<'EOF'
[Timer]
OnCalendar=*-*-* 00/3:00:00
Persistent=true
[Install]
WantedBy=timers.target
EOF
systemctl daemon-reload
systemctl enable --now labhealth.timer
systemctl start labhealth.service
systemctl list-timers --all
systemd-analyze calendar '*-*-* 00/3:00:00'
```
At submission above is root; the quoted date expression is expanded at execution time.

---

**T30 — svcctl script**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
cat > /usr/local/bin/svcctl.sh <<'EOF'
#!/bin/bash
[[ $# == 2 ]] || { echo "Usage: $0 {start|stop|restart|status|check} service" >&2; exit 2; }
action=$1; service=$2
case "$action" in start|stop|restart|status|check) ;; *) echo "Usage: $0 {start|stop|restart|status|check} service" >&2; exit 2;; esac
if ! systemctl cat -- "$service" >/dev/null 2>&1; then echo 'Unknown service' >&2; exit 3; fi
case "$action" in
 check) if systemctl is-active --quiet -- "$service"; then echo RUNNING; else echo STOPPED; exit 1; fi;;
 *) systemctl "$action" -- "$service"; exit $?;;
esac
EOF
chmod 755 /usr/local/bin/svcctl.sh
bash -x /usr/local/bin/svcctl.sh check chronyd
svcctl.sh bogus chronyd; echo "$?"
svcctl.sh check nonexistent-lab.service; echo "$?"
```
Only change harmless lab services when testing start/stop/restart; keep console access.

---

**T31 — CSV users**

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
cat > /root/newusers.csv <<'EOF'
ivan,2200,6000,Ivan Petrov
julia,2201,6000,Julia Kim
kai,2202,6001,Kai Nguyen
EOF
cat > /usr/local/bin/csv_users.sh <<'EOF'
#!/bin/bash
set -euo pipefail
umask 077
touch /root/passwords.txt
chmod 600 /root/passwords.txt
while IFS=, read -r user uid gid fullname || [[ -n $user ]]; do
 [[ -z $user || $user == \#* ]] && continue
 [[ $user =~ ^[a-z_][a-z0-9_-]*$ && $uid =~ ^[0-9]+$ && $gid =~ ^[0-9]+$ ]] || exit 1
 getent group "$gid" >/dev/null
 if id "$user" >/dev/null 2>&1; then echo "Already exists: $user" >&2; exit 1; fi
 password=$(openssl rand -base64 18)
 useradd -m -u "$uid" -g "$gid" -c "$fullname" "$user"
 printf '%s:%s\n' "$user" "$password" | chpasswd
 printf '%s,%s\n' "$user" "$password" >> /root/passwords.txt
done < /root/newusers.csv
EOF
chmod 700 /usr/local/bin/csv_users.sh
csv_users.sh
stat -c '%a' /root/passwords.txt
```

---

**T32 — Health report**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
cat > /root/health_report.sh <<'EOF'
#!/bin/bash
set -euo pipefail
umask 077
mkdir -p /var/log/health
tmp=$(mktemp /var/log/health/.health.XXXXXX)
trap 'rm -f "$tmp"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
{
 hostname; uname -r; uptime
 ps -eo pid,pcpu,comm --sort=-pcpu | sed -n '1,6p'
 df -h
 systemctl --failed --no-pager
} > "$tmp"
mv "$tmp" "/var/log/health/$(hostname)-$(date +%F).log"
# One daily report per hostname; retain the newest 14, not just age>14.
mapfile -t old < <(find /var/log/health -maxdepth 1 -type f -name "$(hostname)-????-??-??.log" -printf '%f\n' | sort -r | tail -n +15)
for name in "${old[@]}"; do rm -- "/var/log/health/$name"; done
EOF
chmod 700 /root/health_report.sh
/root/health_report.sh
# Add via crontab -e: 0 6 2-31 * * /root/health_report.sh
systemctl enable --now crond
```
Question corrected: use a unique temporary file in the destination filesystem, allowing genuinely atomic rename; /tmp may be a separate filesystem.

---

**T33 — Custom webroot (charlie)**

**Beginvoorwaarde:** T13. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
setenforce 1
sed -i 's/^SELINUX=.*/SELINUX=enforcing/' /etc/selinux/config
dnf install -y httpd
mkdir -p /srv/websites/site1
printf 'Site1 charlie\n' > /srv/websites/site1/index.html
cat > /etc/httpd/conf.d/site1.conf <<'EOF'
<VirtualHost *:80>
DocumentRoot /srv/websites/site1
<Directory /srv/websites/site1>
Require all granted
</Directory>
</VirtualHost>
EOF
httpd -t
systemctl enable --now httpd
systemctl restart httpd
curl http://localhost/
journalctl -u httpd --no-pager
ausearch -m AVC -ts recent
semanage fcontext -a -t httpd_sys_content_t '/srv/websites(/.*)?'
restorecon -Rv /srv/websites
systemctl reset-failed httpd
systemctl restart httpd
curl --fail http://localhost/
ps -eZ | grep httpd
```
A webroot label problem normally causes 403 on a request, not a daemon startup failure. If testing remotely, add permanent http to labzone.

---

**T34 — Oplossing**

**Beginvoorwaarde:** T5, T11, T33. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

On charlie root edit effective global sshd config (before Match blocks) to contain both Port 22 and Port 2222. Verify include precedence, then:
```bash
vi /etc/ssh/sshd_config
semanage port -a -t ssh_port_t -p tcp 2222
firewall-cmd --permanent --zone=labzone --add-port=2222/tcp
firewall-cmd --reload
sshd -t
systemctl restart sshd
ss -tlnp
if getsebool ssh_sysadm_login; then
 setsebool -P ssh_sysadm_login on
else
 getsebool use_nfs_home_dirs && setsebool -P use_nfs_home_dirs on
fi
if getsebool container_manage_cgroup; then
 setsebool -P container_manage_cgroup on
else
 echo 'container_manage_cgroup ontbreekt in deze policy; dit subonderdeel is niet uitgevoerd.'
fi
cp /etc/motd /var/www/html/motd.txt
ls -Z /var/www/html/motd.txt
restorecon -v /var/www/html/motd.txt
```
Ordinary cp usually creates the destination policy label already; observe actual context instead of claiming it must be etc_t. Test port 2222 from delta.

---

**T35 — Rootless Nginx (charlie/emma)**

**Beginvoorwaarde:** T4, T5, T6, T23. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: charlie, as user `emma`. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

As root on the application VM:
```bash
dnf install -y podman
loginctl enable-linger emma
firewall-cmd --permanent --zone=labzone --add-port=9090/tcp
firewall-cmd --reload
```
Log in directly as emma via console/SSH (not merely sudo -u). Confirm XDG_RUNTIME_DIR and systemctl --user work. First inspect the actual ARM image; image tags/manifests and application paths are external prerequisites:
```bash
podman pull registry.access.redhat.com/ubi10/nginx-126
podman image inspect registry.access.redhat.com/ubi10/nginx-126
podman volume create emma-nginx-data
podman run --rm --user 0 -v emma-nginx-data:/data:Z registry.access.redhat.com/ubi10/ubi sh -c 'mkdir -p /data/html; printf "Emma Nginx OK\n" > /data/html/index.html; chown -R 1001:0 /data; chmod 755 /data /data/html; chmod 644 /data/html/index.html'
mkdir -p ~/.config/containers/systemd
cat > ~/.config/containers/systemd/emma-nginx.volume <<'EOF'
[Volume]
VolumeName=emma-nginx-data
EOF
cat > ~/.config/containers/systemd/emma-nginx.container <<'EOF'
[Unit]
Description=Lab web container
Wants=network-online.target
After=network-online.target
[Container]
Image=registry.access.redhat.com/ubi10/nginx-126
ContainerName=emma_nginx
PublishPort=9090:8080
Exec=nginx -g "daemon off;"
Volume=emma-nginx.volume:/opt/app-root/src:Z

[Service]
Restart=always
TimeoutStartSec=300
[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user start emma-nginx.service
systemctl --user status emma-nginx.service
curl --fail http://localhost:9090/
```
Do not enable the generated Quadlet service; [Install] is interpreted by the generator. Verify after a normal reboot and from the peer VM. If it fails inspect user journal, image port, path, directory traversal and SELinux labels; do not mark an untested image as verified.
Optional daily restart is a normal user systemd timer, not a Quadlet .timer:
```bash
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/emma-nginx-restart.service <<'EOF'
[Service]
Type=oneshot
ExecStart=/usr/bin/systemctl --user restart emma-nginx.service
EOF
cat > ~/.config/systemd/user/emma-nginx-restart.timer <<'EOF'
[Timer]
OnCalendar=*-*-* 03:00:00
[Install]
WantedBy=timers.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now emma-nginx-restart.timer
```
Create ~/.config/systemd/user first. The timer is optional unless the question explicitly requests it.
