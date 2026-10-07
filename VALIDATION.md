# Validatie — 5 oktober 2026

Uitgevoerd: `python3 tools/validate.py`.

- 13 regressietests slagen met lokale mock-Fusion-antwoorden en tijdelijke fictieve disks.
- Acht geleverde shellscripts en 101 Bash-opdrachtblokken slagen voor syntaxcontrole.
- Alle zes gegenereerde seed-scripts slagen ook voor Bash-syntaxcontrole.
- Examen-diskgroottes, volledige clones, unieke MACs, correcte NIC-types, NVMe-paden en seeds gecontroleerd.
- Bestaande/onbekende bundles, afwijkende eigendom, symlinks, actieve/suspended/locked VM's worden geweigerd.
- Snapshot vereist succesvolle seed; snapshot wordt niet overschreven; reset vereist een bestaande bijgehouden snapshot.
- Seed wordt pas als voltooid geregistreerd na de VM-specifieke guestinfo-marker.
- Gesimuleerde clonefout behoudt de golden. Paden met spaties worden getest.
- Actieve examendocumenten bevatten geen virt-clone/virsh-hostinstructies of oude virtio/SATA Linux-diskpaden.

De CLI-hulp van de lokaal geïnstalleerde vmrun 1.17.0 build 25689522 en vmware-vdiskmanager build 25689522 is gelezen. Clone, snapshot en reset komen in die hulp voor. Er zijn geen echte VM-operaties uitgevoerd; alleen hulpweergave was live.

Nog niet live getest: installatie vanuit DVD, exact gastOS-compatibiliteitsprofiel, bootbaarheid, NetworkManager-profileactivatie, Tools-authenticatie, guestinfo-transport, klonen/snapshots op de hypervisor en functionele uitkomsten van alle examenvragen. Mocktests leveren daarvoor geen bewijs. Een ontbrekende package of CLI-fout stopt de betreffende stap en behoudt de VM; inspecteer de console.

De oorspronkelijke examengrader is een gedeeltelijke controle. Er is geen officiële examen-scoreweging of certificeringsgarantie. Bewaarde upstream-reference-bestanden zijn historische naslag, niet de actieve platformconversie.

Installatievoorwaarden: macOS Apple Silicon, lokale aarch64 DVD ISO, werkend Fusion en een expliciet geïnstalleerde golden VM. Op de Mac worden geen Linux-beheeropdrachten uitgevoerd. Het oorspronkelijke project onder /Users/siebe/Studies/RHCSA/labs/jconwell3115 is niet gewijzigd.
