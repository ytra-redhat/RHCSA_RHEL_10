# Examen 2 — opdrachten (Rocky/RHEL 10, VMware Fusion ARM64)

Community-oefeningen, geen officiële examenvragen of officiële puntentelling.
Lees START-HIER.md. Iedere opdracht noemt de VM. Systeemcommando's worden in de Linux-gast uitgevoerd; Fusion-beheercommando's uitsluitend op de Mac.
Containers, LVM-shrink en eigen SELinux-modules zijn verdieping. Internet is vereist voor externe Flatpak/containerbronnen; offline uitvoering daarvan is niet bewezen.
Voer deze taakvolgorde uit: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35.
Controleer elk blijvend resultaat na een normale reboot en netwerkdiensten vanaf de andere VM. Tijdelijke regels/processen en diagnostische testfouten zijn uitzonderingen.
Werk op lege labdisks; nvme0n1 is nooit een oefendisk. Controleer vooraf lsblk, findmnt / en wipefs -n. Bij bestaande oefendata niet opnieuw formatteren.

**Task 1 — Emergency Recovery via GRUB Kernel Argument** *(charlie)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


The root password on `rhel10-charlie` is unknown. This time, use the **`init=/bin/bash enforcing=0`** method (not `rd.break`) to recover:

1. Interrupt GRUB, edit the kernel line, replace `ro` with `rw` and append `init=/bin/bash enforcing=0`
2. Boot to a raw bash shell
3. Reset the root password to `Ex200Pass!`
4. Ensure SELinux will relabel on next boot
5. Reboot cleanly

---

**Task 2 — Change Default Target from Rescue to Graphical** *(delta)*

**Beginvoorwaarde:** seed voltooid op delta; gebruik het rootwachtwoord van de golden-installatie. Voer uitsluitend de stappen voor de genoemde VM uit.


`rhel10-delta` is booting into `rescue.target`. Change the default target to `graphical.target` and reboot. Verify with `systemctl get-default` and confirm `runlevel` output shows `5`.

Then install the required package group if the GUI is not present.

---

**Task 3 — Bootloader: Disable Quiet Boot and Add Kernel Argument** *(charlie)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


On `charlie`, edit GRUB with the following persistent changes:

- Remove `rhgb` and `quiet` from `GRUB_CMDLINE_LINUX`
- Add `audit=1` and `net.ifnames=0`
- Set `GRUB_TIMEOUT=5`

Regenerate GRUB using `grub2-mkconfig` **and** rebuild the initramfs with `dracut -f`. Reboot and verify with `cat /proc/cmdline`.

---

**Task 4 — Configure Networking with `nmcli` + Custom DNS** *(both nodes)*

**Beginvoorwaarde:** T3. Voer uitsluitend de stappen voor de genoemde VM uit.


| Host    | Hostname              | IPv4               | IPv6            | Gateway        | DNS                     |
| ------- | --------------------- | ------------------ | --------------- | -------------- | ----------------------- |
| charlie | `charlie.ex200.lab` | `10.20.30.11/24` | `fd42::11/64` | NAT/DHCP | NAT/DHCP |
| delta   | `delta.ex200.lab`   | `10.20.30.12/24` | `fd42::12/64` | NAT/DHCP | NAT/DHCP |

- Set the connection to autoconnect at boot
- Add a **connection alias** named `lab-static` on both nodes
- Add both hosts to `/etc/hosts` on each node
- Verify both hosts can ping each other by short hostname (`charlie`, `delta`)

---

**Task 5 — Firewalld: Custom Zone with Rich Rules** *(charlie)*

**Beginvoorwaarde:** T4. Voer uitsluitend de stappen voor de genoemde VM uit.


On `charlie`:

1. Create a **new permanent zone** called `labzone`
2. Assign the `lab-static` connection to `labzone`
3. In `labzone`, permanently allow:
   - `ssh`, `https`, `dns`
   - TCP port range `9000-9010`
4. After step 6, add a **rich rule** to `labzone` that drops all traffic from `10.20.30.100` for `60s`
5. Set `labzone` as the **default zone**
6. Reload and verify with `firewall-cmd --list-all --zone=labzone`

---

