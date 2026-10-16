# Rocky automatisch installeren op jouw MacBook

Deze route vervangt de handmatige installerkeuzes uit hoofdstuk 9 van WERKINSTRUCTIE-MACBOOK-FUSION.md. Ze maakt een **nieuwe** golden in `~/RHCSA-Fusion-auto`. Je huidige VM’s blijven behouden. Een bestaande golden op de bestemming wordt geweigerd; dit script herinstalleert geen bestaande VM.

## Wat automatisch gaat

- De echte ISO-inhoud controleren: Rocky Linux 10, aarch64, BaseOS en AppStream.
- Alle vereiste basispakketten controleren op de DVD.
- Een aparte installatie-ISO met Kickstart maken; de originele DVD blijft intact.
- Automatische boot instellen in zowel de ISO-GRUB als de ingebedde EFI-GRUB.
- Een nieuwe 30 GiB golden met twee NICs maken en de installatie starten.
- Installerkeuzes vastleggen: minimale basis, US-toetsenbord, Europe/Amsterdam, GPT/EFI, XFS/LVM, 2 GiB swap, root en student, SELinux Enforcing en SSH/firewall/Tools.
- NAT/LAB-profielen aan de juiste MACs binden. Student krijgt geen sudo.
- Na geslaagde installatie de gast uitschakelen.

Root- en studentwachtwoorden kies je zelf, elk minimaal 12 tekens. Het script vraagt beide tweemaal. Er zijn geen vaste standaardwachtwoorden. Alleen salted SHA-512-hashes worden in de installatie-ISO opgenomen. Die ISO en tijdelijke installatiebestanden zijn privé; deel ze niet en zet ze niet in Git. Het script geeft geen wachtwoord als procesargument aan OpenSSL.

**Afgebroken met zram0 plus nvme0n1 en een pre-fout op regel 4?** Volg [ZRAM-HERSTEL.md](ZRAM-HERSTEL.md). Daar staat hoe je dezelfde golden en wachtwoorden behoudt met repair-media.

## 1. Eenmalige controle — MAC

Pak de nieuwste code-ZIP uit in de codemap, niet in een VM-bundle. Bewaar eerdere eigen codewijzigingen afzonderlijk. Open Terminal:

```bash
cd "$HOME/Studies/RHCSA/labs/RHCSA-Fusion-v2"
python3 tools/validate.py
command -v xorriso mcopy mdir openssl
```

Op jouw Mac zijn deze hulpmiddelen tijdens de ontwikkeling aangetroffen. Als xorriso/mcopy/mdir ontbreken en je Homebrew al gebruikt:

```bash
brew install xorriso mtools
```

De controller vereist Apple Silicon en Fusion in `/Applications/VMware Fusion.app`. De uitgebreide handleiding beschrijft die controles. De automatische installatie heeft geen tijdelijke HTTP-server, handmatige GRUB-argumenten of internet nodig voor de pakketten: de volledige DVD bevat de installatiemedia. Later examenwerk kan wel internet nodig hebben.

## 2. Paden — MAC

```bash
ISO="$HOME/Downloads/Images/Rocky-10.2-aarch64-dvd1.iso"
VMROOT="$HOME/RHCSA-Fusion-auto"
ls -lh "$ISO"
shasum -a 256 "$ISO"
df -h "$HOME"
```

Vergelijk de ISO-checksum met de officiële checksum voor jouw bestand. Deze naam is jouw eerder opgegeven bestand, geen claim over de nieuwste release. De automatische installer controleert daarnaast .treeinfo en pakketbestanden.

Voor de aangepaste ISO is tijdelijk ongeveer één extra DVD-grootte plus 1 GiB ruimte nodig, naast golden en toekomstige clones. Bij jouw DVD gaat het om circa 10 GiB extra mediaopslag. De ISO zit niet in de ZIP; zij wordt lokaal gemaakt met jouw eigen hashes en unieke VM-MACs.

Laat VMROOT op een nieuwe, aparte locatie staan. Alle volgende controlleracties moeten **dezelfde --root** krijgen. Zonder --root zou de gewone controller de andere standaardmap `~/RHCSA-Fusion-v2` gebruiken.

## 3. Installatie starten — MAC

```bash
python3 RHCSA-Lab-Scripts/install-rocky.py install --iso "$ISO" --root "$VMROOT"
```

