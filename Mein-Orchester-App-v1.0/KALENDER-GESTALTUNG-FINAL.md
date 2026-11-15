# Mein Orchester – verbindliche Kalenderdarstellung (freigegebene Gestaltung)
Stand: 15.11.2026
Status: Vom Nutzer als finale Gestaltung freigegeben; Implementierung in der zentralen Kalenderansicht noch ausstehend.

## Farbregeln für ganze Kalenderzeilen
- Montag bis Freitag: Weiß #FFFFFF.
- Samstag: helles Blaugrau #E9F0F4, kleine Wochentagsbezeichnung „Sa“.
- Sonntag: Blaugrau #E3E9EF, kleine Wochentagsbezeichnung „So“.
- Gesetzlicher Feiertag in Sachsen: Beige #F1E8D8, ausgeschriebener Feiertagsname (z. B. Buß- und Bettag).
- Als „frei“ gekennzeichneter Tag: helles Grün #CDECCB, gesamte Zeile, rechts oder im Zeileninhalt „Frei“.

## Darstellung
- Die Hintergrundfarbe gilt immer für die GESAMTE Zeilenbreite.
- Freie Tage haben besonders kompakte Zeilen, Richtwert 24 px, gerade so hoch, dass Datum, kleiner Wochentag und „Frei“ gut lesbar sind.
- Diensttage behalten die normale Höhe und sämtliche bestehenden Angaben.
- Kleine Wochentagsangaben bleiben sichtbar.
- Priorität der Hintergrundfarbe: Frei > Feiertag > Sonntag/Samstag > Werktag; der Feiertagsname bleibt bei Überschneidungen sichtbar.
- Kalenderdaten, Dienstzeiten, Veranstaltungsbeschreibungen und Navigation dürfen durch die Formatierung nicht verändert werden.

## Technischer Status
Diese Datei dokumentiert die abgenommene Gestaltung. Sie ist noch KEINE Änderung der Kalenderdarstellung in der laufenden App. Die zentrale Datei index.html muss vor Änderungen vollständig gelesen und anschließend getestet werden.
