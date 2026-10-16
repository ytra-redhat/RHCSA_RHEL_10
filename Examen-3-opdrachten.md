# Examen 3 — opdrachten (Rocky/RHEL 10, VMware Fusion ARM64)

Community-oefeningen, geen officiële examenvragen of officiële puntentelling.
Lees START-HIER.md. Iedere opdracht noemt de VM. Systeemcommando's worden in de Linux-gast uitgevoerd; Fusion-beheercommando's uitsluitend op de Mac.
Containers, LVM-shrink en eigen SELinux-modules zijn verdieping. Internet is vereist voor externe Flatpak/containerbronnen; offline uitvoering daarvan is niet bewezen.
Voer deze taakvolgorde uit: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 33, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35.
Controleer elk blijvend resultaat na een normale reboot en netwerkdiensten vanaf de andere VM. Tijdelijke regels/processen en diagnostische testfouten zijn uitzonderingen.
Werk op lege labdisks; nvme0n1 is nooit een oefendisk. Controleer vooraf lsblk, findmnt / en wipefs -n. Bij bestaande oefendata niet opnieuw formatteren.

**Task 1 — Recover an Unbootable System** *(foxtrot)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

`rhel10-foxtrot` no longer boots — it drops to an emergency prompt. The root password is also unknown, so the emergency shell's login prompt is useless to you.

1. Gain access to the system
2. Identify why the boot fails (the cause is in a configuration file)
3. Repair it so the system boots unattended
4. Set the root password to `Ex3Recovery!`
5. Ensure SELinux labels remain correct for any file you edited
6. Reboot and confirm a clean multi-user boot with no manual intervention

---

**Task 2 — One-Shot Boot Into a Different Target** *(foxtrot)*

**Beginvoorwaarde:** T1. Voer uitsluitend de stappen voor de genoemde VM uit.

Without changing the system's default target:

1. Boot `foxtrot` **once** into `rescue.target` using a GRUB kernel argument
2. From that shell, record the output of `systemctl get-default` into `/root/target_check.txt`
3. Reboot normally and confirm the system returns to its usual default target on its own

---

**Task 3 — Manage Kernel Arguments With `grubby`** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

Do **not** hand-edit `/etc/default/grub` for this task.

1. List the currently installed kernels and identify the default one
2. Persistently add the kernel arguments `audit=1` and `transparent_hugepage=never` to **all** installed kernels
3. Persistently remove `rhgb` and `quiet` from all installed kernels
4. Reboot and verify with `/proc/cmdline`
5. Record the resulting `/proc/cmdline` in `/root/cmdline.txt`

---

**Task 4 — Diagnose and Repair a Failed Service** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

A service named `labdata.service` is enabled but fails to start.

1. Determine that it failed and capture the reason — save the diagnostic output to `/root/labdata_diag.txt`
2. Identify the specific missing dependency causing the failure
3. Create the missing component so the service starts successfully. It must run continuously and write the current date to `/var/log/labdata.log` once per minute
4. Ensure the service is running and starts automatically at boot
5. Confirm it is active after a reboot

---

**Task 5 — Override a Unit With a systemd Drop-In** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

Without editing the vendor-supplied unit file, override `sshd.service`:

1. Add a drop-in so `sshd` restarts automatically 30 seconds after any failure
2. Add a custom `Description` of `SSH Daemon (lab-tuned)`
3. Verify the override is being read and identify the exact path of the file you created
4. Record the output of `systemctl show sshd.service -p Restart -p RestartUSec -p Description` into `/root/sshd_override.txt`
5. Demonstrate how you would discard all overrides for a unit (document the command in the same file — do **not** actually run it)

---

**Task 6 — Input/Output Redirection** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

Working in `/root`:

1. Run `ls /etc /nonexistent` so that **stdout only** goes to `/root/redir_out.txt` and **stderr only** goes to `/root/redir_err.txt`
2. Run the same command so that stdout **and** stderr both land in `/root/redir_both.txt` in a single file
3. Append the current date to `/root/redir_out.txt` without truncating it
4. Run `df -h` so the output is written to `/root/df_report.txt` **and** displayed on your terminal at the same time
5. Run `find /etc -name '*.conf'` discarding all error messages but keeping the results in `/root/conf_list.txt`
6. Use a here-document to create `/root/notes.txt` containing three lines of your choice