1. Geef het gekozen rootwachtwoord tweemaal.
2. Geef het gekozen studentwachtwoord tweemaal.
3. Wacht op het maken en controleren van de aangepaste DVD.
4. Fusion opent de nieuwe golden. De automatische installatiemenu-entry start na vijf seconden.
5. Laat de installatie lopen. Er zijn geen normale disk-/software-/accountkeuzes meer nodig.
6. Wacht tot de gast vanzelf uitschakelt.

**Niet vóór dat uitschakelen door naar stap 4.** Als de installer stopt met een fout, bewaar de consolemelding. In de installer staan pre-controles in `/tmp/rhcsa-auto-pre.log`; post-controles komen op de geïnstalleerde root in `/root/rhcsa-auto-post.log`. Een uitgeschakelde VM alleen bewijst niet dat alle controles geslaagd zijn; de afsluitstap hieronder controleert de installatie-marker.

Je kunt alleen de voorbereiding uitvoeren met `--prepare-only`. Start daarna dezelfde voorbereide installer met:

```bash
python3 RHCSA-Lab-Scripts/install-rocky.py start --root "$VMROOT"
```

Gebruik dat startcommando niet nadat de OS-installatie al voltooid is. Stap 4 ontkoppelt juist de automatische DVD.

## 4. Eén keer van de geïnstalleerde disk booten — MAC

Na automatische power-off:

```bash
python3 RHCSA-Lab-Scripts/install-rocky.py boot --root "$VMROOT"
```

Dit vereist een uitgeschakelde gast, stelt HDD-boot in, verwijst de CD/DVD terug naar de originele ISO en verbreekt de CD/DVD-verbinding bij deze boot. Hierdoor start de geïnstalleerde Rocky, niet opnieuw de automatische installer.

De installatie-ISO is alleen voor deze ene golden gemaakt. Gebruik haar niet voor examenclones. Bij create geef je altijd de **originele** ISO uit `$ISO` door.

## 5. Eindcontrole en seal — LINUX ROOT in de NIEUWE Fusion-console

Log in als root met het wachtwoord dat je bij stap 3 gekozen hebt. Controleer:

```bash
cat /etc/os-release
cat /etc/rhcsa-auto-installed
passwd -S root
getenforce
ip -br addr
nmcli -f NAME,UUID,DEVICE con show
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
systemctl is-active vmtoolsd
```

Verwacht Rocky 10 aarch64, een installatie-ID, rootstatus P, Enforcing, NAT-DHCP, fusion-nat/fusion-lab en één systeemdisk. Het US-toetsenbord is bewust vastgelegd; bij wachtwoordinvoer worden geen tekens getoond. De installatie heeft geen siebe-account aangemaakt; student is de gewone gastgebruiker zonder sudo. Je Mac-account blijft uiteraard hetzelfde.

Laat nu de meegeïnstalleerde eindcontrole uitvoeren en golden uitschakelen voor cloning:

```bash
bash /root/rhcsa-finish-golden.sh
```

Dit controleert installatiemarker, architectuur, SELinux, één disk, rootstatus, student-sudo en actieve services. Daarna worden SSH-hostkeys gegarandeerd aangemaakt, timesync uitgeschakeld en seal uitgevoerd. Bij een controlefout stopt het script; golden wordt dan niet als goedgekeurde basis sealed.

Verwacht: golden gaat uit. **Niet opnieuw starten vóór cloning.** De handmatige guest-golden.sh-bootstrap en sudo-opschoning zijn voor deze nieuwe automatische route niet meer nodig; die instellingen zijn al in Kickstart vastgelegd. Seal blijft een expliciete laatste stap zodat je eerst rootlogin en console kunt controleren.

## 6. Examen 1 maken — MAC

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py create --exam 1 --iso "$ISO" --root "$VMROOT"
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node alpha --root "$VMROOT"
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node bravo --root "$VMROOT"
```

Open beide Linux-consoles en log als root in met het gekozen golden-wachtwoord. Houd de consoles open. Controleer unieke machine-ID’s, SSH-hostkeys en extra disks zoals in hoofdstuk 13 van de uitgebreide handleiding.

MAC:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py seed --node alpha --root "$VMROOT"
python3 RHCSA-Lab-Scripts/fusion-lab.py seed --node bravo --root "$VMROOT"
```

