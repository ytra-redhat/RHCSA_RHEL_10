# Volledige werkinstructie — RHCSA Fusion op jouw MacBook

Versie: 9 oktober 2026. Hoort bij de codeboom RHCSA-Fusion-v2.

Deze handleiding gaat uit van jouw eerder getoonde omgeving: een MacBook met Apple Silicon, VMware Fusion, Rocky Linux 10 aarch64, een bestaande rhel10-golden en oudere oefen-VM’s. Het exacte MacBook-model, werkgeheugen en de huidige Fusion-versie zijn niet vastgesteld. Controleer ze hieronder. De naam Rocky-10.2-aarch64-dvd1.iso is jouw eerder opgegeven bestandsnaam, geen claim dat dit de nieuwste release is.

**Aanbevolen route voor jou:** behoud je bestaande VM’s. Maak in een aparte map een volledige kopie van de bestaande golden. Bereid alleen die kopie voor. Maak daarna nieuwe examenclones. Als de oude golden al examenwerk bevat, gebruik de route voor een nieuwe installatie.

Dit document beschrijft de hele inrichting. De afzonderlijke 105 examenantwoorden staan in de drie antwoorddocumenten. Ze zijn niet bedoeld om tijdens de inrichting allemaal uit te voeren: daarmee zou je de oefeningen al oplossen.

## Inhoud

1. Wat je bouwt en hoe het werkt
2. Waar je commando’s uitvoert
3. Eisen, capaciteit en bestanden
4. Oude omgeving behouden
5. Code uitpakken en Mac controleren
6. ISO kiezen en variabelen instellen
7. Netwerk en disks begrijpen
8. Route A: bestaande golden kopiëren
9. Route B: nieuwe Rocky-installatie
10. Nieuwe golden herkennen en bestanden overzetten
11. Golden voorbereiden en sudo opschonen
12. Golden controleren en seal uitvoeren
13. Examen 1 maken, voorbereiden en vastleggen
14. Examen 1 uitvoeren en root herstellen
15. Controleprogramma’s gebruiken
16. Examen 2 volledig opzetten
17. Examen 3 volledig opzetten
18. Dagelijks werken, reset en backups
19. Problemen oplossen
20. Eindcontrole, logboek en bronnen

## 1. Wat je bouwt

Golden is één geïnstalleerde Linux-VM met de benodigde basishulpmiddelen. Hij is geen examenmachine. Van golden worden volledige, zelfstandige kopieën gemaakt. Een seed bereidt iedere kopie voor: netwerkprofielen, defecte instellingen en het juiste uitgangspunt voor de opdrachten. Een snapshot bewaart dat uitgangspunt.

```text
MacBook + VMware Fusion
│
├── Bestaande omgeving — behouden
│   ├── servera / serverb
│   ├── oude rhel10-golden
│   └── oude alpha / bravo
│
└── Nieuwe omgeving: ~/RHCSA-Fusion-v2
    ├── rhel10-golden  ← kopie van oude golden, of nieuwe installatie
    │       │ bootstrap → controle → seal → uitgeschakeld houden
    │       ├── examen 1: alpha + bravo
    │       ├── examen 2: charlie + delta
    │       └── examen 3: echo + foxtrot
    │
    └── Per examenpaar:
        create → start → seed → poweroff → snapshot exam-ready-v2
        → start → opdrachten → antwoorden/controles → reboot/peercontrole
        → eventueel poweroff → reset → opnieuw oefenen
```

| Begrip | Betekenis | Wanneer gebruiken |
|---|---|---|
| template | Lege nieuwe VM met één systeemdisk en twee NICs | Alleen voor een nieuwe OS-installatie |
| import-golden | Volledige kopie van een bestaande golden | Aanbevolen als jouw oude golden schoon is |
| bootstrap | Basispakketten en profielen in de nieuwe golden | Eénmalige voorbereiding; gecontroleerd herhaalbaar |
| seal | Golden klaarmaken voor unieke clone-identiteiten | Laatste stap vóór klonen; schakelt golden uit |
| create | Examenclones en voorgeschreven extra disks maken | Per examenpaar |
| seed | Beginfouten en examenuitgangspunt aanleggen | Alleen op nieuwe, onbewerkte clones |
| snapshot | Examenstart vastleggen | Na geslaagde seed, op uitgeschakelde gast |
| reset | Examenwerk terugdraaien naar die snapshot | Alleen als je opnieuw wilt oefenen |
| verify | Een deel van de oplossingen controleren | Tijdens/na examenwerk in Linux |

`phase=ready` in hostmetadata betekent dat de hardware/controllerfase klaar is. Het bewijst niet dat Linux geïnstalleerd, bootstrap geslaagd, golden sealed of alle opdrachten opgelost zijn.

## 2. Waar je commando’s uitvoert

| Aanduiding | Waar | Voorbeeld |
|---|---|---|
| MAC | Terminal op macOS, in de uitgepakte codemap | python3 RHCSA-Lab-Scripts/fusion-lab.py plan --exam 1 |
| FUSION | VMware Fusion-app | VM openen, scherm bekijken, instellingen controleren |
| LINUX ROOT | Fusion-console van de genoemde Linux-VM, ingelogd als root | systemctl poweroff |
| LINUX GEBRUIKER | Echte login van de gevraagde gebruiker | Een opdracht voor alice of emma |

De Mac-blokken zijn geschreven voor jouw zsh-terminal. Linux-blokken gebruiken Bash. Zo gebruiken de Mac-vragen printf gevolgd door read, omdat Bash-optie read -p niet dezelfde betekenis heeft in zsh.

Een prompt zoals `[root@rhel10-alpha ~]#` is Linux root. Een prompt met jouw Mac-map is macOS. Typ de prompt zelf niet over. Onderstaande blokken bevatten alleen de commando’s.

Voer blokken één voor één uit. Lees eerst de uitleg en controleer de uitkomst voordat je naar het volgende blok gaat. Een foutmelding is een reden om de betreffende stap te onderzoeken, niet om de volgende tien stappen alsnog uit te voeren.

Werk bij netwerkvoorbereiding en herstel via de Fusion-console. Een SSH-verbinding kan verdwijnen zodra een profiel verandert. Rootcommando’s in deze handleiding hebben daarom meestal geen sudo. Op de Mac gebruik je geen sudo voor de controller.

## 3. Eisen en capaciteit

### Hardware en software

- Apple Silicon MacBook: macOS moet `arm64` tonen. Deze codeboom ondersteunt geen Intel-Mac.
- VMware Fusion geïnstalleerd als `/Applications/VMware Fusion.app`.
- Werkende Python 3 op de Mac. Gebruik de bestaande installatie als `python3 --version` werkt.
- Volledige Rocky/RHEL 10 aarch64 DVD-ISO met BaseOS en AppStream. Geen x86_64, boot-ISO of minimal-ISO voor deze labopzet.
- Internet op de Mac en NAT in de gasten voor bootstrap/pakketinstallatie.
- Bekend rootwachtwoord in golden. Bewaar labwachtwoorden in een wachtwoordmanager of persoonlijke notitie; niet in Git.

De controller geeft iedere examenclone 2 vCPU en 4 GiB RAM. Twee gelijktijdige clones vragen samen ongeveer 8 GiB gast-RAM, naast macOS en Fusion. Op een Mac met weinig RAM wordt dit krap. Begin met één examenpaar en sluit andere gasten af. De template-golden heeft eveneens 2 vCPU en 4 GiB RAM; import behoudt verder de broninstellingen totdat de clones worden gemaakt.

### Opslag

Alle nieuwe gasten gebruiken volledige clones. De dunne disks nemen aanvankelijk minder ruimte in dan hun maximale capaciteit, maar kunnen groeien. Snapshots en oude VM’s gebruiken extra ruimte.

| Onderdelen | Nominale virtuele diskcapaciteit |
|---|---:|
| Nieuwe golden-template | 30 GiB |
| Alpha + bravo, systeemdisks en extra disks | 85 GiB |
| Charlie + delta | 86 GiB |
| Echo + foxtrot | 82 GiB |
| Nieuwe 30 GiB golden + alle zes clones | 283 GiB |