---

**Task 7 — grep and Regular Expressions** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

Save each answer to the file named in brackets:

1. Every line in `/etc/passwd` for a user with a UID of exactly four digits `[/root/g1.txt]`
2. Every line in `/etc/ssh/sshd_config` that is **not** a comment and **not** blank `[/root/g2.txt]`
3. A count (number only) of how many users use `/sbin/nologin` as their shell `[/root/g3.txt]`
4. Every IPv4 address appearing anywhere in `/var/log/`, listed once each, printing **only the address** and not the whole line `[/root/g4.txt]`
5. Every line in `/etc/services` beginning with `http` followed by any character other than `s` `[/root/g5.txt]`
6. All files under `/etc` containing the case-insensitive string `selinux`, showing filename and line number `[/root/g6.txt]`

---

**Task 8 — Locating Files With `find`** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

Save results to the indicated files:

1. All files under `/var` larger than 5 MiB (5 × 1024 × 1024 bytes) `[/root/f1.txt]`
2. All files under `/etc` modified in the last 7 days `[/root/f2.txt]`
3. All files anywhere under `/home` and `/srv` owned by UID 3100 (do not create emma here; Task 11 does that) `[/root/f3.txt]`
4. All directories under `/etc` with permissions exactly `0700` `[/root/f4.txt]`
5. All `*.log` files under `/var/log` with -mtime +3 (more than three complete 24-hour age units), copied — not moved — into `/root/oldlogs/`, preserving source directory paths to avoid basename collisions in a **single** `find` command
6. All empty files under `/tmp`, deleted in a single command

---

**Task 9 — Archives and Compression** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

1. Create a **gzip**-compressed tar archive of `/etc/ssh` at `/root/ssh_backup.tar.gz`
2. Create a **bzip2**-compressed tar archive of the same directory at `/root/ssh_backup.tar.bz2`
3. Compare the two file sizes and record which is smaller in `/root/compression.txt`
4. List the contents of the gzip archive **without extracting it**, saving the listing to `/root/archive_list.txt`
5. Extract **only** `etc/ssh/sshd_config` from the gzip archive into `/root/restore/`
6. Create an archive of `/var/log` at `/root/logs.tar.gz` that **excludes** everything under `/var/log/journal`
7. Extract `/root/ssh_backup.tar.bz2` into `/root/restore_full/`, preserving permissions

---

**Task 10 — Use the System Documentation** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

No internet. Answer each using only on-system documentation, writing answers into `/root/docs_answers.txt` (one numbered line each):

1. Which manual **section** documents the `passwd` **file format** (as opposed to the command)?
2. Search all man pages for ones whose description mentions "partition table" — list the command names
3. What `journalctl` option limits output to the current boot? Cite the man page you found it in
4. Name any file under `/usr/share/doc/` that documents `chrony`, giving its full path
5. Using `info`, name the top-level node listing for the `coreutils` documentation
6. Which config file does `man 5 fstab` say is described, and what is the **sixth** field used for?

---

**Task 11 — Users With a Customized Skeleton** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

1. Add a file `/etc/skel/lab_welcome.txt` containing `Welcome to the EX200 lab` and a directory `/etc/skel/projects/`
2. Create group `research` with GID `7000`
3. Create users `emma` (UID 3100) and `noah` (UID 3101), both with primary group `research`
4. Confirm both received the skeleton content in their home directories
5. Create user `oscar` (UID 3102) whose home directory is `/opt/oscar` and confirm the skeleton content was placed there too
6. Move `noah`'s home directory to `/srv/homes/noah` **with its existing contents**, and verify `noah` can still log in and lands there

---

**Task 12 — sudo Defaults and Logging** *(echo)*

**Beginvoorwaarde:** T11. Voer uitsluitend de stappen voor de genoemde VM uit.

Create `/etc/sudoers.d/lab3_defaults`:

1. The `research` group may run all commands, with a password
2. Set a `Defaults` entry so sudo credentials are cached for `0` minutes (password every time) for the `research` group
3. Set a `Defaults` entry logging all sudo activity to `/var/log/sudo_lab.log`
4. Set a `Defaults` entry adding `/usr/local/lab/bin` to sudo's `secure_path`
5. Validate the file syntax before it takes effect, and verify with `sudo -l -U emma`

