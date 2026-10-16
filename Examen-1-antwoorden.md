# Examen 1 — volledige antwoordensleutel

35 antwoordsecties. Voer deze in taakvolgorde uit; in examen 3 komt T33 vóór T16. Lees de beginvoorwaarde bij elke taak. Reeds behaalde doelen hoef je niet opnieuw te veranderen.

Korte uitvoerregels: [ZO-VOER-JE-DE-OPDRACHTEN-UIT.md](ZO-VOER-JE-DE-OPDRACHTEN-UIT.md).
Alle systeemblokken hieronder zijn bedoeld voor een **rootconsole in de genoemde Linux-VM**. Blokken voor alice/emma zijn bedoeld voor een echte login van die gebruiker. Een rootprompt is geen Mac-terminal.
Voer antwoordsecties niet automatisch als één script uit: ze bevatten herstarts, interactieve editors, verwachte fouten en netwerk/diskwijzigingen. Bestandsentries worden één keer toegevoegd; inspecteer fstab/hosts vóór herhaling.
Guest-uitvoering is nog niet end-to-end bewezen; zie VALIDATIE.md. Functionele controles in de antwoorden zijn de acceptatiecriteria.

**T1 — Root recovery**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: bravo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

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

**T2 — Boot target**

**Beginvoorwaarde:** T1. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: bravo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

Begin na T1 met normale rootlogin op bravo. De bedoelde examenbeginstand is `graphical.target`; dit zegt niets over de aanwezigheid van een desktop.
```bash
systemctl get-default
systemctl set-default multi-user.target
reboot
```
Na normale rootlogin:
```bash
systemctl get-default
systemctl is-active multi-user.target
```
Verwacht `multi-user.target` en `active`. Als dit vooraf al zo stond, is dit onderdeel al opgelost: noteer dat. Alleen om deze specifieke opdracht opnieuw te oefenen: zet eerst `systemctl set-default graphical.target`, herstart, en voer vervolgens de oplossing uit. Dit reset geen andere examenopdrachten.

---

**T3 — GRUB (alpha)**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

Edit /etc/default/grub. Set GRUB_TIMEOUT=10, GRUB_TIMEOUT_STYLE=countdown and append quiet once inside the quoted GRUB_CMDLINE_LINUX value; preserve root/LVM arguments.
```bash
vi /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg --update-bls-cmdline
reboot
```

Na de herstart: log opnieuw in op dezelfde VM als root en voer dit nieuwe blok uit.
```bash
cat /proc/cmdline
```
Expect quiet and a 10-second countdown at the next boot. If already correct, record that; do not add duplicate quiet.

---

**T4 — Network (both nodes)**

**Beginvoorwaarde:** T3. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: both nodes. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

De **interface** is het apparaat (`enp2s0`, `enp3s0`, of na T3 `ethX`). Het **profiel** bevat de instellingen. `fusion-nat` hoort bij Fusion NAT en verzorgt internet; `fusion-lab` hoort bij host-only en verzorgt verkeer tussen de twee examen-VM's. We wijzigen uitsluitend het labprofiel en noemen dat daarna `lab-static`. De interface verandert daardoor niet van naam.

Voer dit blok op **alpha**, als root in de Fusion-console uit. Kopieer het volledig; vul geen UUID in. Het selecteert exact één bestaand labprofiel; bij geen of meerdere treffers blijft de configuratie intact en krijg je een STOP-melding.
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
 nmcli con mod uuid "$lab_uuid" connection.id lab-static ipv4.method manual ipv4.addresses 192.168.100.10/24 ipv4.gateway '' ipv4.dns '' ipv4.never-default yes ipv6.method manual ipv6.addresses fd00::10/64 ipv6.gateway '' ipv6.dns '' ipv6.never-default yes connection.autoconnect yes || return
 nmcli con up uuid "$lab_uuid" || return
 hostnamectl set-hostname alpha.lab.local || return
}
configure_lab
unset -f configure_lab
```
Bij STOP: voer de volgende blokken niet uit. Bij succes staat het labadres op de interface die bij het MAC-gebonden profiel hoort. Je hoeft de interfacenaam niet te raden.


De **interface** is het apparaat (`enp2s0`, `enp3s0`, of na T3 `ethX`). Het **profiel** bevat de instellingen. `fusion-nat` hoort bij Fusion NAT en verzorgt internet; `fusion-lab` hoort bij host-only en verzorgt verkeer tussen de twee examen-VM's. We wijzigen uitsluitend het labprofiel en noemen dat daarna `lab-static`. De interface verandert daardoor niet van naam.

Voer dit blok op **bravo**, als root in de Fusion-console uit. Kopieer het volledig; vul geen UUID in. Het selecteert exact één bestaand labprofiel; bij geen of meerdere treffers blijft de configuratie intact en krijg je een STOP-melding.
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
 nmcli con mod uuid "$lab_uuid" connection.id lab-static ipv4.method manual ipv4.addresses 192.168.100.20/24 ipv4.gateway '' ipv4.dns '' ipv4.never-default yes ipv6.method manual ipv6.addresses fd00::20/64 ipv6.gateway '' ipv6.dns '' ipv6.never-default yes connection.autoconnect yes || return
 nmcli con up uuid "$lab_uuid" || return
 hostnamectl set-hostname bravo.lab.local || return
}
configure_lab
unset -f configure_lab
```
Bij STOP: voer de volgende blokken niet uit. Bij succes staat het labadres op de interface die bij het MAC-gebonden profiel hoort. Je hoeft de interfacenaam niet te raden.

