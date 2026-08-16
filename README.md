# cheety/skills

Eine Arbeitsumgebung für LLM-gestützte Softwareentwicklung: acht Prinzipien, ein
sprachunabhängiger Regelprüfer, dessen Regeln **selbst getestet** sind, und ein
Test-zuerst-Zyklus, der mechanisch nachweisbar ist.

Stack-Profile für **Laravel** (29 Regeln), **TypeScript** (25) und **Python** (20).

```bash
npx skills@latest add cheety/skills --skill setup-cheety-skills --skill harness-laravel
node .claude/skills/setup-cheety-skills/install.mjs --stack laravel --forge github
```

Vollständige Anleitung: [`INSTALL.md`](INSTALL.md).

---

## Was installiert wird

| Pfad im Projekt | Was |
|---|---|
| `AGENTS.md` | Die acht Prinzipien, Definition of Done, Sprachregel |
| `tools/arch-check/` | Regelprüfer plus Selbsttest der Regeln |
| `tools/skill-eval/` | Issue-Rubrik und Prüfung des Test-zuerst-Zyklus |
| `profiles/<stack>/PROFILE.md` | Wie die Prinzipien in diesem Stack aussehen |
| `.forgejo/`, `.github/` oder `.gitlab/` + `.gitlab-ci.yml` | Workflows, Issue- und PR-/MR-Vorlagen der gewählten Forge |
| `FORGES.md` | Die Unterschiede zwischen den drei Forges, die still fehlschlagen |
| `.claude/commands/` | `/issue` `/spec` `/plan` `/implement` `/bug` `/review` |

**Nur der gewählte Stack.** `npx skills` kennt keine Stacks — es installiert
Skill-Verzeichnisse. Die Auswahl passiert deshalb im Installer.

**Nur die gewählte Forge.** `--forge forgejo` (Vorgabe), `github`, `gitlab` oder
`none`. `python3 tools/forge_check.py .` prüft anschließend, dass die Dateien zur
Syntax der Forge passen — eine aus einer anderen Forge kopierte Datei läuft dort
oft *fast*.

## Die zwölf Skills

| Gruppe | Skills |
|---|---|
| Setup | `setup-cheety-skills` — Bootstrap, trägt Installer und alle Profile |
| Stacks | `harness-laravel` · `harness-typescript` · `harness-python` |
| Ablauf | `write-issue` · `split-spec` · `make-plan` · `implement-feature` · `fix-bug` · `write-tests` · `write-migration` · `code-review` |

Die Ablauf-Skills sind stackneutral. Was konkret gilt, steht im Profil.

## Die Idee dahinter

Drei Sätze tragen alles Weitere:

1. **Kein Code ohne Issue** — und kein Issue ohne überprüfbare Akzeptanzkriterien
   und ausdrückliche Nicht-Ziele.
2. **Der Mensch besitzt die Spezifikation und die Freigabe.** Das Modell besitzt
   den Entwurf.
3. **Wer einen PR öffnet, ist der Autor** — unabhängig davon, wer getippt hat.

Der Rest sind Mechanismen, die das durchsetzbar machen.

### Zwischen Spezifikation und Issue liegt eine Ebene

