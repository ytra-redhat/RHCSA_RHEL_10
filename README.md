# RHCSA-oefenexamens op VMware Fusion — Apple Silicon

Deze versie bouwt voort op `jconwell3115/RHCSA_RHEL_10` en past de drie oefenexamens aan voor **macOS, VMware Fusion en ARM64 Rocky/RHEL 10**. Datum: 5 oktober 2026. De oorspronkelijke bestanden staan ongewijzigd onder `upstream-reference/`, uitsluitend als naslag; voer de KVM-code daar niet uit op je Mac.

De opdrachten zijn community-oefeningen. Onderdelen over containers, eigen SELinux-modules en andere verdieping zijn behouden, maar zijn geen bewijs van officiële EX200-dekking of beoordeling.

## Wat je krijgt

- Een Fusion-controller voor een golden VM en zes volledige onafhankelijke clones.
- Drie examenomgevingen met de originele aantallen en groottes van extra disks.
- Golden-bootstrap en VM-specifieke seeds voor de opzettelijk gebroken uitgangstoestanden.
- Een NAT-NIC voor internet en een aparte host-only-NIC voor het oefennetwerk.
- VM-specifieke MACs, machine-ID's en SSH-hostsleutels.
- Eenmalige `exam-ready` snapshots en expliciet terugzetten van uitgeschakelde VM's.
- Aangepaste examendocumenten en gedeeltelijke beoordelaars met foutstatussen.

Er worden geen bestaande VM's verwijderd. `create` weigert bestaande bundles, `reset` zet alleen een bijgehouden eigen exam-VM terug. De controller stopt VM's niet automatisch: schakel ze normaal uit vóór snapshots, terugzetten of disks toevoegen.

## Vereisten

- Apple Silicon Mac (`uname -m` geeft `arm64`), Python 3 en VMware Fusion onder `/Applications/VMware Fusion.app`.
- Een lokale **aarch64 DVD ISO**, bijvoorbeeld `Rocky-10.2-aarch64-dvd1.iso`. Een boot/minimal ISO bevat niet de benodigde BaseOS/AppStream-repositories. Controleer de SHA256 bij de uitgever. De controller controleert alleen pad en bestandsnaam, niet de ISO-inhoud.
- RHEL 10 aarch64 kan ook, met een eigen subscription voor de golden-installatie. Rocky gebruikt eigen repositories; `subscription-manager`-opdrachten in de examens zijn alleen voor RHEL.
- Voldoende vrije diskruimte: systeemdisks zijn 30 GiB en groeien dynamisch. Zes volledige clones plus de golden kunnen bij volledig gebruik ruim 200 GiB innemen.
- 4 GiB RAM en twee vCPU's per VM. Start slechts één examenpaar tegelijk.
- Werkende Fusion Shared with my Mac (NAT) en Private to my Mac (host-only) netwerken.

Alle **hostcommando's** hieronder voer je op de Mac uit, vanuit deze pakketmap. Alle **gastcommando's** voer je in de juiste Rocky/RHEL-VM uit. De controller gebruikt `vmrun` en `vmware-vdiskmanager`; hij wijzigt de globale Fusion-netwerken niet.

## 1. Golden VM maken en installeren

Op de Mac:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py template --iso /absoluut/pad/Rocky-10.2-aarch64-dvd1.iso
python3 RHCSA-Lab-Scripts/fusion-lab.py open-golden
```

Standaardmap: `~/RHCSA-Fusion-jconwell`. Een andere map kan met de globale optie, vóór het subcommando:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py --root /pad/naar/lab template --iso /pad/naar/aarch64-dvd.iso
```

Installeer via Fusion een minimale Rocky/RHEL 10-gast op de **enige 30 GiB disk**. Kies EFI, houd SELinux enforcing en stel een bekend rootwachtwoord in. Activeer bij installatie de NAT-NIC. Er hoeft geen GUI in Linux te zijn: de Fusion-console blijft beschikbaar. Voor RHEL: registreer de golden en configureer package-toegang vóór de bootstrap.

Kopieer `RHCSA-Lab-Scripts/guest-golden.sh` naar de golden (bijvoorbeeld via SSH/scp nadat je tijdelijk een installatieaccount hebt aangemaakt) en voer het **binnen de golden als root** uit. Met `sudo` gebruik je een interactieve terminal:

```bash
sudo bash guest-golden.sh
```