Op **beide VM's**, na succesvolle configuratie, als root:
```bash
# Verwijder eerst eventuele eerdere labregels met dezelfde namen, om dubbelen te voorkomen.
vi /etc/hosts
printf '192.168.100.10 alpha.lab.local alpha\n192.168.100.20 bravo.lab.local bravo\n' >> /etc/hosts
nmcli -f NAME,UUID,DEVICE con show
ip -br address
ip route
ip -6 route
```
De default route naar internet hoort bij NAT; het labprofiel heeft geen gateway. Test pas wanneer beide VM's zijn ingesteld.

Op **alpha**:
```bash
ping -c 2 bravo
ping -6 -c 2 fd00::20
```
Op **bravo**:
```bash
ping -c 2 alpha
ping -6 -c 2 fd00::10
```

Voor het DNS-deel, op **beide VM's**:
```bash
nmcli con mod id fusion-nat ipv4.dns '8.8.8.8 1.1.1.1' ipv4.ignore-auto-dns yes
nmcli con up id fusion-nat
nmcli -f IP4.DNS device show
```
Dit verandert DNS op NAT; het statische labprofiel krijgt geen DNS of gateway.

---

**T5 — Firewall (alpha)**

**Beginvoorwaarde:** T4. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
systemctl enable --now firewalld
firewall-cmd --permanent --zone=public --add-service=ssh
firewall-cmd --permanent --zone=public --add-service=http
firewall-cmd --permanent --zone=internal --add-port=5900-5910/tcp
nmcli con mod lab-static connection.zone public
nmcli con up lab-static
firewall-cmd --reload
firewall-cmd --zone=public --query-service=http
firewall-cmd --permanent --zone=public --query-service=http
firewall-cmd --zone=public --add-port=8080/tcp
firewall-cmd --zone=public --query-port=8080/tcp
firewall-cmd --reload
firewall-cmd --zone=public --query-port=8080/tcp
```
Last query should return no (exit 1): the rule was runtime-only. Internal zone rule is stored; it applies only to traffic assigned to internal.

---

**T6 — Users (alpha)**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
groupadd -g 5000 sysadmins
groupadd -g 5001 developers
groupadd -g 5002 contractors
useradd -m -u 1050 -g developers -G sysadmins alice
useradd -m -u 1051 -g developers -G contractors -s /bin/bash bob
useradd -m -u 1052 -g contractors -s /sbin/nologin carol
useradd -m -u 1053 -g sysadmins -e "$(date -d '+90 days' +%F)" dave
for user in alice bob carol dave; do getent passwd "$user"; id "$user"; done
```

---

**T7 — Password aging**

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
for user in alice bob carol dave; do echo "${user}:Lab@12345"; done | chpasswd
chage alice -m 7 -M 60 -W 10
passwd bob -n 5 -x 90 -w 14 -i 10
chage carol -d 0
```

Create /etc/security/pwquality.conf.d/90-lab.conf with minlen=8, and verify pam_pwquality is in the active password stack:
```bash
mkdir -p /etc/security/pwquality.conf.d
printf 'minlen = 8\n' > /etc/security/pwquality.conf.d/90-lab.conf
authselect current
grep pam_pwquality /etc/pam.d/system-auth
chage -l carol
```
Test password rejection as a normal user, not as root. Carol remains nologin; chage only changes her expiry flag.

---

**T8 — Sudo (alpha)**

**Beginvoorwaarde:** T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

Edit with visudo, so syntax is checked before saving:
```bash
visudo -f /etc/sudoers.d/lab_sudo
```
```sudoers
Cmnd_Alias PKGMGMT = /usr/bin/dnf
%sysadmins ALL=(ALL) NOPASSWD: ALL
%developers ALL=(ALL) PKGMGMT, /usr/bin/systemctl
alice ALL=(ALL) /usr/sbin/useradd, /usr/sbin/userdel
```
```bash
chmod 440 /etc/sudoers.d/lab_sudo
visudo -c
sudo -l -U alice
sudo -l -U bob
```
Alice also inherits unrestricted sudo from sysadmins. Her explicit rule cannot restrict those grants.

---

**T9 — Set-GID collaborative directory**

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
mkdir -p /data/devshare
chown alice:developers /data/devshare
chmod 3770 /data/devshare
```