---

**Task 13 — ACL Masks and Default Inheritance** *(echo)*

**Beginvoorwaarde:** T11. Voer uitsluitend de stappen voor de genoemde VM uit.

Create `/srv/shared/data`, owned by `emma:research`, mode `2770`:

1. Grant `noah` `rwx` via an access ACL **and** a default ACL
2. Grant group `wheel` `r-x` via an access ACL **and** a default ACL
3. Set the ACL **mask** to `r-x` and record — in `/root/acl_effective.txt` — what `noah`'s *effective* permissions become and why
4. Create a file inside as `emma` and show the default ACL was inherited
5. Restore the mask to `rwx` and confirm `noah`'s effective permissions change back

---

**Task 14 — SELinux Contexts: `cp` vs `mv`** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

1. Create `/root/site_index.html` containing `Context Test`
2. Record its SELinux context in `/root/context_report.txt`
3. **Copy** it to `/var/www/html/copied.html`; record the resulting context
4. **Move** a second identical file to `/var/www/html/moved.html`; record the resulting context
5. Explain in the same report which operation produced the wrong context for httpd and why
6. Fix the incorrect file using the policy-driven tool (not `chcon`)
7. Copy a third file to `/var/www/html/preserved.html` in a way that **deliberately keeps** the source context, and note the option used

---

**Task 15 — Two Connection Profiles and Resolution Order** *(echo; static peer setup on foxtrot)*

**Beginvoorwaarde:** T1. Voer uitsluitend de stappen voor de genoemde VM uit.

1. Configure the host-only connection as a profile named `lab3-static` with the IPv4 and **IPv6 address** from the environment table; leave its gateway and DNS empty and use never-default for both families; it must autoconnect at boot
2. For the DHCP alternative, use Fusion host-only DHCP (its subnet differs from the static exam subnet). Confirm the configured host-only network actually offers DHCP. Create a **second** profile named `lab3-dhcp` on the same interface set to DHCP for IPv4 and automatic for IPv6, with autoconnect **disabled**
3. Demonstrate switching between the two profiles and switching back to `lab3-static`
4. Add both hosts to `/etc/hosts`
5. Explain in `/root/resolution.txt`: which file controls the *order* in which hostname lookups consult files vs DNS, and which line in it applies
6. Verify `foxtrot` resolves and responds by short hostname

---
On foxtrot also configure its static IPv4/IPv6, hostname and both hosts entries before testing connectivity.

---

**Dependency: T33 vóór T16. Dezelfde Apache moet eerst worden gerepareerd.**

**Task 16 — Firewalld Port Forwarding and Masquerade** *(echo)*

**Beginvoorwaarde:** T15, T33. Voer uitsluitend de stappen voor de genoemde VM uit.

1. Ensure `httpd` is installed, enabled, and serving on port `80`
2. In the default zone, permanently forward incoming TCP port `8888` to local port `80`
3. Enable masquerading permanently in that zone
4. Permanently allow the `http` service
5. Reload and verify with `firewall-cmd --list-all`
6. Confirm from `foxtrot` that `curl http://echo.ex200.net:8888` reaches the web server

---

**Task 17 — Repository Setup and Package Queries** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

1. Mount the Rocky 10 DVD persistently at `/mnt/dvd` (must not block boot if the disc is absent)
2. Create a single repo file `/etc/yum.repos.d/lab3.repo` defining `BaseOS` and `AppStream` from that mount, with `gpgcheck=1` using the key on the media
3. Verify with `dnf repolist`
4. Determine which **package** provides the file `/usr/bin/semanage` `[/root/q1.txt]`
5. Determine which **package** owns the already-installed file `/etc/chrony.conf` `[/root/q2.txt]`
6. List every file the `chrony` package installs `[/root/q3.txt]`
7. Search for packages whose summary mentions "network manager" `[/root/q4.txt]`

---

**Task 18 — Transaction History and Rollback** *(echo)*

**Beginvoorwaarde:** T17. Voer uitsluitend de stappen voor de genoemde VM uit.

