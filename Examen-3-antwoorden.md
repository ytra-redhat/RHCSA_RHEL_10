# Examen 3 — volledige antwoordensleutel

35 antwoordsecties. Voer deze in taakvolgorde uit; in examen 3 komt T33 vóór T16. Lees de beginvoorwaarde bij elke taak. Reeds behaalde doelen hoef je niet opnieuw te veranderen.

Korte uitvoerregels: [ZO-VOER-JE-DE-OPDRACHTEN-UIT.md](ZO-VOER-JE-DE-OPDRACHTEN-UIT.md).
Alle systeemblokken hieronder zijn bedoeld voor een **rootconsole in de genoemde Linux-VM**. Blokken voor alice/emma zijn bedoeld voor een echte login van die gebruiker. Een rootprompt is geen Mac-terminal.
Voer antwoordsecties niet automatisch als één script uit: ze bevatten herstarts, interactieve editors, verwachte fouten en netwerk/diskwijzigingen. Bestandsentries worden één keer toegevoegd; inspecteer fstab/hosts vóór herhaling.
Guest-uitvoering is nog niet end-to-end bewezen; zie VALIDATIE.md. Functionele controles in de antwoorden zijn de acceptatiecriteria.

**T1 — Boot recovery**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: foxtrot. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

Open GRUB with **e**. On the `linux` line change the standalone `ro` to `rw`, remove any `rd.break`, and append `init=/bin/bash enforcing=0`. Boot with Ctrl-X.
In the resulting root Bash (PID 1), run:
```bash
mount -o remount,rw /
vi /etc/fstab
# Remove only the nonexistent UUID=deadbeef... seed entry.
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
Use Ex3Recovery!; keep every valid filesystem entry.

---

**T2 — One-shot boot to rescue.target**

**Beginvoorwaarde:** T1. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: foxtrot. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
# At GRUB append systemd.unit=rescue.target to the linux line and use Ctrl-X.
# Execute only the following in the resulting rescue shell:
systemctl get-default > /root/target_check.txt   # still shows multi-user.target
reboot
```

A kernel argument applies to that boot only — `systemctl set-default` is what would make it permanent, and you deliberately did not run it.

---

**T3 — grubby**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
grubby --info=ALL
grubby --default-kernel
grubby --update-kernel=ALL --args="audit=1 transparent_hugepage=never"
grubby --update-kernel=ALL --remove-args="rhgb quiet"
reboot
```

Na de herstart: log opnieuw in op dezelfde VM als root en voer dit nieuwe blok uit.
```bash
cat /proc/cmdline > /root/cmdline.txt
```

---

**T4 — Failed service**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
systemctl status labdata.service > /root/labdata_diag.txt
journalctl -xeu labdata.service >> /root/labdata_diag.txt
# Reason: ExecStart=/usr/local/sbin/labdata-collect does not exist (status=203/EXEC)

tee /usr/local/sbin/labdata-collect >/dev/null <<'EOF'
#!/bin/bash
while true; do
    date >> /var/log/labdata.log
    sleep 60
done
EOF
chmod +x /usr/local/sbin/labdata-collect
restorecon -v /usr/local/sbin/labdata-collect
systemctl daemon-reload
systemctl reset-failed labdata.service
systemctl enable --now labdata.service
systemctl is-active labdata.service
```

The unit passes `--daemon`; the script ignores unknown arguments, which is fine. `203/EXEC` always means "the binary named in ExecStart could not be executed" — missing, not executable, or bad interpreter.

---

**T5 — Drop-in override**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
systemctl edit sshd.service
```
Creates `/etc/systemd/system/sshd.service.d/override.conf`:

```ini
[Unit]
Description=SSH Daemon (lab-tuned)

[Service]
Restart=on-failure
RestartSec=30
```

```bash
systemctl daemon-reload
systemctl restart sshd
systemctl show sshd.service -p Restart -p RestartUSec -p Description > /root/sshd_override.txt
echo "# To discard all overrides: systemctl revert sshd.service" >> /root/sshd_override.txt
systemctl cat sshd.service      # shows vendor unit + drop-in and their paths
```

> Gotcha worth knowing: overriding a **list-valued** directive like `ExecStart=` requires clearing it first with an empty `ExecStart=` line, then setting the new value. Scalar directives like `Restart=` simply replace.

---

**T6 — Redirection**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
ls /etc /nonexistent > /root/redir_out.txt 2> /root/redir_err.txt
ls /etc /nonexistent > /root/redir_both.txt 2>&1     # order matters
date >> /root/redir_out.txt
df -h | tee /root/df_report.txt
find /etc -name '*.conf' 2>/dev/null > /root/conf_list.txt
cat > /root/notes.txt <<'EOF'
line one
line two
line three
EOF
```

`> file 2>&1` works; `2>&1 > file` does **not** — the duplication happens before stdout is redirected. `&> file` is the bash shorthand.

---

**T7 — grep and regex**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
grep -E '^[^:]+:[^:]*:[0-9]{4}:' /etc/passwd > /root/g1.txt
grep -vE '^\s*(#|$)' /etc/ssh/sshd_config > /root/g2.txt
grep -c '/sbin/nologin$' /etc/passwd > /root/g3.txt
grep -rhoE '([0-9]{1,3}\.){3}[0-9]{1,3}' /var/log/ 2>/dev/null | awk -F. 'NF==4 && $1<=255 && $2<=255 && $3<=255 && $4<=255' | sort -u > /root/g4.txt
grep -E '^http[^s]' /etc/services > /root/g5.txt
grep -rin 'selinux' /etc/ 2>/dev/null > /root/g6.txt
```

Key pieces: `-E` for extended regex, `-o` prints only the match, `-h` suppresses filenames, `-c` counts, `-v` inverts, `-r` recurses, `-n` adds line numbers, `-i` ignores case. `[^s]` is "any character except s".

---

**T8 — find**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
find /var -type f -size +5242880c > /root/f1.txt
find /etc -type f -mtime -7 > /root/f2.txt
find /home /srv -uid 3100 > /root/f3.txt
find /etc -type d -perm 0700 > /root/f4.txt

mkdir -p /root/oldlogs
find /var/log -name '*.log' -mtime +3 -exec cp --parents -t /root/oldlogs -- {} +
find /tmp -type f -empty -delete
```