Mode `3770` = SGID (2000) + sticky (1000) + `rwxrwx---`.
```bash
runuser -u bob -- touch /data/devshare/bob-test
stat -c "%U:%G %a" /data/devshare/bob-test
```

---

**T10 — Umask (both)**

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: both nodes. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
printf 'umask 0007\n' > /etc/profile.d/99-lab-umask.sh
runuser -l student -c 'umask; touch ~/mask-test; mkdir ~/mask-dir; stat -c "%a" ~/mask-test ~/mask-dir'
```
Expect 0007, 660, 770 in a fresh Bash login. This controls interactive login defaults; programs can explicitly request stricter modes. Do not claim it forces all daemons or applications to use these permissions.

---

**T11 — SSH (alpha → bravo)**

**Beginvoorwaarde:** T1, T4, T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha → bravo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

Op bravo, als root in de console, open de configuratie en zet `PermitRootLogin yes` en `PasswordAuthentication yes` in het globale deel vóór eventuele `Match`-blokken. Inspecteer ook de include-bestanden: sshd gebruikt bij deze opties de eerste gevonden waarde. Dit is uitsluitend de exameninstelling.
```bash
vi /etc/ssh/sshd_config
ls /etc/ssh/sshd_config.d
```
Valideer en herstart. Ga alleen verder als `sshd -T` daadwerkelijk beide waarden `yes` toont:
```bash
sshd -t
systemctl restart sshd
sshd -T | grep -E "^(permitrootlogin|passwordauthentication) "
groupadd -g 5001 developers
useradd -m -u 1050 -g developers alice
printf 'alice:Lab@12345\n' | chpasswd
```
On alpha root:
```bash
ssh-keygen -t rsa -b 4096 -N "" -f /root/.ssh/id_rsa
ssh-copy-id root@bravo
ssh -o BatchMode=yes root@bravo hostname
```
In an actual alice login on alpha:
```bash
ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519
ssh-copy-id alice@bravo
ssh -o BatchMode=yes alice@bravo hostname
```
Do not overwrite an existing private key; choose a new filename and use -i if necessary.

---

**T12 — Transfers (alpha root)**

**Beginvoorwaarde:** T11. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha → bravo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
scp /etc/hosts root@bravo:/tmp/hosts_from_alpha
rsync -a /etc/sysconfig/ root@bravo:/tmp/sysconfig_backup/
sftp root@bravo
```
Inside sftp:
```text
put /etc/motd /tmp/motd
bye
```
```bash
ssh root@bravo "ls -l /tmp/hosts_from_alpha /tmp/motd; ls /tmp/sysconfig_backup"
```

---

**T13 — Repositories**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
mkdir -p /mnt/rhel10iso
mount /dev/sr0 /mnt/rhel10iso

# Create the repo 
tee /etc/yum.repos.d/rhel10-local.repo >/dev/null <<'EOF'
[BaseOS]
name=Base OS Packages from DVD
baseurl=file:///mnt/rhel10iso/BaseOS
enabled=1
gpgcheck=0

[AppStream]
name=AppStream Packages from DVD
baseurl=file:///mnt/rhel10iso/AppStream
enabled=1
gpgcheck=0
EOF

# Verify
dnf repolist
ls /mnt/rhel10iso/

# Make persist past reboot
echo '/dev/sr0  /mnt/rhel10iso  iso9660  ro,nofail  0 0' | tee -a /etc/fstab

# Test persistence without reboot
umount /mnt/rhel10iso 2>/dev/null
systemctl daemon-reload
mount -a
dnf repolist
ls /mnt/rhel10iso/
```

---

**T14 — Package management**

**Beginvoorwaarde:** T13. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
rpm -q httpd
# Expected absent before installation on a fresh clone.
dnf install vim-enhanced tmux wget httpd -y
rpm -qc httpd
mkdir -p /root/downloads
dnf download --destdir /root/downloads/ nmap
rpm -K /root/downloads/nmap-*.rpm
# NOKEY betekent: ondertekeningssleutel ontbreekt; dit is geen bewezen geldige handtekening.
dnf install -y /root/downloads/nmap-*.rpm
rpm -e nmap

# Verify Uninstall, use before uninstall to verify present
rpm -qa nmap
```

---

**T15 — Package groups, Flatpak, versioned RPMs**

**Beginvoorwaarde:** T13. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
# Part A
dnf group list
dnf group info "Development Tools"
dnf group install "Development Tools" -y
dnf group remove "Development Tools" -y

# Part B: eerst het ontbrekende programma installeren. Internet vereist.
dnf install -y flatpak
flatpak --system remotes
flatpak --system remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak --system search gimp
flatpak --system install flathub org.gimp.GIMP -y
flatpak --system list
# Optional in a graphical ordinary-user session: flatpak run org.gimp.GIMP
flatpak --system update -y
flatpak --system uninstall org.gimp.GIMP -y
flatpak --system uninstall --unused -y

