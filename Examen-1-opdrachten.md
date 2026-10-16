# Examen 1 — opdrachten (Rocky/RHEL 10, VMware Fusion ARM64)

Community-oefeningen, geen officiële examenvragen of officiële puntentelling.
Lees START-HIER.md. Iedere opdracht noemt de VM. Systeemcommando's worden in de Linux-gast uitgevoerd; Fusion-beheercommando's uitsluitend op de Mac.
Containers, LVM-shrink en eigen SELinux-modules zijn verdieping. Internet is vereist voor externe Flatpak/containerbronnen; offline uitvoering daarvan is niet bewezen.
Voer deze taakvolgorde uit: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35.
Controleer elk blijvend resultaat na een normale reboot en netwerkdiensten vanaf de andere VM. Tijdelijke regels/processen en diagnostische testfouten zijn uitzonderingen.
Werk op lege labdisks; nvme0n1 is nooit een oefendisk. Controleer vooraf lsblk, findmnt / en wipefs -n. Bij bestaande oefendata niet opnieuw formatteren.

**Task 1 — Break Into bravo and Reset Root Password** *(bravo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


The root password on `rhel10-bravo` is unknown. Break into the system using the `init=/bin/bash enforcing=0` method, reset the root password to `RedHat10!`, and ensure SELinux labels are updated before the next boot. Reboot and confirm login.

---

**Task 2 — Configure Boot Target** *(bravo)*

**Beginvoorwaarde:** T1. Voer uitsluitend de stappen voor de genoemde VM uit.


After breaking into bravo, confirm it is currently booting to `graphical.target`. Change the default boot target to `multi-user.target`. Reboot and verify the system boots without a GUI.

---

**Task 3 — Modify the Bootloader** *(alpha)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


Edit the GRUB configuration on `rhel10-alpha` with the following changes:

- Set `GRUB_TIMEOUT=10`
- Add the line: `GRUB_TIMEOUT_STYLE=countdown`
- Append `quiet` to the end of `GRUB_CMDLINE_LINUX`

Regenerate the GRUB config and reboot to verify.

---

**Task 4 — Configure Static IP and Hostname** *(both nodes)*

**Beginvoorwaarde:** T3. Voer uitsluitend de stappen voor de genoemde VM uit.


Configure the following on each server using `nmcli`. Configurations must survive reboot.

| Host  | Hostname            | IPv4                  | IPv6            | Gateway           |
| ----- | ------------------- | --------------------- | --------------- | ----------------- |
| alpha | `alpha.lab.local` | `192.168.100.10/24` | `fd00::10/64` | NAT/DHCP |
| bravo | `bravo.lab.local` | `192.168.100.20/24` | `fd00::20/64` | NAT/DHCP |

For the DNS exercise, use 8.8.8.8 and 1.1.1.1 as resolvers; set them on the NAT profile `fusion-nat`; keep the lab profile free of DNS and a gateway. Add entries for both hosts to `/etc/hosts` on both systems. Confirm connectivity between nodes by hostname.

---

**Task 5 — Configure Firewall for SSH and HTTP** *(alpha)*

**Beginvoorwaarde:** T4. Voer uitsluitend de stappen voor de genoemde VM uit.


On `alpha`:

- Ensure `sshd` is permanently allowed in the `public` zone
- Permanently allow HTTP traffic (port 80/tcp) in the `public` zone
- After the reload, add a runtime-only rule allowing port `8080/tcp`; verify that it disappears on another reload. Task 35 adds its own permanent rule.
- Permanently allow TCP ports `5900-5910` in the `internal` zone
- Reload and confirm permanent rules persist; temporary rules are excluded from reboot persistence

---

**Task 6 — Create Users and Groups** *(alpha)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


Create the following users and groups. All UIDs and GIDs must be set as specified.

```
Groups:
  sysadmins  GID: 5000
  developers GID: 5001
  contractors GID: 5002

Users:
  alice   UID: 1050  primary: developers   supplementary: sysadmins
  bob     UID: 1051  primary: developers   supplementary: contractors  shell: /bin/bash
  carol   UID: 1052  primary: contractors  no login shell
  dave    UID: 1053  primary: sysadmins    account expires: 90 days from today
```

Verify each user's entry in `/etc/passwd` and group memberships with `id`.

---

**Task 7 — Password Aging Policy** *(alpha)*

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.


- Set the password for all users created in Task 6 to `Lab@12345` — do it non-interactively, in one command
- Using `chage`, configure `alice` with: minimum 7 days, maximum 60 days, warn 10 days
- Using `passwd`, configure `bob` with: minimum 5 days, maximum 90 days, warn 14 days, inactive 10 days
- Force `carol` to change her password on next login
- Set minimum password length to 8 using PAM pwquality configuration; verify the active PAM chain. Carol remains nologin: the age flag alone does not allow login.

---

**Task 8 — Configure sudo Access** *(alpha)*

**Beginvoorwaarde:** T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit.


Create a sudoers drop-in file in `/etc/sudoers.d/`. Configure:

- `sysadmins` group: full sudo access with no password
- `developers` group: can run `dnf` and `systemctl` with sudo
- `alice`: can run `/usr/sbin/useradd` and `/usr/sbin/userdel` in addition to her group grants (grants are additive)
- Create a command alias `PKGMGMT` for `/usr/bin/dnf`

Validate using `sudo -l -U alice`.

---

**Task 9 — Set-GID Collaborative Directory** *(alpha)*

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.


Create a shared directory `/data/devshare`:

- Owned by `alice:developers`
- Permissions: owner=rwx, group=rwx, other=no access
- Set the **set-GID** bit so new files inherit the `developers` group
- Set the **sticky bit** so users can only delete their own files
- Create a test file as `bob` and verify group ownership is `developers`

---

**Task 10 — Standard File Permissions & Umask** *(both nodes)*

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.


- On `alpha`, configure the system-wide umask so all newly created files default to `660` and directories default to `770`. Make this persistent for all users.
- On `bravo`, apply the same setting.
- Verify by creating a test file and directory as a regular user.

---

**Task 11 — Configure Key-Based SSH Authentication** *(alpha → bravo)*

**Beginvoorwaarde:** T1, T4, T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit.


On `alpha` as `root`:

1. Generate an RSA key pair (4096-bit, no passphrase)
2. Copy the public key to `root@bravo`
3. Confirm passwordless SSH from alpha to bravo

On `alpha` as `alice`:

1. Generate an ed25519 key pair
2. Copy the public key to `alice@bravo` (create alice on bravo if needed)
3. Confirm passwordless SSH from alice@alpha to alice@bravo

Ensure `PermitRootLogin yes` & `PasswordAuthentication yes` is set in `/etc/ssh/sshd_config` on bravo.

---

**Task 12 — Secure File Transfer** *(alpha → bravo)*

**Beginvoorwaarde:** T11. Voer uitsluitend de stappen voor de genoemde VM uit.


- Use `scp` to copy `/etc/hosts` from alpha to `/tmp/hosts_from_alpha` on bravo
- Use `rsync` to synchronize the `/etc/sysconfig/` directory from alpha to `/tmp/sysconfig_backup/` on bravo
- Use `sftp` interactively to upload `/etc/motd` from alpha to bravo's `/tmp/`

---

**Task 13 — Configure Repositories** *(alpha)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


Configure a local YUM/DNF repository from the Rocky 10 installation DVD ISO for this Fusion lab:

1. Mount the Rocky 10 DVD ISO at `/mnt/rhel10iso`
2. Create a repo file `/etc/yum.repos.d/rhel10-local.repo` with:
   - `[BaseOS]` section pointing to `file:///mnt/rhel10iso/BaseOS`
   - `[AppStream]` section pointing to `file:///mnt/rhel10iso/AppStream`
   - Both enabled, `gpgcheck=0`
3. Verify with `dnf repolist`
4. Make the mount persist across reboot — and test that persistence **without** rebooting

---

**Task 14 — Package Management Operations** *(alpha)*

**Beginvoorwaarde:** T13. Voer uitsluitend de stappen voor de genoemde VM uit.


- Install the `vim-enhanced`, `tmux`, and `wget` packages
- Verify `httpd` package is not installed; install it
- Query the installed `httpd` package and list all its configuration files
- Download (but don't install) the `nmap` package RPM to `/root/downloads/`
- Use `rpm` to verify the integrity of a package file
- Install `nmap` from the downloaded RPM
- Remove `nmap` with `rpm`

---

**Task 15 — Package Groups & Flatpak *(alpha)***

**Beginvoorwaarde:** T13. Voer uitsluitend de stappen voor de genoemde VM uit.


Part A — Package groups:

- List available package groups
- Install the "Development Tools" group
- Remove it

Part B — Flatpak (now a mandatory RHCSA objective):

- Add the Flathub remote
- Search for, install, update, and remove an available aarch64 application. Running a GUI app requires a graphical session; on a minimal guest record that limitation instead.
- Clean up unused runtimes

Part C — Installing an alternate app-stream version (the modern replacement for module streams):

- Discover what versioned `postgresql` packages are available, install `postgresql-server`, and confirm the installed version
- Determine whether `postgresql` is delivered as a module on RHEL 10, and record what you find

---

**Task 16 — Create GPT Partitions** *(bravo, /dev/nvme0n2)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


Using `/dev/nvme0n2` on bravo:

1. Create a GPT partition table
2. Create a 1 GiB partition (`nvme0n2p1`) — type: Linux filesystem
3. Create a 500 MiB partition (`nvme0n2p2`) — type: Linux swap
4. Create a 2 GiB partition (`nvme0n2p3`) — type: Linux filesystem
5. Run `partprobe` to inform the kernel
6. Verify with `lsblk` and `fdisk -l /dev/nvme0n2`

---

**Task 17 — Create and Mount File Systems by UUID** *(bravo)*

**Beginvoorwaarde:** T16. Voer uitsluitend de stappen voor de genoemde VM uit.


1. Format `nvme0n2p1` as **XFS**
2. Format `nvme0n2p3` as **ext4** with label `DATASTORE`
3. Create mount points `/mnt/xfs_data` and `/mnt/ext4_data`
4. Add persistent entries to `/etc/fstab` using **UUID** for xfs_data and **LABEL** for ext4_data
5. Run `mount -a` and verify with `df -hT`
6. Create a test file in each mount point and reboot to confirm persistence

---

**Task 18 — Configure Swap Space** *(bravo)*

**Beginvoorwaarde:** T16. Voer uitsluitend de stappen voor de genoemde VM uit.


1. Format `nvme0n2p2` as swap with label `EXTRASWAP`
2. Add a persistent swap entry to `/etc/fstab` with priority `10`
3. Activate the swap and verify with `swapon -s` and `free -h`
4. Reboot and confirm the swap and its priority survived

---

**Task 19 — Create and Manage LVM** *(bravo, /dev/nvme0n3)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


Using `/dev/nvme0n3` (full disk, unpartitioned):

1. Initialize `/dev/nvme0n3` as a physical volume
2. Create a volume group `vg_lab` with PE size 16 MiB
3. Create logical volume `lv_data` with size **512 MiB (32 extents)**
4. Create logical volume `lv_logs` using **25 extents**
5. Format `lv_data` as XFS and `lv_logs` as ext4
6. Mount both persistently under `/mnt/lv_data` and `/mnt/lv_logs`
7. Verify with `pvs`, `vgs`, `lvs`

---

**Task 20 — Extend a Logical Volume** *(bravo)*

**Beginvoorwaarde:** T19. Voer uitsluitend de stappen voor de genoemde VM uit.


Extend the `lv_data` logical volume (from Task 19) to **1 GiB** total size:

1. Verify there is enough free space in `vg_lab`
2. Extend the LV and grow the filesystem in one command
3. Confirm the new size with `df -h /mnt/lv_data`

---

**Task 21 — Configure NFS Server** *(bravo)*

**Beginvoorwaarde:** T4. Voer uitsluitend de stappen voor de genoemde VM uit.


On `bravo` (NFS server):

1. Install `nfs-utils`
2. Create directories `/export/shared` and `/export/readonly`
3. Make `/export/shared` genuinely writable by clients — you should be able to name more than one approach and justify the one you pick
4. Add entries to `/etc/exports`:
   - `/export/shared` — read/write for `192.168.100.0/24`
   - `/export/readonly` — read-only for `192.168.100.10`
5. Start and enable `nfs-server.service`
6. Add permanent firewall rules for `nfs`, `mountd`, `rpc-bind`
7. Confirm exports with `exportfs -v`

---

**Task 22 — Mount NFS on Client** *(alpha)*

**Beginvoorwaarde:** T21, T4. Voer uitsluitend de stappen voor de genoemde VM uit.


On `alpha` (NFS client):

1. Create mount points `/mnt/nfs_shared` and `/mnt/nfs_ro`
2. Mount them using NFS entries in `/etc/fstab` with the `_netdev` option
3. Verify with `mount -a` and `df -hT`
4. Create a test file in `/mnt/nfs_shared` and verify it appears on bravo

---

**Task 23 — Configure AutoFS** *(alpha)*

**Beginvoorwaarde:** T21, T4. Voer uitsluitend de stappen voor de genoemde VM uit.


On `alpha`, configure `autofs` to automatically mount user home directories from bravo:

1. Install `autofs`
2. Configure a direct map for `/export/shared` from bravo at the local path `/autodir`
3. Configure an indirect map so user home directories from `bravo:/export/home` auto-mount under `/mnt/autohome/<username>` on access
4. Start and enable `autofs`
5. Test by switching to a user whose home directory should be mounted

> You will need to create and export `/export/home` on bravo first, with a test user whose home lives there.

---

**Task 24 — File Permission Diagnostics** *(alpha)*

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.


The following files and directories have incorrect permissions. Fix them:

1. `/var/www/html/` — should be owned by `root:root`, world-readable, but not world-writable
2. Create `/secure/app/` — owned by `alice:developers`, no access for others, SGID set
3. A persistent fixture file `/var/tmp/badperms` exists with permissions `777` — change to `640`, owner `bob`, group `developers`
4. Find all world-writable files under `/etc` and report them (save list to `/root/world_writable.txt`)

---

**Task 25 — Configure Time Synchronization** *(both nodes)*

**Beginvoorwaarde:** T4. Voer uitsluitend de stappen voor de genoemde VM uit.


1. Install `chrony` if not present
2. Configure `/etc/chrony.conf` to use `pool 2.rhel.pool.ntp.org iburst` as the primary source
3. Start and enable `chronyd`
4. Verify sync with `chronyc tracking` and `timedatectl`
5. Set the timezone to `America/Chicago` on alpha and `UTC` on bravo

---

**Task 26 — Manage Tuning Profiles** *(alpha)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


1. Install and start the `tuned` service
2. List all available profiles
3. Display the currently active profile
4. Change the active profile to `throughput-performance`
5. Verify the active profile
6. Set up a **merged profile** combining `virtual-guest` and `powersave` — create a custom profile called `lab-custom` in `/etc/tuned/lab-custom/`
7. Apply `lab-custom` as the active profile
8. Make sure it survives a reboot — verify every file that controls profile persistence on RHEL 10

---

**Task 27 — Process Management** *(alpha)*

**Beginvoorwaarde:** T14. Voer uitsluitend de stappen voor de genoemde VM uit.


1. Launch three background `dd if=/dev/zero of=/dev/null` processes
2. Use `ps`, `top`, or `pidstat` to identify them
3. Use `renice` to change the niceness of one process to `10`
4. Use `renice` to change the same process niceness to `-5` (requires root)
5. Kill all `dd` processes using `killall`
6. Start a `sleep 3600` process, then send it `SIGSTOP`, then `SIGCONT`, then `SIGTERM`
7. Use `nice` to launch a new process `sleep 1000` with niceness `15`

---

**Task 28 — Persistent Journal and Log Management** *(both nodes)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


1. Configure `systemd-journald` to store logs persistently using a drop-in under `/etc/systemd/journald.conf.d/`
2. Verify the journal directory is created at `/var/log/journal/`
3. Use `journalctl` to:
   - Show logs since last boot
   - Filter logs for the `sshd` service
   - Show only error-level and above messages
   - Show the last 50 lines
4. Configure `rsyslog` to write all `*.info` messages to `/var/log/messages.info`
5. Use `logger` to send a test message and verify it appears in the correct log file

---

**Task 29 — Schedule Tasks** *(alpha)*

**Beginvoorwaarde:** T6. Voer uitsluitend de stappen voor de genoemde VM uit.


1. Using `at`, schedule a job to run in 5 minutes that appends `"Scheduled at task ran"` to `/var/log/at_test.log`
2. Using `crontab -e` for user `alice`, create a cron job that appends the current date to `~/cron_test.log` every day at 8:00 AM
3. Create a **systemd timer** unit that runs a script `/usr/local/bin/hourly_check.sh` every hour. The script should echo the date to `/var/log/hourly.log`
   - Create the service unit: `/etc/systemd/system/hourly-check.service`
   - Create the timer unit: `/etc/systemd/system/hourly-check.timer`
   - Enable and start the timer

---

**Task 30 — Conditional Script** *(alpha)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


Write a script `/usr/local/bin/syscheck.sh` that:

- Accepts one argument: `cpu`, `mem`, `disk`, or `all`
- If `cpu`: display platform-neutral CPU information using `lscpu` (ARM may have no x86 Model name field)
- If `mem`: display total and available memory from `free -h`
- If `disk`: display disk usage summary from `df -hT`
- If `all`: run all three checks
- If no argument or invalid argument: print usage instructions and exit with code `1`
- Make the script executable and test each argument

---

**Task 31 — Looping Script with User Creation** *(alpha)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


Write a script `/usr/local/bin/bulk_users.sh` that:

- Reads usernames from `/root/userlist.txt` (create this file with 5 usernames)
- For each username:
  - Create the user if it does not already exist
  - Set the password equal to the username
  - Print a success or "already exists" message
- Use a `for` loop with command substitution

---

**Task 32 — Backup Script with Cron** *(alpha)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


Write a script `/root/etcbackup.sh` that:

- Creates a compressed tar archive of `/etc` named with the current date: `etc_backup_YYYY-MM-DD.tar.gz`
- Saves it to `/root/backups/` (create if not exists)
- Removes backups older than 7 days
- Logs the backup filename and timestamp to `/var/log/etcbackup.log`

Schedule this script to run at **11:30 PM every night except Sunday** using cron.

---

**Task 33 — SELinux Modes and Contexts** *(both nodes)*

**Beginvoorwaarde:** T10, T14. Voer uitsluitend de stappen voor de genoemde VM uit.


1. On `alpha`: Confirm SELinux is in `enforcing` mode — set it persistently if not
2. On `bravo`: Set SELinux to `permissive` mode persistently (edit `/etc/selinux/config`)
3. On `alpha`:
   - Create `/webtest/index.html` with content `"Hello RHCSA"`
   - Check the SELinux context — it will be wrong for serving with httpd
   - Use `semanage fcontext` to add the correct `httpd_sys_content_t` context for `/webtest(/.*)?`
   - Apply the context with `restorecon -Rv /webtest`
   - Start httpd and verify the page is served

---

**Task 34 — SELinux Ports and Booleans** *(alpha)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.


1. Configure `httpd` to listen on port `8181`
   - Add the non-standard port to the SELinux policy for `http_port_t`
   - Confirm with `semanage port -l | grep http`
2. Check the current state of the boolean `httpd_can_network_connect`
3. Enable the boolean persistently
4. Check the boolean `httpd_enable_homedirs` and enable it persistently
5. Copy `/etc/hosts` to `/var/www/html/hosts.txt` — check and restore the SELinux context

---

**Task 35 — Deploy a Container as a Systemd Service (Quadlet)** *(alpha, as alice)*

**Beginvoorwaarde:** T4, T5, T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit.


As user `alice` (rootless container):

1. Search for and pull the `ubi10/httpd-24` image from `registry.access.redhat.com`
2. Inspect the image and identify the exposed port
3. Create a directory `~/web_content/` and add a file `index.html` with content: `"Welcome to Alice's Containerized Web Server!"`
4. Run the container named `alice_web` in detached mode:
   - Map local port `8080` to container port `8080`
   - Bind-mount `~/web_content/` to `/var/www/html/` with `:Z` for SELinux
5. Verify the container is running with `podman ps`
6. Test with `curl http://localhost:8080`
7. Create a **Podman Quadlet** at `~/.config/containers/systemd/alice-web.container` that reproduces that container as a user systemd service, starting at login. It must set the image, container name, published port, and the bind-mounted volume with the correct SELinux relabel flag, and restart always.
8. Enable user lingering for `alice`
9. Reload the user daemon and start the service
10. Reboot and confirm the container starts automatically and the webpage is accessible
