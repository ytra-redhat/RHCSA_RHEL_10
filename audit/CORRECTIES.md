# Afhandeling van alle 69 auditbevindingen

Aangepast betekent code/tekst behandeld; geen claim dat elk gastresultaat live bewezen is. Zie VALIDATIE.md en GAST-ACCEPTATIE.md. Historische bestanden zijn uitgesloten in plaats van als actief alternatief gerepareerd.

## C01 — Een half aangemaakt examenpaar kan niet worden hervat

Create behoudt ready nodes en maakt de ontbrekende node; test_second_clone_resume.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## C02 — Aanmaken heeft geen betrouwbare herstelstaat

Atomische fasemetadata; bekende hardware/import-config hervatten; unknown bundles bewaren. Add-disk uitgeschakeld. Template/clone-failure recovery in HERSTEL.md.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## C03 — Seedmarker wordt te vroeg gezet

network/fixtures checkpoints, completion na chpasswd, handshake-reconciliatie en marker-republish. Root-password laatste fase kan handmatig herstel vereisen; niet blind reseeden.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## C04 — Unieke machine-ID is niet bewezen

Nieuwe golden-copy seal wist IDs/hostkeys vóór clone. Seed controleert sealrecords/verschillende golden-ID en fingerprint. Onderlinge clone-ID/hostkeyvergelijking in gastacceptatie blijft verplicht.

Status: LOKAAL + GASTACCEPTATIE OPEN.

## C05 — Verwijderen van wheel maakt student niet noodzakelijk niet-sudo

Bootstrap controleert student en andere niet-root installatieaccounts met sudo -l; stopt en noemt account. Alleen gerichte handmatige grants verwijderen op de nieuwe kopie.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## C06 — Golden-bootstrap kan zijn eigen SSH-verbinding verbreken

SSH_CONNECTION guard; vervangende profielen vóór uitschakelen van installerprofielen. Alleen Fusion-console.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## C07 — Golden garandeert niet alle gebruikte hulpmiddelen

Uitgebreide infrastructuurpakketlijst; httpd/podman/skopeo/Flatpak expliciet waar nodig. DNS/DVD/ARM availability blijft guest preflight.

Status: LOKAAL + GASTACCEPTATIE OPEN.

## C08 — VMX-parser gooit onbekende regels weg

Onbekende VMX-regel/duplicaat geweigerd vóór schrijven; VMX-backup vóór directe edit.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## C09 — Ownership en diskcontrole zijn minder streng dan geclaimd

MAC/ID/schema-layout, state-symlink, controllers, VMDK-path/chain/capaciteit en gastdiskaantal/capaciteit controleren. Chain check zonder repair.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## C10 — CLI mist status en diagnostiek

Status, next-step, timeouts/redactie; --root voor/na action; wrapper genoemd create, geen teardown.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## C11 — Fusion-tijdsynchronisatie kan chrony-oefeningen beïnvloeden

Periodieke VMware time sync uit; guest-toolbox uitschakelen. Chrony selected-source controleren; hypervisor-events en live guest behaviour niet gemeten.

Status: LOKAAL + GASTACCEPTATIE OPEN.

## C12 — Eerdere lockfout is aangepast, maar de tests missen die regressie

Snapshot/reset laten Fusion locks beheren; directe edits blijven poweroff/unlocked. Lockfixture en running/suspended-negatieve tests.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## C13 — Netwerkhulp kan niet opnieuw worden gebruikt

Netwerkhelper op expliciet geselecteerde UUID, herhaalbaar na profielrename, behoudt zone.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A01 — bravo begint met verkeerde boot target

Bravo seed graphical.target; alpha GRUB beginwaarden niet reeds opgelost.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A02 — Vijf antwoordsecties ontbreken in examen 1

Examen 1 alle 35 antwoorden; ontbrekende secties en hostname/hosts/Apache-listener ingevuld.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A03 — Veertien antwoordsecties ontbreken in examen 2

Examen 2 alle 35 antwoorden; scripts, services, users/ACLs/transfers/mounts en timers aangevuld.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A04 — GRUB-antwoorden passen kernelargs niet betrouwbaar toe

BLS --update-bls-cmdline bij wijzigingen via GRUB_CMDLINE_LINUX; grubby route afzonderlijk.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A05 — Firewallvragen spreken zichzelf tegen

Permanente reload vóór tijdelijke regel; runtime expiry/reload zichtbaar; containerpoort apart permanent.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A06 — Sudo-eisen voor alice zijn onderling onverenigbaar

Alice-grants expliciet additief; onmogelijk only-eis verwijderd.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A07 — login.defs is geen betrouwbare PAM-wachtwoordlengtepolicy

pwquality drop-in en actieve PAM-chain; gewone gebruiker test; carol nologin/age onderscheiden.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A08 — Examen 1 ISO-mountpoint wordt niet aangemaakt