# Part C
dnf list postgresql\*        # discover available versioned packages
dnf install postgresql-server -y
rpm -q postgresql-server
```

Record what the installed DNF actually supports:
```bash
dnf --version
dnf module list postgresql
```
If modularity is unsupported or no stream is listed, record that output. Do not infer an available module from legacy instructions; install the actual RPM package.

---

**T16 — GPT partitions**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: bravo, /dev/nvme0n2. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
# Open fdisk
fdisk /dev/nvme0n2
```

Typ onderstaande toetsinvoer uitsluitend **binnen fdisk**, niet in Bash.

```text
# Inside fdisk:
g          # Create GPT partition table

n          # Create nvme0n2p1
<Enter>    # Partition number 1
<Enter>    # First sector
+1G        # Size

n          # Create nvme0n2p2
<Enter>    # Partition number 2
<Enter>    # First sector
+500M      # Size

t          # Change partition type
2          # Select partition 2
L          # List types; select Linux swap from the actual list
0657FD6D-A4AB-43C4-84E5-0933C84B4F4F # Volledige Linux-swap-type-GUID

n          # Create nvme0n2p3
<Enter>    # Partition number 3
<Enter>    # First sector
+2G        # Size

p          # Verify partition layout

w          # Write changes and exit
```

```bash
# Inform the kernel of partition table changes
partprobe /dev/nvme0n2

# Verify
lsblk
fdisk -l /dev/nvme0n2
```

Expected Result:

```text
/dev/nvme0n2p1    1G    Linux filesystem
/dev/nvme0n2p2  500M    Linux swap
/dev/nvme0n2p3    2G    Linux filesystem
```

---

**T17 — Filesystems by UUID and LABEL**

**Beginvoorwaarde:** T16. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: bravo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
# Create filesystems
mkfs.xfs /dev/nvme0n2p1
mkfs.ext4 -L DATASTORE /dev/nvme0n2p3

# Create mount points
mkdir -p /mnt/xfs_data
mkdir -p /mnt/ext4_data

# Get UUID of nvme0n2p1
UUID=$(blkid -s UUID -o value /dev/nvme0n2p1)

# Add persistent mounts to /etc/fstab
echo "UUID=${UUID} /mnt/xfs_data xfs defaults 0 0" | tee -a /etc/fstab
echo "LABEL=DATASTORE /mnt/ext4_data ext4 defaults 0 0" | tee -a /etc/fstab

# Mount all filesystems
systemctl daemon-reload
mount -a

# Verify
df -hT
lsblk -f

# Create test files
touch /mnt/xfs_data/xfs_test.txt
touch /mnt/ext4_data/ext4_test.txt

# Reboot and verify persistence
reboot
```

After reboot:

```bash
df -hT
ls /mnt/xfs_data
ls /mnt/ext4_data
```

Expected Result:

```text
/dev/nvme0n2p1 mounted on /mnt/xfs_data (xfs) using UUID=
/dev/nvme0n2p3 mounted on /mnt/ext4_data (ext4) using LABEL=DATASTORE

/mnt/xfs_data/xfs_test.txt exists
/mnt/ext4_data/ext4_test.txt exists
```

---

**T18 — Swap with priority**

**Beginvoorwaarde:** T16. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: bravo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
# Create swap signature
mkswap -L EXTRASWAP /dev/nvme0n2p2

# Get UUID
UUID=$(blkid -s UUID -o value /dev/nvme0n2p2)

# Add persistent swap entry with priority 10
echo "UUID=${UUID} none swap defaults,pri=10 0 0" | tee -a /etc/fstab

# Verify fstab
tail -1 /etc/fstab

# Enable swap
swapon -a

# Verify
swapon --show
free -h

# Reboot and verify persistence
reboot
```

After reboot:

```bash
swapon --show
free -h
```

Expected Result:

```text
NAME      TYPE SIZE USED PRIO
/dev/nvme0n2p2 partition 500M   0B   10
```

And:

```text
Total swap: original swap plus the extra 500 MiB partition
```

---

**T19 — LVM**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: bravo, /dev/nvme0n3. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
# Create physical volume
pvcreate /dev/nvme0n3

# Create volume group with 16 MiB PE size
vgcreate -s 16M vg_lab /dev/nvme0n3

# Create logical volumes
lvcreate -L 512M -n lv_data vg_lab
lvcreate -l 25 -n lv_logs vg_lab

# Format logical volumes
mkfs.xfs /dev/vg_lab/lv_data
mkfs.ext4 /dev/vg_lab/lv_logs

# Create mount points
mkdir -p /mnt/lv_data
mkdir -p /mnt/lv_logs

# Get UUIDs
UUID_DATA=$(blkid -s UUID -o value /dev/vg_lab/lv_data)
UUID_LOGS=$(blkid -s UUID -o value /dev/vg_lab/lv_logs)

