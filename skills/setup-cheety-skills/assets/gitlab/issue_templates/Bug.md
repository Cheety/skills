<!--
Titel: [Bug]: <kurze Beschreibung>

GitLab kennt keine Issue-Formulare. Die Felder sind daher Ueberschriften, und
was in Forgejo `validations.required` erzwingt, steht hier als Hinweis: Ein
leerer Abschnitt bedeutet, dass die Umsetzung raet.

**Ohne Reproduktion wird nicht gefixt.** Wenn du sie nicht hast, ist das kein
Hindernis — trag ein, was du weisst, und lass die uebrigen Felder offen. Ein
Issue mit offener Frage ist besser als eines mit erfundener Antwort.
-->

## Reproduktion

<!-- Nummerierte Schritte. Pflicht. -->

1. Als Kunde mit mehr als 10 Rechnungen anmelden
2. Rechnungsuebersicht oeffnen
3. Auf "Mahnung senden" klicken

## Erwartet vs. tatsaechlich

<!-- Pflicht. -->

```
Erwartet:     Eine Mahnung, Status wechselt auf "Mahnung"
Tatsaechlich: Zwei identische Mahnungsmails, Status korrekt
```

## Umgebung und Haeufigkeit

<!-- Pflicht. Beispiel: Produktion, seit Deploy vom 14.08., etwa jede 5. Mahnung -->

## Nicht-Ziele

<!--
Pflichtfeld. Was wird in diesem Issue ausdruecklich nicht angefasst? Das ist die
wirksamste Einzelmassnahme gegen Over-Engineering.

- Kein Refactoring der Mahnlogik
- Keine Umstellung des Queue-Treibers
-->

## Betroffene Pfade

<!-- Pflicht. Ohne Pfad sucht die Umsetzungssitzung im ganzen Repository.
     Beispiel: app/Jobs/VersendeMahnungsMail.php, app/Actions/Rechnung/ -->

## Groesse

<!-- Genau eine Zeile stehen lassen. -->

- [ ] S (< 100 Zeilen)
- [ ] M (< 400 Zeilen)

/label ~bug