**Task 6 — Users and Groups with Custom Home & Shell** *(charlie)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


    Groups:
      ops        GID: 6000
      qateam     GID: 6001
      auditors   GID: 6002  (system group)

    Users:
      emma    UID: 2100  primary: ops       supplementary: qateam        home: /srv/users/emma
      frank   UID: 2101  primary: qateam    supplementary: auditors      shell: /bin/zsh (install zsh)
      gina    UID: 2102  primary: ops                                     comment: "Gina — DBA"
      henry   UID: 2103  primary: auditors  no interactive shell (nologin)

Verify home directories exist, permissions are `700`, and use `getent` to confirm group memberships.

---

**Task 7 — Password Aging via `chage` + PAM `pwquality`** *(charlie)*

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.


- Set the password for all Task 6 users to `Init!Pass2026`
- `emma`: min 3 days, max 45 days, warn 7 days, inactive 14 days
- `frank`: password must be changed on next login, account locks 5 days after expiry
- `gina`: account expires **2027-01-01**
- Configure `/etc/security/pwquality.conf.d/90-lab.conf`:
  - `minlen = 12`
  - `dcredit = -1` (at least 1 digit)
  - `ucredit = -1` (at least 1 uppercase)
  - `ocredit = -1` (at least 1 special char)
- Test a bad password as a normal user (root bypasses quality rejection unless enforce_for_root is configured)

---

**Task 8 — Sudo with User Aliases and NOPASSWD Command Alias** *(charlie)*

**Beginvoorwaarde:** T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit.


Create `/etc/sudoers.d/lab_sudo`:

- User_Alias `OPSTEAM = emma, gina`
- User_Alias `QAUSERS = frank`
- Cmnd_Alias `NETADMIN = /usr/bin/nmcli, /usr/sbin/ip, /usr/sbin/ss`
- Cmnd_Alias `SVCMGMT = /usr/bin/systemctl status *, /usr/bin/systemctl restart httpd`
- `OPSTEAM` may run `NETADMIN` **without** password
- `QAUSERS` may run `SVCMGMT` **with** password
- The `auditors` group may run `/usr/bin/cat /var/log/*` only

Validate with `visudo -cf /etc/sudoers.d/lab_sudo` and `sudo -l -U emma`.

---

**Task 9 — ACLs on a Shared Project Directory** *(charlie)*

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.


Create `/srv/project/phoenix`:

- Owned by `gina:ops`, mode `2770` (SGID)
- Grant `frank` **rwx** via ACL (default + access ACL)
- Grant the `auditors` group **read-only** access via ACL (default + access ACL)
- Deny `henry` all access with an ACL entry
- Verify with `getfacl /srv/project/phoenix`
- Have `gina` create a file inside and confirm `frank` can edit it and `henry` cannot read it

---

**Task 10 — Umask Per-Group and Symlinks** *(both nodes)*

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.


On `charlie`:

- Set the default `umask` for members of `ops` to `0027` (group readable, world excluded)
- Leave all other users at the distribution default
- Do this via a drop-in file in `/etc/profile.d/`

On `delta`:

- Create `/opt/data/original.txt` with content `"exam data"`
- Create a **hard link** `/opt/data/hardlink.txt`
- Create a **symbolic link** `/root/softlink.txt` → `/opt/data/original.txt`
- Delete `/opt/data/original.txt` and demonstrate which link still works
- Explain the inode difference (add a comment in `/root/link_notes.txt`)

---

**Task 11 — SSH Key Auth + Disable Password Auth for a Specific User** *(charlie ↔ delta)*

**Beginvoorwaarde:** T4, T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit.


1. As `root` on `charlie`, generate an **ecdsa-sha2-nistp521** key (no passphrase)
2. Copy the key to `root@delta` using `ssh-copy-id`
3. Create `emma` on `delta` (same UID) and set up key auth from `emma@charlie` → `emma@delta` using an **ed25519** key with passphrase `Lab#2026`
4. On `delta`, configure `sshd_config` so:
   - `PermitRootLogin` = `prohibit-password`
   - `PasswordAuthentication no` **for user `emma` only** (use a `Match User emma` block)
   - `AllowUsers root emma frank`
5. Reload `sshd` and validate with `sshd -t`

---

**Task 12 — Secure File Transfer with Bandwidth Limit + Checksums** *(charlie ↔ delta)*

**Beginvoorwaarde:** T11. Voer uitsluitend de stappen voor de genoemde VM uit.