# Add persistent mounts
echo "UUID=${UUID_DATA} /mnt/lv_data xfs defaults 0 0" | tee -a /etc/fstab
echo "UUID=${UUID_LOGS} /mnt/lv_logs ext4 defaults 0 0" | tee -a /etc/fstab

# Verify fstab
tail -2 /etc/fstab

# Mount and verify
systemctl daemon-reload
mount -a
df -hT

# Verify LVM layout
pvs
vgs
lvs
```

Expected Result:

```text
PV: /dev/nvme0n3     VG: vg_lab
VG PE size: 16.00 MiB
lv_data  512.00m  (XFS)   -> /mnt/lv_data
lv_logs  400.00m  (ext4)  -> /mnt/lv_logs     # 25 extents x 16 MiB
```

---

**T20 — Extend an LV**

**Beginvoorwaarde:** T19. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: bravo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
# Verify free space in the volume group
vgs vg_lab

# Extend LV to 1 GiB and grow filesystem in one command
lvextend -L 1G -r /dev/vg_lab/lv_data

# Confirm new size
df -h /mnt/lv_data
lvs
```

Expected Result:

```text
lv_data  vg_lab  1.00g   -> /mnt/lv_data (XFS)

df -h shows /mnt/lv_data ~1.0G
```

---

**T21 — NFS server (bravo)**

**Beginvoorwaarde:** T4. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: bravo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

Choose one policy: this lab maps shared writes to nfsuser 1500 using all_squash. This sacrifices per-user ownership intentionally; no_root_squash is not needed.
```bash
dnf install -y nfs-utils
groupadd -g 1500 nfsuser
useradd -u 1500 -g nfsuser -M -s /sbin/nologin nfsuser
mkdir -p /export/shared /export/readonly
chown nfsuser:nfsuser /export/shared
chmod 2770 /export/shared
printf '/export/shared 192.168.100.0/24(rw,sync,all_squash,anonuid=1500,anongid=1500,no_subtree_check)\n/export/readonly 192.168.100.10(ro,sync,root_squash,no_subtree_check)\n' > /etc/exports.d/lab.exports
systemctl enable --now nfs-server
for service in nfs mountd rpc-bind; do firewall-cmd --permanent --zone=public --add-service="$service"; done
firewall-cmd --reload
exportfs -rav
exportfs -v
```

---

**T22 — NFS client**

**Beginvoorwaarde:** T21, T4. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
# Install NFS utilities (needed for the client too)
dnf install -y nfs-utils

# Create mount points
mkdir -p /mnt/nfs_shared
mkdir -p /mnt/nfs_ro

# Add persistent NFS entries to /etc/fstab
echo "192.168.100.20:/export/shared /mnt/nfs_shared nfs _netdev 0 0" | tee -a /etc/fstab
echo "192.168.100.20:/export/readonly /mnt/nfs_ro nfs _netdev 0 0" | tee -a /etc/fstab

# Verify fstab
tail -2 /etc/fstab

# Mount and verify
systemctl daemon-reload
mount -a
df -hT

# Create test file on the shared (rw) mount
touch /mnt/nfs_shared/from_alpha.txt
ls -l /mnt/nfs_shared
```

On bravo, confirm the file appeared:

```bash
ls -l /export/shared
```

Expected Result:

```text
192.168.100.20:/export/shared   -> /mnt/nfs_shared  (nfs4)
192.168.100.20:/export/readonly -> /mnt/nfs_ro       (nfs4)

/export/shared/from_alpha.txt   visible on bravo
```

---

**T23 — Autofs homes**

**Beginvoorwaarde:** T21, T4. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

On bravo root:
```bash
mkdir -p /export/home
groupadd -g 1600 autouser
useradd -m -u 1600 -g autouser -d /export/home/autouser autouser
passwd autouser
semanage fcontext -a -e /home /export/home
restorecon -Rv /export/home
printf '/export/home 192.168.100.0/24(rw,sync,root_squash,no_subtree_check)\n' > /etc/exports.d/home.exports
exportfs -rav
```
On alpha root:
```bash
dnf install -y autofs
groupadd -g 1600 autouser
useradd -M -u 1600 -g autouser -d /mnt/autohome/autouser autouser
passwd autouser
printf '/- /etc/auto.direct\n' > /etc/auto.master.d/direct.autofs
printf '/autodir -fstype=nfs4,rw,hard bravo:/export/shared\n' > /etc/auto.direct
printf '/mnt/autohome /etc/auto.home\n' > /etc/auto.master.d/home.autofs
printf '* -fstype=nfs4,rw,hard bravo:/export/home/&\n' > /etc/auto.home
setsebool -P use_nfs_home_dirs on
systemctl enable --now autofs
ls /autodir
su - autouser
```
In autouser shell:
```bash
pwd
touch ~/from-alpha
exit
```
Verify on bravo: /export/home/autouser/from-alpha is UID 1600. Do not create a local home at the automount path.

---

**T24 — Permission diagnostics**

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
# Fix /var/www/html — root:root, world-readable, not world-writable
chown root:root /var/www/html
chmod 755 /var/www/html

# Verify
ls -ld /var/www/html

# Create /secure/app — alice:developers, no access for others, SGID
mkdir -p /secure/app
chown alice:developers /secure/app
chmod 2770 /secure/app

# Verify
ls -ld /secure/app


# Fix /var/tmp/badperms — 640, bob:developers
touch /var/tmp/badperms
chown bob:developers /var/tmp/badperms
chmod 640 /var/tmp/badperms

# Verify
ls -l /var/tmp/badperms

# Find world-writable files under /etc and save the list
find /etc -perm -o+w -type f > /root/world_writable.txt

# Verify
cat /root/world_writable.txt
```