Mountpoints vooraf, fstab gericht testen/reload.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A09 — Gevraagde swaplabel ontbreekt in antwoord

mkswap -L EXTRASWAP; device en priority samen controleren; totale swap inclusief oorspronkelijk device.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A10 — LVM-size in vraag en verwachting is onmogelijk met deze PE-grootte

LV-vraag/antwoord 512 MiB (32 extents ×16); numerieke checks.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A11 — pvmove verandert striping niet automatisch naar linear

Geen automatic-linear claim; echte segtype/stripes/devices opnemen en data-integriteit guest-testen.

Status: LOKAAL + GASTACCEPTATIE OPEN.

## A12 — NFS-writevraag heeft geen schrijfbare uitgangstoestand

Bewust all_squash UID1500 voor gedeelde labwrites; echte clientwrite. Team NFS gedeelde research UID/GID; geen onbedoelde rootrechten.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A13 — showmount is geen geldige doorslaggevende NFSv4-only test

NFSv4 exportfs/versions en daadwerkelijke clientmount; geen beslissend showmount.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A14 — AutoFS-home-oefeningen zijn niet volledig ingericht

Expliciete users/homes, UID/GID, labels, use_nfs_home_dirs, hard mounts, login/write. T23 emma-homekeys behouden.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A15 — Permission-repair heeft ontbrekende objecten en groep

Persistente badperms-fixture /var/tmp en finance-fixtures; gina:ops; SUID-script beperking beschreven.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A16 — chronyd HUP-theorie is onjuist

Chronyd restart; HUP-reload claim verwijderd.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A17 — Reinstall garandeert geen herstel van gewijzigde nanorc

nanorc backup, gerichte verwijdering, reinstall en rpm -V; noreplace beschreven.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A18 — Rocky-antwoorden gebruiken een Red Hat-media-key

Distro signing key expliciet kiezen/importeren en DVD-package signature verifiëren; geen verkeerd RedHat-keypad.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A19 — DNF- en Flatpak-oefeningen hebben onnodige of ontbrekende voorwaarden

DNF priority direct, Flatpak --system, ARM app preflight, GUI-run optioneel, RPM dependencies via dnf.

Status: LOKAAL + GASTACCEPTATIE OPEN.

## A20 — Logrotate mist het heropenen van rsyslog-output

Logrotate postrotate HUP rsyslog, nieuwe logger-events na rotatie en rsyslog configcheck.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A21 — TuneD-theorie is te algemeen voor deze minimal VM

Geen generieke ppd claim; tuned-ppd alleen indien aanwezig; cpufreq N/A op niet-ondersteunende gast.

Status: LOKAAL + GASTACCEPTATIE OPEN.

## A22 — at-jobs schrijven als de submitter

Rootconsole prelude, afzonderlijke user logins; root at jobs en redirections correct.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A23 — Backupscripts kunnen succes melden na falen

Exitchecks/temporary archive/atomic publish; falende tar houdt oude backups en logt FAILED; useradd fouten stoppen.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A24 — syscheck wijkt af van vraag en ARM-output kan leeg zijn

Exact één syscheck argument; platform-neutrale lscpu; vier goede/ongeldige paden functioneel getest.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A25 — Quadlet-enable is onjuist

Geen enable generated Quadlet; [Install], stop/remove eerdere container, echte usermanager en linger, peer/reboottests.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A26 — Quadlet-volume is niet gekoppeld aan de containerunit

Quadlet Volume=emma-nginx.volume; helper UID0/relabel/chown; normal user timer/service. Nginx-126/html subdir/foreground command aan primaire bron gecorrigeerd.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A27 — Apache-opdracht komt vóór reparatie van dezelfde gebroken service

Expliciete taakvolgorde T33 vóór T16.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A28 — Task 8 kan Task 11 al blokkeren

Task 8 gebruikt UID3100 en maakt geen emma; Task 11 doet skeleton-useraanmaak.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A29 — UID-regex matcht ook de GID

Regex verankert UID-veld; IPv4-octettenfilter; negatieve UID/GID-fixture.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A30 — Home-verplaatsing mist parent, labels en inlogvoorwaarden

Parent/mapping voor verhuisde homes, -m bij useradd, expliciete labwachtwoorden en echte logincheck.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A31 — systemctl show gebruikt de verkeerde property en laadt sshd niet opnieuw

RestartSec directive behouden; show RestartUSec; restart sshd na daemon-reload.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A32 — Swap-vervanging hardcodeert RHEL-VG op Rocky

Echt oude swapdevice kiezen; alleen activatie verwijderen en LV behouden, geen hardcoded rhel-swap/lvremove.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A33 — AutoFS-antwoord mount op verkeerd pad