- Use `rsync` over SSH from `charlie` to `delta`, syncing `/etc/skel/` to `/tmp/skel_backup/`:
  - Preserve permissions, ownership, timestamps
  - Limit bandwidth to `500 KB/s`
  - Delete extraneous files on destination
- Use `sftp` in **batch mode** with a batch file `/root/sftp_batch.txt` that uploads `/etc/hostname` from charlie to `/tmp/` on delta
- Generate a SHA-256 checksum of `/etc/hostname` on both sides and confirm they match

---

**Task 13 — Configure Two Repositories + GPG Key Import** *(charlie)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


1. Mount the Rocky 10 DVD ISO at `/mnt/rhel10`
2. Create `/etc/yum.repos.d/lab-baseos.repo` and `/etc/yum.repos.d/lab-appstream.repo` (**two separate files** this time)
3. Both must have `gpgcheck=1` — select/import the correct Rocky 10 or RHEL 10 signing key for this DVD; retain gpgcheck=1
4. Set `enabled=1` and `metadata_expire=1h`
5. Priority: BaseOS = `10`, AppStream = `20` (built-in DNF repo option; no priorities plugin required)
6. Confirm with `dnf repolist enabled` and by listing packages available from `lab-baseos` only

---

**Task 14 — Flatpak: Configure Remote + Install App** *(charlie, requires GUI or CLI-only ok)*

**Beginvoorwaarde:** T13. Voer uitsluitend de stappen voor de genoemde VM uit.


1. Install `flatpak` from RPM
2. Add the **Flathub** remote system-wide (not per-user)
3. Search for the app `gedit` (or `org.gnome.gedit`)
4. Install it system-wide
5. List installed Flatpak apps
6. Uninstall it and remove unused runtimes

*(If no internet: document steps in `/root/flatpak_procedure.txt` and skip installation.)*

---

**Task 15 — RPM Verification + Reinstall** *(charlie)*

**Beginvoorwaarde:** T13. Voer uitsluitend de stappen voor de genoemde VM uit.


1. Install `nano` and record its version
2. Verify the installed package reports no modifications — output should be clean
3. Modify `/etc/nanorc` (add a comment) and verify again — confirm the `5` (checksum) flag appears
4. Restore the config file to its packaged state
5. Query which package owns `/etc/hosts`
6. Query all files installed by the `chrony` package
7. List all installed packages sorted by install date

---

**Task 16 — GPT Partitions with `parted` (Scripted)** *(charlie, `/dev/nvme0n2`)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


Using **`parted` in non-interactive mode** (not `fdisk`/`gdisk`) on `/dev/nvme0n2`:

1. Create GPT label
2. Create partitions:

   - `nvme0n2p1`: 2 GiB — for XFS
   - `nvme0n2p2`: 1 GiB — for swap
   - `nvme0n2p3`: rest of disk — for LVM (flag: `lvm`)
3. Verify alignment with `parted /dev/nvme0n2 align-check optimal 1`
4. Run `partprobe /dev/nvme0n2`

---

**Task 17 — VFAT Filesystem + Mount by Label** *(charlie)*

**Beginvoorwaarde:** T16. Voer uitsluitend de stappen voor de genoemde VM uit.


- Format `nvme0n2p1` as **XFS** with label `charlieXFS`
- Create a small VFAT filesystem on `/dev/nvme0n3` (use partition `nvme0n3p1`, size 500 MiB) with label `USBDATA`
- Mount points: `/mnt/charliexfs` and `/mnt/usbdata`
- `/etc/fstab`:
  - `nvme0n2p1` mounted by **UUID**
  - `nvme0n3p1` mounted by **LABEL**, mount options `noexec,nodev,nosuid`
- Run `systemctl daemon-reload`, then `mount -a`
- Reboot and confirm both are mounted

---

**Task 18 — Swap File (Not Partition) with Priority** *(delta)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


This exam variant uses a **swap file** instead of a swap partition:

1. Create a `1 GiB` file at `/swap/extraswap.img` (use `dd` or `fallocate`)
2. Set permissions to `0600`
3. Format it with `mkswap`
4. Add to `/etc/fstab` with priority `20`, activate with `swapon -a`
5. Verify with `swapon --show` and `free -h`

---

**Task 19 — LVM with Striping and Custom PE Size** *(charlie, `/dev/nvme0n2p3` + `/dev/nvme0n4`)*