Deze tabel gaat uit van een 30 GiB golden-systeemdisk. Een geïmporteerde grotere systeemdisk vergroot de totalen. De tabel is geen voorspelling van werkelijk gebruikte opslag en omvat geen ISO, snapshots, backups of bestaande omgeving. Controleer vrije ruimte vóór ieder paar. Bij onvoldoende ruimte stop je vóór create; verwijder geen bestaande VM om een foutmelding te omzeilen.

### Twee verschillende mappen

| Wat | Pad voor jouw inrichting |
|---|---|
| Nieuwe code en documentatie | ~/Studies/RHCSA/labs/RHCSA-Fusion-v2 |
| Nieuwe VM-bundles | ~/RHCSA-Fusion-v2 |
| Oude VM-bundles | ~/RHCSA-Fusion-jconwell |
| DVD-ISO, volgens jouw eerdere pad | ~/Downloads/Images/Rocky-10.2-aarch64-dvd1.iso |

De naam van de code- en VM-map is gelijk, maar hun volledige pad is anders. Houd dat onderscheid aan. Voer controllercommando’s nooit uit vanuit een `.vmwarevm`-bundle.

Een `.vmwarevm` is een pakket dat Finder als één bestand kan tonen. Daarin zitten de `.vmx`, virtuele disks, snapshots en het eigen statebestand. Verplaats of bewerk die inhoud niet tijdens gebruik.

## 4. Oude omgeving behouden

Je Windows-VM, gewone Rocky-VM, servera en serverb blijven buiten deze inrichting. Ook oude alpha/bravo blijven beschikbaar voor losse oefeningen. De controller gebruikt standaard uitsluitend de nieuwe VM-map.

1. Noteer in Fusion welke VM de oude golden is.
2. Open de locatie van haar bundle in Finder en noteer het volledige pad.
3. Controleer in Linux of dit werkelijk golden is en of er al examenaccounts, oefenpartities of services aangemaakt zijn.
4. Sluit de bron-golden normaal af wanneer je wilt kopiëren. Suspend is onvoldoende.
5. Maak desgewenst een externe kopie van de uitgeschakelde bundle, bijvoorbeeld op een andere disk. Een snapshot is geen externe backup.

Voer bootstrap, seal en seed nooit op de oude bron uit. De nieuwe import maakt een onafhankelijke kopie. Bij twijfel over de bronstaat gebruik je route B.

Je hoeft de oude alpha/bravo niet aan te passen voor deze nieuwe route. De oude `exam-ready` snapshots zijn geen bewezen v2-startpunt en worden niet voor v2-reset gebruikt.

## 5. Code uitpakken en de Mac controleren

### Code plaatsen

Pak de ZIP uit in Finder. Plaats de map met README.md, tools en RHCSA-Lab-Scripts onder `~/Studies/RHCSA/labs/`. Het eindresultaat moet zijn:

```text
~/Studies/RHCSA/labs/RHCSA-Fusion-v2/
    README.md
    WERKINSTRUCTIE-MACBOOK-FUSION.md
    RHCSA-Lab-Scripts/fusion-lab.py
    tools/validate.py
    Examen-1-opdrachten.md
    ...
```

Als daar al een eerdere codemap staat, bewaar die onder een andere naam en plaats de nieuwe map daarnaast. Overschrijf geen map met jouw eigen wijzigingen. Je VM-map staat elders en hoeft hiervoor niet verplaatst te worden.

### Controle — MAC

```bash
uname -m
sw_vers
python3 --version
ls -l "/Applications/VMware Fusion.app/Contents/Library/vmrun"
ls -l "/Applications/VMware Fusion.app/Contents/Library/vmware-vdiskmanager"
df -h "$HOME"
cd "$HOME/Studies/RHCSA/labs/RHCSA-Fusion-v2"
pwd
ls README.md RHCSA-Lab-Scripts/fusion-lab.py tools/validate.py
python3 tools/validate.py
```

Verwacht: `arm64`, beide Fusion-hulpmiddelen bestaan, de juiste codemap en aan het einde geslaagde tests met `OK`. Het aantal tests kan bij latere versies veranderen; deze release heeft 69 regressies. De tests maken geen echte examen-VM’s.

Open Fusion één keer normaal. Accepteer noodzakelijke eigen systeem-/netwerktoestemmingen als Fusion daarom vraagt. Bekijk via het menu About/Over VMware Fusion welke versie je gebruikt en noteer die. Als de hulpmiddelen niet bestaan, herstel eerst de Fusion-installatie. Installeer geen losse vmrun van een andere hypervisor.

### Archive-checksum

Bij de ZIP staat een `.sha256`-bestand. Vergelijk de berekende waarde met die regel. MAC, nadat je het pad naar jouw gedownloade ZIP hebt aangepast:

```bash
shasum -a 256 "$HOME/Downloads/RHCSA-Fusion-v2-met-werkinstructie-2026-10-09.zip"
```

Het checksum-bestand bevat de juiste naam en waarde voor die specifieke ZIP. De checksum van de eerdere ZIP geldt niet voor de aangevulde ZIP.

## 6. ISO kiezen en variabelen instellen

**MAC, in iedere nieuwe Terminal-sessie waarin je create/template gebruikt:**

```bash
cd "$HOME/Studies/RHCSA/labs/RHCSA-Fusion-v2"
ISO="$HOME/Downloads/Images/Rocky-10.2-aarch64-dvd1.iso"
printf '%s\n' "$ISO"
ls -lh "$ISO"
shasum -a 256 "$ISO"
```

Vervang het ISO-pad als jouw bestand anders heet of elders staat. Vergelijk de checksum met de officiële checksum voor exact die ISO. Gebruik het in jouw systeem aanwezige, gecontroleerde bestand; verander niet alleen de naam van een x86_64-image naar aarch64.

`ISO=...` is een shellvariabele. Zij bestaat alleen in die Terminal-sessie. Open je een nieuw venster, stel haar opnieuw in. Export is voor deze commando’s niet nodig: `--iso "$ISO"` geeft de waarde direct door. Een leeg ISO leidt tot `Provide a local DVD ISO`.

Het script controleert bestand, extensie en naamindicaties; het bewijst niet zelfstandig de architectuur of de inhoud van de ISO. Verplaats de ISO niet nadat de CD/DVD-verwijzing is ingesteld. De media worden later ook voor repository-oefeningen gebruikt.

## 7. Netwerk en disks begrijpen

### Netwerk

Iedere nieuwe VM heeft twee virtuele netwerkadapters:

| Adapter | Fusion-instelling | Doel | Adressering |
|---|---|---|---|
| ethernet0 / mac0 | Share with my Mac / NAT | Internet en toegang vanaf de Mac | DHCP |
| ethernet1 / mac1 | Private to my Mac / host-only | Verkeer tussen examenpartners | Statisch pas bij de netwerkopdracht |

De controller stelt dit in. Maak niet handmatig een derde adapter aan. Gebruik voor het lab geen bridged Wi-Fi-adapter. NAT-adressen kunnen veranderen; voorbeelden zoals 172.16.63.143 uit je screenshot zijn geen vaste adressen.

De tweede adapter heeft na voorbereiding bewust geen statisch examenadres. Dat is onderdeel van de netwerkopdracht. De tabel hieronder is het doel na die opdracht, niet iets wat je vooraf op golden moet instellen.

| Examen | Node | IPv4 /24 | IPv6 /64 |
|---|---|---|---|
| 1 | alpha | 192.168.100.10 | fd00::10 |
| 1 | bravo | 192.168.100.20 | fd00::20 |
| 2 | charlie | 10.20.30.11 | fd42::11 |
| 2 | delta | 10.20.30.12 | fd42::12 |
| 3 | echo | 172.16.40.21 | fd10::21 |
| 3 | foxtrot | 172.16.40.22 | fd10::22 |