Master /net en mapkey team; werkelijk /net/team.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A34 — Journalretentie is geen harde totale cap

Storage=persistent, flush/rotate/vacuum, retentie geen exacte quota.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A35 — Cron vraagt een script dat nergens wordt gemaakt

labreport.sh gemaakt/executable, usertest en crond; checker active cronregel en exact at allowlist.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A36 — diskwatch test niet alle gevraagde paden

Exact findmnt --mountpoint; vier diskwatch exitpaden met mocktools getest, gasttest met wegwerp-tmpfs.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A37 — userreport telt niet noodzakelijk geldige login-shells

Login shell executable + /etc/shells met nologin/false uitgesloten; primary-groupinterpretatie beschreven.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A38 — SELinux-denialgenerator en audit2allow-invoer zijn onbetrouwbaar

Synthetisch 0644-bestand, explicit chcon, AVC-testperiode/procesfilter en .te-inspectie.

Status: LOKAAL + GASTACCEPTATIE OPEN.

## A39 — SELinux-diagnose mist dependencies en gefaseerde test

Audit tools preflight; eerst port, daarna request/filedenial; reset-failed; nieuwe audit-window.

Status: LOKAAL + GASTACCEPTATIE OPEN.

## A40 — Auto-update en rootless volume vereisen extra verificatie

Publieke/private registry gescheiden, persistent authfile/auto-update drop-in, helper :Z, rootless volume perms; ARM/runtime nog guestacceptatie.

Status: LOKAAL + GASTACCEPTATIE OPEN.

## A41 — Netwerkantwoord stelt peer en effectieve resolutie niet volledig in

Foxtrot static peer toegevoegd, echte NSS hosts-regel gekopieerd; cp/mv cross-filesystem nuance.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A42 — Find/archive-antwoorden slaan enkele bewijsstappen over

5MiB bytes exact, leeftijdseenheid duidelijk, copy --parents, compressie-uitkomst gemeten.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A43 — Hersteltekst en rebootverificatie zijn verwarrend

Eén init=/bin/bash route, geen Ctrl-D/exit, / remount, relabel, normale reboot en runtimechecks.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## A44 — Officiële examendekking en scores worden nog onjuist gesuggereerd

Geen officiële score/doelaantallen; objective scope/verdieping consistent, eigen studieopdrachten.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## G01 — Runtime-checks bewijzen geen permanente firewallregels

Runtime én permanent exact getokeniseerd; peer checks expliciet handmatig.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## G02 — Adres- en getalchecks geven foutpositieven

JSON exact adressen, device+priority samen, numerieke LVM bytes, negatieve fixtures.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## G03 — Geldige syntax betekent geen correcte sudo-policy

Geen volledige taak-PASS uit visudo/text; alle sudo/ACL/umask/timer-subcriteria expliciet MANUAL.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## G04 — De grader wijzigt zelf het beoordeelde systeem

Read-only failed-unit/findmnt checks; grader voert geen mount -a of herstel uit.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## G05 — Examen 3 drop-incheck zoekt verkeerde property

Effectieve Restart/RestartUSec/Description; geen verplicht override-filename.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## G06 — semodule-check verwacht onjuiste volledige regel

Exact module naamveld, versievelden toegestaan.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## G07 — Bind-sourcecheck matcht de verkeerde findmnt-weergave

Exact target en stat device:inode van payload door beide paden, onafhankelijk van aparte /srv-filesystem.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## G08 — Tekstchecks laten niet-werkende of te ruime jobs door

Exact at allowlist, actieve cronentry, toolfouten ERROR. Onvolledige rsyslog/PV-textchecks vervangen door handmatige werkingseisen.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## G09 — Veel opdrachten hebben geen enkele automatische check

Alle 105 taaknummers in dekkingsmatrix; automatische bewijschecks per subcriterium en verplichte MANUAL; geen totaalscore.

Status: AANGEPAST; GASTWERKING VOLGENS ACCEPTATIEPLAN.

## G10 — De bestaande suite bevestigt vooral aannames van de implementatie

Regressies plus echte script-foutpaden, inhoudsdekking, negatieven, echte diskmanager-fixture. Volledige Rocky E2E blijft NOT RUN, expliciet vermeld.

Status: LOKAAL + GASTACCEPTATIE OPEN.

## H01 — Historische KVM-rebuild is destructief en geen Fusion-route

KVM-archivecode niet opgenomen; geen destructieve KVM-route in actieve codeboom.

Status: HISTORISCHE CODE UITGESLOTEN.

## H02 — Historische downloader bevat tokenachtige voorbeelddata

Historische downloader/tokenachtige voorbeelddata niet opgenomen; actieve helper alleen officiële links.

Status: HISTORISCHE CODE UITGESLOTEN.