**Beginvoorwaarde:** T16. Voer uitsluitend de stappen voor de genoemde VM uit.


1. Initialize `/dev/nvme0n2p3` and `/dev/nvme0n4` as physical volumes (whole `nvme0n4`, no partition)
2. Create VG `vg_lab2` with PE size **32 MiB**
3. Create a **striped** LV `lv_stripe` with 2 stripes across both PVs, size `1 GiB`
4. Create a **linear** LV `lv_home2` sized using **80 extents**
5. Format `lv_stripe` as **ext4** and `lv_home2` as **XFS**
6. Mount both persistently at `/mnt/stripe` and `/mnt/home2`
7. Verify with `pvs`, `vgs`, `lvs -a -o+devices`

---

**Task 20 — Reduce a VG, Then Extend an LV** *(charlie)*

**Beginvoorwaarde:** T19. Voer uitsluitend de stappen voor de genoemde VM uit.


1. Migrate all extents off `/dev/nvme0n4`. A plain `pvmove` **can fail here because of stripe allocation constraints** — work out why, and find the flag that makes it succeed
2. Remove `/dev/nvme0n4` from `vg_lab2` (`vgreduce`)
3. Wipe the LVM signature from `/dev/nvme0n4` (`pvremove`, `wipefs -a`)
4. Extend `lv_home2` to **use all remaining free space** in `vg_lab2` in a **single command** and grow the XFS filesystem online
5. Confirm with `df -h /mnt/home2` and `lvs -a -o+devices` — record segtype/stripes/devices; migration does not imply conversion to linear

---

**Task 21 — NFSv4 Only With AUTH_SYS** *(delta)*

**Beginvoorwaarde:** T4. Voer uitsluitend de stappen voor de genoemde VM uit.


On `delta` (NFS server):

1. Install `nfs-utils`
2. Disable NFSv3 via `/etc/nfs.conf` — v3 off, v4 and v4.2 on
3. Create `/srv/nfs/projects` and `/srv/nfs/archive`; use an explicitly shared UID/GID or all_squash policy so the intended client writer has DAC access
4. Export them:
   - `/srv/nfs/projects` — read/write to `10.20.30.0/24`, `sync`, `sec=sys`, `no_subtree_check`
   - `/srv/nfs/archive` — read-only to `charlie.ex200.lab`, `sync`, `sec=sys`, `root_squash`
5. Firewall: allow `nfs` service permanently
6. Start/enable `nfs-server`; validate with `exportfs -v`, `/proc/fs/nfsd/versions`, and a real NFSv4 mount; showmount is not decisive for NFSv4-only

---

**Task 22 — NFS Client with `nofail` and Async Options** *(charlie)*

**Beginvoorwaarde:** T21, T4. Voer uitsluitend de stappen voor de genoemde VM uit.


On `charlie`:

1. Mount points: `/mnt/projects` and `/mnt/archive`
2. Add persistent `/etc/fstab` entries mounting both exports as `nfs4`, with `_netdev` and `nofail`; projects read/write, archive read-only
3. Run `systemctl daemon-reload && mount -a`
4. Create a file in `/mnt/projects` as `root` — expect success
5. Try in `/mnt/archive` — expect read-only failure

---

**Task 23 — AutoFS Indirect Map With Wildcard & Custom Timeout** *(charlie)*

**Beginvoorwaarde:** T11, T21, T22. Voer uitsluitend de stappen voor de genoemde VM uit.


Configure autofs to mount user home directories from `delta:/srv/nfs/homes/<user>` under `/net/homes/<user>`:

1. Install `autofs`
2. Create a master map entry for `/net/homes` with a `60`-second timeout and `--ghost` enabled
3. Create the indirect map file using a wildcard key so any username resolves to its export
4. On `delta`: create `/srv/nfs/homes/emma`, add to exports, reload
5. On `charlie`: `su - emma`, then `ls /net/homes/emma` should trigger the mount
6. Wait 60 seconds idle — mount should auto-unmount

---

**Task 24 — Permission Repair Scenario** *(charlie)*

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.


The application at `/opt/finance/` has been broken by a bad `chmod`. Fix these issues:

1. `/opt/finance/` — currently `000`; should be `2750`, owned by `gina:ops`
2. `/opt/finance/reports/` — should inherit group `ops` via SGID
3. `/opt/finance/bin/run_report.sh` — needs `0754` and setuid `gina` (mode `4754`)
4. `/opt/finance/private/` — must be `0700`, owned by `gina:ops`
5. Find every SUID binary under `/usr/bin` and save to `/root/suid_list.txt`

---

**Task 25 — Chrony Server + Client** *(both nodes)*

**Beginvoorwaarde:** T4. Voer uitsluitend de stappen voor de genoemde VM uit.


- On `delta`: configure `chrony` as an **NTP server** for the `10.20.30.0/24` subnet. Enable and start `chronyd`, open firewall for `ntp`.
- On `charlie`: configure `chrony` client to use **delta only** as its time source; remove pool/server defaults.
- Verify with `chronyc sources -v` on charlie — delta should be selected with `^*`; `^+` is only a candidate.
- Set timezone: `charlie` → `Europe/London`, `delta` → `Asia/Tokyo`.

---

**Task 26 — Tuned: Create a Fully Custom Profile** *(charlie)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


1. Install and enable `tuned`
2. Create a **new** profile `lab-highio` in `/etc/tuned/lab-highio/tuned.conf`:
   - Inherit from `throughput-performance`
   - Set `vm.dirty_ratio = 40`
   - Set `vm.swappiness = 10`
   - Request CPU governor `performance`; record N/A if the Fusion guest exposes no cpufreq interface
3. Activate it
4. Confirm with `tuned-adm active` and `sysctl vm.swappiness`
5. Verify persistence after reboot

---

**Task 27 — Nice, Cgroup Limits, and Killing by Pattern** *(charlie)*

**Beginvoorwaarde:** T13. Voer uitsluitend de stappen voor de genoemde VM uit.


1. Launch a CPU-heavy task (`openssl speed -multi 2 &`, or `stress-ng --cpu 2 &`)
2. Launch a task that genuinely consumes RAM — writing into `/dev/shm` (tmpfs) works without extra packages. Watch it with `free -h`, and clean up afterward: the file stays resident in RAM even after the writer exits
3. Identify the top CPU consumer using `ps` with a sort field
4. Change one process's nice value from its default to `19`
5. Launch a process bounded to 20% of a CPU using a transient systemd scope
6. Kill all `stress-ng` and `openssl` processes by matching the full command line
7. Restart `chronyd` after a configuration change and verify its sources. SIGHUP terminates chronyd; it is not a reload operation.

---

**Task 28 — Journal Forwarding + Log Rotation** *(charlie)*

**Beginvoorwaarde:** T7, T8. Voer uitsluitend de stappen voor de genoemde VM uit.


1. Enable persistent journal storage, max disk size `500M`
2. Configure `journald` to **forward to syslog**
3. Configure `rsyslog` to write `authpriv.*` to `/var/log/secure.lab`, and rotate it weekly keeping 8 weeks via `/etc/logrotate.d/secure.lab`
4. Test: attempt a failed `sudo` as `frank` → confirm the entry appears in both the journal (matched by command name) and `/var/log/secure.lab`
5. Prune journal entries older than 7 days

---

**Task 29 — Systemd Timer with OnCalendar Every 3 Hours** *(charlie)*

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.


1. `at`: schedule for 3 minutes from now: append `"at-fired $(date)"` to `/var/log/at_lab.log`
2. `cron`: as `emma`, run `df -h > ~/disk_report.log` every **weekday at 07:15**
3. `systemd timer`:
   - Service `/etc/systemd/system/labhealth.service` runs `/usr/local/bin/labhealth.sh`
   - Script writes `uptime`, `free -m`, and `df -h /` to `/var/log/labhealth.log`
   - Timer `/etc/systemd/system/labhealth.timer` fires **every 3 hours**, `Persistent=true`
   - Enable timer, verify with `systemctl list-timers --all`

---

**Task 30 — Argument Parser with `case` Statement** *(charlie)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


Write `/usr/local/bin/svcctl.sh` that:

- Takes **two** arguments: `<action>` and `<service>`
- Valid actions: `start`, `stop`, `restart`, `status`, `check`
- `check` should print `RUNNING` or `STOPPED` based on `systemctl is-active`
- Any other action → print usage to `stderr` and exit `2`
- If service does not exist (`systemctl cat` fails), print `"Unknown service"` and exit `3`
- Return proper exit codes; test with `bash -x`