**Expected Results:**

```text
/var/www/html   drwxr-xr-x  root root
/secure/app     drwxrws---  alice developers
/var/tmp/badperms   -rw-r-----  bob developers
/root/world_writable.txt   contains any world-writable files found under /etc
```

---

**T25 — Chrony**

**Beginvoorwaarde:** T4. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: both nodes. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
# Install chrony if not present
dnf install -y chrony

# Add the primary NTP source to /etc/chrony.conf
# (comment out existing pool/server lines first for a clean config)
sed -i 's/^pool /#pool /; s/^server /#server /' /etc/chrony.conf
echo "pool 2.rhel.pool.ntp.org iburst" | tee -a /etc/chrony.conf

# Verify the line was added
grep "2.rhel.pool.ntp.org" /etc/chrony.conf

# Enable and start chronyd
systemctl enable --now chronyd

# Restart to apply config changes, then verify
systemctl restart chronyd
chronyc tracking
chronyc sources -v
timedatectl

# Timezone — alpha
timedatectl set-timezone America/Chicago
timedatectl

```

Alleen op **bravo**, als root:
```bash
timedatectl set-timezone UTC
timedatectl
```

---

**T26 — Tuned**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
# Install, enable, and start tuned
dnf install -y tuned
systemctl enable --now tuned

# List all available profiles
tuned-adm list

# Show the currently active profile
tuned-adm active

# Change active profile to throughput-performance
tuned-adm profile throughput-performance

# Verify the active profile
tuned-adm active

# Create the merged custom profile 'lab-custom'
mkdir -p /etc/tuned/lab-custom
tee /etc/tuned/lab-custom/tuned.conf <<'EOF'
[main]
summary=Custom merged profile: virtual-guest + powersave
include=virtual-guest,powersave
EOF

# Apply lab-custom and verify
tuned-adm profile lab-custom

systemctl is-enabled tuned
cat /etc/tuned/active_profile
cat /etc/tuned/profile_mode
# Optional integration: inspect only if installed; no assumed ppd layer.
systemctl status tuned-ppd.service

# Reboot and verify
reboot
```

Na herstart opnieuw als root op dezelfde VM:
```bash

# Verify
tuned-adm active       # confirm lab-custom is current
tuned-adm verify  # check applied settings match the profile (may warn on VMs)
tuned-adm list | grep lab-custom   # confirm it appears in the profile list
```

**Expected Results:**

```text
tuned-adm active  ->  Current active profile: lab-custom
```

---

**T27 — Oplossing**

**Beginvoorwaarde:** T14. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

Install psmisc/sysstat if missing; kill only the lab processes.


```bash
# Launch three background dd processes
dd if=/dev/zero of=/dev/null &
dd if=/dev/zero of=/dev/null &
dd if=/dev/zero of=/dev/null &

# Identify them
ps -C dd -o pid,ni,pcpu,comm
# or watch live:
top -c            # press 'q' to quit
# or:
pidstat 1 3       # 1-sec samples, 3 times

# Grab one PID to work with
PID=$(pgrep -n dd)     # newest dd process
echo "$PID"

# Set niceness to 10 (raising nice = lower priority, allowed as user)
renice -n 10 -p "$PID"

# Set niceness to -5 (lowering nice = higher priority, requires root)
renice -n -5 -p "$PID"

# Verify the nice change
ps -o pid,ni,comm -p "$PID"

# Kill all dd processes
killall dd

# Confirm none remain
pgrep -x dd || echo "no dd processes running"
ps -C dd

# Signal lifecycle on a sleep process
sleep 3600 &
SPID=$!
echo "sleep PID: $SPID"

kill -SIGSTOP "$SPID"     # pause (state T)
ps -o pid,stat,comm -p "$SPID"

kill -SIGCONT "$SPID"     # resume (state S)
ps -o pid,stat,comm -p "$SPID"

kill -SIGTERM "$SPID"     # terminate
pgrep -x sleep || echo "sleep terminated"

# Launch a niced process
nice -n 15 sleep 1000 &
ps -o pid,stat,ni,comm -p $!
```

Expected Results:

```text
Step 3:  NI = 10   (as regular user)
Step 4:  NI = -5   (root required)
Step 5:  all dd processes gone
Step 6:  STAT T (stopped) -> S (sleeping) -> process ends
Step 7:  new sleep with NI = 15
```

