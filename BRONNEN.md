# Primaire bronnen bij de correcties

Gecontroleerd 8–9 oktober 2026. Commands en beschikbaarheid in jouw geïnstalleerde versie moeten daarnaast in de guest worden bevestigd.

- EX200-doelen: https://www.redhat.com/en/services/training/ex200-red-hat-certified-system-administrator-rhcsa-exam
- RHEL 10 GRUB/BLS: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/managing_monitoring_and_updating_the_kernel/configuring-kernel-command-line-parameters
- Quadlet generator / Install / volume dependencies: https://docs.podman.io/en/stable/markdown/podman-systemd.unit.5.html
- Nginx 1.26 catalog: https://catalog.redhat.com/en/software/containers/rhel10/nginx-126/677d3718e58b5a1ae5598058
- Nginx mounted-content layout/foreground command: https://raw.githubusercontent.com/sclorg/nginx-container/master/1.26/README.md
- HTTPD mounted content and UID: https://raw.githubusercontent.com/sclorg/httpd-container/master/2.4/root/usr/share/container-scripts/httpd/README.md
- RHEL 10 package manifest: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html-single/package_manifest/index
- machine-ID initialization: https://raw.githubusercontent.com/systemd/systemd/main/man/systemd-machine-id-setup.xml
- RestartUSec exposed property: https://raw.githubusercontent.com/systemd/systemd/main/src/core/dbus-service.c
- journalctl rotation/vacuum: https://www.freedesktop.org/software/systemd/man/latest/journalctl.html
- PAM pwquality/root enforcement: https://raw.githubusercontent.com/libpwquality/libpwquality/master/doc/man/pam_pwquality.8.pod
- Chrony signal implementation: https://raw.githubusercontent.com/mlichvar/chrony/master/util.c and https://raw.githubusercontent.com/mlichvar/chrony/master/main.c
- rsyslog output reopening: https://docs.rsyslog.com/doc/configuration/modules/omfile.html
- DNF repository options: https://dnf.readthedocs.io/en/latest/conf_ref.html
- Firewalld permanent/runtime/reload: https://firewalld.org/documentation/man-pages/firewall-cmd.html
- LVM pvmove allocation: https://man7.org/linux/man-pages/man8/pvmove.8.html
- NFS exports: https://man7.org/linux/man-pages/man5/exports.5.html
- SSH first-value/Match handling: https://man.openbsd.org/sshd_config
- Rocky signing-key distribution: https://dl.rockylinux.org/pub/rocky/

Fusion diskmanager syntax was checked against the actual installed binary (build 25689522). The local disk test used only a new disposable fixture, never a VM disk.

## Aanvullende uitvoerbaarheidscontrole, 10 oktober 2026

- NetworkManager nmcli, selectie op id/uuid en wijzigen van profielen: https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nmcli.html
- NetworkManager profielinstellingen: https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nm-settings-nmcli.html
- Podman Quadlet: generator, userpaden en [Install] in plaats van systemctl enable van een gegenereerde service: https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html
- Nginx imageproject (toepassingspaden moeten bij het gebruikte image gecontroleerd worden): https://github.com/sclorg/nginx-container/blob/master/1.26/README.md

Documentatiecontrole bewijst geen succesvolle uitvoering van een concreet ARM-image op deze VM's. Die controle blijft expliciet onderdeel van T35.
