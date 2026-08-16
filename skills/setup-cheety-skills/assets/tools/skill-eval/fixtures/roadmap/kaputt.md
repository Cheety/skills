---
typ: fahrplan                          # !! RM_TYP
quelle:                                # !! RM_QUELLE
status: aktiv
---

# Kaputter Fahrplan

Jede geplante Verletzung traegt einen Marker in genau der Zeile, in der sie
gefunden werden muss. Findet `roadmap_check.py --self-test` nicht jede davon
oder schlaegt es auf `gut.md` an, ist die Regel nicht fertig.

## M0 — Fundament                      <!-- !! RM_NO_BLOCKED_BY -->

Definition of Done: Die CI laeuft gruen.

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| Projektgeruest | chore | M | nein — reine Vorarbeit |

## M1 — Rechnungsentwurf

Blockiert von: M3                      <!-- !! RM_FORWARD_REF -->
Definition of Done: Ein Entwurf laesst sich speichern.

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| Migration fuer die Rechnungstabelle | feature | S | nein — erst mit dem Formular nutzbar |  <!-- !! RM_LAYER_SPLIT -->
| Rechnungsformular | epic | L | ja — die Buchhaltung legt Entwuerfe an |  <!-- !! RM_KIND !! RM_SIZE -->

## M2 — Versand

Blockiert von: M7                      <!-- !! RM_DANGLING -->
Definition of Done: Eine Rechnung wird verschickt.

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| Zahlungseingang erfassen | feature |  <!-- !! RM_ROW -->

## M2 — Versand, zweiter Anlauf        <!-- !! RM_DUPLICATE_ID -->

Blockiert von: M0
Definition of Done: Wie oben, nur doppelt vergeben.

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| Versandprotokoll | chore | S | ja — belegt jeden Versand |

## M3 — Haertung                       <!-- !! RM_NO_ISSUES -->

Blockiert von: M0
Definition of Done: Fehler landen im Error-Tracking.

## M5 — Mahnwesen

Blockiert von: M6                      <!-- !! RM_CYCLE -->
Definition of Done: Eine ueberfaellige Rechnung wird gemahnt.

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| Mahnung verschicken | feature | M | ja — die Buchhaltung mahnt |

## M6 — Mahngebuehren

Blockiert von: M5
Definition of Done: Eine Mahnung traegt eine Gebuehr.

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| Gebuehr auf die Mahnung rechnen | feature | S | ja — sichtbar auf dem Beleg |

## M8 — Archivierung                   <!-- !! RM_NO_DOD -->

Blockiert von: M0

| Issue | Typ | Groesse | Nuetzlich ohne den Rest? |
|---|---|---|---|
| Alte Rechnungen archivieren | chore | M | ja — haelt die Uebersicht schnell |
