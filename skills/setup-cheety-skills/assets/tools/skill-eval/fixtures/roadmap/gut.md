---
typ: roadmap
quelle: docs/specs/rechnungswesen.md
status: aktiv
---

# Rechnungswesen

Rechnungen von Entwurf bis Zahlungseingang. Die Reihenfolge folgt zwei Kriterien:
was ohne was nicht baubar ist, und was teuer zu aendern ist, wenn es falsch ist.

Diese Datei ist die saubere Fixture. Sie enthaelt absichtlich Zeilen, die wie
eine Verletzung aussehen — ein chore, der fuer sich genommen nutzlos ist, ein
Meilensteinname mit zwei Gedankenstrichen, eine Rueckwaertskante ueber zwei
Stufen. Keine davon darf anschlagen.

## M0 — Fundament

Blockiert von: —
Definition of Done: Ein leeres Beispielmodul laesst sich erzeugen, die CI erfasst
es, und der Architektur-Test schlaegt bei einem absichtlich gesetzten
Cross-Import fehl.

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| Projektgeruest mit Container und Datenbank | chore | M | nein — reine Vorarbeit, siehe AGENTS 2.5 |
| Architektur-Test gegen schichtfremde Importe | chore | S | ja — greift ab dem ersten Modul |

## M1 — Persistenz-Konventionen

Blockiert von: M0
Definition of Done: Ein Modell nutzt Base-Model und Factory, der Test laeuft
gruen.

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| Base-Model, Casts, Soft Deletes | chore | M | nein — Konvention, kein Verhalten |
| Factory- und Seeder-Basis | chore | S | ja — ab hier hat jeder Test Daten |

## M2 — Rechnungsentwurf — inkl. Positionen

Blockiert von: M1
Definition of Done: Die Buchhaltung legt einen Entwurf mit Positionen an und
findet ihn nach einem Neuladen wieder.

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| Rechnung als Entwurf anlegen | feature | M | ja — der Entwurf ist fuer sich nutzbar |
| Positionen zum Entwurf erfassen | feature | M | ja — ergaenzt den Entwurf sichtbar |

## M3 — Versand

Blockiert von: M2
Definition of Done: Eine verschickte Rechnung wechselt den Status, und ein
zweiter Versandlauf erzeugt keine zweite Mail.

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| Rechnung verschicken | feature | M | ja — Versand ist der Zweck |
| Mail-Versand idempotent machen | chore | S | ja — verhindert Doppelmails sofort |

## M4 — Zahlungseingang

Blockiert von: M2
Definition of Done: Ein erfasster Zahlungseingang schliesst die Rechnung, und
die Uebersicht zeigt offene von bezahlten getrennt.

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| Zahlungseingang erfassen | feature | M | ja — die Buchhaltung bucht ab |
| Uebersicht offen gegen bezahlt | feature | S | ja — beantwortet die Alltagsfrage |
