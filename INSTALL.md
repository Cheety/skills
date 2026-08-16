# Installation

## Für Nutzer: ins eigene Projekt installieren

```bash
# 1. Skills holen — Setup, ein Stack, und die sieben Workflow-Skills
npx skills@latest add cheety/skills \
  --skill setup-cheety-skills \
  --skill harness-laravel \
  --skill write-issue --skill make-plan --skill implement-feature \
  --skill fix-bug --skill write-tests --skill write-migration --skill code-review

# 2. Harness ins Projekt schreiben — nur der gewählte Stack
node .claude/skills/setup-cheety-skills/install.mjs --stack laravel --forge github

# 3. Nachweisen, dass es wirkt
python3 tools/arch-check/eval.py --profile laravel
python3 tools/arch-check/arch_check.py . --profile laravel --coverage
```

Ohne `--skill` zeigt die CLI eine Auswahl. `setup-cheety-skills` muss dabei sein — es
trägt den Installer und die Profile.

**Stack statt `laravel`:** `harness-typescript` oder `harness-python`, und beim
Installer entsprechend `--stack typescript` bzw. `--stack python`.

**Forge statt `github`:** `--forge forgejo` (Vorgabe), `--forge gitlab` oder
`--forge none`. Geschrieben wird genau eine: Workflows, Issue-Vorlagen und die
PR-/MR-Vorlage. Was sich zwischen den Forges still unterscheidet, steht in
`FORGES.md`; `python3 tools/forge_check.py .` prüft es mechanisch.

### Warum zwei Schritte

`npx skills` kennt keine Stacks. Es installiert Skill-**Verzeichnisse**, und ein
Verzeichnis nimmt seine Dateien mit. Die Stack-Auswahl passiert deshalb im
Installer: Er schreibt genau ein Profil, dessen Fixtures und dessen
Werkzeugkonfiguration ins Projekt — nicht alle drei.

Schritt 3 ist nicht optional. Ein Profil, das ein Prinzip gar nicht abdeckt,
meldet „0 Befunde" — ununterscheidbar von einer sauberen Codebasis. `--coverage`
macht die Lücke sichtbar.

## Aktualisieren

```bash
npx skills update setup-cheety-skills
node .claude/skills/setup-cheety-skills/install.mjs --stack laravel --dry-run
```

`skills update` frischt das Skill-Verzeichnis auf. Es fasst die Kopien in deinem
Projekt **nicht** an — die gehören dir. Der `--dry-run` zeigt, was sich
unterscheidet, `--force` übernimmt es.

## Zweiten Stack ergänzen

Installer erneut mit dem anderen Stack aufrufen. Profile liegen nebeneinander,
der Prüfer nimmt `--profile` pro Lauf. `.harness.json` hält den ersten für die CI
fest.

## Ohne Netz

```bash
# ZIP entpacken, dann
npx skills@latest add /pfad/zu/cheety-skills --skill '*' --copy --yes
node /pfad/zu/cheety-skills/skills/setup-cheety-skills/install.mjs --stack python
```

Lokale Pfade sind ein unterstütztes Quellformat.

---

# Für Betreiber: das Repository veröffentlichen

Der Inhalt des ZIPs ist das Repository — eine reine Skill-Quelle, ohne zweite
Kopie der Harness in der Wurzel. Nach `github.com/cheety/skills` hochladen:

```bash
git init && git add -A
git commit -m "Impl: engineering harness with stack profiles"
git remote add origin git@github.com:cheety/skills.git
git push -u origin main
```

## Was die CLI erwartet

| Anforderung | Wo geprüft |
|---|---|
| `skills/<name>/SKILL.md` oder `skills/<kategorie>/<name>/SKILL.md`, höchstens zwei Ebenen | `scripts/skills_check.py` |
| Frontmatter mit `name` und `description`, gültiges YAML | ebenda |
| `name` kleingeschrieben, ohne Leerzeichen, gleich dem Verzeichnisnamen | ebenda |

```bash
python3 scripts/skills_check.py .
npx skills@latest add ./ --list    # zeigt, was Nutzer sehen werden
```

**Der Fallstrick, der diesen Prüfer nötig gemacht hat:** Ein unquotierter
Doppelpunkt in `description:` macht das Frontmatter ungültig. Die CLI überspringt
den Skill dann **stillschweigend** — er fehlt einfach in `--list`, ohne Fehler.
Genau so ist hier `fix-bug` verschwunden und erst beim Abzählen aufgefallen.

## Layout

```
skills/
├── setup-cheety-skills/     Bootstrap: Installer + alle Profile als Assets
│   ├── SKILL.md
│   ├── install.mjs
│   └── assets/             tools/, forgejo/, github/, gitlab/, stacks/{laravel,typescript,python}/
├── stacks/
│   ├── harness-laravel/    Profilbeschreibung, 29 Regeln
│   ├── harness-typescript/ 25 Regeln
│   └── harness-python/     20 Regeln
└── workflow/               die sieben stackneutralen Arbeitsschritte
```

Die Assets liegen bewusst in `setup-cheety-skills`, nicht in den Stack-Skills: So kann
man später einen zweiten Stack ergänzen, ohne ein weiteres Skill nachzuinstallieren.