De host-only adapter krijgt geen gateway of DNS. NAT houdt de internetroute. Gebruik `ipv4.never-default yes` en `ipv6.never-default yes` zoals de antwoorden beschrijven. Een verkeerde default-route kan pakketdownloads breken.

NAT en host-only namen in Linux zijn niet gegarandeerd enp2s0/enp3s0. Match de MAC-adressen met de hostmetadata; gok niet op de volgorde van een screenshot. Het standaard host-only netwerk is gedeeld door deze nieuwe gasten. De examenparen zijn niet volledig van elkaar geïsoleerd. Werk met één paar tegelijk en schakel andere examengasten uit. Bij conflict met een VPN of een bestaand netwerk stop je en onderzoek je de routes; wijzig examen-IP’s niet willekeurig.

### Disks

| Node | Systeemdisk | Extra disks volgens plan |
|---|---|---|
| alpha | nvme0n1 | nvme0n2: 10 GiB |
| bravo | nvme0n1 | nvme0n2: 10 GiB; nvme0n3: 5 GiB |
| charlie | nvme0n1 | nvme0n2: 8 GiB; nvme0n3: 6 GiB; nvme0n4: 4 GiB |
| delta | nvme0n1 | nvme0n2: 8 GiB |
| echo | nvme0n1 | nvme0n2: 8 GiB; nvme0n3: 6 GiB |
| foxtrot | nvme0n1 | nvme0n2: 8 GiB |

Controleer altijd werkelijk met `lsblk`: de tabel is de voorgeschreven layout, geen toestemming om blind een device te formatteren. Een device met `/`, `/boot` of `/boot/efi` is onderdeel van je systeem. De seed maakt geen oefenpartities of bestandenystemen op de extra disks. Die moeten leeg blijven tot hun opdracht.

MAC:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py plan --exam 1
python3 RHCSA-Lab-Scripts/fusion-lab.py plan --exam 2
python3 RHCSA-Lab-Scripts/fusion-lab.py plan --exam 3
```

## 8. Route A — bestaande golden kopiëren

Gebruik deze route als golden nog schoon is: geen eerder uitgevoerd examen, alleen één NVMe-systeemdisk, ARM Linux met EFI. Bootstrap controleert later aanvullende afwijkingen. Een oude marker alleen bewijst geen schone staat.

### Bron controleren — LINUX ROOT, oude golden

```bash
hostnamectl
uname -m
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
systemctl is-active vmtoolsd
```

Verwacht aarch64. De systeemdisk mag partities en LVM bevatten: dat is normaal. Extra oefendisks zijn op golden niet toegestaan. Noteer het bekende rootwachtwoord en jouw installatieaccount.

Schakel de bron normaal uit:

```bash
systemctl poweroff
```

### Volledige kopie — MAC

Zoek de exacte .vmx in de oude bundle. Voor jouw eerder gebruikte locatie:

```bash
ls -l "$HOME/RHCSA-Fusion-jconwell/rhel10-golden.vmwarevm/rhel10-golden.vmx"
python3 RHCSA-Lab-Scripts/fusion-lab.py import-golden --source "$HOME/RHCSA-Fusion-jconwell/rhel10-golden.vmwarevm/rhel10-golden.vmx"
python3 RHCSA-Lab-Scripts/fusion-lab.py open-golden
```

Als de .vmx anders heet, geef het werkelijk gevonden pad door. Een bundle-pad zonder .vmx is onvoldoende. Import kan enkele minuten duren. Start geen tweede controlleractie zolang kopiëren loopt.

Verwacht een nieuwe bundle onder `~/RHCSA-Fusion-v2/rhel10-golden.vmwarevm`. Fusion toont bij deze kopie v2 in de displaynaam. Controleer de bundlelocatie om verwarring met de oude golden uit te sluiten.

**Ga hierna direct naar hoofdstuk 10. Voer route B niet óók uit.**

Bij `Existing golden destination preserved` of een onbekende bestemming: onderzoek wat al bestaat. Een tweede import is geen reset. Bewaar bestaande bundles; zie hoofdstuk 19.

## 9. Route B — nieuwe Rocky-installatie

**Voorkeursroute voor een nieuwe installatie:** [AUTOMATISCHE-INSTALLATIE.md](AUTOMATISCHE-INSTALLATIE.md). Die automatiseert de keuzes hieronder, vraagt alleen je root-/studentwachtwoorden en gebruikt `~/RHCSA-Fusion-auto`. Voeg bij verder examenwerk telkens `--root "$VMROOT"` toe aan Mac-controllercommando’s. Voer na automatische installatie niet óók de handmatige bootstrap uit. De rest van dit hoofdstuk blijft beschikbaar als handmatig alternatief.

Gebruik dit uitsluitend als route A niet geschikt is. De nieuwe bestemming moet vrij zijn. Als daar een bruikbare v2-golden staat, behoud haar en gebruik die; template is geen herinstallatieknop.

### Lege VM maken — MAC

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py template --iso "$ISO"
python3 RHCSA-Lab-Scripts/fusion-lab.py open-golden
```

Verwacht een nieuwe 30 GiB NVMe-disk, EFI, twee NICs en de DVD gekoppeld. Als Linux al geïnstalleerd blijkt, controleer eerst de bestemming; begin niet opnieuw met formatteren.

### Installeren — FUSION / Rocky installer

1. Kies installatie van Rocky Linux vanaf de DVD.
2. Kies toetsenbordindeling die overeenkomt met wat je daadwerkelijk gebruikt. Test bijzondere tekens; wachtwoordproblemen kunnen een layoutprobleem zijn.
3. Kies taal en tijdzone. UTC of Europe/Amsterdam zijn mogelijk; noteer je keuze.
4. Controleer installation source: de gekoppelde volledige DVD.
5. Kies **Minimal Install**. Voeg niet alvast httpd, tmux, nano, zsh, containers of examenaccounts toe. Als de DVD/softwareselectie anders heet, kies de minimale serverbasis zonder oefenpakketten.
6. Kies alleen de ene nieuwe 30 GiB systeemdisk als installation destination. Automatische LVM-indeling is bruikbaar. Geen disk uit de oude omgeving selecteren. Geen extra labdisk of versleuteling voor deze eenvoudige herstelroute.
7. Activeer de NAT-interface als netwerk nodig is. Match zo nodig MACs met het nieuwe statebestand. Host-only hoeft tijdens installatie geen IP te krijgen.
8. Stel hostname bijvoorbeeld op rhel10-golden. Bootstrap zet dit later definitief.
9. Stel een bekend rootwachtwoord in en zorg dat root niet gelockt blijft. Rootlogin via de lokale console is nodig. Root-SSH inschakelen is niet nodig.
10. Maak een installatieaccount, bijvoorbeeld siebe. Indien de installer dit vereist of je het nodig hebt voor kopiëren/beheer, geef het tijdelijk administratorrechten. Die worden op de nieuwe golden later gericht verwijderd.
11. Gebruik geen extra security profile dat aanvullende toegangsbeperkingen toevoegt; SELinux blijft wel Enforcing.
12. Begin de installatie en wacht op voltooiing.
13. Reboot. Als opnieuw de installer verschijnt, schakel de gast normaal uit en verbreek in Fusion de CD/DVD-verbinding bij opstarten. Verwijder het ISO-bestand niet. Start vervolgens van de systeemdisk.

### Eerste login — LINUX ROOT, nieuwe golden

```bash
cat /etc/os-release
uname -m
passwd -S root
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
getenforce
ip -br addr
```

Verwacht Rocky 10, aarch64, rootstatus P en Enforcing. De exacte partitiegroottes hangen van de installer af. Eén disk met EFI-/boot-/rootpartities en eventueel swap is normaal.

Test rootlogin werkelijk: log op de nieuwe golden-console uit en opnieuw als root in, vóór je verdergaat. Geen zichtbaar wachtwoord tijdens typen is normaal. Als rootlogin niet werkt, herstel het via je tijdelijke sudo-installatieaccount met `sudo passwd root`, controleer status en test opnieuw. Rootstatus P in de echte rootfs bewijst niet dat een initramfs-emergency-shell dezelfde credentials heeft.