Use a `case` statement, not chained `if/elif`.

---

**Task 31 — While-Read Loop That Processes a CSV** *(charlie)*

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.


Write `/usr/local/bin/csv_users.sh`:

- Input file `/root/newusers.csv` with format `username,uid,gid,fullname`:

  ivan,2200,6000,Ivan Petrov
  julia,2201,6000,Julia Kim
  kai,2202,6001,Kai Nguyen
- For each line:

  - Skip lines starting with `#` or blank lines
  - Create the user with the given UID, GID (assume group exists), and full name as comment
  - Set a random password generated with `openssl`
  - Append `username,password` to `/root/passwords.txt` (mode `0600`)
- Use `while IFS=, read -r ...` and `[[ ... ]]` tests

---

**Task 32 — Reporting Script with Trap and Cleanup** *(charlie)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


Write `/root/health_report.sh`:

- Collects: hostname, kernel, uptime, load, top 5 CPU processes, disk usage, failed systemd units
- Writes to a unique temporary file under `/var/log/health/` first, then atomically moves to `/var/log/health/$(hostname)-$(date +%F).log`
- Uses `trap` to clean up the tmp file on error/interrupt
- Rotates: keep only 14 daily reports
- Schedule via **cron** at `06:00` every day **except the 1st of the month**

---

**Task 33 — SELinux for a Custom Web Root** *(charlie)*

**Beginvoorwaarde:** T13. Voer uitsluitend de stappen voor de genoemde VM uit.


1. Confirm SELinux is `enforcing`; if not, set it permanently
2. Install `httpd`, enable, start
3. Create `/srv/websites/site1/`; add `index.html` = `"Site1 charlie"`
4. Configure `httpd` to use `/srv/websites/site1/` as `DocumentRoot` (drop-in `/etc/httpd/conf.d/site1.conf`)
5. On restart, `httpd` fails or serves 403 — diagnose it from the journal and the audit log
6. Apply the correct persistent file context for `/srv/websites` and everything below it
7. Verify with `curl http://localhost/` → returns `"Site1 charlie"`
8. Confirm the process context of `httpd`

---

**Task 34 — Non-Standard SSH Port with SELinux + Booleans** *(charlie)*

**Beginvoorwaarde:** T5, T11, T33. Voer uitsluitend de stappen voor de genoemde VM uit.


1. Configure `sshd` to listen on **port 2222** in addition to 22
2. Add `2222/tcp` to the SELinux policy so sshd may bind it
3. Add firewall rule for port `2222/tcp` in `labzone` (persistent)
4. Restart `sshd`, confirm it is listening on both ports
5. Enable persistently the boolean `ssh_sysadm_login` (or `use_nfs_home_dirs` if not present) and verify
6. Set the boolean `container_manage_cgroup` on persistently
7. Copy `/etc/motd` to `/var/www/html/motd.txt`; observe its context is `admin_home_t` or `etc_t`; fix it so it becomes `httpd_sys_content_t`

---

**Task 35 — Rootless Container with Persistent Volume + Quadlet Timer** *(charlie, as user `emma`)*

**Beginvoorwaarde:** T4, T5, T6, T23. Voer uitsluitend de stappen voor de genoemde VM uit.


As user `emma` (rootless):

1. As root, enable **linger** for `emma`
2. Log in as `emma`, ensure `XDG_RUNTIME_DIR` is set
3. Search and pull `registry.access.redhat.com/ubi10/nginx-126` (**nginx**, not httpd this time)
4. Inspect the image; note the exposed port and the user it runs as
5. Create a named **podman volume** `emma-nginx-data` and place `html/index.html` in it containing `Emma Nginx OK` (the volume is mounted at /opt/app-root/src)
6. Create Quadlet **volume** and **container** files under `~/.config/containers/systemd/`:
   - A `.volume` unit declaring the named volume
   - A `.container` unit running the nginx image as `emma_nginx`, publishing host port `9090` to container port `8080`, mounting the volume at the nginx web root with the correct SELinux relabel flag, restarting always, and allowing a generous start timeout
7. Reload the user daemon and start the service
8. Test: `curl http://localhost:9090/` from `emma`
9. **Bonus** — create a normal systemd user timer/service (not a Quadlet timer) that restarts the container every night at 03:00
10. Reboot; verify container starts automatically without emma logging in