1. Install the `tmux` package
2. Display the transaction history and identify the ID of that installation `[/root/history_id.txt]`
3. Show the detailed contents of that transaction
4. **Undo** that transaction using `dnf`'s history mechanism — do not use `dnf remove`
5. Confirm `tmux` is no longer installed
6. Redo the transaction to reinstall it, again using the history mechanism

---

**Task 19 — RPM-Level Operations** *(echo)*

**Beginvoorwaarde:** T17. Voer uitsluitend de stappen voor de genoemde VM uit.

1. Download — do not install — the `zsh` RPM into `/root/rpms/`
2. Without installing it, list the files the package **would** install `[/root/rpm1.txt]`
3. Without installing it, display the package's scriptlets `[/root/rpm2.txt]`
4. Extract **only** the `zsh` man page from the RPM into `/root/extracted/` without installing the package
5. Verify the package signature
6. Install the downloaded RPM with dnf to resolve dependencies, then verify the installed package reports no modifications

---

**Task 20 — GPT Partitioning and Type Codes With `fdisk`** *(echo, `/dev/nvme0n2`)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

Exam 1 drove `fdisk` interactively and Exam 2 used `parted -s`. This time, use `fdisk` but focus on **partition type codes** and on capturing the layout in a machine-readable form.

1. Create a fresh GPT table on `/dev/nvme0n2`
2. Create `nvme0n2p1` = 3 GiB, type **Linux filesystem**
3. Create `nvme0n2p2` = 2 GiB, type **Linux LVM** — you must change the type, not accept the default
4. Inform the kernel, then verify with `lsblk` and `fdisk -l`
5. Dump the partition table — including each partition's **type GUID and PARTUUID** — to `/root/gpt_layout.txt`
6. Save a restorable backup of the partition table to `/root/nvme0n2-parttable.bak`, and record in `/root/gpt_layout.txt` the command that would restore it

---

**Task 21 — Shrink a Logical Volume** *(echo, `/dev/nvme0n2p2` + `/dev/nvme0n3`)*

**Beginvoorwaarde:** T20. Voer uitsluitend de stappen voor de genoemde VM uit.

1. Create PVs on `/dev/nvme0n2p2` and `/dev/nvme0n3`, and VG `vg_ex3` with an 8 MiB PE size
2. Create LV `lv_shrink` of **4 GiB**, formatted **ext4**, mounted persistently at `/mnt/shrink`
3. Write a test file into it and record a checksum of that file
4. Shrink `lv_shrink` — filesystem **and** logical volume — to **2 GiB**
5. Remount it and prove the test file is intact by comparing the checksum
6. Record in `/root/shrink_notes.txt` why this task could not have been done had the filesystem been XFS

---

**Task 22 — Replace Swap Cleanly** *(foxtrot, `/dev/nvme0n2`)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

1. Record the current swap configuration `[/root/swap_before.txt]`
2. Create a 1 GiB partition `/dev/nvme0n2p1` and format it as swap with the label `EX3SWAP`
3. Add it to `/etc/fstab` **by LABEL** with priority `5`
4. Activate it and verify both the label and the priority are in effect
5. Deactivate and permanently remove activation of the **original** swap device (leave its inactive LV allocated) — it must not return after reboot
6. Reboot and confirm `EX3SWAP` is the only active disk-backed swap; any installer-provided zram swap may remain active `[/root/swap_after.txt]`

---

**Task 23 — Mount Options and Live Remount** *(foxtrot)*

**Beginvoorwaarde:** T22. Voer uitsluitend de stappen voor de genoemde VM uit.

1. Create a 2 GiB partition `/dev/nvme0n2p2`, format XFS, mount persistently at `/data/vault` with options `noexec,nosuid,nodev`
2. Copy any executable binary into `/data/vault` and demonstrate it will not execute; record the error `[/root/noexec_proof.txt]`
3. Remount `/data/vault` **read-only without unmounting it** and prove writes fail
4. Remount it read-write again, still without unmounting
5. Use `findmnt` to display the active options and save them `[/root/mount_opts.txt]`

---

**Task 24 — Bind Mount in fstab** *(foxtrot)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

1. Create `/srv/appdata` containing a file `payload.txt`
2. Create `/opt/app/data`
3. Configure a **bind mount** in `/etc/fstab` so `/srv/appdata` also appears at `/opt/app/data`
4. Activate it without rebooting and confirm `payload.txt` is visible at both paths
5. Reboot and confirm the bind mount returns automatically

