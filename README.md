# Mein Orchester – Android-Prototyp

Paketname: `de.meinorchester.app`.

Enthält drei Bereiche: **Dienstplan** (Dienste lokal hinzufügen und löschen), **Notenarchiv** (PDF-Dateien über die Android-Dateiauswahl verknüpfen und öffnen), **Mein Konto** (Name und Instrument lokal speichern).

**Wichtig:** Dies ist ein funktionsfähiger *Ausgangsstand*, keine produktionsreife Orchesterverwaltung. Keine Anmeldung, keine Mehrbenutzerverwaltung, keine Synchronisation, keine Zugriffsrechte, keine Serveranbindung. Daten werden lokal gespeichert. Eine Deinstallation kann diese Daten entfernen. Keine sensiblen oder vertraulichen Orchesterunterlagen verwenden, bevor eine sichere Lösung umgesetzt ist.

## APK ohne PC über GitHub Actions erstellen

1. Auf github.com ein **privates** neues Repository `MeinOrchester` erstellen (ohne automatisch angelegte README).
2. ZIP auf dem Handy entpacken. Den **Inhalt** des Ordners `MeinOrchester` einschließlich `.github/workflows/android.yml` in das Repository hochladen. GitHub Web-Oberfläche erlaubt mehrere Dateien; versteckte `.github`-Ordner müssen erhalten bleiben. Falls der Browser-Upload umständlich ist, kann man die Dateien alternativ mit GitHub Mobile oder einem Git-Client übertragen.
3. Im Repository **Actions** öffnen und den Workflow **Android APK bauen** ausführen (falls nötig: Actions für das Repository aktivieren). Ein Push auf `main` oder `master` startet den Build ebenfalls.
4. Nach erfolgreichem Lauf unter **Artifacts** `MeinOrchester-APK` herunterladen, ZIP entpacken und `app-debug.apk` auf dem Honor 50 installieren. Android kann dafür die Erlaubnis „Apps aus dieser Quelle installieren“ verlangen.

Der erste Cloud-Build wurde hier **nicht ausgeführt**. Der Build benötigt Zugang zu Google Maven, Android SDK und Gradle. Die Debug-APK ist nur für Tests geeignet und wird automatisch mit einem Debug-Schlüssel signiert. Für eine spätere veröffentlichte Version braucht es einen sicheren Release-Schlüssel.