Het script vraagt welke NIC NAT is en welke host-only. Vergelijk de MAC-adressen met `fusion-state.json` in de golden-bundle op je Mac. Het vraagt ook om een wachtwoord voor `student`, een account zonder sudo. Verwijder vóór het klonen eventuele extra installatieaccounts met sudo, zodat de onbekende rootwachtwoorden niet via een ander administratoraccount kunnen worden omzeild.

Controleer:

```bash
cat /etc/rhcsa-fusion-golden
systemctl is-active vmtoolsd
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
nmcli con show
systemctl poweroff
```

Golden mag geen extra disks, gedane examenantwoorden of kapotte services bevatten. Houd de rootlogin beschikbaar voor het seeden via VMware Tools; dit vereist geen root-SSH-login. De `guestOS`-compatibiliteitsidentifier is `arm-rhel9-64`, net als bij de eerdere werkende Fusion-configuratie; de geïnstalleerde distributie blijft versie 10.

## 2. Een examenpaar bouwen

Op de Mac, terwijl golden uitgeschakeld is:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py plan --exam 1
./RHCSA-Lab-Scripts/rebuild-rhcsa-labs.sh --exam 1 --iso /absoluut/pad/Rocky-10.2-aarch64-dvd1.iso
```

Voor examen 2/3 vervang je het examennummer. `rebuild` is nu een veilige create-wrapper: **geen automatische teardown**. Alle clones behouden hun eigen volledige disks. ISO blijft gekoppeld voor de lokale repository-opdrachten; bootvolgorde is hard disk vóór CD.

| Examen | VM | Extra disks | Statisch oefenadres |
|---|---|---|---|
| 1 | alpha | 10 GiB | 192.168.100.10/24 |
| 1 | bravo | 10 + 5 GiB | 192.168.100.20/24 |
| 2 | charlie | 8 + 6 + 4 GiB | 10.20.30.11/24 |
| 2 | delta | 8 GiB | 10.20.30.12/24 |
| 3 | echo | 8 + 6 GiB | 172.16.40.21/24 |
| 3 | foxtrot | 8 GiB | 172.16.40.22/24 |

Deze statische adressen bestaan pas na de netwerkopdracht. NAT heeft vooraf DHCP; host-only wordt bij het seeden eerst zonder IP-profiel klaargezet. Alle paren delen één host-only Ethernet-netwerk. Verschillende subnets betekenen geen netwerkisolatie; start één paar tegelijk.

## 3. Seeds uitvoeren en uitgangssnapshot maken

Voor elke VM van je paar:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node alpha
python3 RHCSA-Lab-Scripts/fusion-lab.py seed --node alpha
```

De controller vraagt het rootwachtwoord van golden, kopieert het unieke seed-script via VMware Tools en voert het uit. Wacht tot de gewone login en VMware Tools beschikbaar zijn. Het wachtwoord wordt niet opgeslagen, maar kan tijdens `vmrun` tijdelijk in de procesargumenten staan.

Seeds controleren beide unieke MACs, ARM64, het disk-aantal, de systeemdisk en lege oefendisks. De voltooiingsmarker wordt via VMware guestinfo gelezen; een gestart gastprogramma alleen geldt niet als bewijs van succesvolle seeding. Bij een fout: inspecteer de Fusion-console; de VM blijft behouden.

- **alpha:** schone basis.
- **bravo:** rootwachtwoord onbekend.
- **charlie:** rootwachtwoord onbekend.
- **delta:** volgende boot naar rescue.target; rootwachtwoord blijft bekend.
- **echo:** mislukte labdata.service en httpd met onjuiste padcontext/poort 8404.
- **foxtrot:** ontbrekende fstab-UUID en onbekend rootwachtwoord.

Na succesvolle seed: schakel de VM normaal uit via Fusion **Shut Down**, of `systemctl poweroff` in een nog geopende rootconsole. Doe dit vóór de volgende boot. Bij de drie wachtwoord-seeds blijft een bestaande console-rootlogin actief; sluit die pas na shutdown. Gebruik geen Suspend of gedwongen Power Off.