`-perm 0700` = exactly those bits; `-perm -0700` = at least those bits; `-perm /0700` = any of them. `-exec ... \;` runs once per file, `-exec ... +` batches (faster, but the batching form puts filenames at the end so it doesn't suit `cp` to a destination without `-t`).

---

**T9 — Archives**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
tar czf /root/ssh_backup.tar.gz /etc/ssh
tar cjf /root/ssh_backup.tar.bz2 /etc/ssh
gzip_size=$(stat -c %s /root/ssh_backup.tar.gz)
bzip_size=$(stat -c %s /root/ssh_backup.tar.bz2)
if (( gzip_size < bzip_size )); then winner=gzip; elif (( bzip_size < gzip_size )); then winner=bzip2; else winner=equal; fi
printf 'gzip=%s bzip2=%s smaller=%s\n' "$gzip_size" "$bzip_size" "$winner" > /root/compression.txt
tar tzf /root/ssh_backup.tar.gz > /root/archive_list.txt

mkdir -p /root/restore
tar xzf /root/ssh_backup.tar.gz -C /root/restore etc/ssh/sshd_config

tar czf /root/logs.tar.gz --exclude='/var/log/journal' /var/log

mkdir -p /root/restore_full
tar xjpf /root/ssh_backup.tar.bz2 -C /root/restore_full
```

`c`=create, `x`=extract, `t`=list, `z`=gzip, `j`=bzip2, `J`=xz, `f`=file, `p`=preserve permissions, `-C`=change to directory. Paths inside the archive are relative (`etc/ssh/...`, no leading `/`) — that's why the single-file extraction omits the leading slash.

---

**T10 — System documentation**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

Use the installed documentation and record actual answers, not invented filenames:
```bash
mandb
man 5 passwd
man -k 'partition table'
man journalctl
find /usr/share/doc -iname '*chrony*' -o -path '*/chrony/*'
info coreutils
man 5 fstab
vi /root/docs_answers.txt
```
Six numbered answers: 1 section 5; 2 command names actually listed by apropos; 3 -b/--boot from journalctl(1); 4 an existing chrony documentation file with full path; 5 the actual top-level info node; 6 /etc/fstab, fs_passno controls filesystem check order (0 disabled, 1 root, 2 other). Save all six.

---

**T11 — Skeleton and home relocation**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
echo "Welcome to the EX200 lab" | tee /etc/skel/lab_welcome.txt
mkdir -p /etc/skel/projects

groupadd -g 7000 research
useradd -m -u 3100 -g research emma
useradd -m -u 3101 -g research noah
ls -a /home/emma /home/noah          # skeleton copied at creation time

useradd -u 3102 -g research -d /opt/oscar -m oscar
ls -a /opt/oscar

mkdir -p /srv/homes
semanage fcontext -a -e /home /srv/homes
usermod -d /srv/homes/noah -m noah
getent passwd noah
restorecon -Rv /srv/homes/noah  # relocated homes need relabeling
```

`-m` with `-d` **moves** the existing contents. Skeleton files are copied only at creation — editing `/etc/skel` later does not retroactively update existing users.
```bash
printf 'emma:Lab@12345\nnoah:Lab@12345\noscar:Lab@12345\n' | chpasswd
runuser -l noah -c 'pwd; ls lab_welcome.txt projects'
```
Verify a real noah password login too. Ensure the moved home parent is traversable and its policy-equivalent labels are applied.

---

**T12 — Defaults**

**Beginvoorwaarde:** T11. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
visudo -f /etc/sudoers.d/lab3_defaults
```

```
Defaults:%research    timestamp_timeout=0
Defaults              logfile="/var/log/sudo_lab.log"
Defaults              secure_path="/usr/local/lab/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

%research   ALL=(ALL) ALL
```

```bash
chmod 440 /etc/sudoers.d/lab3_defaults
visudo -cf /etc/sudoers.d/lab3_defaults
visudo -c
sudo -l -U emma
```

Editing with `visudo -f` is the safe path — it syntax-checks before saving. `Defaults:%group` scopes a default to a group; `timestamp_timeout=0` forces a password on every invocation.

---

**T13 — ACL mask**

**Beginvoorwaarde:** T11. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
mkdir -p /srv/shared/data
chown emma:research /srv/shared/data
chmod 2770 /srv/shared/data

setfacl -m u:noah:rwx -m g:wheel:r-x /srv/shared/data
setfacl -d -m u:noah:rwx -d -m g:wheel:r-x /srv/shared/data

setfacl -m m::r-x /srv/shared/data
getfacl /srv/shared/data > /root/acl_effective.txt
```

`getfacl` now shows `user:noah:rwx  #effective:r-x`. The mask is the **ceiling** on every named user, named group, and the owning group — effective permission is the ACL entry ANDed with the mask, so `noah`'s write bit is masked off without his entry changing.

```bash
runuser -u emma -- touch /srv/shared/data/test.txt
getfacl /srv/shared/data/test.txt      # inherited from the default ACL
setfacl -m m::rwx /srv/shared/data
getfacl /srv/shared/data               # noah effective rwx again
```

---

**T14 — cp vs mv contexts**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
echo "Context Test" > /root/site_index.html
cp /root/site_index.html /root/site_index2.html
cp /root/site_index.html /root/site_index3.html

ls -Z /root/site_index.html      > /root/context_report.txt

cp /root/site_index.html /var/www/html/copied.html
ls -Z /var/www/html/copied.html  >> /root/context_report.txt   # httpd_sys_content_t ✔

mv /root/site_index2.html /var/www/html/moved.html
ls -Z /var/www/html/moved.html   >> /root/context_report.txt   # admin_home_t ✘

restorecon -v /var/www/html/moved.html

cp --preserve=context /root/site_index3.html /var/www/html/preserved.html
ls -Z /var/www/html/preserved.html >> /root/context_report.txt
```

**`cp` creates a new inode**, so it inherits the *destination directory's* default context — correct for httpd. **`mv` preserves the inode and its label**, dragging `admin_home_t` along — httpd is denied. This is the single most common SELinux trap on the exam. `restorecon` reapplies the policy default; `chcon` sets a label that a relabel will later undo.
This inode-preserving mv explanation applies within the same filesystem. For a cross-filesystem move inspect actual label behaviour. Record the explanation in context_report.txt, then restorecon preserved.html after recording the deliberately wrong label.

---

**T15 — Network profiles and peer**

**Beginvoorwaarde:** T1. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo; static peer setup on foxtrot. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

De **interface** is het apparaat (`enp2s0`, `enp3s0`, of na T3 `ethX`). Het **profiel** bevat de instellingen. `fusion-nat` hoort bij Fusion NAT en verzorgt internet; `fusion-lab` hoort bij host-only en verzorgt verkeer tussen de twee examen-VM's. We wijzigen uitsluitend het labprofiel en noemen dat daarna `lab3-static`. De interface verandert daardoor niet van naam.

Voer dit blok op **echo**, als root in de Fusion-console uit. Kopieer het volledig; vul geen UUID in. Het selecteert exact één bestaand labprofiel; bij geen of meerdere treffers blijft de configuratie intact en krijg je een STOP-melding.
```bash
configure_lab() {
 local lab_uuid name uuid
 local -a matches=()
 while IFS=: read -r uuid name; do
  case "$name" in fusion-lab|lab3-static) matches+=("$uuid");; esac
 done < <(nmcli -t -f UUID,NAME connection show)
 if (( ${#matches[@]} != 1 )); then
  echo 'STOP: verwacht precies één fusion-lab of lab3-static; toon nmcli -f NAME,UUID,DEVICE con show' >&2
  return 1
 fi
 lab_uuid=${matches[0]}
 nmcli con mod uuid "$lab_uuid" connection.id lab3-static ipv4.method manual ipv4.addresses 172.16.40.21/24 ipv4.gateway '' ipv4.dns '' ipv4.never-default yes ipv6.method manual ipv6.addresses fd10::21/64 ipv6.gateway '' ipv6.dns '' ipv6.never-default yes connection.autoconnect yes || return
 nmcli con up uuid "$lab_uuid" || return
 hostnamectl set-hostname echo.ex200.net || return
}
configure_lab
unset -f configure_lab
```
Bij STOP: voer de volgende blokken niet uit. Bij succes staat het labadres op de interface die bij het MAC-gebonden profiel hoort. Je hoeft de interfacenaam niet te raden.


De **interface** is het apparaat (`enp2s0`, `enp3s0`, of na T3 `ethX`). Het **profiel** bevat de instellingen. `fusion-nat` hoort bij Fusion NAT en verzorgt internet; `fusion-lab` hoort bij host-only en verzorgt verkeer tussen de twee examen-VM's. We wijzigen uitsluitend het labprofiel en noemen dat daarna `lab3-static`. De interface verandert daardoor niet van naam.

Voer dit blok op **foxtrot**, als root in de Fusion-console uit. Kopieer het volledig; vul geen UUID in. Het selecteert exact één bestaand labprofiel; bij geen of meerdere treffers blijft de configuratie intact en krijg je een STOP-melding.
```bash
configure_lab() {
 local lab_uuid name uuid
 local -a matches=()
 while IFS=: read -r uuid name; do
  case "$name" in fusion-lab|lab3-static) matches+=("$uuid");; esac
 done < <(nmcli -t -f UUID,NAME connection show)
 if (( ${#matches[@]} != 1 )); then
  echo 'STOP: verwacht precies één fusion-lab of lab3-static; toon nmcli -f NAME,UUID,DEVICE con show' >&2
  return 1
 fi
 lab_uuid=${matches[0]}
 nmcli con mod uuid "$lab_uuid" connection.id lab3-static ipv4.method manual ipv4.addresses 172.16.40.22/24 ipv4.gateway '' ipv4.dns '' ipv4.never-default yes ipv6.method manual ipv6.addresses fd10::22/64 ipv6.gateway '' ipv6.dns '' ipv6.never-default yes connection.autoconnect yes || return
 nmcli con up uuid "$lab_uuid" || return
 hostnamectl set-hostname foxtrot.ex200.net || return
}
configure_lab
unset -f configure_lab
```
Bij STOP: voer de volgende blokken niet uit. Bij succes staat het labadres op de interface die bij het MAC-gebonden profiel hoort. Je hoeft de interfacenaam niet te raden.

Op **beide VM's**, na succesvolle configuratie, als root:
```bash
# Verwijder eerst eventuele eerdere labregels met dezelfde namen, om dubbelen te voorkomen.
vi /etc/hosts
printf '172.16.40.21 echo.ex200.net echo\n172.16.40.22 foxtrot.ex200.net foxtrot\n' >> /etc/hosts
nmcli -f NAME,UUID,DEVICE con show
ip -br address
ip route
ip -6 route
```
De default route naar internet hoort bij NAT; het labprofiel heeft geen gateway. Test pas wanneer beide VM's zijn ingesteld.

Op **echo**:
```bash
ping -c 2 foxtrot
ping -6 -c 2 fd10::22
```
Op **foxtrot**:
```bash
ping -c 2 echo
ping -6 -c 2 fd10::21
```

Alleen op **echo**, voor het aanvullende DHCP-profiel: bepaal de gebruikte labinterface uit het actieve statische profiel. De bestaande MAC-binding bepaalt de juiste kaart.
```bash
LAB_IF=$(nmcli -g GENERAL.DEVICES con show id lab3-static)
printf 'Labinterface: %s\n' "$LAB_IF"
```
Ga alleen door als precies één echte interface getoond wordt (geen `--` of lege regel). Gebruik vervolgens:
```bash
nmcli con add type ethernet ifname "$LAB_IF" con-name lab3-dhcp ipv4.method auto ipv4.never-default yes ipv4.ignore-auto-dns yes ipv6.method auto ipv6.never-default yes ipv6.ignore-auto-dns yes connection.autoconnect no
nmcli con up id lab3-dhcp
ip -br addr show "$LAB_IF"
nmcli con up id lab3-static
printf '/etc/nsswitch.conf bepaalt de resolutievolgorde. Actuele regel:\n' > /root/resolution.txt
grep '^hosts:' /etc/nsswitch.conf >> /root/resolution.txt
```
Als Fusion host-only geen DHCP aanbiedt, kan activeren mislukken. Noteer dit als niet uitgevoerde DHCP-controle, herstel `lab3-static` met het laatste nmcli-commando en controleer beide pings opnieuw. Maak bij herhaling niet nog een lab3-dhcp-profiel.

---

**T16 — Oplossing**

**Beginvoorwaarde:** T15, T33. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

Voer eerst T15 (beide VM's) en T33 (echo) uit. T33 herstelt de bestaande Apache-server op poort 8404. Dit onderdeel voegt een aparte virtual host op poort 80 toe, zodat de gevraagde pagina geen toevallig resultaat van een andere virtual host is.

Op **echo**, root:
```bash
printf 'echo web\n' > /var/www/html/index.html
chmod 755 /var/www/html
chmod 644 /var/www/html/index.html
cat > /etc/httpd/conf.d/echo-forward.conf <<'EOF'
<VirtualHost *:80>
DocumentRoot /var/www/html
<Directory /var/www/html>
Require all granted
</Directory>
</VirtualHost>
EOF
restorecon -Rv /var/www/html
httpd -t
systemctl restart httpd
curl --fail http://localhost:80/
firewall-cmd --permanent --zone=public --add-service=http
firewall-cmd --permanent --zone=public --add-forward-port=port=8888:proto=tcp:toport=80
firewall-cmd --permanent --zone=public --add-masquerade
firewall-cmd --reload
firewall-cmd --zone=public --list-all
```
Verwacht lokaal `echo web`; de permanente public-zone moet de forward-regel tonen. `fusion-lab`/`lab3-static` is door de seed aan public toegewezen.

Op **foxtrot**, root:
```bash
curl --fail http://echo.ex200.net:8888/
```
Verwacht `echo web`. Een HTTP-fout of ontbrekende pagina is geen geslaagde controle. Masquerade wordt hier toegevoegd omdat de opdracht het vraagt; de forward gaat naar dezelfde VM, zonder `toaddr`.

---

**T17 — DVD repos and queries (echo)**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
mkdir -p /mnt/dvd
printf '/dev/sr0 /mnt/dvd iso9660 ro,nofail 0 0\n' >> /etc/fstab
systemctl daemon-reload
mount /mnt/dvd
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
cat > /etc/yum.repos.d/lab3.repo <<EOF
[BaseOS]
name=DVD BaseOS
baseurl=file:///mnt/dvd/BaseOS
enabled=1
gpgcheck=1
gpgkey=file://$KEY
[AppStream]
name=DVD AppStream
baseurl=file:///mnt/dvd/AppStream
enabled=1
gpgcheck=1
gpgkey=file://$KEY
EOF
dnf repolist
dnf provides '*/semanage' > /root/q1.txt
rpm -qf /etc/chrony.conf > /root/q2.txt
rpm -ql chrony > /root/q3.txt
dnf search 'network manager' > /root/q4.txt
```

---

**T18 — Oplossing**

**Beginvoorwaarde:** T17. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

Before starting, tmux must be absent; otherwise installation is a no-op, not a new transaction.


```bash
dnf install -y tmux
dnf history list | head
read -r -p 'Actual tmux installation transaction ID: ' ID
[[ $ID =~ ^[0-9]+$ ]] || exit 1
printf '%s\n' "$ID" > /root/history_id.txt
dnf history info "$ID"
dnf history undo "$ID" -y
rpm -q tmux                       # not installed
dnf history redo "$ID" -y
rpm -q tmux
```

`undo` reverses a transaction (removing what it installed); `redo` re-applies it; `rollback <id>` reverts everything *after* that point.

---

**T19 — RPM operations**

**Beginvoorwaarde:** T17. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
mkdir -p /root/rpms
# Bij herhaling: verplaats eerder gedownloade zsh-RPM's eerst naar een aparte backupmap.
dnf download --destdir /root/rpms zsh
cd /root/rpms
```
Controleer dat er precies één zsh-RPM is voordat je verdergaat:
```bash
find /root/rpms -maxdepth 1 -name 'zsh-*.rpm' -type f
```
Bij meerdere bestanden: kies eerst één versie en bewaar de andere buiten deze map. Bij nul bestanden is de download mislukt. Vervolgens:
```bash
rpm -qlp zsh-*.rpm      > /root/rpm1.txt      # -p = query the package FILE
rpm -q --scripts -p zsh-*.rpm > /root/rpm2.txt

mkdir -p /root/extracted && cd /root/extracted
rpm2cpio /root/rpms/zsh-*.rpm | cpio -idmv './usr/share/man/man1/zsh.1*'

rpm -K /root/rpms/zsh-*.rpm       # signature check
dnf install -y /root/rpms/zsh-*.rpm
rpm -V zsh                        # silence = unmodified
```

`-p` makes any `rpm -q` operate on an uninstalled `.rpm` file. `rpm2cpio | cpio -idmv` extracts without installing; `rpm2archive` is the newer equivalent.

---

**T20 — fdisk, type codes, and a table backup**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo, `/dev/nvme0n2`. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
fdisk /dev/nvme0n2
```
Binnen **fdisk**, één invoer per vraag (Enter betekent alleen de Enter-toets):

| Vraag/handeling | Invoer |
|---|---|
| Nieuwe GPT, alleen op de lege extra schijf | `g` |
| Nieuwe partitie | `n` |
| Nummer | `1` |
| Beginsector | Enter |
| Eindsector/grootte | `+3G` |
| Nieuwe partitie | `n` |
| Nummer | `2` |
| Beginsector | Enter |
| Eindsector/grootte | `+2G` |
| Type wijzigen | `t` |
| Partitienummer | `2` |
| Linux LVM-type | `E6D6D379-F507-44C2-A23C-238F2A3DF928` |
| Controleer 3 GiB en 2 GiB | `p` |
| Alleen bij correcte layout: schrijf en sluit | `w` |

Terug in **Bash**:
```bash
partprobe /dev/nvme0n2
lsblk /dev/nvme0n2
fdisk -l /dev/nvme0n2
```

Capture the layout with type GUIDs and PARTUUIDs, and take a restorable backup:

```bash
# sfdisk's dump format shows type= (GUID) and uuid= (PARTUUID) per partition
sfdisk -d /dev/nvme0n2 | tee /root/gpt_layout.txt
lsblk -o NAME,SIZE,PARTTYPENAME,PARTUUID /dev/nvme0n2 | tee -a /root/gpt_layout.txt

# Restorable backup of the partition table
sfdisk -d /dev/nvme0n2 | tee /root/nvme0n2-parttable.bak
echo '# Restore with: sfdisk /dev/nvme0n2 < /root/nvme0n2-parttable.bak' \
  | tee -a /root/gpt_layout.txt
```

Gebruik de volledige type-GUID uit de tabel; numerieke snelcodes kunnen per util-linux-versie verschillen. `fdisk` wordt door util-linux geleverd en ondersteunt GPT. Het aparte gdisk-pakket is niet nodig.

---

**T21 — Shrink an ext4 LV**

**Beginvoorwaarde:** T20. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo, `/dev/nvme0n2p2` + `/dev/nvme0n3`. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
pvcreate /dev/nvme0n2p2 /dev/nvme0n3
vgcreate -s 8M vg_ex3 /dev/nvme0n2p2 /dev/nvme0n3
lvcreate -L 4G -n lv_shrink vg_ex3
mkfs.ext4 /dev/vg_ex3/lv_shrink
mkdir -p /mnt/shrink
echo "UUID=$(blkid -s UUID -o value /dev/vg_ex3/lv_shrink) /mnt/shrink ext4 defaults 0 0" \
  | tee -a /etc/fstab
systemctl daemon-reload
mount -a

dd if=/dev/urandom of=/mnt/shrink/testfile bs=1M count=50
sha256sum /mnt/shrink/testfile | tee /root/checksum_before.txt

# --- the shrink ---
umount /mnt/shrink                       # ext4 CANNOT shrink while mounted
e2fsck -f /dev/vg_ex3/lv_shrink
lvreduce -L 2G -r /dev/vg_ex3/lv_shrink  # -r drives resize2fs via fsadm
systemctl daemon-reload
mount -a

sha256sum -c /root/checksum_before.txt
lvs vg_ex3

cat > /root/shrink_notes.txt <<'EOF'
De ondersteunde XFS-procedure in deze Rocky-labomgeving is online groeien.
Gebruik geen lvreduce op een bestaand XFS-filesysteem.
Reducing an XFS-backed LV would destroy the filesystem, so the only route
is backup, lvreduce, mkfs.xfs, restore.
EOF
```

Always shrink the **filesystem before** the volume. `-r` does both in the right order; doing `lvreduce` alone on a full-size filesystem silently truncates it.

---

**T22 — Replace swap (foxtrot)**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: foxtrot, `/dev/nvme0n2`. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
swapon --show=NAME,TYPE,SIZE,PRIO > /root/swap_before.txt
free -h >> /root/swap_before.txt
cat /root/swap_before.txt
# Kies de oorspronkelijke schijfswap, nooit /dev/zram0.
read -r -p 'Original swap device from that output: ' OLD_SWAP
swapon --show=NAME --noheadings | awk -v old="$OLD_SWAP" '$1==old {found=1} END {exit !found}'
# Only after checking that this is the original device:
fdisk /dev/nvme0n2
```
Binnen fdisk: `g` alleen op de gecontroleerde lege extra schijf; `n`, nummer `1`, Enter voor beginsector, `+1G`, `t`, type-GUID `0657FD6D-A4AB-43C4-84E5-0933C84B4F4F`, `p` ter controle, `w`. Bij slechts één partitie vraagt `t` niet om een partitienummer.
Terug in Bash:
```bash
partprobe /dev/nvme0n2
mkswap -L EX3SWAP /dev/nvme0n2p1
cp -a /etc/fstab /root/fstab.before-swap
printf 'LABEL=EX3SWAP none swap defaults,pri=5 0 0\n' >> /etc/fstab
swapon /dev/nvme0n2p1
swapon --show=NAME,SIZE,PRIO
blkid /dev/nvme0n2p1
swapoff "$OLD_SWAP"
vi /etc/fstab
# Remove ONLY the old swap entry. Keep LABEL=EX3SWAP.
findmnt --verify --verbose
systemctl daemon-reload
swapon -a
reboot
```

Na de herstart: log opnieuw in op dezelfde VM als root en voer dit nieuwe blok uit.
```bash
swapon --show=NAME,SIZE,PRIO > /root/swap_after.txt
```
Keep the inactive original LV allocated. Removing its activation from fstab satisfies this exercise without risking resume/rd.lvm.lv references. If physically removing it as an optional extra, first inspect and remove its resume and swap-specific bootargs using grubby; never remove the root LV. Check available RAM before swapoff; if it fails, stop and investigate rather than force it.

---

**T23 — Mount options and remount**

**Beginvoorwaarde:** T22. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: foxtrot. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
fdisk /dev/nvme0n2
```
Binnen fdisk: `n`, partitienummer `2`, Enter voor beginsector, `+2G` voor grootte, `p` ter controle, `w` om te schrijven. **Geen `g`**: partitie 1 uit T22 moet behouden blijven.
Terug in Bash:
```bash
partprobe /dev/nvme0n2
mkfs.xfs /dev/nvme0n2p2
mkdir -p /data/vault
echo "UUID=$(blkid -s UUID -o value /dev/nvme0n2p2) /data/vault xfs defaults,noexec,nosuid,nodev 0 0" \
  | tee -a /etc/fstab
systemctl daemon-reload
mount -a

cp /bin/ls /data/vault/
/data/vault/ls 2> /root/noexec_proof.txt     # "Permission denied"

mount -o remount,ro /data/vault
touch /data/vault/x 2>> /root/noexec_proof.txt   # "Read-only file system"
mount -o remount,rw /data/vault
findmnt /data/vault > /root/mount_opts.txt
```

`mount -o remount` changes options on a live mount without unmounting — useful when a filesystem is busy.

---

**T24 — Bind mount**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: foxtrot. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
mkdir -p /srv/appdata /opt/app/data
echo "bind payload" | tee /srv/appdata/payload.txt
echo '/srv/appdata  /opt/app/data  none  bind  0 0' | tee -a /etc/fstab
systemctl daemon-reload
mount -a
ls /opt/app/data/payload.txt
findmnt /opt/app/data
reboot
```

Filesystem type is `none` and the option is `bind`. `mount --bind /srv/appdata /opt/app/data` is the ad-hoc equivalent.

---

**T25 — NFS team (foxtrot)**

**Beginvoorwaarde:** T15. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: foxtrot. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
dnf install -y nfs-utils
groupadd -g 7000 research
useradd -m -u 3100 -g research emma
mkdir -p /export/team
chown root:research /export/team
chmod 2770 /export/team
printf '/export/team 172.16.40.0/24(rw,sync,root_squash,no_subtree_check)\n' > /etc/exports.d/team.exports
systemctl enable --now nfs-server
for service in nfs mountd rpc-bind; do firewall-cmd --permanent --zone=public --add-service="$service"; done
firewall-cmd --reload
exportfs -rav
exportfs -v
cp -a /etc/exports.d/team.exports /root/team.exports.good
# Only for this isolated lab diagnostic, introduce the typo temporarily:
printf '/export/team 172.16.40.0/24 (rw,sync,no_subtree_check)\n' > /etc/exports.d/team.exports
exportfs -rav > /root/exports_typo.txt 2>&1
exportfs -v >> /root/exports_typo.txt
cp -a /root/team.exports.good /etc/exports.d/team.exports
exportfs -rav
exportfs -v
```
Record actual parser errors/options, not assumed behaviour. Normal client emma UID 3100/GID 7000 can write; squashed client root cannot. Test from echo as emma after T26.

---

**T26 — Autofs (echo)**

**Beginvoorwaarde:** T11, T15, T25. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
dnf install -y autofs
printf '/net /etc/auto.team --timeout=45\n' > /etc/auto.master.d/team.autofs
printf 'team -fstype=nfs4,rw,hard foxtrot.ex200.net:/export/team\n' > /etc/auto.team
systemctl enable --now autofs
ls /net/team
findmnt --mountpoint /net/team
runuser -u emma -- touch /net/team/from-emma
```
Wait idle at least 45 seconds plus the expiry scan interval; do not ls the path during that wait. Inspect findmnt without accessing the directory. Result is /net/team, not /net/team/team.

---

**T27 — journalctl filtering**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
journalctl -b -u sshd                                   > /root/j1.txt
journalctl --since "09:00" --until "12:00"              > /root/j2.txt
journalctl --since yesterday -p err                     > /root/j3.txt
journalctl --no-pager _COMM=sudo > /root/j4.txt
journalctl --disk-usage                                 > /root/j5.txt

journalctl --rotate --vacuum-size=200M
mkdir -p /etc/systemd/journald.conf.d
mkdir -p /var/log/journal
printf '[Journal]\nStorage=persistent\nSystemMaxUse=200M\nSystemMaxFileSize=25M\n' | tee /etc/systemd/journald.conf.d/90-rhcsa-size.conf
systemctl restart systemd-journald
```

Een lege selectie is mogelijk wanneer er geen gebeurtenissen in het gekozen tijdvenster of van sudo bestaan. Dat is geen bewijs van een fout of van een uitgevoerde sudo-oefening. Controleer eerst de brongebeurtenis.

`-u` matches the systemd unit; `_COMM=` matches the process name regardless of unit — different tools for different questions. Time strings accept `yesterday`, `-1h`, and `"YYYY-MM-DD HH:MM:SS"`.
```bash
systemd-tmpfiles --create --prefix /var/log/journal
journalctl --flush
journalctl --disk-usage
```
Vacuum removes archived files, not active ones. SystemMaxUse is retention policy; it is not an exact hard storage quota.

---

**T28 — Persistent sysctl**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
tee /etc/sysctl.d/99-lab3.conf >/dev/null <<'EOF'
net.ipv4.ip_forward = 1
vm.swappiness = 20
kernel.pid_max = 65536
EOF

sysctl -p /etc/sysctl.d/99-lab3.conf     # or: sysctl --system
sysctl net.ipv4.ip_forward vm.swappiness kernel.pid_max > /root/sysctl_verify.txt
reboot
```

`sysctl --system` reloads every file in the drop-in directories in order; `-p <file>` loads just one. Files in `/etc/sysctl.d/` are read in lexical order, which is why the `99-` prefix wins.

---

**T29 — at, at.allow, cron.d**

**Beginvoorwaarde:** T11. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
systemctl enable --now atd crond
echo 'echo "at job ran" >> /var/log/at3.log' | at now + 10 minutes
atq
read -r -p "Job number from atq: " JOB
at -c "$JOB" > /root/at_job.txt
atrm "$JOB"
atq                                        # empty

echo emma | tee /etc/at.allow         # allow-list: only emma (plus root)
chmod 644 /etc/at.allow

tee /etc/cron.d/labreport >/dev/null <<'EOF'
45 5 * * 1,4 emma /usr/local/bin/labreport.sh
EOF

cat > /root/crond_note.txt <<'EOF'
A /etc/cron.d file has five time fields, then a USER field and a command:
  min hr dom mon dow  USER  command
A user crontab (crontab -e) has no user field - it always runs as its owner.
EOF
```

If `/etc/at.allow` exists, only users listed in it may use `at` and `/etc/at.deny` is ignored entirely. `cron.allow`/`cron.deny` work the same way for cron.
```bash
cat > /usr/local/bin/labreport.sh <<'EOF'
#!/bin/bash
set -euo pipefail
{ date; df -h; } >> "$HOME/labreport.log"
EOF
chmod 755 /usr/local/bin/labreport.sh
restorecon -v /usr/local/bin/labreport.sh
runuser -l emma -c /usr/local/bin/labreport.sh
systemctl enable --now crond
runuser -u emma -- atq
runuser -u noah -- atq
```
Noah must be denied. /etc/at.allow has exactly emma (root is exempt); keep it readable so allowed users can check the list. Do not erase other queued jobs: verify only your job was removed.

---

**T30 — Chrony**

**Beginvoorwaarde:** T15. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: beide. Uitvoering: rootconsole.**

Uitsluitend op **foxtrot**, root:
```bash
sed -i 's/^pool /#pool /; s/^server /#server /' /etc/chrony.conf
echo 'allow 172.16.40.0/24' | tee -a /etc/chrony.conf
echo 'local stratum 10'     | tee -a /etc/chrony.conf
systemctl enable --now chronyd && systemctl restart chronyd
firewall-cmd --permanent --add-service=ntp && firewall-cmd --reload

```

Uitsluitend op **echo**, root:
```bash
sed -i 's/^pool /#pool /; s/^server /#server /' /etc/chrony.conf
echo 'server foxtrot.ex200.net iburst' | tee -a /etc/chrony.conf
systemctl restart chronyd
chronyc sources -v                      # foxtrot marked ^* once selected

timedatectl set-local-rtc 0
timedatectl set-timezone America/Denver
timedatectl > /root/time_status.txt
```

`local stratum 10` lets the server serve time even when it has no upstream source — necessary in an offline lab.

---

**T31 — diskwatch.sh**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
tee /usr/local/bin/diskwatch.sh >/dev/null <<'EOF'
#!/bin/bash
set -euo pipefail

usage() { echo "Usage: $0 <mountpoint>" >&2; exit 2; }

[[ $# -eq 1 ]] || usage
target="$1"

if ! findmnt -n --mountpoint "$target" >/dev/null 2>&1; then
    echo "Not mounted: $target" >&2
    exit 3
fi

pct=$(df --output=pcent "$target" | tail -1 | tr -d ' %')

if (( pct >= 80 )); then
    echo "CRITICAL: $target at ${pct}%"
    exit 1
fi

echo "OK: $target at ${pct}%"
exit 0
EOF
chmod 755 /usr/local/bin/diskwatch.sh

mkdir -p /mnt/diskwatch-test
mount -t tmpfs -o size=10M tmpfs /mnt/diskwatch-test
{
 diskwatch.sh; echo "usage=$?"
 diskwatch.sh /not-a-lab-mount; echo "not-mounted=$?"
 diskwatch.sh /mnt/diskwatch-test; echo "OK=$?"
 dd if=/dev/zero of=/mnt/diskwatch-test/fill bs=1M count=9
 diskwatch.sh /mnt/diskwatch-test; echo "CRITICAL=$?"
} > /root/diskwatch_tests.txt 2>&1
umount /mnt/diskwatch-test
rmdir /mnt/diskwatch-test
```

With `set -e` a non-zero command aborts the script, so the `if ! findmnt` guard must wrap the test — a bare `findmnt` would kill the script before your custom exit code ran.

---

**T32 — userreport.sh**

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
tee /usr/local/bin/userreport.sh >/dev/null <<'EOF'
#!/bin/bash
OUT=/var/log/userreport.txt

{
  echo "=== User Report: $(date) ==="

  echo -n "Accounts with valid login shells: "
  count=0
  while IFS=: read -r name password uid gid gecos home shell; do
   case "$shell" in */nologin|*/false) continue;; esac
   if [[ -x $shell ]] && grep -Fxq "$shell" /etc/shells; then count=$((count+1)); fi
  done < /etc/passwd
  printf '%s\n' "$count"

  echo "Top 5 UIDs:"
  sort -t: -k3 -n -r /etc/passwd | head -5 | cut -d: -f1,3

  echo "Groups with no members:"
  awk -F: '$4 == "" {print $1}' /etc/group

  echo -n "Locked accounts: "
  passwd -Sa 2>/dev/null | awk '$2 == "L"' | wc -l
} > "$OUT"
EOF
chmod +x /usr/local/bin/userreport.sh
/usr/local/bin/userreport.sh
cat /var/log/userreport.txt
```

Note the "no members" check reads field 4 of `/etc/group` — users whose *primary* group it is are not listed there, which is the expected behavior for this report.

---

**T33 — Apache diagnosis (echo; before T16)**

**Beginvoorwaarde:** T15. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

```bash
getenforce
systemctl start httpd
systemctl status httpd --no-pager > /root/selinux_diag.txt
journalctl -u httpd --no-pager >> /root/selinux_diag.txt
ausearch -m AVC -ts recent >> /root/selinux_diag.txt
ausearch -m AVC -ts recent | audit2why >> /root/selinux_diag.txt
# First fix: port; inspect existing labels before -a.
semanage port -l | grep http_port_t
semanage port -a -t http_port_t -p tcp 8404
systemctl reset-failed httpd
systemctl start httpd
curl http://localhost:8404/
# The request now exposes the file-label denial.
ausearch -m AVC -ts recent | audit2why >> /root/selinux_diag.txt
semanage fcontext -a -t httpd_sys_content_t '/srv/intranet(/.*)?'
restorecon -Rv /srv/intranet
systemctl restart httpd
# Record the start of the verification window, then perform one request.
START=$(date '+%H:%M:%S')
curl --fail http://localhost:8404/
ausearch -m AVC -c httpd -ts "$START"
```
Expected body Echo Intranet OK; the last search should find no new httpd AVCs for that window. Old denials remain in the audit log. Ensure auditd and audit2why exist; optional sealert requires setroubleshoot-server. Reboot and repeat request/window test. Port and labels, not a broad allow module, fix these two defects.

---

**T34 — Local policy module (echo; optional depth)**

**Beginvoorwaarde:** T33. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

First complete T33, keep SELinux enforcing, and use only harmless synthetic content. This is outside the core EX200 objective set.
```bash
printf 'Synthetic policy test\n' > /srv/intranet/secret.txt
chmod 644 /srv/intranet/secret.txt
chcon -t admin_home_t /srv/intranet/secret.txt
ls -Z /srv/intranet/secret.txt
START=$(date '+%H:%M:%S')
curl http://localhost:8404/secret.txt
ausearch -m AVC -c httpd -ts "$START" --raw > /root/labhttpd.avc
cd /root
audit2why < labhttpd.avc
audit2allow -M labhttpd < labhttpd.avc
cat labhttpd.te
```
Read the .te before installing; it must contain only the synthetic test denials from the verification window. If unrelated events appear, do not install: repeat with a narrower interval/audit serial.
```bash
semodule -i /root/labhttpd.pp
semodule -l | awk '$1=="labhttpd"'
curl --fail http://localhost:8404/secret.txt
printf 'This module broadens httpd access to admin_home_t. A mislabeled file should normally be fixed with restorecon, not a custom module.\n' > /root/policy_module.txt
```
Keep the module only while evaluating this optional exercise; afterwards remove with semodule -r labhttpd and restorecon secret.txt. A full relabel resets chcon, so the intentionally wrong test context is not a persistent application configuration.

---

**T35 — Rootless container (echo/emma)**

**Beginvoorwaarde:** T11, T15. Voer uitsluitend de stappen voor de genoemde VM uit.

**VM: echo, as user `emma`. Uitvoering: rootconsole, behalve blokken die expliciet een gewone gebruiker noemen.**

As root on the application VM:
```bash
dnf install -y podman skopeo
loginctl enable-linger emma
firewall-cmd --permanent --zone=public --add-port=9191/tcp
firewall-cmd --reload
```
Log in directly as emma via console/SSH (not merely sudo -u). Confirm XDG_RUNTIME_DIR and systemctl --user work. First inspect the actual ARM image; image tags/manifests and application paths are external prerequisites:
```bash
podman pull registry.access.redhat.com/ubi10/httpd-24
podman image inspect registry.access.redhat.com/ubi10/httpd-24
podman volume create emma-site
podman run --rm --user 0 -v emma-site:/data:Z registry.access.redhat.com/ubi10/ubi sh -c 'printf "Echo Container OK\n" > /data/index.html; chmod 755 /data; chmod 644 /data/index.html'
mkdir -p ~/.config/containers/systemd
cat > ~/.config/containers/systemd/emma-site.volume <<'EOF'
[Volume]
VolumeName=emma-site
EOF
cat > ~/.config/containers/systemd/emma-site.container <<'EOF'
[Unit]
Description=Lab web container
Wants=network-online.target
After=network-online.target
[Container]
Image=registry.access.redhat.com/ubi10/httpd-24
ContainerName=emma_site
PublishPort=9191:8080
Volume=emma-site.volume:/var/www/html:Z
Environment=LAB_ENV=exam3
AutoUpdate=registry
[Service]
Restart=always
TimeoutStartSec=300
[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user start emma-site.service
systemctl --user status emma-site.service
curl --fail http://localhost:9191/
```
Do not enable the generated Quadlet service; [Install] is interpreted by the generator. Verify after a normal reboot and from the peer VM. If it fails inspect user journal, image port, path, directory traversal and SELinux labels; do not mark an untested image as verified.
As root install skopeo; as emma:
```bash
skopeo inspect docker://registry.access.redhat.com/ubi10/ubi:latest > ~/skopeo_inspect.txt
skopeo list-tags docker://registry.access.redhat.com/ubi10/ubi > ~/skopeo_tags.txt
mkdir -p ~/.config/containers
podman login --authfile ~/.config/containers/auth.json registry.redhat.io
chmod 600 ~/.config/containers/auth.json
printf '%s\n' "$HOME/.config/containers/auth.json" > ~/auth_path.txt
systemctl --user enable --now podman-auto-update.timer
```
Registry login requires your own account and is independent of the public access.redhat.com image. For private auto-updates add REGISTRY_AUTH_FILE with this absolute file path to a drop-in for podman-auto-update.service. Do not assume a runtime auth.json survives reboot. Test timer, dry-run auto-update and user journal. No credentials are supplied by this package.
