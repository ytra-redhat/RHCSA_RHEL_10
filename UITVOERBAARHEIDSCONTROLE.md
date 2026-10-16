# Uitvoerbaarheidscontrole — 10 oktober 2026

Alle 105 opdrachtsecties en 105 antwoordsecties zijn opnieuw gelezen voor taakvolgorde, VM-scope, beginvoorwaarden, ontbrekende programma's, interactieve invoer en samenhang tussen opdrachten. Dit pakket vervangt de vorige antwoorden. Het verandert je bestaande VM's niet en vereist geen herinstallatie.

## Herstelde fouten

- Examen 3 T12: niet-bestaande `vi-f`/`vi-cf` en afgebroken sudo-commando hersteld naar visudo/sudo, met volledige syntaxcontrole en mode 440.
- Examen 3 T13: ontbrekend runuser-commando hersteld.
- Examen 3 T27: leeg `_COMM=`-filter hersteld naar `_COMM=sudo`.
- Alle netwerksecties: afzonderlijke blokken voor elke VM met concrete adressen; geen handmatige UUID-invoer. Unieke profielselectie met expliciete STOP bij afwijkende beginstand. Profielnaam, interfacenaam en NAT/labrol uitgelegd.
- Alle taken: beginvoorwaarden naast de opdracht én naast het antwoord. Examen 3 T33 moet vóór T16; NFS-clientopdrachten vereisen de serverstappen op de andere VM.
- Examen 1 T2: reeds correct target expliciet behandeld; opnieuw oefenen heeft een concrete, beperkte beginstap. Root recovery onderscheidt een onbekend wachtwoord van een account zonder wachtwoord.
- Examen 1 T15: Flatpak wordt eerst geïnstalleerd. Examen 2 T3 gebruikt de beschikbare vi-editor.
- Examen 1 T25 en examen 3 T30: server/client en verschillende tijdzones in afzonderlijke VM-blokken.
- Alle commando's ná reboot in aparte blokken; onjuist `reboot -h now` vervangen.
- Examen 1 T33: directory 755 en index 644 expliciet gezet. T10's umask 0007 zou anders Apache-toegang verhinderen.
- Examen 3 T16: expliciete virtual host op poort 80; forward 8888 test een vastgestelde pagina, onafhankelijk van T33's poort 8404.
- Examen 3 T20/T22/T23: fdisk-invoer apart van Bash; volledige type-GUIDs, behoud van de bestaande swappartitie bij T23.
- Examen 3 T22: oorspronkelijke swaplijst getoond vóór invoer; onderscheid tussen schijfswap en zram in opdracht hersteld.
- Examen 2 T27: wacht op voltooid schrijven naar tmpfs vóór meten/verwijderen.
- Examen 2 T30: ongeldige actie geeft de gevraagde usage-uitvoer.
- Examen 2 T34: ontbrekende SELinux-booleans worden gecontroleerd vóór wijziging.
- Examen 3 T35: ontbrekende skopeo-installatie toegevoegd.
- RPM-signatuurcontrole: NOKEY niet gelijkgesteld aan een bewezen geldige handtekening; zsh-extractie vereist precies één RPM.
- DVD-opdrachten noemen de werkelijk gebruikte Rocky-DVD; pwquality-bestand in opdracht en antwoord gelijkgetrokken. pvmove-falen niet als gegarandeerd voorgesteld.

## Wat is bewezen, en wat niet?

Lokale regressietests controleren controllergedrag met fixtures, installerbewaking, scripts, antwoorddekking, shellsyntax en nieuwe netwerkselectie. Fake nmcli-tests bewijzen de selectie en stoplogica; ze bewijzen geen netwerkactivatie in een echte VM.

Geen van de 105 taken is in deze review volledig op de zes levende VM's uitgevoerd. Er is daarom **geen garantie dat alle opdrachten probleemloos lopen op jouw huidige, deels gewijzigde VM's**. Je kunt de bestaande VM's behouden. Controleer de beginvoorwaarde voordat je een taak herhaalt en gebruik de acceptatie-uitvoer bij die taak. Formatteringsopdrachten zijn voor de aangegeven ongebruikte extra schijven.

De volgende punten vereisen nog concrete guest-controle: DNF-groepen en optionele GUI; Flatpak ARM-apps/internet; containerimage ARM-manifest, pad, poort en rebootgedrag; stripe-migratie met jouw LVM-versie; SELinux-policybooleans en labelgedrag; Fusion host-only DHCP; offline chrony; daadwerkelijke timeruitvoering. Een ontbrekende externe voorwaarde telt als **niet uitgevoerd**, niet als PASS. De oudere VALIDATIE/GAST-ACCEPTATIE-bestanden bevatten aanvullende controleprocedures en hun historische bewijs.

De uitgebreide antwoorden bevatten nog Engelstalige uitleg. Het korte Nederlandse uitvoerblad legt de kopieerregels uit; het is niet nodig het hele handboek opnieuw te lezen. Een requirement van nul ambiguïteiten kan pas worden vrijgegeven na de nog ontbrekende end-to-end guest-controle; dat wordt hier niet als voltooid voorgesteld.

