# Start hier — RHCSA Fusion v2

**Bijgewerkt 10 oktober 2026:** begin met [het korte uitvoerblad](ZO-VOER-JE-DE-OPDRACHTEN-UIT.md). [Controleverslag van alle 105 taken](UITVOERBAARHEIDSCONTROLE.md). Deze update verandert bestaande VM’s niet.

Voor de uitgebreide stap-voor-stapinrichting: [WERKINSTRUCTIE-MACBOOK-FUSION.md](WERKINSTRUCTIE-MACBOOK-FUSION.md).

De bedoeling: golden is de geïnstalleerde basis; twee kopieën vormen een oefenexamen. De voorbereiding maakt bewust verkeerde instellingen. Jij lost die op met de opdrachten. Antwoorden en controles helpen achteraf.

```text
Bestaande golden (blijft behouden)
        ↓ volledige kopie
Nieuwe golden in ~/RHCSA-Fusion-v2 (eenmalig voorbereiden + uitschakelen)
        ↓ volledige kopieën
Examen 1: alpha + bravo → voorbereiden → uitschakelen → exam-ready-v2
        ↓ starten en opdrachten uitvoeren
Antwoorden vergelijken → controles → normale reboot → controles vanaf andere VM
        ↓ alleen als je opnieuw wilt oefenen
Uitschakelen → reset naar exam-ready-v2 → opnieuw beginnen
```

## 1. Pak deze code uit op de Mac

Plaats de uitgepakte code bijvoorbeeld in `~/Studies/RHCSA/labs/RHCSA-Fusion-v2`.
Dat is **de code**, niet een .vmwarevm-map. De VM-map is een andere map:
`~/RHCSA-Fusion-v2`. Gebruik dezelfde naam alleen zoals deze twee volledige paden aangeven.

**Mac-terminal:**

```bash
cd ~/Studies/RHCSA/labs/RHCSA-Fusion-v2
pwd
python3 tools/validate.py
python3 RHCSA-Lab-Scripts/fusion-lab.py plan --exam 1
ISO="$HOME/Downloads/Images/Rocky-10.2-aarch64-dvd1.iso"
ls -l "$ISO"
```

Pas uitsluitend het ISO-pad aan als jouw DVD elders staat. Vereist: Apple Silicon, VMware Fusion in /Applications, Rocky/RHEL 10 aarch64 volledige DVD met BaseOS/AppStream. Controleer de gepubliceerde ISO-checksum bij de uitgever. De bestandsnaam alleen bewijst de inhoud niet.

## 2. Gebruik je bestaande golden als bron

Lees **BESTAANDE-VMS.md**. Je hoeft Rocky niet opnieuw te installeren als golden nog niet als examenmachine is gebruikt.
Schakel de bron-golden normaal uit. Gebruik de exacte .vmx-file; geen draaiende/suspended gast.

**Mac-terminal, in de nieuwe codemap:**

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py import-golden --source "$HOME/RHCSA-Fusion-jconwell/rhel10-golden.vmwarevm/rhel10-golden.vmx"
python3 RHCSA-Lab-Scripts/fusion-lab.py open-golden
```

Dit maakt een volledige kopie in `~/RHCSA-Fusion-v2`. De oude VM's blijven behouden.
Een bestaande bestemming wordt nooit overschreven. Bij onbekende half gemaakte bundles: lees HERSTEL.md; verwijder geen locks.

Alternatief voor wie geen bruikbare golden heeft, **Mac**:

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py template --iso "$ISO"
python3 RHCSA-Lab-Scripts/fusion-lab.py open-golden
```

Installeer Rocky op die nieuwe golden. Stel rootwachtwoord in, onthoud het. Geen oefenpartities op de systeemdisk. De template heeft NAT + host-only NICs en 30 GiB disk. Daarna volgen dezelfde guest-stappen hieronder.

Voor een nieuwe installatie zonder handmatige installerkeuzes: volg [AUTOMATISCHE-INSTALLATIE.md](AUTOMATISCHE-INSTALLATIE.md). Deze route stelt golden al in en gebruikt een andere VM-root; volg niet tegelijk de handmatige bootstrap hieronder.

## 3. Bereid uitsluitend de nieuwe golden voor

Kopieer `guest-golden.sh` en `guest-seal.sh` naar de **nieuwe** golden; kopiëren mag via scp naar je installatieaccount. Log daarna in via de **Fusion-console als root**. Voer netwerkvoorbereiding niet via SSH uit.
Als de gekopieerde golden geen NAT-adres heeft doordat het oude profiel aan een andere MAC/interface gebonden is, maak in de **nieuwe golden-console als root** tijdelijk een DHCP-profiel:

```bash
ip -br link
read -r -p 'NAT-interface, gematcht met mac0 van de nieuwe host-state: ' NAT_IF
nmcli con add type ethernet ifname "$NAT_IF" con-name v2-copy-nat ipv4.method auto ipv6.method disabled
nmcli con up v2-copy-nat
ip -br addr
```

De bootstrap schakelt dit tijdelijke profiel later uit. Gebruik dit alleen als het NAT-adres ontbreekt.
Een concreet kopieervoorbeeld vanaf de Mac:

```bash
scp RHCSA-Lab-Scripts/guest-golden.sh RHCSA-Lab-Scripts/guest-seal.sh siebe@NAT-IP-VAN-NIEUWE-GOLDEN:/tmp/
```

Vervang account/IP door de waarden uit de nieuwe gast (`ip -br addr`). De kopie kan door een veranderd MAC-adres eerst een nieuw DHCP-adres krijgen; lees dat in Fusion. Gebruik de daadwerkelijke accountnaam; `siebe` is alleen jouw eerder getoonde installatieaccount.

