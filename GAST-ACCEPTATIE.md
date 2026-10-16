# Gastacceptatie — nog uit te voeren op echte Rocky/RHEL 10 ARM64

De lokale tests zijn geen bewijs dat alle 105 taken op gasten zijn uitgevoerd. Deze checklist sluit die laatste testlaag. Werk alleen met de nieuwe v2-gasten; oude VM's hoeven hiervoor niet te worden veranderd.

## Voor examen 1

1. Beide clones hebben verschillende machine-ID's en SSH-hostkey-fingerprints; MACs matchen de eigen manifesten. Golden was sealed vóór cloning.
2. Seed voltooit zonder fout; guestinfo-ID, /etc/rhcsa-fusion-seeded en host seeded=True horen bij dezelfde node.
3. Na seed: bravo default graphical.target; alpha /etc/default/grub timeout 3, style menu, geen quiet in de configured arguments. Maak snapshot vóór examenwerk.
4. /var/tmp/badperms bestaat op alpha met 777; geen examenaccounts vooraf. Extra disks zijn leeg en hebben plan-capaciteiten; root staat uitsluitend op nvme0n1.
5. Na T1: normale boot zonder init=/bin/bash/enforcing=0, root-login werkt. Na T2: multi-user.target. Na T3: timeout/countdown 10 en quiet na reboot.
6. Werk elke taak af met de functionele bewijsstappen in Examen-1-antwoorden.md. Bewaar eigen notities van de 35 taken; de checker alleen is onvoldoende.
7. Beide kanten van NFS/SSH/HTTP/IPv6 testen; echte gebruikers testen ACL, sudo, umask en autofs-homes.
8. Reboot beide zonder tijdelijke kernelargs. Voer read-only checker op beide uit. Documenteer ERROR/FAIL en alle handmatige subcriteria; geen 'geslaagd' op basis van alleen syntax.
9. Rootless Quadlet na reboot zonder gebruikerslogin; peer curl 8080 exact juiste body. Image/ARM-manifest, container-port, webroot, SELinux en UID moeten werkelijk worden gecontroleerd.
10. Reset-test alleen nadat je eigen werk veilig is: uitgeschakeld naar exam-ready-v2, daarna controleren dat de beginfouten terug zijn. Bron-golden en oude gasten blijven ongewijzigd.

## Examen 2 aanvullend

- Delta start rescue.target; rootwachtwoord bekend op delta, onbekend op charlie.
- T3: NIC-renaming beïnvloedt MAC-gebonden profielen niet; opnieuw console/IP controleren.
- T11 vóór SSH-passwordbeperking: beide key-logins testen. Daarna emma password-only afwijzen.
- T17: XFS entry per UUID; VFAT per LABEL; exacte mountopties na reboot. T18 swapfile 1 GiB en priority 20 op hetzelfde filedevice.
- T20: pvmove op echte LVM-versie, data/checksums behouden, segmenttype opnemen; geen lineair-conversieclaim.
- T21/T22: NFSv4-only versies plus echte client-write op projects en write-failure archive. Geen doorslaggevende showmount-test.
- T23: emma echte NFS-home-login/write en behouden SSH-keys; autofs expiry niet verstoren door herhaalde toegang.
- Nginx 1.26: html/index.html onder /opt/app-root/src, expliciete nginx foreground command, named-volume Quadlet dependency, werkende peer curl 9090.

## Examen 3 aanvullend

- Foxtrot recovery verwijdert alleen de bogus UUID; geen echte fstab-entry. Echo labdata en webservice echt defect vóór reparatie.
- Volg volgorde T33 vóór T16. Toon beide afzonderlijke SELinux-problemen en juiste fixes; beperk audit-verificatie tot een nieuwe requestperiode.
- UID-regex niet verwarren met GID; IPv4-octetten ≤255; find bewaart bronpaden; compressiewinnaar werkelijk uit gemeten groottes.
- Nieuwe homes hebben juiste labels en wachtwoord/login; /srv/homes/noah parent bestaat.
- Swapvervanging kiest het echte oude device; oude LV blijft inactief toegewezen. Geen blind rhel-swap-pad of lvremove.
- Bindmount compare stat device:inode van hetzelfde payload; controleer na reboot. AutoFS-pad /net/team, geen dubbel team.
- diskwatch alle 4 uitkomsten met wegwerp-tmpfs, systeemdisk niet vullen. Scriptfoutcodes/logs bewaren.
- Lokale SELinux-module: uitsluitend synthetische testcase en gefilterde AVCs; .te inspecteren. Dit is verdieping, niet een core EX200-vereiste.
- Publieke container ≠ private registry-login. Persistent authfile alleen met eigen account; auto-update timer en user journal controleren.

## Acceptatieresultaat

Maak per examen een notitie met OS/kernel/Fusion-versie, ISO-checksum, image-digests, uitgevoerde taken, reboot/peerresultaten en resterende fouten. Totdat deze laag is uitgevoerd geldt de ZIP als lokaal gecontroleerde releasecandidate, niet als live bewezen exameninstallatie.
