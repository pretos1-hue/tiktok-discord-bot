# TikTok → Discord Bot (kostenlos, via GitHub Actions)

Postet automatisch ein neues TikTok-Video von **@pretos_real** in deinen
Discord-Kanal `#Social-Media`. Läuft komplett kostenlos auf GitHub Actions,
kein eigener Server nötig.

## Einrichtung

1. **Neues Repository auf GitHub anlegen** (kann privat sein).
2. Diese drei Dateien in das Repo hochladen, mit genau dieser Struktur:
   ```
   check_tiktok.py
   .github/workflows/tiktok-discord.yml
   README.md
   ```
3. **Secret hinterlegen:** Repo → Settings → Secrets and variables → Actions
   → "New repository secret"
   - Name: `DISCORD_WEBHOOK_URL`
   - Wert: die Webhook-URL deines `#Social-Media`-Kanals (aus Discord →
     Kanal bearbeiten → Integrationen → Webhooks)
4. **Schreibrechte für Actions aktivieren:** Repo → Settings → Actions →
   General → "Workflow permissions" → **"Read and write permissions"**
   auswählen und speichern. (Nötig, damit der Bot `last_tiktok_id.txt`
   zurück ins Repo schreiben darf.)
5. Fertig. Der Workflow läuft ab jetzt automatisch alle 15 Minuten.
   Zum sofortigen Testen: Reiter "Actions" → "TikTok zu Discord" →
   "Run workflow".

## Wichtig zu wissen

- **Nicht 100 % narrensicher:** TikTok blockt gelegentlich automatisierte
  Anfragen von Cloud-IPs (wie denen von GitHub Actions) oder ändert sein
  Seitenlayout. Wenn der Bot plötzlich nichts mehr postet, im Actions-Log
  nachsehen — meist reicht eine kleine Anpassung im Skript.
- **Erster Lauf:** Beim allerersten Durchlauf gibt es noch keine
  `last_tiktok_id.txt` — dein aktuell neuestes Video wird dann einmalig
  gepostet. Das ist normal.
- Nach 60 Tagen ohne Repo-Aktivität deaktiviert GitHub geplante Workflows
  automatisch. Falls das passiert: Actions-Tab → Workflow wieder aktivieren.
- Username ändern: einfach `TIKTOK_USERNAME` oben in `check_tiktok.py`
  anpassen.