---

**Task 25 — NFS Server With a Diagnostic Step** *(foxtrot)*

**Beginvoorwaarde:** T15. Voer uitsluitend de stappen voor de genoemde VM uit.

1. Install `nfs-utils`, create `/export/team` owned appropriately for group write access
2. Export it read/write to `172.16.40.0/24`
3. Start and enable `nfs-server`, and open the firewall for `nfs`, `mountd`, and `rpc-bind`
4. Deliberately introduce a typo in `/etc/exports` (e.g. a space between the client and its options), re-export, and record what changes about the resulting export `[/root/exports_typo.txt]`
5. Fix the typo, re-export, and verify the correct options with `exportfs -v`
6. Confirm from `echo` that the share can be listed remotely

---

**Task 26 — AutoFS With an Indirect Map** *(echo)*

**Beginvoorwaarde:** T11, T15, T25. Voer uitsluitend de stappen voor de genoemde VM uit.

1. On `foxtrot`, export `/export/team` (from Task 25) to the lab subnet
2. On `echo`, install `autofs` and configure an **indirect** map so `foxtrot:/export/team` mounts on demand at `/net/team`
3. Set the idle unmount timeout to `45` seconds
4. Enable and start `autofs`
5. Trigger the mount by accessing the path, and confirm it appears in `findmnt`
6. Confirm it unmounts itself after the idle period

---

**Task 27 — Journal Filtering by Time and Field** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

Save each result to the indicated file:

1. All journal entries from the current boot for `sshd` only `[/root/j1.txt]`
2. All entries between `09:00` and `12:00` today `[/root/j2.txt]`
3. All entries since yesterday at priority `err` or worse `[/root/j3.txt]`
4. All entries generated by the `sudo` command, matched by the command field rather than the unit `[/root/j4.txt]`
5. The current on-disk size of the journal `[/root/j5.txt]`
6. Rotate/vacuum archived journals to 200M and configure persistent SystemMaxUse=200M. This is retention policy, not a byte-exact filesystem quota. in the journald configuration

---

**Task 28 — Persistent Kernel Parameters** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

Using a drop-in file — do **not** edit `/etc/sysctl.conf`:

1. Set `net.ipv4.ip_forward = 1`
2. Set `vm.swappiness = 20`
3. Set `kernel.pid_max = 65536`
4. Apply them without rebooting
5. Verify each is live, and record the values in `/root/sysctl_verify.txt`
6. Reboot and confirm all three survived

---

**Task 29 — `at`, Access Control, and `/etc/cron.d`** *(echo)*

**Beginvoorwaarde:** T11. Voer uitsluitend de stappen voor de genoemde VM uit.

1. Ensure `atd` is running. Schedule a job for 10 minutes from now that appends `at job ran` to `/var/log/at3.log`
2. List the queue, then display the **contents** of that queued job `[/root/at_job.txt]`
3. Delete the job and confirm the queue is empty
4. Configure `at` so that **only** user `emma` may submit jobs — no other non-root user
5. Create a job in `/etc/cron.d/labreport` (not a user crontab) that runs `/usr/local/bin/labreport.sh` **as user `emma`** every Monday and Thursday at 05:45
6. Explain in `/root/crond_note.txt` how a `/etc/cron.d` entry differs in format from a user crontab entry

---
Create labreport.sh: write date and df -h to ~/labreport.log; make it executable and test it as emma.

---

**Task 30 — Time Synchronization** *(both)*

**Beginvoorwaarde:** T15. Voer uitsluitend de stappen voor de genoemde VM uit.

1. On `foxtrot`, configure `chrony` to serve time to `172.16.40.0/24` and open the firewall for NTP
2. On `echo`, configure `chrony` to use **only** `foxtrot` as its time source
3. Verify from `echo` that `foxtrot` is the selected source
4. Set the hardware clock policy so the system uses UTC, and set `echo`'s timezone to `America/Denver`
5. Record `timedatectl` output on `echo` `[/root/time_status.txt]`

---

**Task 31 — Script With Strict Mode and Exit Codes** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