## Dekking per taak

Elke onderstaande rij betekent: opdracht/antwoord herlezen, beginvoorwaarden aangegeven, statische review uitgevoerd; volledige guest-uitvoering **niet uitgevoerd**. De taakverwijzingen gelden ook wanneer de voorafgaande taak op de andere VM moet worden gedaan.

| Examen | Taak | Onderwerp | Beginvoorwaarde |
|---|---|---|---|
| 1 | 1 | Root recovery | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 2 | Boot target | T1. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 3 | GRUB (alpha) | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 4 | Network (both nodes) | T3. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 5 | Firewall (alpha) | T4. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 6 | Users (alpha) | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 7 | Password aging | T6. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 8 | Sudo (alpha) | T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 9 | Set-GID collaborative directory | T6. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 10 | Umask (both) | T6. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 11 | SSH (alpha → bravo) | T1, T4, T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 12 | Transfers (alpha root) | T11. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 13 | Repositories | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 14 | Package management | T13. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 15 | Package groups, Flatpak, versioned RPMs | T13. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 16 | GPT partitions | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 17 | Filesystems by UUID and LABEL | T16. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 18 | Swap with priority | T16. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 19 | LVM | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 20 | Extend an LV | T19. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 21 | NFS server (bravo) | T4. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 22 | NFS client | T21, T4. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 23 | Autofs homes | T21, T4. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 24 | Permission diagnostics | T6. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 25 | Chrony | T4. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 26 | Tuned | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 27 | Oplossing | T14. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 28 | Persistent journal and rsyslog | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 29 | at, cron, systemd timer | T6. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 30 | syscheck script | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 31 | Bulk users | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 32 | Reliable backup | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 33 | SELinux and webroot | T10, T14. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 34 | Oplossing | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 1 | 35 | Rootless HTTPD (alpha / alice) | T4, T5, T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 1 | Root recovery | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 2 | Target (delta) | seed voltooid op delta; gebruik het rootwachtwoord van de golden-installatie. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 3 | Bootloader | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 4 | Network (both nodes) | T3. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 5 | Custom firewall (charlie) | T4. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 6 | Users (charlie) | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 7 | Password policy (charlie) | T6. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 8 | Sudo (charlie) | T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 9 | ACLs (charlie) | T6. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 10 | Umask and links | T6. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 11 | SSH keys and Match | T4, T6, T7. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 12 | Transfer (charlie root) | T11. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 13 | DVD repositories (charlie) | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 14 | Flatpak (charlie) | T13. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 15 | RPM config restoration (charlie) | T13. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 16 | parted scripted | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 17 | XFS and VFAT (charlie) | T16. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 18 | Swap file (delta) | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 19 | Striped and linear LVM (charlie) | T16. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 20 | Migrate PV (charlie) | T19. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 21 | NFSv4 server (delta) | T4. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 22 | NFS client (charlie) | T21, T4. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 23 | Autofs home | T11, T21, T22. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 24 | Permissions (charlie) | T6. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 25 | Chrony server/client | T4. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 26 | TuneD (charlie) | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 27 | Process management | T13. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 28 | Journal and logrotate (charlie) | T7, T8. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 29 | Scheduling (charlie) | T6. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 30 | svcctl script | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 31 | CSV users | T6. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 32 | Health report | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 33 | Custom webroot (charlie) | T13. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 34 | Oplossing | T5, T11, T33. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 2 | 35 | Rootless Nginx (charlie/emma) | T4, T5, T6, T23. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 1 | Boot recovery | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 2 | One-shot boot to rescue.target | T1. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 3 | grubby | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 4 | Failed service | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 5 | Drop-in override | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 6 | Redirection | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 7 | grep and regex | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 8 | find | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 9 | Archives | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 10 | System documentation | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 11 | Skeleton and home relocation | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 12 | Defaults | T11. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 13 | ACL mask | T11. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 14 | cp vs mv contexts | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 15 | Network profiles and peer | T1. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 16 | Oplossing | T15, T33. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 17 | DVD repos and queries (echo) | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 18 | Oplossing | T17. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 19 | RPM operations | T17. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 20 | fdisk, type codes, and a table backup | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 21 | Shrink an ext4 LV | T20. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 22 | Replace swap (foxtrot) | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 23 | Mount options and remount | T22. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 24 | Bind mount | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 25 | NFS team (foxtrot) | T15. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 26 | Autofs (echo) | T11, T15, T25. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 27 | journalctl filtering | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 28 | Persistent sysctl | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 29 | at, at.allow, cron.d | T11. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 30 | Chrony | T15. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 31 | diskwatch.sh | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 32 | userreport.sh | een correct voorbereide examen-VM (seed voltooid). Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 33 | Apache diagnosis (echo; before T16) | T15. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 34 | Local policy module (echo; optional depth) | T33. Voer uitsluitend de stappen voor de genoemde VM uit. |
| 3 | 35 | Rootless container (echo/emma) | T11, T15. Voer uitsluitend de stappen voor de genoemde VM uit. |
