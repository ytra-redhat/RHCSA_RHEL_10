# Zo voer je de opdrachten uit

1. Open het opdrachtbestand van het gekozen examen. Begin bij T1. Examen 3 heeft één afwijking: voer T33 vóór T16 uit en ga daarna verder met T17.
2. Kijk bij elke taak naar **VM** en **Beginvoorwaarde**. Alpha/bravo zijn examen 1; charlie/delta examen 2; echo/foxtrot examen 3. De golden is uitsluitend een installatiesjabloon: daar voer je geen examenopdrachten uit.
3. Alle systeemcommando's gaan in de **Linux-console van die VM als root**. Je Mac-terminal gebruik je alleen voor de installatie/controller. Een blok dat alice/emma vermeldt voer je uit na een echte login als die gebruiker.
4. Kopieer één Bash-blok tegelijk. Bij een fout stop je vóór de volgende wijziging. Sommige tests horen te mislukken: alleen waar dit expliciet vermeld is, geldt die fout als verwachte uitkomst.
5. Bestandsinhoud (`ini`, `sudoers`, `text`) hoort in het genoemde bestand of programma, niet in Bash. Bij `vi`: `i` om te typen, Esc en `:wq` om te bewaren. Bij `visudo` moet de syntaxcontrole slagen. `EOF`-blokken schrijf je als volledig Bash-blok, inclusief de afsluitende regel `EOF`.
6. `reboot` beëindigt je sessie. Log opnieuw in en gebruik het daaropvolgende blok. Shellvariabelen blijven niet bewaard na herstart of een nieuwe login.
7. Een `read -r -p 'vraag' NAAM` kopieer je letterlijk, inclusief `NAAM`. Daarna verschijnt de vraag: pas dan typ je de gevraagde waarde en druk je Enter. Zet nooit een UUID of getal op de plaats van `NAAM`.
8. Bij diskopdrachten: `/dev/nvme0n1` is altijd de systeemschijf. Formatteringscommando's gaan uitsluitend naar de extra schijf die de taak noemt. Controleer `lsblk -f` en de gegeven beginstand voordat je formatteert. Een al ingerichte schijf is geen lege beginstand.
9. Bij herhaling: inspecteer bestaande gebruikers, profielen, fstab-regels en SELinux-regels. Voeg geen duplicaten toe en formatteer geen reeds gebruikte schijf. Een examenreset is een aparte actie; de antwoorden zijn geen resetscript.

## Netwerk: twee kaarten, twee profielen

| Begrip | Functie | Voorbeeld bij jouw alpha |
|---|---|---|
| Interface | Linux-netwerkkaart | enp2s0 en enp3s0 |
| fusion-nat | MAC-gebonden instellingen voor NAT/internet, DHCP | enp2s0, 172.16.63.148 op jouw screenshot |
| fusion-lab | MAC-gebonden instellingen voor host-only, aanvankelijk geen IP | enp3s0 op jouw screenshot |
| lab-static | Nieuwe profielnaam na T4, examen 1 en 2 | dezelfde host-only kaart |
| lab3-static | Nieuwe profielnaam na T15, examen 3 | dezelfde host-only kaart |

Interfacenamen en DHCP-adressen kunnen veranderen. De antwoorden selecteren het bestaande labprofiel op naam en wijzigen het via zijn UUID. De MAC-binding houdt het profiel bij de juiste kaart. Als je profielen zelf hebt hernoemd, stop bij de gemelde afwijking: maak niet nog een profiel op een willekeurige kaart.

## Beginstand en bewijs

Een ingesteld rootwachtwoord is normaal: bij de herstelopdracht is het **onbekend gemaakt**, niet verwijderd. De golden heeft juist een bekend installatie-wachtwoord. Een standaardtarget dat al gelijk is aan het doel betekent dat die taak al opgelost is of de examenbeginstand afwijkt. Controleer dit vóór oefenen; herinstalleren is hiervoor niet nodig.

De ZIP is statisch en met lokale regressietests gecontroleerd. De volledige 105 opdrachten zijn niet achtereenvolgens op jouw zes VM's uitgevoerd. Externe beschikbaarheid (Flatpak, pakketgroepen, containerimages), GUI en hardwareopties zijn afzonderlijke voorwaarden. Een niet beschikbare voorwaarde is **niet uitgevoerd**, geen geslaagd resultaat. Zie UITVOERBAARHEIDSCONTROLE.md.
