# Bestaande VM's: wat verandert er?

## Kort antwoord

Behoud servera, serverb, oude golden, alpha en bravo. Er wordt niets automatisch aangepast.
De nieuwe versie gebruikt standaard **~/RHCSA-Fusion-v2** als VM-map. De oorspronkelijke **~/RHCSA-Fusion-jconwell** wordt alleen gebruikt als expliciete bron voor een volledige golden-kopie.

| VM | Actie |
|---|---|
| servera / serverb | Geen wijziging. Blijven gewone oefengasten. |
| Oude rhel10-golden | Normaal uitschakelen voor kopiëren; geen bootstrap/seal op deze bron uitvoeren. |
| Oude alpha / bravo | Behouden voor losse oefeningen. Hun oude snapshots zijn geen bewezen v2-examenstart. |
| Nieuwe golden-kopie | Bootstrap v2, installatie-sudo opschonen, seal, uitschakelen. |
| Nieuwe alpha / bravo | Volledige clones, v2-seed, nieuwe exam-ready-v2 snapshots. |

De schoonste route zonder herinstallatie is uitgewerkt in START-HIER.md. Controleer vóór het kopiëren vrije ruimte: volledige clones gebruiken extra opslag en kunnen groeien. De nominale diskgroottes staan in plan; dunne disks verbruiken niet direct hun volle capaciteit.
Maak eventueel met Fusion op uitgeschakelde oude gasten een snapshot met een nieuwe naam `voor-v2-behouden`. Overschrijf bestaande snapshots niet. Een snapshot is geen externe backup; een kopie van de uitgeschakelde bundle kan als aparte backup worden bewaard.

## Sudo opschonen — alleen op de NIEUWE golden-kopie

Je kunt als root in de Fusion-console werken. Controleer eerst dat dit de nieuwe kopie is; kijk naar de bundlelocatie in Fusion. De oude bron blijft behouden.

```bash
hostnamectl --static
getent passwd student siebe
sudo -l -U student
sudo -l -U siebe
id student
id siebe
```

Gebruik alleen accountnamen die daadwerkelijk bestaan. Als student of jouw installatieaccount wheel-lid is, verwijder uitsluitend dat groepslidmaatschap op de kopie:

```bash
gpasswd -d student wheel
gpasswd -d siebe wheel
```

Voer een regel alleen uit als de betreffende gebruiker werkelijk lid is. Andere gewone gebruikers die sudo mogen worden door bootstrap genoemd; behandel hen afzonderlijk.

Een expliciete sudoers-regel blijft ondanks verwijderen uit wheel bestaan. Vind de relevante regels:

```bash
ls -l /etc/sudoers.d
visudo
```

Bekijk drop-ins afzonderlijk met `visudo -f /etc/sudoers.d/BESTAAND-BESTAND`. Vervang BESTAAND-BESTAND door een werkelijk gevonden naam. Verwijder alleen de grant voor het genoemde installatie-/studentaccount, bijvoorbeeld `student ALL=(ALL) NOPASSWD:ALL`. Verwijder geen andere regels of bestanden blind. Laat de standaard rootregel bestaan.

```bash
visudo -c
sudo -l -U student
sudo -l -U siebe
```

Verwacht voor gewone oefenaccounts dat zij geen sudo mogen. Root moet nog in de console kunnen inloggen met het bekende labwachtwoord. Nu bootstrap opnieuw uitvoeren; hij kan de netwerkprofielen hergebruiken.

## Als de golden-kopie al oefenpakketten bevat

Bootstrap stopt als httpd/tmux/nano/zsh of examenaccounts aanwezig zijn. Een gewerkt examen is geen schone golden. Kies een onbewerkte golden of maak een nieuwe installatie als de staat niet betrouwbaar te herstellen is.
Voor alleen een toevallig aanwezig pakket op de kopie: bekijk `dnf remove --assumeno PAKKET` en de voorgestelde dependencies. Verwijder het pas als de lijst uitsluitend wegwerp-oefensoftware raakt. Nooit op de oude bron of servera/serverb. Geen automatische massale verwijdering.

## Doorwerken op oude alpha/bravo zonder nieuwe start

Dat mag voor losse oefeningen. Als T2/T3 al correct zijn, registreer 'reeds ingesteld'; draai niet opnieuw formatterings- of useradd-stappen. Je kunt de nieuwe antwoordensleutel als naslag gebruiken, maar je oude voorbereiding is niet gelijk aan v2. De nieuwe seed mag niet op een oude of al bewerkte examengast worden uitgevoerd.
V2 weigert legacy-snapshot/reset en seed in legacy bundles. Geef de nieuwe controller niet je oude VM-map als --root om die weigering te omzeilen.

## Identiteit controleren

Voer op beide nieuwe clones uit vóór seed, noteer de waarden:

```bash
cat /etc/machine-id
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
ip -br link
```

Machine-ID's en hostkey-fingerprints moeten onderling verschillen. Interface-MACs moeten met de nieuwe host-state overeenkomen. Seed weigert een machine-ID gelijk aan de vastgelegde golden-ID. Als IDs toch gelijk zijn: stop; geen seed, geen snapshot. Controleer seal/cloneprocedure.

Er zijn tijdens het maken van deze ZIP geen VM's veranderd, opnieuw opgebouwd, afgesloten of gereset.