Op de Mac:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py snapshot --node alpha
```

Herhaal voor bravo of de twee nodes van een ander examen. Dit maakt `exam-ready`; bestaande snapshots worden niet overschreven. Bij sommige Fusion-versies/API's kan een CLI-operatie ontbreken: stop bij de fout en volg de diagnostiek. Live ondersteuning is nog niet getest.

## 4. Examen uitvoeren

Open het betreffende examendocument in deze map en start beide gasten. Gebruik de Fusion-console voor herstel. `rw init=/bin/bash enforcing=0` start in de geïnstalleerde root: remount **`/`**, niet `/sysroot`. De antwoordsecties bevatten de herstelprocedure. Zorg voor SELinux-herlabeling en herstel enforcing na de boot.

NVMe-benaming is aangepast:

| Oorspronkelijk | Fusion ARM |
|---|---|
| /dev/vda of /dev/sda | /dev/nvme0n1 — systeemdisk |
| /dev/vdb of /dev/sdb | /dev/nvme0n2 — eerste oefendisk |
| /dev/vdc of /dev/sdc | /dev/nvme0n3 — tweede oefendisk |
| /dev/vdd of /dev/sdd | /dev/nvme0n4 — derde oefendisk |
| /dev/vdb1 | /dev/nvme0n2p1 |

Controleer namen in de gast. Bij afwijkende enumeratie: stop en pas de opdrachten bewust aan. Nooit formatteren op basis van alleen de grootte of een oude naam.

Bij de netwerkopdracht: wijzig uitsluitend het host-only-profiel. NAT houdt de default route en DNS. Een `.1`-adres in het oefensubnet is **geen** door dit pakket aangemaakte router of DNS-server. `guest-network.sh` is een optionele oplossing voor de statische profielconfiguratie, geen setupstap vóór het examen. Voeg zelf de peer-hostnames aan `/etc/hosts` toe. Opdracht 15 van examen 3 gebruikt daarnaast DHCP van het echte Fusion host-only-netwerk, dat een ander subnet heeft.

Voor graders geldt: voer in de gast na herstart `sudo bash ex1-verify.sh` uit (of ex2/ex3). Een onbekende host geeft status 2, mislukte controles status 1. Het bestaan van een journalmap is vervangen door het kunnen zien van een eerdere boot. Dat vereist bewust een herstart nadat je persistent logging hebt ingericht. Deze scripts zijn **spotchecks** en geen officiële complete examengrader.

## 5. Terugzetten en opnieuw oefenen

Schakel beide VM's normaal uit. Dan op de Mac:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py reset --node alpha
python3 RHCSA-Lab-Scripts/fusion-lab.py reset --node bravo
```

Dit verwerpt de gastwijzigingen sinds `exam-ready`, inclusief antwoorden en wachtwoordwijzigingen. Golden en andere VM's worden niet teruggezet. Verander de hardware/disks na de ready-snapshot niet. Start de VM's opnieuw om een nieuwe poging te beginnen. Seed niet opnieuw na een reset: de uitgangssnapshot bevat de seeds al.

Een extra disk vóór seeding kan met:

```bash
./RHCSA-Lab-Scripts/add-disk.sh --node alpha --size 4
```

Dit breidt de seedcontrole uit, maar wijzigt de examenvragen niet. Voor de drie standaardexamens zijn de disks al aangemaakt.

## Validatie en bronnen

Zie [VALIDATION.md](VALIDATION.md) en [CHANGELOG.md](CHANGELOG.md). De hier beschikbare Fusion CLI-hulp is gelezen; er zijn **geen echte VM's aangemaakt, geïnstalleerd, geseed of teruggezet** bij het maken van dit pakket. De golden-installatie is bewust een expliciete gebruikersstap. Lokale mocks toetsen orchestratielogica, geen gast- of hypervisorwerking.

- Oorspronkelijk project: https://github.com/jconwell3115/RHCSA_RHEL_10
- Officiële EX200-doelen: https://www.redhat.com/en/services/training/ex200-red-hat-certified-system-administrator-rhcsa-exam
- Fusion ARM-architectuur: https://knowledge.broadcom.com/external/article/315609
- Fusion ARM-gastcompatibiliteit: https://knowledge.broadcom.com/external/article/315602

Er wordt geen nieuwe licentie voor de upstream-teksten geclaimd; oorspronkelijke bronvermelding blijft behouden. Dit is een lokale aangepaste distributie voor jouw studie, geen upstream-publicatie.

Correctie van het RHEL 10 UEFI-GRUB-pad gebaseerd op: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/managing_monitoring_and_updating_the_kernel/reinstalling-grub