## 10. Nieuwe golden herkennen en bestanden overzetten

### Identiteit — MAC

```bash
cat "$HOME/RHCSA-Fusion-v2/rhel10-golden.vmwarevm/fusion-state.json"
python3 RHCSA-Lab-Scripts/fusion-lab.py status
```

State hoort bij node golden en schema 2. Noteer mac0 en mac1. Dit bestand staat op de Mac binnen de nieuwe bundle, niet in /etc van Linux. Examengasten hebben later ieder hun eigen statebestand in hun eigen bundle.

### Interfaces — LINUX ROOT, nieuwe golden

```bash
ip -br link
ip -br addr
nmcli -f NAME,UUID,DEVICE con show
```

Schrijf de interface met mac0 als NAT op en die met mac1 als LAB. Alleen een naam als enp2s0 zegt niet welke functie de interface heeft.

### Als NAT geen adres heeft

Een geïmporteerd profiel kan aan de oude MAC gebonden zijn. Gebruik op de nieuwe golden, in de rootconsole:

```bash
read -r -p 'Naam van de NAT-interface, gematcht met mac0: ' NAT_IF
nmcli con add type ethernet ifname "$NAT_IF" con-name v2-copy-nat ipv4.method auto ipv6.method disabled
nmcli con up v2-copy-nat
ip -br addr
```

Doe dit alleen als er nog geen bruikbaar NAT-profiel is. Bij een reeds bestaand v2-copy-nat-profiel gebruik je `nmcli con up v2-copy-nat`; maak geen duplicaat. Bootstrap schakelt concurrerende installerprofielen later uit.

Test DNS en repositories op de nieuwe golden:

```bash
getent hosts download.rockylinux.org
dnf repolist
```

Een mislukte ping alleen bewijst geen internetstoring. DNS en een geslaagde repository-verbinding zijn bruikbaarder. Voor een verse installatie, als SSH nog niet actief is:

```bash
dnf install -y openssh-server
systemctl enable --now sshd
systemctl is-active sshd
```

Als firewalld actief is en SSH wordt geblokkeerd, voeg uitsluitend de SSH-service toe aan de zone van de NAT-interface. Controleer eerst `firewall-cmd --get-active-zones`; voeg geen brede allow-all regel toe.

### Scripts kopiëren — MAC

Neem het NAT-IP uit `ip -br addr`. Gebruik je werkelijke installatieaccount. Onderstaand blok vraagt beide waarden:

```bash
printf 'Installatieaccount in de nieuwe golden: '
IFS= read -r INSTALL_USER
printf 'NAT IPv4 van de nieuwe golden: '
IFS= read -r GOLDEN_IP
scp RHCSA-Lab-Scripts/guest-golden.sh RHCSA-Lab-Scripts/guest-seal.sh "$INSTALL_USER@$GOLDEN_IP:/tmp/"
```

Accepteer een nieuwe hostkey alleen nadat je bevestigd hebt dat het IP de nieuwe golden is. Verkeerd bekend IP/hostkey? Controleer eerst de VM en fingerprint; verwijder niet je gehele known_hosts-bestand.

### Aankomst — LINUX ROOT, nieuwe golden

```bash
ls -l /tmp/guest-golden.sh /tmp/guest-seal.sh
```

Als scp niet werkt, los eerst IP/sshd/firewall/accounttoegang op. Golden-bootstrap kan niet zonder de scripts. Ga niet uit van werkende gedeelde mappen op deze ARM-gast; deze procedure gebruikt expliciet scp.

## 11. Golden voorbereiden en sudo opschonen

### Bootstrap — LINUX ROOT, nieuwe golden, Fusion-console

Controleer dat sudo beschikbaar is, zodat het script de rechten van gewone accounts werkelijk kan onderzoeken. Installeer het eerst op de nieuwe golden; dit geeft op zichzelf geen extra gebruikersrechten.

```bash
dnf install -y sudo
bash /tmp/guest-golden.sh
```

Het script installeert basishulpmiddelen, activeert VMware Tools/NetworkManager/SSH/firewall, maakt fusion-nat en fusion-lab, zet multi-user.target, controleert accounts/pakketten, stelt student in en schakelt Fusion-timesync uit. Sommige stappen zijn interactief.

Bij de interfacevragen:

- NAT interface: de Linux-naam die bij mac0 hoort.
- Host-only interface: de Linux-naam die bij mac1 hoort.
- Student-wachtwoord: kies een bekend labwachtwoord en noteer het.

De nieuwe golden mag niet vooraf alle antwoorden bevatten. Daarom kan het script stoppen op oefenaccounts, oefenpakketten of sudo-rechten. Dat is een concrete voorbereidingseis, geen reden om de controles te verwijderen.

### Tijdelijke sudo-rechten verwijderen

Je installatieaccount kan nog in wheel zitten. Werk uitsluitend op de nieuwe kopie en houd de rootconsole open.

```bash
getent passwd student siebe
id student
id siebe
sudo -l -U student
sudo -l -U siebe
```

Vervang siebe als jouw installatieaccount anders heet. `getent`/`id` kunnen voor een niet-bestaand account falen: behandel alleen echte accounts.

Als het genoemde account werkelijk wheel-lid is:

```bash
gpasswd -d siebe wheel
```

Doe hetzelfde voor student alleen als hij nog wheel-lid blijkt. Bootstrap probeert dat lidmaatschap al te verwijderen. Het account zelf blijft bestaan.

Een expliciete sudoers-grant kan blijven bestaan. Controleer:

```bash
ls -l /etc/sudoers.d
visudo
```

Open een gevonden drop-in afzonderlijk met `visudo -f /etc/sudoers.d/werkelijke-bestandsnaam`. Die voorbeeldnaam moet worden vervangen. Verwijder alleen de grant voor het betreffende gewone installatie-/studentaccount. Behoud de rootregel en andere noodzakelijke configuratie.

```bash
visudo -c
sudo -l -U student
sudo -l -U siebe
```

Verwacht een geldige sudoers-configuratie en geen toegestane sudo-commando’s voor die gewone oefenaccounts. Andere gewone accounts met sudo worden door bootstrap genoemd; behandel ze afzonderlijk. Verwijder geen gehele sudoers-map en geen gebruikers blind.

Voer bootstrap opnieuw uit. Het script kan zijn eigen netwerkprofielen hergebruiken:

```bash
bash /tmp/guest-golden.sh
```

### Oefenpakketten of accounts aanwezig

Bij bijvoorbeeld httpd, tmux, nano, zsh of alice/emma op golden onderzoek je of de bron werkelijk schoon was. Een reeds gewerkt examen is geen goede basis.

Voor alleen een toevallig geïnstalleerd oefenpakket kun je op de nieuwe kopie eerst `dnf remove --assumeno PAKKET` bekijken. Controleer de dependencylijst. Verwijder uitsluitend bedoelde oefensoftware als dat verantwoord is voor deze wegwerpkopie. Bij veel afwijkingen is route B duidelijker. Voer dit niet op servera/serverb of de oude golden uit.

## 12. Golden controleren en seal uitvoeren

### Controle vóór seal — LINUX ROOT, nieuwe golden