In beide open Linux-rootconsoles na geslaagde seed:

```bash
systemctl poweroff
```

MAC, nadat beide werkelijk uit zijn:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py snapshot --node alpha --root "$VMROOT"
python3 RHCSA-Lab-Scripts/fusion-lab.py snapshot --node bravo --root "$VMROOT"
python3 RHCSA-Lab-Scripts/fusion-lab.py status --exam 1 --root "$VMROOT"
```

Gebruik vervolgens de opdrachten/antwoorden en de uitgebreide handleiding. Let op: ieder Mac-controllercommando in die handleiding krijgt bij deze route aanvullend `--root "$VMROOT"`. Linux-commando’s veranderen daardoor niet.

## 7. Examen 2 en 3

Golden moet sealed en uit zijn. Met dezelfde originele ISO en dezelfde VMROOT:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py create --exam 2 --iso "$ISO" --root "$VMROOT"
python3 RHCSA-Lab-Scripts/fusion-lab.py create --exam 3 --iso "$ISO" --root "$VMROOT"
```

Daarna per paar start → rootconsoles openen → identiteiten controleren → seed → normale power-off → snapshots. Gebruik voor examen 2 charlie/delta; voor examen 3 echo/foxtrot. Volg hoofdstuk 16/17 en voeg bij ieder Mac-controllercommando dezelfde --root toe. Werk met één paar tegelijk.

## 8. Nieuwe Terminal-sessie

Variabelen zijn niet permanent. Stel ze iedere nieuwe sessie opnieuw in:

```bash
cd "$HOME/Studies/RHCSA/labs/RHCSA-Fusion-v2"
ISO="$HOME/Downloads/Images/Rocky-10.2-aarch64-dvd1.iso"
VMROOT="$HOME/RHCSA-Fusion-auto"
python3 RHCSA-Lab-Scripts/fusion-lab.py status --root "$VMROOT"
```

State van de automatische golden staat op de Mac in `~/RHCSA-Fusion-auto/rhel10-golden.vmwarevm/fusion-state.json`. Media-controles staan in `~/RHCSA-Fusion-auto/auto-install/media-check.json`.

## Beveiliging tegen verkeerde inrichting

Vóór partitioneren verlangt Kickstart ARM/EFI, precies één 30 GiB NVMe-disk zonder signatures/partities, precies twee NICs en de twee unieke verwachte MACs. De diskcommando’s zijn beperkt tot nvme0n1. Een herhaalde boot van de automatische DVD op een al geïnstalleerde disk hoort daarom vóór wissen te stoppen. Die guards zijn aanvullende bescherming, geen toestemming om de ISO elders te gebruiken of fouten te negeren.

De host maakt alleen een nieuwe golden. De ISO wordt niet op bestaande bundles aangesloten. Onbekende of bestaande bestemmingen worden behouden. Een mislukte poging wordt niet blind hervat: bewaar de foutdetails en de onvolledige map. Begin na onderzoek zo nodig in een andere lege VMROOT. Verwijder geen bestaande VM of lockfiles.

## Wat daadwerkelijk gecontroleerd is

De aangepaste mediaopbouw is werkelijk uitgevoerd met jouw aanwezige Rocky-10.2-aarch64-dvd1.iso. De uitvoer heeft een bootbare UEFI-entry, dezelfde automatische GRUB-configuratie op beide plekken, de Kickstart en de vereiste pakketten. Zie validation-evidence/auto-media-test.json. De test-ISO bevat alleen fictieve testhashes en wordt niet meegeleverd of op een VM gestart.

Volledige installatie/boot/seal op een echte nieuwe VM is nog niet uitgevoerd. De lokale tests en het Kickstart-schema zijn geen bewijs van een geslaagde gastinstallatie; de console-/marker-/servicecontroles hierboven sluiten die laag voor jouw uitvoering.

[Red Hat: Kickstart-installaties starten](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/automatically_installing_rhel/starting-kickstart-installations), [Red Hat: Kickstart-commando’s](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/automatically_installing_rhel/kickstart-commands-and-options-reference), [GNU xorriso: bootinstellingen behouden bij ISO-aanpassing](https://www.gnu.org/software/xorriso/man_1_xorriso.html).
