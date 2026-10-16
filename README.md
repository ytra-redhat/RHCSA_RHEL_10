# RHCSA Fusion v2

**Bijgewerkt 10 oktober 2026:** begin met [het korte uitvoerblad](ZO-VOER-JE-DE-OPDRACHTEN-UIT.md). [Controleverslag van alle 105 taken](UITVOERBAARHEIDSCONTROLE.md). Deze update verandert bestaande VM’s niet.

Herstel van de installer-zramfout: **[ZRAM-HERSTEL.md](ZRAM-HERSTEL.md)**.

Automatische nieuwe Rocky-installatie: **[AUTOMATISCHE-INSTALLATIE.md](AUTOMATISCHE-INSTALLATIE.md)**. Deze route gebruikt een aparte VM-map `~/RHCSA-Fusion-auto`.

Volledige inrichting voor jouw MacBook: **[WERKINSTRUCTIE-MACBOOK-FUSION.md](WERKINSTRUCTIE-MACBOOK-FUSION.md)** (ook als .txt meegeleverd).

Korte route: **[START-HIER.md](START-HIER.md)**.
Bestaande VM's behouden: **[BESTAANDE-VMS.md](BESTAANDE-VMS.md)**.
Fout tijdens voorbereiding: **[HERSTEL.md](HERSTEL.md)**.
Wat gecontroleerd is: **[VALIDATIE.md](VALIDATIE.md)**.

| Examen | VM's | Opdrachten | Antwoorden |
|---|---|---|---|
| 1 | alpha + bravo | [35 opdrachten](Examen-1-opdrachten.md) | [35 antwoorden](Examen-1-antwoorden.md) |
| 2 | charlie + delta | [35 opdrachten](Examen-2-opdrachten.md) | [35 antwoorden](Examen-2-antwoorden.md) |
| 3 | echo + foxtrot | [35 opdrachten](Examen-3-opdrachten.md) | [35 antwoorden](Examen-3-antwoorden.md) |

De VM-map is standaard `~/RHCSA-Fusion-v2`. De codeboom mag bijvoorbeeld in `~/Studies/RHCSA/labs/RHCSA-Fusion-v2` staan. Nooit commando's uitvoeren vanuit een .vmwarevm-map.
Geen automatische teardown. Reset bestaat uitsluitend als expliciete actie naar `exam-ready-v2`. V2 seed/reset weigert legacy bundles.

De oorspronkelijke community-opdrachten zijn herwerkt; dit is geen officiële Red Hat examenomgeving. Containers, SELinux-modules en LVM-shrink zijn aanvullende verdieping. De publicatie van deze ZIP bewijst geen volledige uitvoering op echte Rocky-gasten: de status per controlelaag staat in VALIDATIE.md.

Herkomst: https://github.com/jconwell3115/RHCSA_RHEL_10 en de lokale Fusion-aanpassing die in de audit van 8–9 oktober 2026 onderzocht is. Er is in de onderzochte lokale checkout geen expliciet LICENSE-bestand aangetroffen; deze bewerking voegt geen licentieclaim toe. Oude KVM-scripts, tokenachtige voorbeelddata en achterhaalde controller-backups zijn niet opgenomen.
