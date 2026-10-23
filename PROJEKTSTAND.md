# Mein Orchester – Projektstand
Stand: 23. Oktober 2026

## Grundsatz
Berufsorchester-App für Dienstplan, Notenarchiv und Navigation. Bestehende bestätigte Daten nicht ohne Rückfrage ändern. Ursprüngliche kurze Ping-Töne als Startklang beibehalten; keine neue Melodie.

## Technik
- Repository: ov-erzphil/MeinOrchester
- Entwicklungsbranch: main
- Unveränderter Sicherungsbranch: backup-2026-10-23 (angelegt 23.10.2026)
- Externe ZIP-Sicherung des Sicherungsbranches durch Projektverantwortlichen heruntergeladen.
- GitHub Pages / Browser-App vorhanden; aktueller Veröffentlichungsstand und Synchronisierung noch zu prüfen.
- Repository wurde am 23.10.2026 als öffentlich angezeigt. Repository-Sichtbarkeit und Pages-Zugriff sind getrennt zu beurteilen.

## Dienstplan
- Bisherige Korrekturen als Arbeitsstand bestätigt bis zum letzten bestätigten Dienst am 10.01.2027.
- Vorausplan ab 12.01.2027 ungeklärt / widersprüchlich; nicht ohne Rückfrage übernehmen.
- Google-Kalender-Synchronisierung und richtige Kontoauswahl überprüfen.
- Dienstorte und Produktionen nicht ungeprüft überschreiben.

## Notenarchiv
- Vollständiges Google-Drive-Notenarchiv anzeigen, nicht nur eine Auswahl.
- Live-Synchronisierung und PDF-Öffnung noch prüfen.

## Navigation – beschlossene Gestaltung, noch nicht implementiert
- Mobile Zweispaltenansicht: Kalender links, Navigationsbereich rechts.
- Nach Auswahl eines Kalendereintrags erscheint die Navigation rechts auf ungefähr derselben sichtbaren Höhe.
- Navigationskarte bleibt beim Scrollen sichtbar und vollständig bedienbar.
- Nur ein Button „Navigieren zum Dienstort“; zusätzlichen Google-Maps-Button entfernen.
- Zweiter Button „Verkehrslage Rückfahrt“: Google-Maps-Route vom jeweiligen Dienstort zum vom Nutzer hinterlegten Rückfahrziel; Verkehr und geschätzte Reisezeit in Maps.
- Dezente Farbcodierung: Blau für Anreise, Grün für Rückfahrt; insgesamt ruhige, professionelle Gestaltung.

## Zugangsschutz – beschlossenes Konzept, noch nicht implementiert
- Keine Selbstregistrierung; einmalig persönlicher Zugangscode pro Orchestermitglied.
- Auf demselben Gerät danach automatische Anmeldung, solange Berechtigung gültig ist.
- Einzelne Nutzerzugänge zentral sperrbar.
- Sichere serverseitige Prüfung erforderlich; kein gemeinsames Passwort im öffentlich abrufbaren JavaScript.
- Bei Sperrung erneute Onlineprüfung; bereits heruntergeladene Daten können nicht rückwirkend entfernt werden.
- Datenschutz und minimale Verwaltung beachten.

## Veröffentlichung und Sicherheit
- Alte Browser-Version soll bei Bedarf vorübergehend nicht mehr erreichbar sein; GitHub Pages deaktivieren erst nach Prüfung und ausdrücklicher Freigabe.
- Ein Pages-Stopp allein entfernt keine bereits lokal gespeicherten oder anderweitig veröffentlichten Kopien.
- Keine bestätigten Daten ohne Rückfrage verändern.

## Nächste Arbeitsschritte
1. GitHub-Dateien, Veröffentlichungsweg und tatsächliche Browser-Version prüfen.
2. Google-Kalender-Anbindung und Datenstand verifizieren.
3. Vollständiges Google-Drive-Notenarchiv prüfen.
4. Mobile Navigation und Rückfahrbutton implementieren.
5. Einfache sichere persönliche Anmeldung und Sperrfunktion planen und umsetzen.
6. Erst nach Tests die neue Version veröffentlichen.

## Dokumentationsregel
Diese Datei nach wesentlichen bestätigten Entscheidungen aktualisieren. Den Sicherungsbranch vom 23.10.2026 nicht ändern. Die Datei ist eine Arbeitszusammenfassung, kein vollständiger Export der Chatverläufe.