Write `/usr/local/bin/diskwatch.sh`:

- Enable strict error handling (`set -euo pipefail`)
- Accepts exactly one argument: a mount point
- If no argument is given → usage message to **stderr**, exit `2`
- If the argument is not a currently mounted path → `"Not mounted: <arg>"` to **stderr**, exit `3`
- If usage of that filesystem is at or above 80% → print `CRITICAL: <arg> at NN%`, exit `1`
- Otherwise print `OK: <arg> at NN%`, exit `0`
- Test all four paths and record each exit code in `/root/diskwatch_tests.txt`

---

**Task 32 — Text Processing Report Script** *(echo)*

**Beginvoorwaarde:** een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit.

Write `/usr/local/bin/userreport.sh` that produces a report at `/var/log/userreport.txt` containing:

- Total number of accounts with a **valid login shell** (not `nologin` or `false`)
- The five highest UIDs on the system with their usernames
- Every group that currently has **no** members listed in `/etc/group`
- A count of accounts whose passwords are locked
- All values must be derived by processing command/file output — no hard-coded numbers
- Run it and confirm the report is populated
- A valid shell is executable, listed in /etc/shells, and is not nologin or false. Empty group field 4 excludes primary members.

---

**Task 33 — Diagnose SELinux Violations From Scratch** *(echo)*

**Beginvoorwaarde:** T15. Voer uitsluitend de stappen voor de genoemde VM uit.

`httpd` is installed and configured to serve `/srv/intranet` on port `8404`, but it does not work. You are **not** told what is wrong.

1. Attempt to start `httpd` and capture the failure `[/root/selinux_diag.txt]`
2. Use the audit tools to identify **every** SELinux denial involved — there is more than one distinct problem
3. Use the tool that explains *why* a denial occurred, and record its explanation in the same file
4. Fix each problem using the correct persistent mechanism for that problem type
5. Start `httpd`, confirm `curl http://localhost:8404/` returns `Echo Intranet OK`
6. Confirm no new denials are generated, and that everything survives a reboot

---

**Task 34 — Build and Install a Local Policy Module** *(echo)*

**Beginvoorwaarde:** T33. Voer uitsluitend de stappen voor de genoemde VM uit.

> Stretch task — beyond typical EX200 depth, but directly in service of "diagnose and address routine SELinux policy violations."

1. Ensure SELinux is `enforcing`
2. Generate a denial: have `httpd` attempt something the policy forbids (for example, reading a file labeled `admin_home_t` placed in its document root)
3. Confirm the denial appears in the audit log
4. Generate a **named local policy module** from that denial called `labhttpd`
5. Install the module and confirm it appears in the module list
6. Verify the action now succeeds
7. Record in `/root/policy_module.txt` why `restorecon` or a boolean would usually be the better fix

---

**Task 35 — Registry Tooling and a Self-Updating Rootless Container** *(echo, as user `emma`)*

**Beginvoorwaarde:** T11, T15. Voer uitsluitend de stappen voor de genoemde VM uit.

1. As `root`, ensure `podman` and `skopeo` are installed and enable **lingering** for `emma`
2. As `emma`, use **`skopeo`** — not `podman` — to inspect `docker://registry.access.redhat.com/ubi10/ubi:latest` and record the image digest and available labels `[/home/emma/skopeo_inspect.txt]`
3. Use `skopeo` to list the available tags for that repository `[/home/emma/skopeo_tags.txt]`
4. Authenticate to `registry.redhat.io` with `podman login` and record where the credentials file is stored `[/home/emma/auth_path.txt]` *(if offline, document the exact command and expected path instead)*
5. Create a podman volume `emma-site` and place an `index.html` in it containing `Echo Container OK`
6. Create a **Quadlet** at `~/.config/containers/systemd/emma-site.container` that:
   - runs `registry.access.redhat.com/ubi10/httpd-24`
   - publishes host port `9191` to the container's HTTP port
   - mounts the `emma-site` volume at the web root with the correct SELinux relabel flag
   - sets the environment variable `LAB_ENV=exam3`
   - enables **automatic image updates** from the registry
7. Start the service, verify with `curl http://localhost:9191/`
8. Enable the rootless timer that performs automatic updates
9. Reboot and confirm the container starts with no login from `emma`