```bash
cat /etc/rhcsa-fusion-golden
passwd -S root
getent passwd student
systemctl is-active vmtoolsd
systemctl is-active sshd
systemctl is-active NetworkManager
systemctl is-active firewalld
systemctl get-default
getenforce
nmcli -f NAME,UUID,DEVICE con show
ip -br addr
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
cat /etc/machine-id
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Verwacht marker `jconwell-fusion-golden-v2`, root P, actieve services, multi-user.target, Enforcing, één systeemdisk, DHCP op NAT, fusion-lab zonder examen-IP. Noteer machine-ID en hostkey-fingerprint als controlegegevens.

Controleer dat beide scripts nog in /tmp staan. Verplaats of kopieer ze zo nodig opnieuw vóór seal. /tmp is geen permanente bron voor toekomstige werkzaamheden.

### Seal — LINUX ROOT, Fusion-console

```bash
bash /tmp/guest-seal.sh
```

Seal bewaart golden-identiteit als referentie, maakt machine-id leeg, verwijdert de hostkeys van deze nieuwe kopie en schakelt haar uit. Clones krijgen bij hun eerste boot eigen identiteiten.

**Verwacht: golden gaat uit. Start haar nu niet opnieuw voordat je clones maakt.** Dat zij uit staat is de gewenste toestand. Seal geeft geen exam-ready snapshot aan golden.

Als je de nieuwe golden toch opnieuw hebt gestart, controleer haar toestand en voer seal opnieuw in de console uit vóór het maken van verdere clones. Als het script niet meer in /tmp staat, kopieer het opnieuw. Gebruik nooit seal op een examengast of de oude golden.

## 13. Examen 1 maken, voorbereiden en vastleggen

### 13.1 Create — MAC

```bash
cd "$HOME/Studies/RHCSA/labs/RHCSA-Fusion-v2"
ISO="$HOME/Downloads/Images/Rocky-10.2-aarch64-dvd1.iso"
python3 RHCSA-Lab-Scripts/fusion-lab.py create --exam 1 --iso "$ISO"
python3 RHCSA-Lab-Scripts/fusion-lab.py status --exam 1
```

Verwacht alpha en bravo met schema 2, phase ready en seeded False. Clone/diskaanmaak kan minuten duren. Wacht op afronding.

Als er al complete v2-clones bestaan, meldt create dat die behouden zijn. Create is geen herinstallatie, geen reset en geen automatische seed. Gebruik dan status om de werkelijke vervolgstap te bepalen.

### 13.2 Start en consoles — MAC / FUSION

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node alpha
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node bravo
```

Wacht op beide loginprompts. Log **op beide consoles als root in met het golden-wachtwoord**. Houd deze rootconsoles open tot na seed en shutdown. Op bravo wordt dat wachtwoord tijdens seed bewust onbekend.

### 13.3 Clone-identiteiten en disks — LINUX ROOT, beide gasten

```bash
hostnamectl --static
cat /etc/machine-id
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
systemctl is-active vmtoolsd
ip -br link
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
```

De hostnamen kunnen vóór seed nog golden zijn; seed zet ze. Machine-ID’s en hostkey-fingerprints moeten onderling en met de oude golden-identiteit verschillen. MACs moeten bij de eigen bundle horen. Stop bij gelijke identiteiten; onderzoek seal voordat je seed uitvoert.

MAC:

```bash
cat "$HOME/RHCSA-Fusion-v2/rhel10-alpha.vmwarevm/fusion-state.json"
cat "$HOME/RHCSA-Fusion-v2/rhel10-bravo.vmwarevm/fusion-state.json"
```

Controleer extra_sizes: alpha [10], bravo [10,5]. De extra disks moeten leeg zijn. Als er partities/signatures of eerder werk op staan: geen seed; je hebt geen nieuwe examenstart.

### 13.4 Seed — MAC

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py seed --node alpha
python3 RHCSA-Lab-Scripts/fusion-lab.py seed --node bravo
python3 RHCSA-Lab-Scripts/fusion-lab.py status --exam 1
```

Geef bij iedere wachtwoordvraag het geërfde golden-rootwachtwoord. Je ziet geen tekens bij invoer. VMware Tools moet actief zijn. Het wachtwoord wordt niet opgeslagen door de controller; vmrun gebruikt het lokaal als procesargument voor gastauthenticatie. Gebruik hiervoor je labwachtwoord.

Verwacht seeded True na beide geslaagde acties. De seed heeft netwerk/fixtures-checkpoints; lees de exacte fout bij een stop. Herhaal niet nadat je examenwerk bent begonnen.

### 13.5 Uitgangspunt controleren — LINUX ROOT, nog geopende consoles

Op beide:

```bash
hostnamectl --static
cat /etc/rhcsa-fusion-seeded
ls -l /var/lib/rhcsa-fusion/network.done /var/lib/rhcsa-fusion/fixtures.done
```

Alpha:

```bash
grep -E '^GRUB_(TIMEOUT|TIMEOUT_STYLE|CMDLINE_LINUX)=' /etc/default/grub
stat -c '%a %n' /var/tmp/badperms
```

Verwacht timeout 3, zonder toegevoegde quiet, en badperms 777. Bravo:

```bash
systemctl get-default
```

Verwacht graphical.target. Er hoeft op een minimale installatie geen volledige grafische desktop te verschijnen: voor de targetopdracht gaat het om de ingestelde systemd-default.

Los deze fouten nu nog niet op. Ze zijn het examenuitgangspunt. Bravo’s rootwachtwoord is bewust onbekend na seed; een reeds geopende rootconsole blijft bruikbaar om normaal uit te schakelen.

### 13.6 Normaal uitschakelen — LINUX ROOT, beide consoles

```bash
systemctl poweroff
```

Wacht totdat beide echt uit zijn. Geen suspend en geen geforceerde power-off. Als geen rootconsole open was, gebruik Fusion’s normale guest shutdown met werkende Tools.

MAC:

```bash
"/Applications/VMware Fusion.app/Contents/Library/vmrun" -T fusion list
```

Alpha en bravo mogen niet in de running list staan. Andere VM’s kunnen er wel staan, maar kosten geheugen. Een gestopt icoontje of alleen een geselecteerde libraryregel bewijst geen power-off.

### 13.7 Snapshots — MAC

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py snapshot --node alpha
python3 RHCSA-Lab-Scripts/fusion-lab.py snapshot --node bravo
python3 RHCSA-Lab-Scripts/fusion-lab.py status --exam 1
```

Verwacht bij beide powered off, seeded True en snapshot exam-ready-v2. Een bestaande snapshot wordt behouden, niet overschreven. Als de naam al bestaat, controleer of je al klaar was. Maak niet onder dezelfde naam een nieuw startpunt na examenwerk.

**Dit is het overdrachtsmoment: examen 1 is voorbereid.** Golden blijft uit; de snapshots vormen je herhaalbare beginpunt.

## 14. Examen 1 uitvoeren en root herstellen