---

**T28 — Persistent journal and rsyslog**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: both nodes. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
# Configure journald for persistent storage
mkdir -p /etc/systemd/journald.conf.d
printf '[Journal]\nStorage=persistent\n' | tee /etc/systemd/journald.conf.d/90-rhcsa.conf
systemd-tmpfiles --create --prefix /var/log/journal

# Create the persistent journal directory (journald will also do this itself on restart)
mkdir -p /var/log/journal
systemd-tmpfiles --create --prefix /var/log/journal

# Restart journald to apply
systemctl restart systemd-journald
journalctl --flush

# Verify the directory exists and journald is using it
ls -ld /var/log/journal
journalctl --disk-usage

# Logs since last boot
journalctl -b

# Filter logs for the sshd service
journalctl -u sshd

# Only error-level and above
journalctl -p err

# Last 50 lines
journalctl -n 50

# Configure rsyslog to write all *.info messages to /var/log/messages.info
echo "*.info    /var/log/messages.info" | tee -a /etc/rsyslog.conf

# Restart rsyslog to apply
systemctl enable --now rsyslog
systemctl restart rsyslog

# Send a test message and verify it landed in the right log
logger "RHCSA test message from $(hostname)"
grep "RHCSA test message" /var/log/messages.info
```

Expected Results:

```text
Step 1-2:  /etc/systemd/journald.conf.d/90-rhcsa.conf has Storage=persistent; /var/log/journal/ exists after restart
Step 3:    journalctl -b, -u sshd, -p err, -n 50 all return filtered output
Step 4:    /var/log/messages.info receives *.info and higher messages after rsyslog restart
Step 5:    logger test line appears in /var/log/messages.info
```

---

**T29 — at, cron, systemd timer**

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
# 1. at — one-time job in 5 minutes
# Ensure atd is running
systemctl enable --now atd

# Schedule the job
echo 'echo "Scheduled at task ran" >> /var/log/at_test.log' | at now + 5 minutes

# Verify it's queued
atq
at -l              # same thing

# 2. cron — daily job for user alice at 8:00 AM
# Edit alice's crontab (as alice, or use -u as root)
crontab -e -u alice

# Add this line:
# In crontab editor: 0 8 * * * date >> ~/cron_test.log

# Verify:
crontab -l -u alice

# 3. systemd timer — hourly script
# Create the script
tee /usr/local/bin/hourly_check.sh <<'EOF'
#!/bin/bash
echo "$(date)" >> /var/log/hourly.log
EOF
chmod +x /usr/local/bin/hourly_check.sh

# Create the service unit
tee /etc/systemd/system/hourly-check.service <<'EOF'
[Unit]
Description=Hourly check script

[Service]
Type=oneshot
ExecStart=/usr/local/bin/hourly_check.sh
EOF

# Create the timer unit
tee /etc/systemd/system/hourly-check.timer <<'EOF'
[Unit]
Description=Run hourly-check every hour

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Reload systemd, enable and start the TIMER (not the service)
systemctl daemon-reload
systemctl enable --now hourly-check.timer

# Verify
systemctl status hourly-check.timer
systemctl list-timers hourly-check.timer
```

Expected Results:

```text
at:      atq shows one queued job
cron:    crontab -l -u alice shows the 8:00 AM line
timer:   list-timers shows hourly-check.timer with a NEXT run time
```

---

**T30 — syscheck script**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
cat > /usr/local/bin/syscheck.sh <<'EOF'
#!/bin/bash
set -euo pipefail
[[ $# == 1 ]] || { echo "Usage: $0 {cpu|mem|disk|all}" >&2; exit 1; }
cpu() { lscpu; }
mem() { free -h; }
disk() { df -hT; }
case "$1" in
 cpu) cpu;; mem) mem;; disk) disk;; all) cpu; mem; disk;;
 *) echo "Usage: $0 {cpu|mem|disk|all}" >&2; exit 1;;
esac
EOF
chmod 755 /usr/local/bin/syscheck.sh
for option in cpu mem disk all; do syscheck.sh "$option"; done
syscheck.sh; echo "exit=$?"
syscheck.sh invalid; echo "exit=$?"
syscheck.sh cpu mem; echo "exit=$?"
```

---

**T31 — Bulk users**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
printf 'testuser1\ntestuser2\ntestuser3\ntestuser4\ntestuser5\n' > /root/userlist.txt
cat > /usr/local/bin/bulk_users.sh <<'EOF'
#!/bin/bash
set -euo pipefail
[[ $(id -u) == 0 ]] || exit 1
for user in $(cat /root/userlist.txt); do
 [[ $user =~ ^[a-z_][a-z0-9_-]*$ ]] || { echo "Invalid user: $user" >&2; exit 1; }
 if id "$user" >/dev/null 2>&1; then echo "$user already exists"; continue; fi
 useradd -m "$user"
 printf '%s:%s\n' "$user" "$user" | chpasswd
 echo "$user created and password set"
done
EOF
chmod 700 /usr/local/bin/bulk_users.sh
bulk_users.sh
```
Username-as-password is only this requested lab exercise, not an operational password policy.

