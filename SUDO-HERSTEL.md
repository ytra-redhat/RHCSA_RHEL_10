# Sudo-controle herstellen op de bestaande golden

De geïnstalleerde Rocky-golden hoeft niet opnieuw geïnstalleerd te worden.
Op deze VM toont `sudo -l -U student` dat student geen sudo mag gebruiken, maar geeft het commando toch status 0 terug. De oude eindcontrole interpreteerde alleen die status.

Voer dit uit als root in de **Linux-console van rhel10-golden in Fusion**, niet in de Mac-terminal:

```bash
cp -p /root/rhcsa-finish-golden.sh /root/rhcsa-finish-golden.sh.before-sudo-fix
python3 - <<'PYFIX'
from pathlib import Path
p = Path('/root/rhcsa-finish-golden.sh')
s = p.read_text()
old = "! sudo -l -U student >/dev/null 2>&1 || { echo 'Student heeft onverwacht sudo'; exit 1; }"
new = 'SUDO_REPORT=$(LC_ALL=C sudo -l -U student 2>&1) || true\nprintf \'%s\\n\' "$SUDO_REPORT" | grep -Eq \'^User student is not allowed to run sudo on .+\\.$\' || { echo \'Sudo-rechten student niet veilig uitgesloten\'; exit 1; }'
if s.count(old) != 1:
    raise SystemExit('STOP: verwachte oude controle niet precies eenmaal gevonden; bestand niet gewijzigd')
p.write_text(s.replace(old, new))
print('Sudo-controle hersteld')
PYFIX
bash -n /root/rhcsa-finish-golden.sh
bash /root/rhcsa-finish-golden.sh
```

De laatste opdracht voert de overige controles uit, bereidt de golden voor op klonen en schakelt de VM uit. Wacht tot Fusion aangeeft dat de VM uit staat. Deze reparatie wijzigt geen sudo-rechten of wachtwoorden.

De nieuwe codeboom bevat dezelfde correctie voor toekomstige installaties en voor guest-golden.sh. Op de bestaande gast is de sudo-controle inmiddels aangepast en succesvol gepasseerd. De eindprocedure stopte daarna wegens de ontbrekende map /var/lib/dbus. Deze map is aangemaakt. De console wacht op bevestiging van het terugzetten van de opgeslagen machine-id voordat de eindprocedure opnieuw verdergaat. De uiteindelijke uitschakeling is nog niet bevestigd.

## Huidige consoleprompt

Als de console precies `cp: overwrite '/etc/machine-id'?` toont: typ `y` en druk Enter. Dit zet de eerder opgeslagen machine-id terug; daarna start de reeds ingevoerde eindprocedure automatisch. Wacht op uitschakeling van de golden. Start de golden daarna niet opnieuw voordat je de examenklonen maakt.

De nieuwe guest-seal.sh maakt /var/lib/dbus zelf aan en bewaart de oorspronkelijke machine-id ook bij een herhaalde poging.