### Begin — MAC

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node alpha
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node bravo
```

Open Examen-1-opdrachten.md. Werk in volgorde op de genoemde VM. Als een taak beide nodes noemt, voer haar op beide uit met de juiste adressen/namen. De antwoordensleutel is naslag, geen monolithisch installatiescript.

### Eerste taak: root op bravo herstellen

Deze procedure hoort bij de nieuwe v2-examenopdracht, niet bij golden-bootstrap.

1. Open bravo’s Fusion-console en geef de gast toetsenbordfocus.
2. Reboot de gast naar het GRUB-menu. Gebruik Escape/pijltoets tijdens boot om het menu zichtbaar te houden; het juiste moment kan een tweede normale poging vragen.
3. Selecteer de kernelentry, druk e.
4. Zoek de regel die begint met linux. De regel kan op het scherm over meerdere visuele regels lopen.
5. Verander het losse argument ro naar rw. Verander niet letters binnen root= of rd.lvm.lv=.
6. Verwijder een eventueel rd.break-argument.
7. Voeg aan het einde van dezelfde linux-regel toe: `init=/bin/bash enforcing=0`.
8. Laat de initrd-regel intact.
9. Start met Ctrl-X zoals GRUB aangeeft. F10 is een alternatief als GRUB dat vermeldt; op een Mac kan Fn nodig zijn voor F-toetsen. Command-X is geen Ctrl-X.

In de root-Bash-shell:

```bash
mount -o remount,rw /
passwd root
touch /.autorelabel
sync
exec /sbin/init
```

Gebruik het wachtwoord dat de opdracht voorschrijft. Bij passwd verschijnt geen invoer op het scherm. Wacht op de succesmelding voordat je verdergaat.

**Geen exit en geen Ctrl-D in deze shell.** Bash is hier PID 1. Je werkt in de geïnstalleerde root; remount `/`, niet `/sysroot`. De eerder geziene fout `/sysroot: mount point does not exist` past bij het verkeerde pad in deze herstelwijze.

Wacht op SELinux-herlabeling en eventuele reboot. Onderbreek actieve herlabeling niet met herhaalde power-offs. Na normale login doe je een normale reboot zonder de GRUB-regel opnieuw te wijzigen:

```bash
reboot
```

Na opnieuw inloggen als root:

```bash
passwd -S root
getenforce
cat /proc/cmdline
```

Verwacht P, Enforcing en geen init=/bin/bash of enforcing=0. Tijdelijke GRUB-editorwijzigingen worden niet als blijvende config opgeslagen.

`rd.break` is een andere herstelroute. Gebruik de twee procedures niet door elkaar. De melding dat de rootaccount gelockt is in een dracut-shell bewijst niet dat het wachtwoord in de echte Linux-root nog gelockt is. De v2-antwoorden gebruiken daarom bovenstaande afzonderlijke route; Fusion zelf is daarmee niet automatisch de oorzaak.

### Daarna de taken

- T2: op bravo default target wijzigen naar multi-user.target.
- T3: op alpha GRUB-timeout/quiet wijzigen, BLS bijwerken, rebootcontrole.
- Netwerktaken: vanuit Fusion-console; NAT behouden en host-only statisch instellen.
- Disktaken: vooraf lsblk/parted/wipefs inspecteren; alleen voorgeschreven lege extra disk gebruiken.
- Gebruikerstaken: werkelijk als die gebruiker testen. Root kan rechten omzeilen en is geen valide ACL/umask-gebruikerscontrole.
- Persistente services, mounts en firewall: na normale reboot opnieuw controleren.

Voor GRUB op deze Rocky/RHEL 10 opzet staat de antwoordensleutel op:

```bash
grub2-mkconfig -o /boot/grub2/grub.cfg --update-bls-cmdline
```

Schrijf niet blind naar het kleine EFI-stubbestand. Raadpleeg op de gast `grub2-mkconfig --help` en `man grub2-mkconfig`; distributieopties kunnen in help duidelijker staan dan in de manpage.

## 15. Controleprogramma’s gebruiken

De checker draait op Linux, niet op de Mac. Hij verandert geen gastconfiguratie. Een PASS geldt voor één bewijscheck. MANUAL betekent dat subcriteria/functionele tests nog door jou moeten worden gecontroleerd. ERROR, bijvoorbeeld ontbrekende tools, is geen geslaagde taak. Exitcode 0 betekent niet automatisch dat alle taken voltooid zijn.

### Code overzetten naar elke gast — MAC

Maak een overdrachtsarchief buiten de codeboom. Dit bevat de scripts en tools, niet je VM-bundles:

```bash
cd "$HOME/Studies/RHCSA/labs/RHCSA-Fusion-v2"
tar -czf /tmp/rhcsa-v2-gastbestanden.tgz RHCSA-Lab-Scripts tools
printf 'Account met SSH-login in de doelgast: '
IFS= read -r TRANSFER_USER
printf 'Bereikbaar NAT- of lab-IP van de doelgast: '
IFS= read -r GUEST_IP
scp /tmp/rhcsa-v2-gastbestanden.tgz "$TRANSFER_USER@$GUEST_IP:/tmp/"
```

Gebruik een werkende gewone SSH-account. Ga niet uit van root-SSH. Voer dit voor iedere gast uit. Hergebruik het IP niet zonder te controleren naar welke gast het wijst. De netwerktaken kunnen inmiddels vaste lab-IP’s hebben ingesteld.

### Uitpakken — LINUX ROOT, doelgast

```bash
mkdir -p /root/RHCSA-Fusion-v2
tar -xzf /tmp/rhcsa-v2-gastbestanden.tgz -C /root/RHCSA-Fusion-v2
```

Examen 1 alpha:

```bash
python3 /root/RHCSA-Fusion-v2/tools/verify.py --exam 1 --node alpha
```

Examen 1 bravo:

```bash
python3 /root/RHCSA-Fusion-v2/tools/verify.py --exam 1 --node bravo
```

De shellwrapper is een alternatief, bijvoorbeeld:

```bash
bash /root/RHCSA-Fusion-v2/RHCSA-Lab-Scripts/ex1-verify.sh --node alpha
```

Lees CONTROLE-DEKKING.md en de functionele controles in de antwoorden. Test HTTP/NFS/SSH ook vanaf de andere node. Een service die lokaal actief is, kan nog door firewall, naamresolutie of rechten onbruikbaar zijn.

Voor een opgeslagen controle-uitvoer op de gast:

```bash
python3 /root/RHCSA-Fusion-v2/tools/verify.py --exam 1 --node alpha > /root/controle-examen1-alpha.txt 2>&1
```

Bekijk het bestand en registreer FAIL/ERROR/MANUAL. Voer na een normale reboot dezelfde checks opnieuw uit. Gebruik GAST-ACCEPTATIE.md als volledige praktijkchecklist.

## 16. Examen 2 volledig opzetten

Golden moet nog sealed en uitgeschakeld zijn. Heb je golden gestart sinds de laatste seal, seal haar opnieuw vóór create. Sluit alpha/bravo normaal af om geheugen vrij te maken; reset is hiervoor niet nodig.

### Create/start — MAC

```bash
cd "$HOME/Studies/RHCSA/labs/RHCSA-Fusion-v2"
ISO="$HOME/Downloads/Images/Rocky-10.2-aarch64-dvd1.iso"
python3 RHCSA-Lab-Scripts/fusion-lab.py create --exam 2 --iso "$ISO"
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node charlie
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node delta
```

Log op beide consoles als root in met het golden-wachtwoord. Houd de consoles open. Controleer unieke machine-ID/SSH-hostkeys, MACs en disks zoals bij examen 1. Charlie moet extra 8/6/4 GiB hebben; delta 8 GiB. Geen eerder examenwerk.

### Seed — MAC

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py seed --node charlie
python3 RHCSA-Lab-Scripts/fusion-lab.py seed --node delta
python3 RHCSA-Lab-Scripts/fusion-lab.py status --exam 2
```

Verwacht seeded True. Charlie’s rootwachtwoord wordt onbekend. Delta houdt het bekende wachtwoord en krijgt rescue.target als default. Op charlie is /opt/finance bewust ontoegankelijk gemaakt. Repareer die beginfouten nog niet.

### Uit en snapshots

Op iedere nog geopende LINUX ROOT-console:

```bash
systemctl poweroff
```

MAC:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py snapshot --node charlie
python3 RHCSA-Lab-Scripts/fusion-lab.py snapshot --node delta
python3 RHCSA-Lab-Scripts/fusion-lab.py status --exam 2
```

Verwacht powered off en exam-ready-v2 op beide. Daarna:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node charlie
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node delta
```

Werk Examen-2-opdrachten.md af. Charlie T1 gebruikt rootherstel. Delta kan bij rescue-boot om het bekende rootwachtwoord vragen. Dat is niet dezelfde situatie als een onbekend rootwachtwoord op charlie.

Belangrijke afhankelijkheden: test beide SSH-key-logins vóór je wachtwoordtoegang voor emma beperkt; volg de NFS/homevolgorde in de antwoorden; maak een 1 GiB swapfile met de juiste prioriteit; test LVM-verplaatsing met echte data/checksums. Controleer Nginx vanaf de peer en na reboot.

Checker op de juiste LINUX ROOT-gast:

```bash
python3 /root/RHCSA-Fusion-v2/tools/verify.py --exam 2 --node charlie
```

Op delta gebruik je hetzelfde commando met `--node delta`. Zet de code eerst over zoals hoofdstuk 15 beschrijft.

## 17. Examen 3 volledig opzetten

Sluit de andere examenparen normaal af. Golden blijft sealed en uit.

### Create/start — MAC

```bash
cd "$HOME/Studies/RHCSA/labs/RHCSA-Fusion-v2"
ISO="$HOME/Downloads/Images/Rocky-10.2-aarch64-dvd1.iso"
python3 RHCSA-Lab-Scripts/fusion-lab.py create --exam 3 --iso "$ISO"
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node echo
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node foxtrot
```