---

**T32 — Reliable backup**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
cat > /root/etcbackup.sh <<'EOF'
#!/bin/bash
set -euo pipefail
umask 077
mkdir -p /root/backups
output=/root/backups/etc_backup_$(date +%F).tar.gz
tmp=$(mktemp /root/backups/.backup.XXXXXX)
trap 'rm -f "$tmp"' EXIT
if tar -czf "$tmp" -C / etc; then
 mv "$tmp" "$output"
 printf '%s Created %s\n' "$(date -Is)" "$output" >> /var/log/etcbackup.log
 find /root/backups -type f -name 'etc_backup_*.tar.gz' -mtime +7 -delete
else
 printf '%s FAILED %s\n' "$(date -Is)" "$output" >> /var/log/etcbackup.log
 exit 1
fi
EOF
chmod 700 /root/etcbackup.sh
/root/etcbackup.sh
# Add with crontab -e (preserve other entries):
# 30 23 * * 1-6 /root/etcbackup.sh
systemctl enable --now crond
```
A changing /etc can make tar return 1; this script deliberately reports that as failure and does not publish/delete backups.

---

**T33 — SELinux and webroot**

**Beginvoorwaarde:** T10, T14. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: both nodes. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

On alpha root:
```bash
sed -i 's/^SELINUX=.*/SELINUX=enforcing/' /etc/selinux/config
setenforce 1
dnf install -y httpd
mkdir -p /webtest
printf 'Hello RHCSA\n' > /webtest/index.html
chmod 755 /webtest
chmod 644 /webtest/index.html
# Nodig na T10: root heeft in een nieuwe login umask 0007.
ls -Zd /webtest
semanage fcontext -a -t httpd_sys_content_t '/webtest(/.*)?'
restorecon -Rv /webtest
cat > /etc/httpd/conf.d/webtest.conf <<'EOF'
<VirtualHost *:80>
DocumentRoot /webtest
<Directory /webtest>
Require all granted
</Directory>
</VirtualHost>
EOF
httpd -t
systemctl enable --now httpd
systemctl restart httpd
curl --fail http://localhost/
```
On bravo root:
```bash
sed -i 's/^SELINUX=.*/SELINUX=permissive/' /etc/selinux/config
setenforce 0
getenforce
```
If booted with selinux=0, remove that argument and do a relabel/reboot before setenforce.

---

**T34 — Oplossing**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

On alpha root; keep port 80 and add a second listener:
```bash
printf 'Listen 8181\n' > /etc/httpd/conf.d/lab-port.conf
semanage port -a -t http_port_t -p tcp 8181
setsebool -P httpd_can_network_connect on
setsebool -P httpd_enable_homedirs on
cp /etc/hosts /var/www/html/hosts.txt
ls -Z /var/www/html/hosts.txt
restorecon -v /var/www/html/hosts.txt
httpd -t
systemctl restart httpd
ss -ltnp
getsebool httpd_can_network_connect httpd_enable_homedirs
```
If port already has http_port_t, do not add twice; inspect semanage port -l first. Remote 8181 access additionally needs a firewall rule if requested.

---

**T35 — Rootless HTTPD (alpha / alice)**

**Beginvoorwaarde:** T4, T5, T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: alpha, as alice. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

As root install podman, enable lingering for alice and permanently allow 8080/tcp in public. In an actual alice login:
```bash
podman pull registry.access.redhat.com/ubi10/httpd-24
podman image inspect registry.access.redhat.com/ubi10/httpd-24
mkdir -p ~/web_content
printf "Welcome to Alice's Containerized Web Server!
" > ~/web_content/index.html
chmod 755 ~/web_content
chmod 644 ~/web_content/index.html
podman run -d --name alice_web -p 8080:8080 -v "$HOME/web_content:/var/www/html:Z" registry.access.redhat.com/ubi10/httpd-24
podman ps
curl --fail http://localhost:8080/
podman stop alice_web
podman rm alice_web
mkdir -p ~/.config/containers/systemd
cat > ~/.config/containers/systemd/alice-web.container <<EOF
[Container]
Image=registry.access.redhat.com/ubi10/httpd-24
ContainerName=alice_web
PublishPort=8080:8080
Volume=$HOME/web_content:/var/www/html:Z
[Service]
Restart=always
TimeoutStartSec=300
[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user start alice-web.service
```
Root commands:
```bash
dnf install -y podman
loginctl enable-linger alice
firewall-cmd --permanent --zone=public --add-port=8080/tcp
firewall-cmd --reload
```
Run these root commands first. Do not enable the generated service. After reboot test from bravo: curl --fail http://alpha:8080/. ARM image availability must be checked online before a timed run.