Ein Architekturpapier ist kein Issue und wird auch keines, indem man es
aufteilt. `write-issue` erkennt das selbst — zählt es zwei der Signale
(Dokument statt Satz, Systeme statt Verhalten, eine Reihenfolge, ein Slice-Satz
mit zwei „und"), übergibt es an `split-spec`.

```
Spec  ──►  Meilenstein  ──►  Issue  ──►  Pull Request
```

Der übersprungene Mittelschritt ist der teure. Die Issues werden dabei ganz
brauchbar; verloren geht die **Reihenfolge** — was vor was existieren muss und
was kaputtgeht, wenn man sie verletzt. Dafür hat ein Issue kein Feld.
`Verwandt: #142` ist ein Querverweis, keine Bedingung.

Der Fahrplan ist deshalb eine **Datei im Repository**, kein Issue: Issues werden
geschlossen, die Baureihenfolge muss im vierten Monat noch lesbar sein. Und sie
wird geprüft, denn genau sie verfällt still:

```bash
python3 tools/skill-eval/roadmap_check.py docs/roadmap
```

Hängende Verweise, Zyklen, und Meilensteine in einer Reihenfolge, in der niemand
bauen kann — oben nach unten *ist* die Baureihenfolge, sonst liest sie keiner.

### Regeln gehören ins Werkzeug

Eine Regel, die nicht automatisch durchgesetzt wird, verfällt binnen Monaten.
Deshalb liegen die Prinzipien als **Daten** in `profiles/<stack>.json`, nicht als
Prosa — und jede Regel hat eine Fixture-Datei mit einer eingebauten Verletzung
*und* sauberem Code, der wie eine Verletzung aussieht.

```bash
python3 tools/arch-check/eval.py --profile laravel
```

Findet der Prüfer nicht jede eingebaute Verletzung oder schlägt er auf sauberen
Code an, ist die Regel nicht fertig.

### Ein unvollständiges Profil ist von sauberem Code nicht zu unterscheiden

Beides meldet „0 Befunde". Deshalb:

```bash
python3 tools/arch-check/arch_check.py . --profile laravel --coverage
```

Das listet, welche der acht Prinzipien ein Profil abdeckt. Fehlt eines, muss es
entweder Regeln bekommen oder ausdrücklich als `not_applicable` erklärt werden —
Schweigen durch Erklärung, nicht durch Vergessen.

### Test zuerst, mit Nachweis

Gerüst → roter Lauf → Commit `Test:` → Umsetzung → Commit `Impl:`. Der Grund ist
enger als bei Menschen: Entstehen Code und Test im selben Durchgang, wird im
Zweifel der Test an den Code angepasst.

`tools/skill-eval/cycle_check.py` liest die Git-Historie und belegt es — der
Test-Commit steht vorher, und ausgecheckt an dieser Stelle ist die Suite **rot**.
Ohne diesen Punkt ist „ich habe den Test zuerst geschrieben" eine Behauptung.

Eine Ausnahme hat eine eigene Kategorie: **Charakterisierungstests** halten
bereits korrektes Verhalten fest und können nicht rot sein. Ihr Nachweis läuft
über eine Mutation — die geprüfte Logik wird gebrochen, der Test muss rot werden.

---

## An diesem Repository arbeiten

Es ist ein reines Setup-Repository. Die Harness liegt vollständig und **einmalig**
unter `skills/setup-cheety-skills/assets/`, weil `npx skills` Skill-Verzeichnisse
installiert und nicht aus ihnen herausgreifen kann.

```
skills/
├── setup-cheety-skills/     Bootstrap
│   ├── SKILL.md
│   ├── install.mjs          Stack-Auswahl passiert hier
│   └── assets/              AGENTS.md, tools/, forgejo/, github/, gitlab/, commands/, stacks/
├── stacks/                  harness-{laravel,typescript,python}
└── workflow/                die acht Arbeitsschritte
scripts/skills_check.py      prüft dieses Repo als Skill-Quelle
.github/workflows/           CI dieses Repos (nicht die ausgelieferte)
```

In der Wurzel liegt bewusst **keine zweite Kopie**. Eine frühere Fassung hatte
eine, und sie ist binnen eines Tages abgedriftet.

```bash
python3 scripts/skills_check.py .        # Frontmatter, Namen, Discovery-Tiefe
npx skills@latest add ./ --list          # zeigt, was Nutzer sehen werden
```

**Der Fallstrick, gegen den `skills_check.py` gebaut ist:** Ein unquotierter
Doppelpunkt in `description:` macht das Frontmatter ungültig. Die CLI überspringt
den Skill dann **stillschweigend** — kein Fehler, er fehlt einfach in `--list`.
Genau so ist hier einmal `fix-bug` verschwunden und erst beim Abzählen aufgefallen.

## Lizenz

MIT — siehe [`LICENSE`](LICENSE).