Log op beide consoles als root in met het golden-wachtwoord; houd ze open. Controleer identiteiten/MACs en lege extra disks: echo 8/6 GiB, foxtrot 8 GiB.

### Seed — MAC

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py seed --node echo
python3 RHCSA-Lab-Scripts/fusion-lab.py seed --node foxtrot
python3 RHCSA-Lab-Scripts/fusion-lab.py status --exam 3
```

Verwacht seeded True. Foxtrot krijgt een bewust foutieve fstab-UUID en een onbekend rootwachtwoord. Na de volgende boot is herstel nodig; dit is de beginopdracht. Echo heeft defecte labdata/webservice-instellingen. Los niets vooraf op.

Schakel beide in de nog geopende LINUX ROOT-consoles normaal uit:

```bash
systemctl poweroff
```

### Snapshots en examen — MAC

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py snapshot --node echo
python3 RHCSA-Lab-Scripts/fusion-lab.py snapshot --node foxtrot
python3 RHCSA-Lab-Scripts/fusion-lab.py status --exam 3
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node echo
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node foxtrot
```

Werk Examen-3-opdrachten.md af. Gebruik voor foxtrot precies de gecombineerde herstelstappen in Examen-3-antwoorden.md: alleen de bogus fstab-entry behandelen, echte entries behouden. Volg niet uitsluitend de algemene passwd-procedure uit hoofdstuk 14 en laat de fstab-fout vervolgens staan.

**Verplichte afwijking van nummer-volgorde: T33 vóór T16.** De SELinux/webservice-oefening heeft die afhankelijkheid expliciet. Het opdrachtenbestand vermeldt haar.

Gebruik voor swapvervanging het echte oude swapdevice. Het oude LV blijft inactief toegewezen; geen blinde lvremove. Test diskwatch op de beschreven wegwerp-tmpfs, niet door je systeemdisk te vullen. Een publieke containerimage bewijst geen geslaagde private-registry-authenticatie.

Checker op LINUX ROOT echo:

```bash
python3 /root/RHCSA-Fusion-v2/tools/verify.py --exam 3 --node echo
```

Op foxtrot gebruik `--node foxtrot`. Zet eerst de code over zoals hoofdstuk 15.

## 18. Dagelijks werken, reset en backups

### Nieuwe Terminal-sessie

MAC:

```bash
cd "$HOME/Studies/RHCSA/labs/RHCSA-Fusion-v2"
ISO="$HOME/Downloads/Images/Rocky-10.2-aarch64-dvd1.iso"
python3 RHCSA-Lab-Scripts/fusion-lab.py status
```

Gebruik create niet als dagelijks startcommando. Start alleen het paar waaraan je werkt. Voor examen 1:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node alpha
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node bravo
```

### Pauzeren

Bewaar bestanden in Linux en sluit beide gasten normaal af met `systemctl poweroff`. Laat snapshots ongemoeid. Bij later start gaat je examenwerk verder waar je gebleven bent. Reset is daarvoor niet nodig.

Suspend kan Fusion ondersteunen, maar de controller verlangt power-off voor snapshot/reset/directe hardwarewijzigingen. Resume eerst en sluit normaal af als een gast suspended is. Kies niet geforceerd uitzetten als standaard werkwijze.

### Opnieuw oefenen

Reset vernietigt het examenwerk ná de snapshot binnen de gekozen nieuwe VM. Kopieer gewenste bestanden/notities eerst naar de Mac. Schakel de gasten normaal uit.

MAC, alleen wanneer je werkelijk opnieuw wilt beginnen:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py reset --node alpha
python3 RHCSA-Lab-Scripts/fusion-lab.py reset --node bravo
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node alpha
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node bravo
```

Voor examen 2 gebruik charlie/delta; voor examen 3 echo/foxtrot. Geen create of seed na een normale snapshotreset. De snapshot bevat de geslaagde seed en de beginfouten al.

Als je slechts één node reset, kan de andere node instellingen/accounts/NFS-data hebben die niet meer passen. Voor een volledige nieuwe poging reset je het hele paar. Voor gerichte deelproeven kun je één node bewust resetten, maar registreer de gemengde toestand.

### Backups

Bewaar de oorspronkelijke code-ZIP, ISO-checksum en persoonlijke labnotities. Voor een VM-backup: normaal uitschakelen, Fusion-toegang sluiten en de volledige bundle met snapshots/state naar je backupopslag kopiëren. Geen losse .vmdk uit een snapshotketen kopiëren als volledige backup.

Verplaats de werkende VM-map niet zonder plan: Fusion en controller kunnen nog naar het oude pad verwijzen. Als een andere disk nodig is, geef voortaan consequent `--root /volledig/pad/naar/nieuwe-VM-map` door. Het argument gaat om VM-opslag, niet de codemap. Doe dat vóór aanmaak en verander het niet midden in de inrichting. Geen oud VM-root opgeven om een legacy-weigering te omzeilen.

Verander exam-ready-v2 niet na examenwerk. Een extra handmatige snapshot met een andere beschrijvende naam kan werk bewaren, maar wordt niet door controller-reset als startpunt gebruikt.

## 19. Problemen oplossen

### Bestand fusion-lab.py niet gevonden

Je staat waarschijnlijk in een .vmwarevm-map of de verkeerde codemap. MAC:

```bash
pwd
cd "$HOME/Studies/RHCSA/labs/RHCSA-Fusion-v2"
ls RHCSA-Lab-Scripts/fusion-lab.py
```

Gebruik het nieuwe pad; de oude repository is niet de nieuwe codeboom.

### Provide a local DVD ISO

MAC:

```bash
printf '%s\n' "$ISO"
ls -lh "$ISO"
```

Lege variabele? Opnieuw instellen. Verkeerd pad? Werkelijk bestand zoeken. Naam x86_64/boot/minimal? Juiste aarch64-DVD gebruiken. ISO niet opnieuw hernoemen om de check te passeren.

### Existing bundle / unknown golden preserved

Status en state bekijken. Een ready v2-gast blijft behouden. Een onbekende/legacy-bundle wordt niet automatisch gewist. Geef de controller niet de oude VM-map als nieuwe root.

Een onderbroken clone zonder state blijft onbekend. Schakel haar uit, controleer vmrun list, sluit Fusion-toegang en bewaar die onvolledige bundle via Finder in een aparte quarantaine-map. Maak pas daarna opnieuw de ontbrekende clone. Verplaats geen complete werkende gast of golden. Zie HERSTEL.md.

### Locks ondanks stilstaand library-icoon

Controleer de werkelijke running list en suspendstatus. Een libraryregel toont niet de hele runtime-status. Snapshot/reset laten Fusion eigen locks beheren; de v2-controller verwijdert geen locks. Directe VMX/diskaanpassing stopt wel op locks.

1. Resume zo nodig en sluit de gast normaal af.
2. Wacht op afronding van shutdown en diskactiviteiten.
3. Sluit de toegang tot die VM in Fusion; sluit zo nodig Fusion nadat betrokken gasten normaal uit zijn.
4. Voer één controlleractie opnieuw uit.
5. Blijft Fusion zelf een lockfout geven, bewaar de exacte fout. Geen .lck handmatig wissen.

### VMware Tools niet actief / seed kan niet authenticeren

In de gastconsole:

```bash
systemctl status vmtoolsd --no-pager
rpm -q open-vm-tools
journalctl -u vmtoolsd -b --no-pager -n 60
```

Controleer bootstrap en werkelijk rootwachtwoord. Je moet de gast vóór seed als root kunnen openen. Gebruik niet al het nieuwe herstelde examenwachtwoord als de seed nog het golden-wachtwoord verwacht. Herstel geen rootwachtwoord op een reeds begonnen examen om de seed opnieuw te kunnen draaien.

### Seed onderbroken

Lees de console en exacte fase. Alleen vóór examenwerk mag je een onvoltooide seed hervatten. Kijk op Linux:

```bash
ls -l /var/lib/rhcsa-fusion/network.done /var/lib/rhcsa-fusion/fixtures.done
cat /etc/rhcsa-fusion-seeded
```

Een ontbrekend bestand kan bij een onvoltooide fase normaal zijn. Voeg zelf geen completionmarker toe om de controller te misleiden. Als de completionmarker daadwerkelijk aanwezig is en de host slechts seeded False toont, volg de synchronisatieprocedure in HERSTEL.md. Als het rootwachtwoord al onbekend is en de marker ontbreekt, is handmatig onderzoek/herstel nodig; maak geen exam-ready-v2 van een halve voorbereiding.

### Rootlogin incorrect

Controleer toetsenbordindeling, juiste VM, Caps Lock en of seed het wachtwoord bewust gewijzigd heeft. Gebruik bij de nieuwe golden het installatieaccount om `sudo passwd -S root` te controleren. P betekent dat een wachtwoord ingesteld is; L gelockt. Op bravo/charlie/foxtrot na seed is onbekend root juist bedoeld. Doe dan de relevante examenherstelopdracht.

### /sysroot bestaat niet / read-only root

Bij `rw init=/bin/bash enforcing=0` zit je in de geïnstalleerde root. Gebruik `mount -o remount,rw /`. /sysroot hoort bij een andere initramfs-route. Meng de recepten niet.

### Zwart scherm of schijnbaar hangen na passwd

Wachtwoordtypen is onzichtbaar. Na relabelstart kan diskactiviteit tijd kosten. Leg de laatste zichtbare melding vast, noteer gebruikte kernelargs en hoe je de shell beëindigde. Geen exit/Ctrl-D in PID-1-Bash. Gebruik de antwoordprocedure, normale volgende boot en controles. Een screenshot van alleen een zwart vlak identificeert geen oorzaak.

### NAT werkt niet / labpartner niet bereikbaar

Op de gast:

```bash
ip -br link
ip -br addr
ip route
nmcli -f NAME,UUID,DEVICE con show
getent hosts download.rockylinux.org
```

Match MACs. NAT moet DHCP en default-route hebben. Lab moet na de taak zijn eigen statische adres hebben en geen gateway. Controleer of de peer aan staat en haar netwerktaak gedaan is. Test eerst peer-IP, dan peer-naam, daarna service/poort. Een actieve firewall kan ping/service anders behandelen. Controleer de juiste zones; geen firewall uitschakelen als algemene oplossing.

### Repo, package of image ontbreekt

Bewaar `cat /etc/os-release`, `dnf repolist`, exacte pakket-/imageverwijzing en fout. Controleer internet, DVD-mount en architectuur. Voor Rocky/RHEL kunnen repo-/sleutelkeuzes verschillen; volg het bijbehorende antwoord. Installeer niet vooraf alle examenpakketten op golden. Een extern gewijzigde registry-tag vraagt onderzoek, geen claim dat de hele codeboom bewezen werkt.

### Disk heeft verkeerde capaciteit / al signatures

Niet formatteren om seed tevreden te stellen. Controleer node, state, lsblk, parted print free en `wipefs -n` op het bedoelde extra device. Geen `wipefs -a`, mklabel of mkfs op goed geluk. De controller probeert beschadigde chains niet automatisch te repareren. Bewaar de bundle en foutdetails.

### Snapshot already exists

Dit is behoud van je startpunt. Controleer `status --exam N`; als exam-ready-v2 bestaat, hoef je niet opnieuw snapshot te maken. Als je startpunt onbetrouwbaar blijkt, overschrijf het niet stilzwijgend: bewaar de hele betrokken omgeving en bouw een nieuwe schone start onder een afzonderlijke VM-root.

### Verify geeft FAIL / ERROR / MANUAL

FAIL: gecontroleerd bewijs voldoet niet. ERROR: controle kon niet goed worden uitgevoerd. MANUAL: lees aanvullende criteria en test ze zelf. Op een gedeeltelijk uitgevoerd examen zijn veel FAILs verwacht. Neem de relevante taak/VM/resultaten over in je logboek; gebruik geen percentage als officiële score.

## 20. Eindcontrole en logboek

### Inrichting klaar vóór examenwerk

- Oude VM’s/bron-golden behouden.
- Juiste Mac-codepad en aparte nieuwe VM-map.
- ISO gecontroleerd, nog bereikbaar op het oorspronkelijke pad.
- Nieuwe golden bootstrap succesvol, rootlogin werkt, gewone oefenaccounts geen sudo.
- Golden sealed en uitgeschakeld vóór clone-aanmaak.
- Clones unieke machine-ID’s, hostkeys en juiste MACs.
- Extra disks leeg en met voorgeschreven capaciteit vóór seed.
- Seed voor beide nodes succesvol, host seeded True en guestmarkers passend.
- Verwachte beginfouten aanwezig; nog geen antwoorden uitgevoerd.
- Beide normaal uitgeschakeld en exam-ready-v2 aanwezig.

### Na examenwerk

- Alle 35 taken van het betreffende examen afzonderlijk beoordeeld.
- Beide nodes en relevante echte gebruikers getest.
- Peer-tests voor netwerk/NFS/SSH/HTTP uitgevoerd.
- Normale reboot zonder tijdelijke herstelargs.
- Persistente configuratie na reboot opnieuw gecontroleerd.
- Checkeruitvoer en handmatige subcriteria geregistreerd.
- GAST-ACCEPTATIE.md uitgevoerd voor het gebruikte paar.
- Eigen werk veilig voordat reset wordt gebruikt.

### Logboektemplate

```text
Datum:
Mac-model / RAM:
macOS-versie:
Fusion-versie:
Code-ZIP / checksum:
ISO-pad / checksum:
Golden-route: import / nieuwe installatie
Nieuwe VM-root:
Examen / nodes:
Machine-ID per node:
SSH-hostkey-fingerprint per node:
NAT-interface / MAC / IP per node:
Lab-interface / MAC / IP per node:
Seed voltooid per node:
Snapshot per node:
Uitgevoerde taken:
FAIL / ERROR / handmatige criteria:
Rebootcontrole:
Peer-/gebruikerscontrole:
Nog te onderzoeken:
```

## Wat deze handleiding wel en niet bevestigt

De procedure sluit aan op de meegeleverde code en jouw eerder getoonde ARM/Fusion-omgeving. Lokale regressies en documentatiecontroles zijn uitgevoerd. De volledige inrichting en alle 105 opdrachten zijn niet op jouw echte gasten end-to-end uitgevoerd. Volg VALIDATIE.md en GAST-ACCEPTATIE.md om die laatste testlaag vast te leggen. Je bestaande VM’s zijn bij het schrijven van dit document niet gewijzigd.

## Bronnen en bijbehorende bestanden

De controller en gastscripts in deze ZIP bepalen de exacte commando’s, namen, guardchecks en paden in deze handleiding. Voor de platformvoorwaarden:

- [Broadcom: ARM-gasten en Fusion op Apple Silicon](https://knowledge.broadcom.com/external/article/315602/compatibility-considerations-for-arm-gue.html): gebruik arm64/aarch64 op Apple Silicon.
- [Broadcom: Fusion-netwerkopties](https://knowledge.broadcom.com/external/article?legacyId=1022264): NAT en het private netwerk hebben verschillende functies.
- [Rocky: installatie van Rocky Linux 10](https://docs.rockylinux.org/guides/installation/): installerinstellingen en rootaccount; root is standaard uitgeschakeld als je die niet expliciet instelt.
- [Rocky: ISO-typen](https://docs.rockylinux.org/latest/teams/rel_eng/image/): de volledige DVD bevat de installatiemedia voor deze opzet.

Technische bronverwijzingen voor GRUB, journald, firewalld, SELinux, NFS en containers staan in BRONNEN.md. BESTAANDE-VMS.md behandelt gerichte wijzigingen op de nieuwe golden-kopie. HERSTEL.md behandelt controller-herstel. De drie antwoorddocumenten geven de concrete examenantwoorden; CONTROLE-DEKKING.md beschrijft de graderbeperkingen.
