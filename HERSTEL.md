# Gerichte herstelstappen

## Fout na de tweede clone

Een complete eerste node blijft behouden. Herhaal create met hetzelfde examen/ISO: ontbrekende nodes worden gemaakt, bekende v2-hardwarefasen hervat. Een ready node wordt niet gewist.
Een half gemaakte clone zonder ownership/state wordt nooit automatisch geadopteerd. Controleer status en Fusion-running list. Schakel betrokken gasten normaal uit. Bewaar die onvolledige bundle door hem in Finder naar een aparte quarantaine-map te verplaatsen, nadat Fusion hem niet meer gebruikt. De bestemming wordt daardoor vrij voor create. Verplaats niet een complete VM of golden. Verwijder niets en verwijder geen lockfiles.

## Diskmanager-fout

Hardwarefase blijft in fusion-state.json. Herhaling valideert bestaande disk chain en capaciteit; er wordt niet blind opnieuw een disk gemaakt. Bij verkeerde capaciteit of kapotte chain stopt het programma. Bewaar de bundle; inspecteer exacte fout. Geen -R/-F-repair op een onbekende disk.

## Seed-fout

Lees de Fusion-console. Controleer `/var/lib/rhcsa-fusion/network.done` en `fixtures.done`. Een fase wordt alleen na succes afgevinkt. Herhaling voert onvoltooide fasen opnieuw uit; dit mag uitsluitend vóór examenwerk. De extra disks moeten nog leeg zijn.
Als `/etc/rhcsa-fusion-seeded` bestaat maar host seeded=False is, is de gastvoorbereiding voltooid. In de rootconsole publiceer de marker zonder instellingen te veranderen:

```bash
vmtoolsd --cmd "info-set guestinfo.rhcsa_seed $(cat /etc/rhcsa-fusion-seeded)"
```

Voer daarna op de Mac seed opnieuw uit; een overeenkomende guestinfo-marker synchroniseert alleen hostmetadata, zonder wachtwoordvraag of nieuwe seed.
Als het rootwachtwoord al onbekend is en de laatste markerstap mislukte: gebruik de rootherstelprocedure, onderzoek de marker, publiceer pas na bevestiging van voltooiing. Voor een echt schone examenoefening moet daarna de root-onbekend-uitgangssituatie opnieuw gecontroleerd worden; maak geen exam-ready-v2 op een half herstelde gast.

## Locks / suspend

Status leest de echte vmrun-running list. Een library-icoon is geen bewijs van uitschakelen. Suspend is geen power-off. Sluit de gast normaal af.
Voor snapshot/reset beheert Fusion eigen locks; de controller verwijdert ze niet. Voor directe VMX/diskwijziging zijn locks een stopreden: sluit Fusion-toegang tot die uitgeschakelde VM. Als de API toch een lockfout meldt, bewaar de foutmelding; verwijder geen locks handmatig.

## Zwart scherm na rootherstel

`passwd` toont geen getypte tekens. Wacht op succesmelding. In de init=/bin/bash-shell geen exit/Ctrl-D: PID 1 moet blijven bestaan. Na touch /.autorelabel en sync gebruikt de procedure exec /sbin/init.
Herlabeling kan tijd kosten en een reboot veroorzaken. Een laatste schermmelding, niet alleen 'hangt', is nodig voor diagnose. Herstart niet herhaaldelijk tijdens actieve relabeling. Normaal opnieuw booten zonder tijdelijke GRUB-args; getenforce en /proc/cmdline controleren.
