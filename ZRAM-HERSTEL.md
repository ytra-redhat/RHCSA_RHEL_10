# Herstel van de afgebroken Rocky-installatie — zram-fout

Op jouw screenshot staan loop0, sr0, zram0 en nvme0n1. Er is één echte 30 GiB NVMe-installatiedisk. De Rocky-installer gebruikt daarnaast zram0 als tijdelijke RAM-disk en rapporteert die óók als TYPE=disk. Mijn vorige controle telde beide en stopte ten onrechte bij de pre-installatiecontrole, vóór partitioneren.

De aangepaste controle negeert uitsluitend zram-namen zoals zram0. Alle andere disks blijven meetellen. Ze verlangt dat de enige installatiedisk nvme0n1 is, 30 GiB groot, zonder signatures of partities, in de VM met de verwachte MACs. De controle is niet uitgeschakeld.

## 1. Huidige installer normaal uitschakelen — LINUX installer-shell

In de shell op je screenshot:

```bash
systemctl poweroff
```

Wacht totdat de golden uit staat. Sluit vervolgens Fusion om toegang/locks voor de mediawijziging vrij te geven. Verwijder geen .lck-bestanden. Dit is de gewone installer-shell, niet de PID-1-herstelshell uit een examen.

## 2. Nieuwe code plaatsen — MAC / Finder

Download de ZIP met zramfix. Pak de codeboom uit naar dezelfde codemap:

`~/Studies/RHCSA/labs/RHCSA-Fusion-v2`

Bewaar de vorige codemap onder een andere naam als je eigen wijzigingen wilt behouden. Deze codevervanging staat los van je VM-map. Verplaats of verwijder `~/RHCSA-Fusion-auto` niet; de herstelactie gebruikt juist de bestaande golden en metadata daarin.

## 3. Media herstellen voor dezelfde golden — MAC

```bash
cd "$HOME/Studies/RHCSA/labs/RHCSA-Fusion-v2"
VMROOT="$HOME/RHCSA-Fusion-auto"
python3 RHCSA-Lab-Scripts/install-rocky.py repair-media --root "$VMROOT"
```

Gebruik jouw werkelijk gekozen VMROOT als die afwijkt. Je hoeft geen ISO-pad of wachtwoorden opnieuw in te voeren: die worden uit de eerder gecontroleerde media/metadata hergebruikt. Het script:

- verlangt een uitgeschakelde, herkenbare automatische golden die nog niet via de boot-actie naar de geïnstalleerde root is gestart;
- controleert de checksums van de oorspronkelijke DVD en de vorige automatische ISO;
- hergebruikt de twee bestaande wachtwoordhashes en dezelfde VM-identiteit;
- bouwt een aparte nieuwe ISO met de zramfix;
- bewaart de vorige ISO en een backup van de VMX;
- past uitsluitend de CD/DVD-verwijzing en bootvolgorde aan; de VMDK wordt niet gewijzigd;
- start de gast nog niet automatisch.

De nieuwe media vragen opnieuw ongeveer één DVD-grootte vrije ruimte. De vorige ISO blijft behouden. Bij een checksum- of lockfout stopt de actie; wis geen disks om die fout te omzeilen. De reparatie is bedoeld voor jouw getoonde pre-installatiefout, niet voor een al geïnstalleerde of gebruikte golden.

## 4. Dezelfde installatie opnieuw starten — MAC

```bash
python3 RHCSA-Lab-Scripts/install-rocky.py start --root "$VMROOT"
```

Fusion opent de bestaande golden met de nieuwe media. Wacht op het automatische installatiemenu en de installatie. Zram0 mag blijven bestaan; je hoeft die RAM-disk niet te verwijderen of uit te schakelen. De controle op lege nvme0n1 blijft actief.

Wacht tot Rocky zichzelf na installatie uitschakelt. Bij een andere pre-fout bekijk je opnieuw `/tmp/rhcsa-auto-pre.log`; bij post-fouten de installerconsole en `/root/rhcsa-auto-post.log` op de geïnstalleerde root. Ga niet door naar boot/seal als de installatie is mislukt.

## 5. Van de geïnstalleerde disk starten — MAC

```bash
python3 RHCSA-Lab-Scripts/install-rocky.py boot --root "$VMROOT"
```

Dit verwijdert de automatische ISO uit de bootroute. Log in de nieuwe golden-console in als root met het eerder gekozen wachtwoord.

## 6. Controleren en seal — LINUX ROOT, golden-console

```bash
cat /etc/os-release
cat /etc/rhcsa-auto-installed
getenforce
systemctl is-active vmtoolsd
ip -br addr
bash /root/rhcsa-finish-golden.sh
```

De eindcontrole gebruikt eveneens de gecorrigeerde diskcontrole. Bij succes voert zij seal uit en schakelt golden uit. Start golden daarna niet opnieuw vóór cloning.

## 7. Verder met de examens

Volg AUTOMATISCHE-INSTALLATIE.md vanaf stap 6. Gebruik dezelfde VMROOT bij alle Mac-controlleracties en de originele Rocky-DVD bij create, niet de aangepaste automatische ISO.

Er is voor deze fout geen nieuwe VM nodig en je eerdere wachtwoorden blijven gelden. Tijdens het maken van deze herstelrelease zijn je echte VM’s niet gewijzigd. De tests reproduceren je getoonde lsblk-layout en testen ook dat een tweede echte disk nog steeds wordt geweigerd. Volledige gastinstallatie blijft een aparte praktijkcontrole.
