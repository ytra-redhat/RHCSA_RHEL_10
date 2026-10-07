# Fusion-revisie — 5 oktober 2026

Bron: lokale kopie van https://github.com/jconwell3115/RHCSA_RHEL_10.

- KVM/libvirt-hostinstructies vervangen door een aparte macOS/Fusion ARM64-controller.
- Golden-template op EFI/NVMe, 30 GiB, twee NICs; installatie expliciet via Fusion.
- Volledige clones voor alpha/bravo, charlie/delta, echo/foxtrot; oorspronkelijke extra-diskgroottes behouden.
- NAT voor gateway/DNS; host-only voor statische examenadressen. Geen fictieve router op de `.1`-adressen.
- Disknamen en partitienamen aangepast voor NVMe, ook in antwoordsecties en graders.
- Seed-scripts gegenereerd per VM met unieke MACs, herinitialisatie van machine-ID en SSH-hostsleutels, diskcontroles en een voltooiingsmarker.
- Rootwachtwoorden op bravo/charlie/foxtrot onbekend gemaakt; delta op rescue; echo met service- en SELinux-fouten; foxtrot met foutieve fstab.
- Geen namen-gebaseerde teardown. Bestaande bundles, niet-eigen VM's, actieve/suspended/locked VM's worden behouden.
- Eenmalige exam-ready snapshots en expliciet terugzetten per uitgeschakelde node.
- RHEL-architectuurstrings naar aarch64; Rocky gebruikt eigen repos en slaat RHEL-subscriptionstappen over.
- Ontbrekende journald.conf afgevangen met drop-ins; journalpersistentie wordt met een eerdere boot gecontroleerd.
- Graders geven foutstatussen en weigeren onbekende hostnamen; officiële examengewichten worden niet geclaimd.
- Fdisk-toetsinvoer gescheiden van shellcode; ongeldige `<pid>` en `<jobnum>` placeholders vervangen door invoerprompts.
- Oorspronkelijke bestanden integraal bewaard onder upstream-reference; niet als actieve macOS-installatiecode bedoeld.

Dit is een platformconversie met gerichte correcties, geen volledige inhoudelijke audit van alle 105 oefentaken. Verdiepingsonderdelen uit de bron zijn behouden en herkenbaar als niet-officiële oefenstof. Er is niets naar GitHub gepubliceerd.

- RHEL/Rocky 10 UEFI-GRUB-output naar /boot/grub2/grub.cfg; herstel met tijdelijk enforcing=0, sync en hervatten via /sbin/init.
