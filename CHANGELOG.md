# Wijzigingen — 9 oktober 2026

- Nieuwe, aparte codeboom en aparte standaard VM-map; oorspronkelijke bron en gasten behouden.
- 105 opdrachtsecties en 105 antwoordsecties, inclusief alle 19 eerder ontbrekende antwoorden. Opdrachten en antwoorden gescheiden.
- BLS-correcte GRUB-herbouw, één rootherstelroute met / en exec /sbin/init, normale rebootverificatie.
- Uitgangssituatie hersteld: bravo graphical; alpha timeout 3 zonder quiet; badperms in /var/tmp (geen volatile /tmp) en finance-fixtures.
- Taakconflicten gecorrigeerd: additieve sudo-grants, tijdelijke firewallvolgorde, emma-aanmaak, Apache-reparatie vóór portforward.
- Rocky signing-keykeuze, expliciete mountpoints, swaplabels/groottes/prioriteiten, juiste PE-afronding, correcte AutoFS-paden en NFS-ownership.
- Chronyd restart in plaats van HUP; logrotate laat rsyslog bestanden heropenen; journalretentie correct beschreven.
- Quadlet [Install] en volume-dependency; Nginx 1.26 image/path/command aan primaire bron gekoppeld; rootless login/linger/private auth duidelijk.
- Betrouwbare voorbeeldscripts: geen succeslog na tar-failure, exact aantal arguments, echte exitcodes, gecontroleerde tijdelijke testfilesystem.
- Hervatbare bekende host-hardwarefasen; unknown clone bewaard; atomische metadata; aparte completion/progress in seed; gerichte handshake-reconciliatie.
- Golden seal in plaats van live machine-ID-reset; unieke IDs/hostkeys vereist vóór seed. Geen blinde verwijdering van gebruikers/sudoers.
- Disk chain/capaciteit/padcontroles, VMX-backup en weigering van ongeparseerde regels; timeout, status, gedeelde operation-lock.
- Vaste diskindeling; de oude willekeurige add-disk-actie is bewust uitgeschakeld omdat opdrachten NVMe-slots en capaciteiten vastleggen.
- Read-only checker met exacte waarden, ERROR/FAIL/MANUAL, expliciete handmatige dekking van alle taken. Geen misleidende totaalscore en geen embedded verouderde graders.

audit/CORRECTIES.md koppelt elk van de 69 auditbevindingen aan de behandeling in v2. Onzekerheden waarvoor een echte gast nodig is blijven als acceptatiepunten vermeld.

## Automatische Rocky-installatie

Nieuwe install-rocky.py en AUTOMATISCHE-INSTALLATIE.md: nieuwe golden met ISO/EFI-Kickstart, vaste inrichting en controles vóór partitioneren. Geen bestaande VM overschrijven; aparte standaardroot RHCSA-Fusion-auto. Root/student zonder standaardwachtwoord, private hashmedia, offline pakketbron. Eindcontrole/seal blijft expliciet. Mediaopbouw werkelijk getest, volledige gastinstallatie nog niet.

## Zramfix — 9 oktober 2026

De echte installer meldde zram0 als TYPE=disk. De vorige guard telde dit ten onrechte als tweede installatiedisk. Installer, golden-eindcontrole, bootstrap en seed tellen nu zramN niet mee; extra echte disks blijven geweigerd. Nieuwe repair-media herbouwt uitsluitend installatiemedia voor dezelfde gestopte golden, bewaart hashes/MACs/VMDK/oude ISO en weigert draaiende of reeds naar OS-boot omgeschakelde gasten. Acht regressies toegevoegd voor de gemelde layout, extra hardwaredisks en behoud/weigering bij mediaherstel.

## Sudo-controle 9 oktober 2026

Root-query sudo -l kan bij een geweigerde gebruiker status 0 geven. Golden-controles accepteren nu uitsluitend de expliciete Engelstalige weigering; fouten en verleende rechten stoppen de voorbereiding. Vijf regressietests toegevoegd.

Golden-seal maakt de ontbrekende dbus-map aan en overschrijft een opgeslagen machine-id niet met een lege waarde bij herstart na een onderbroken procedure.

## 2026-10-10 — uitvoerbaarheidscontrole

Alle 105 opdracht-/antwoordsecties herlezen en beginvoorwaarden toegevoegd. Netwerkprofielen zonder UUID-invoer, VM-blokken en herstartstappen gesplitst; afgebroken commando’s, umask/Apache-interactie en overige concrete fouten hersteld. Nieuwe lokale regressietests; geen volledige guest-acceptatie geclaimd. Zie UITVOERBAARHEIDSCONTROLE.md.
