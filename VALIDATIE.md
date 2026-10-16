# Validatie — 9 oktober 2026

Deze release is lokaal gecontroleerd. Volledige uitvoering van de drie examens op echte Rocky-gasten is nog niet uitgevoerd. Gebruik GAST-ACCEPTATIE.md voor die controle; deze ZIP is geen verklaring dat alle gastopdrachten al in jouw VM’s geslaagd zijn.

| Controle | Resultaat |
|---|---|
| Lokale regressies | 69 tests geslaagd |
| Shellsyntax | 9 shellbestanden gecontroleerd |
| Commando’s in documentatie | 252 Bash/sh-blokken syntactisch gecontroleerd, inclusief 12 ingebedde scripts |
| Opdrachten en antwoorden | 3 × 35 unieke opdrachtsecties en 3 × 35 antwoordsecties; 19 ontbrekende antwoorden aangevuld |
| Auditbevindingen | Alle 69 bevindingen gekoppeld aan een behandeling in audit/CORRECTIES.md; niet elke bevinding was een bewezen bug |
| Controledekking | Alle 105 taaknummers opgenomen; handmatige criteria expliciet vermeld in CONTROLE-DEKKING.md |
| Uitgebreide MacBook-handleiding | 65 Bash-blokken gecontroleerd; 27 Mac-blokken ook met zsh-syntaxcontrole; beide invoervraagroutes werkelijk in zsh uitgevoerd |
| Automatische installer | 25 installer-regressies, waaronder daadwerkelijk uitgevoerde pre-guards met fixtures; RHEL10 Kickstart-schema geaccepteerd door pykickstart 3.78 |
| Aangepaste installatie-ISO | Werkelijk opgebouwd uit jouw aanwezige Rocky 10.2 aarch64 DVD; ISO/EFI-GRUB, UEFI-entry, Kickstart-inhoud en pakketaanwezigheid gecontroleerd; bronchecksum ongewijzigd |
| Echte Fusion-diskmanager | Aparte nieuwe 1 GiB testdisk gemaakt; ketenconsistentie en capaciteit gecontroleerd |
| Bestaande broncode | SHA-256-controle tegen het auditmanifest; resultaat in validation-evidence/source-integrity.json |
| ZIP | Inhoud en SHA-256 per bestand gecontroleerd; regressies opnieuw uitgevoerd vanuit een uitgepakte kopie |

## Wat de regressies bewijzen

De hosttests gebruiken gecontroleerde vervangingen voor Fusion-acties. Ze testen onder meer alle zes diskindelingen, hervatten na een onderbroken clone, behoud van bestaande bundles, weigering van onbekende bundles en externe diskverwijzingen, capaciteit, metadata, locks, snapshots, legacy-bundles, exclusieve toegang en het afschermen van wachtwoorden in foutmeldingen.

Negatieve grader-tests controleren onder meer verkeerde IP-adressen, poorten, swapprioriteiten, extra toegestane gebruikers, modulevelden, numerieke waarden, bindmount-identiteit en ontbrekende hulpmiddelen. Een ontbrekend hulpmiddel geeft ERROR. Een gedeeltelijk geslaagde taak blijft MANUAL: de grader geeft geen officiële examenscore.

Zes functionele scriptcontroles voeren Bash werkelijk uit in een geïsoleerde testomgeving: diskwatch, syscheck, svcctl, backup bij succes, backup bij falen en het falen van bulk-useradd. Ze testen ook dat mislukte backups bestaande bestanden behouden en geen succes melden.

Zramfix: de door jou gemelde installer-layout loop0/rom/zram0/nvme0n1 wordt nu gereproduceerd en geaccepteerd. Zram plus een tweede hardwaredisk, een onverwachte disknaam en bestaande signatures blijven geweigerd. Mediaherstel is met vervangingen voor de media-/Fusion-tools getest op behoud van disk, hashes en oude ISO, en op weigering bij draaiende gast, aangepaste ISO, eerdere OS-boot en mislukte mediaopbouw.

De installatieguard-tests voeren Bash uit met geïsoleerde fixtures voor lege disk, bestaande signature, verkeerde capaciteit, extra disk en verkeerde MAC. Zij partitioneren geen disk en bewijzen geen volledige Anaconda-installatie. De aparte Kickstart-validator valideert het schema; pre/post-shells zijn daarnaast syntactisch gecontroleerd.

## Wat nog niet is bewezen

Niet uitgevoerd: installatie met jouw ISO, echte golden-import, volledige VM-clones, seed en snapshots via Fusion op jouw gasten, rootherstel en reboot, alle 105 antwoorden op echte gasten, peer-netwerk/NFS, SELinux-herlabeling, LVM-verplaatsing en bestandenystemen, grafische targets, Flatpak en containerdownloads voor aarch64. Image-tags en pakketbeschikbaarheid kunnen veranderen. De relevante primaire bronnen staan in BRONNEN.md.

Shellsyntax bewijst niet dat een commando inhoudelijk werkt op iedere gast. ShellCheck was niet beschikbaar en is niet uitgevoerd. De volledige gastcontrole staat in GAST-ACCEPTATIE.md; voer die uit op de nieuwe v2-clones, vóór je hun snapshots als betrouwbare examenstart gebruikt.

De bestaande VM-bundles zijn niet gewijzigd. De echte diskmanagercontrole gebruikte uitsluitend een nieuwe wegwerp-testdisk, die niet in de ZIP zit.

## Zelf herhalen

Vanuit de uitgepakte codeboom, op de Mac:

```bash
python3 tools/validate.py
```

Dit draait lokale tests; het verandert geen echte VM’s. De opgeslagen uitvoer staat in validation-evidence/local-tests.txt en validation-evidence/extracted-tests.txt.