**Nieuwe golden, Fusion-console als root:**

```bash
bash /tmp/guest-golden.sh
```

Het nieuwe statebestand staat op de Mac in `~/RHCSA-Fusion-v2/rhel10-golden.vmwarevm/fusion-state.json`. Bekijk het op de Mac met `cat ~/RHCSA-Fusion-v2/rhel10-golden.vmwarevm/fusion-state.json`.
Match NAT en host-only interface met mac0/mac1 uit dit bestand. De interfacevragen gebruiken namen uit `ip -br link`.
Als installatieaccounts nog sudo mogen, volg BESTAANDE-VMS.md en voer bootstrap daarna opnieuw uit. Geen gebruikers blind verwijderen. Controleer dat oefenaccounts en oefenpakketten ontbreken; bootstrap noemt afwijkingen.

**Nieuwe golden, als root, laatste stap:**

```bash
bash /tmp/guest-seal.sh
```

Dit maakt de kopie geschikt om te klonen (nieuwe machine-ID en SSH-hostkeys bij eerste boot) en schakelt haar uit. **Start golden nu niet opnieuw vóór het maken van clones.** Als je haar toch start, voer seal opnieuw uit. De oude golden blijft beschikbaar.

## 4. Maak en bereid examen 1 voor

**Mac:**

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py create --exam 1 --iso "$ISO"
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node alpha
python3 RHCSA-Lab-Scripts/fusion-lab.py start --node bravo
```

Laat beide normaal opstarten, wacht tot VMware Tools actief is. Controleer in iedere console dat root kan inloggen met het golden-wachtwoord.

**Mac:**

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py seed --node alpha
python3 RHCSA-Lab-Scripts/fusion-lab.py seed --node bravo
```

De tool vraagt het geërfde golden-rootwachtwoord. Het wachtwoord wordt niet opgeslagen. VMware vmrun ontvangt het als procesargument voor de lokale gastauthenticatie; gebruik een labwachtwoord.
Seed raakt geen partitie-inhoud aan: hij controleert extra disks en legt instellingen/fouten aan. Op bravo wordt root bewust onbekend, graphical.target ingesteld. Alpha begint met GRUB-timeout 3 en zonder quiet. Het seed-script staat in guest-seeds; voer nooit het script van een andere VM uit.

**Iedere gast, bestaande rootconsole:**

```bash
systemctl poweroff
```

Rootconsole blijft open nadat een wachtwoord is gewijzigd. Was die console niet geopend, gebruik Fusion om de gast normaal af te sluiten; geen force power-off. Bravo hoeft niet opnieuw te booten voordat zijn snapshot is gemaakt.

**Mac, na uitschakelen van beide:**

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py snapshot --node alpha
python3 RHCSA-Lab-Scripts/fusion-lab.py snapshot --node bravo
python3 RHCSA-Lab-Scripts/fusion-lab.py status --exam 1
```

## 5. Opdrachten uitvoeren

Start alpha en bravo. Open **Examen-1-opdrachten.md**. Voer opdrachten in volgorde uit op de genoemde VM, **in Linux**, niet op de Mac.
Gebruik de Fusion-console voor rootherstel, netwerk- en bootwijzigingen. Gebruik na rootherstel een normale login en reboot. Bij `init=/bin/bash` remount je `/` en eindig je met `exec /sbin/init`; geen exit/Ctrl-D.

Leerstand: gebruik Examen-1-antwoorden.md na je eigen poging. Examenstand: houd antwoorden gesloten. Er zijn 35 volledige antwoordsecties, maar niet alle externe images/GUI's en alle gasten zijn hier live getest.

Kopieer de nieuwe codemap naar `/root/RHCSA-Fusion-v2` op elke gast (scp mag na het inrichten van SSH). Voer controles in de gast uit:

```bash
python3 /root/RHCSA-Fusion-v2/tools/verify.py --exam 1 --node alpha
```

Op bravo gebruik `--node bravo`. De wrappers zijn hetzelfde alternatief:
`bash /root/RHCSA-Fusion-v2/RHCSA-Lab-Scripts/ex1-verify.sh --node alpha`.
De checker is read-only en geeft geen officiële score. PASS gaat over één bewijscheck; MANUAL betekent aanvullende handmatige subcriteria. ERROR is geen PASS.

## 6. Opnieuw oefenen

Reset wist jouw examenwerk **binnen de gekozen nieuwe VM** tot de snapshot. Doe dit alleen wanneer je zelf opnieuw wilt beginnen; bewaar eerst gewenste bestanden.
Schakel beide gasten normaal uit. **Mac:**

```bash
python3 RHCSA-Lab-Scripts/fusion-lab.py reset --node alpha
python3 RHCSA-Lab-Scripts/fusion-lab.py reset --node bravo
```

Daarna starten. Oude `exam-ready`-snapshots worden door v2 niet gebruikt.

## Examen 2 en 3

Zelfde route met `--exam 2`: charlie + delta; `--exam 3`: echo + foxtrot. Gebruik hun eigen opdrachten/antwoorden/checkernummer. Werk met één examenpaar tegelijk.
In examen 3 is de verplichte volgorde **T33 vóór T16**; dat staat in het document. Foxtrot is na seed bewust onbootbaar totdat T1 wordt opgelost. Delta begint bewust in rescue.target.

Lees VALIDATIE.md voor wat daadwerkelijk is getest en de nog vereiste gastacceptatie. Gebruik geen upstream KVM-scripts: die zijn niet opgenomen in deze Fusion-codeboom.
