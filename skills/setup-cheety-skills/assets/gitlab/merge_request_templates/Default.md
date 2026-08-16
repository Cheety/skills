Closes #

## Was und warum

<!-- Zwei bis vier Saetze. Der Diff zeigt das Was, hier steht das Warum. -->

## Akzeptanzkriterien

<!-- Aus dem Issue kopiert, jede Zeile einzeln bestaetigt. Nicht ueberflogen. -->

- [ ]
- [ ]

## Stufe-0-Review (Autor)

Nicht verhandelbar. Wer eine Zeile nicht abhaken kann, oeffnet keinen Merge Request.

- [ ] Ich habe **jede geaenderte Zeile gelesen**
- [ ] Ich kann **jede Entscheidung erklaeren**, ohne im Code nachzusehen
- [ ] Ich habe es **lokal laufen sehen**, nicht nur die gruenen Tests
- [ ] Ich habe entfernt, was kein Akzeptanzkriterium verlangt
- [ ] Ich habe geprueft, ob bestehender Code das schon konnte

## Tests

- [ ] Ein Test existiert, der **ohne** diese Aenderung fehlschlaegt
- [ ] Fehlerfall und Wiederholung sind abgedeckt, nicht nur der Erfolgsfall
- [ ] Bestehende Tests wurden **nicht** geaendert
      <!-- Falls doch: hier ausdruecklich begruenden, sonst geht der Merge Request zurueck. -->

## Umfang

Diff geschaetzt (aus dem Plan): ______ Zeilen
Diff tatsaechlich: ______ Zeilen

<!-- Faktor > 2? Hier erklaeren. -->

## Datenbank

- [ ] Keine Migration in diesem PR
- [ ] Migration ist mit alter **und** neuer Codeversion vertraeglich
- [ ] `down()` geschrieben **und lokal ausgefuehrt**

## Nach dem Merge

- [ ] Hinter Feature Flag, Aufraeum-Issue: #___
- [ ] Neues Verhalten erzeugt Log oder Metrik
- [ ] Nichts davon noetig
