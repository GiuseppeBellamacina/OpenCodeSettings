# Guida: replicare questa configurazione di Claude Code da zero

Guida passo-passo per portare un'installazione appena fatta di Claude Code allo stato esatto di questa (com'era al 2026-09-25). Include sia quello configurato insieme in questa sessione sia quello che c'era già prima e non abbiamo toccato.

Convenzione: ogni volta che è possibile do **due strade** — il comando/percorso UI "ufficiale", e la scorciatoia "modifica diretta di `settings.json`" che abbiamo usato in pratica per tutta la sessione perché più affidabile e verificabile.

---

## Fase 0 — Prerequisiti di sistema

Installa questi PRIMA di toccare Claude Code — molti plugin/skill ne dipendono e falliscono silenziosamente senza:

| Strumento | Perché serve | Verifica versione (di riferimento, quella su questa macchina) |
|---|---|---|
| **Node.js + npm** | serve a `typescript-lsp`, npm-installed tools | `node -v` → v24.11.1, `npm -v` → 11.6.2 |
| **Python 3.11+** | serve a graphify, hf CLI | — |
| **uv** (`astral-sh/uv`) | installer isolato usato per graphify e hf | `uv --version` → 0.8.15 |
| **git** | requisito base | — |
| **gh** (GitHub CLI) | usato da mattpocock-skills se scegli GitHub come issue tracker | `gh --version` → 2.101.0. Se manca: `winget install GitHub.cli` |

Installazione uv (se manca):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Fase 1 — Installare Claude Code e fare login

1. Installa l'app desktop Claude Code / la CLI `claude` (a seconda di come usi questa già).
2. Avvia una sessione e fai login con lo stesso account Anthropic (`/login`). **Non copiare mai `.credentials.json` da un'altra macchina** — rigeneralo sempre col login.
3. Verifica che si sia creato `~/.claude/` (su Windows: `C:\Users\<utente>\.claude\`).

---

## Fase 2 — Impostazioni base globali

Apri (o crea) `~/.claude/settings.json` e imposta questi campi base (non legati a plugin/skill):

```json
{
  "model": "opus",
  "advisorModel": "opus",
  "autoUpdatesChannel": "latest",
  "theme": "dark",
  "agentPushNotifEnabled": true,
  "modelSettings": {
    "claude-sonnet-5": {
      "effortLevel": "high"
    }
  },
  "attribution": {
    "commit": "",
    "pr": ""
  }
}
```

Equivalente da comando: `/config` per model/theme; il resto (advisorModel, effortLevel, attribution) è più semplice da scrivere direttamente nel file.

Cosa significano, in breve:
- `model: opus` — modello di default della sessione
- `advisorModel: opus` — modello usato dal tool `advisor`
- `modelSettings.claude-sonnet-5.effortLevel: high` — quando usi Sonnet 5, ragionamento al massimo
- `attribution` vuoto — niente riga "Co-authored-by" o simili nei commit/PR generati

---

## Fase 3 — Plugin dal marketplace ufficiale (`claude-plugins-official`)

Nessuna marketplace da aggiungere, è quella di default. Per ognuno: da sessione interattiva `/plugin install <nome>@claude-plugins-official`, oppure aggiungi direttamente la riga nel blocco `enabledPlugins` di `settings.json` (Claude Code lo scarica/cache da solo alla prossima sessione).

| Plugin | Stato finale voluto | Cosa fa (riassunto) |
|---|---|---|
| `frontend-design` | `true` | linee guida design UI/frontend |
| `code-review` | `true` | skill di code review PR/branch |
| `context7` | `true` | MCP per doc aggiornate di librerie/framework |
| `skill-creator` | `true` | crea/ottimizza skill custom |
| `mattpocock-skills` | `true` | metodologia ingegneristica: grilling, TDD, code review a 2 assi, domain modeling, ecc. — **vedi Fase 7 per il setup per-progetto** |
| `pyright-lsp` | `true` | LSP Python (richiede binario esterno, Fase 6) |
| `typescript-lsp` | `true` | LSP TypeScript/JS (richiede binario esterno, Fase 6) |
| `huggingface-skills` | `false` | **installato ma disattivato** — riattivalo solo se lavori con l'ecosistema HuggingFace/ML; serve poi autorizzare l'MCP da `/mcp` |
| `superpowers` | `false` | **installato ma disattivato** — non l'abbiamo esplorato in questa sessione |

Blocco `enabledPlugins` finale da incollare in `settings.json`:
```json
"enabledPlugins": {
  "frontend-design@claude-plugins-official": true,
  "superpowers@claude-plugins-official": false,
  "code-review@claude-plugins-official": true,
  "context7@claude-plugins-official": true,
  "skill-creator@claude-plugins-official": true,
  "ponytail@ponytail": true,
  "mattpocock-skills@claude-plugins-official": true,
  "huggingface-skills@claude-plugins-official": false,
  "pyright-lsp@claude-plugins-official": true,
  "typescript-lsp@claude-plugins-official": true
}
```
(la voce `ponytail@ponytail` fa parte della Fase 4, non del marketplace ufficiale — è qui solo perché nello stesso blocco JSON.)

---

## Fase 4 — Marketplace custom: ponytail

Non è nel marketplace ufficiale, va aggiunto a parte:

```
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```
Oppure, scorciatoia diretta in `settings.json`:
```json
"extraKnownMarketplaces": {
  "ponytail": {
    "source": {
      "source": "github",
      "repo": "DietrichGebert/ponytail"
    }
  }
}
```
più la riga `"ponytail@ponytail": true` nel blocco `enabledPlugins` sopra.

**Cos'è**: rende Claude uno "sviluppatore senior pigro" — YAGNI, stdlib prima di dipendenze custom, diff minimo. Attivo su ogni sessione via hook `SessionStart`. Default livello **full**; cambialo con `/ponytail lite|full|ultra`, disattivalo con "stop ponytail".

Facoltativo — statusline che mostra `[PONYTAIL:FULL]` nella barra di stato (te lo propone da solo al primo avvio se manca):
```json
"statusLine": { "type": "command", "command": "powershell -ExecutionPolicy Bypass -File \"<percorso-plugin>\\hooks\\ponytail-statusline.ps1\"" }
```

---

## Fase 5 — CLAUDE.md globale

Crea/modifica `~/.claude/CLAUDE.md`:
```markdown
# graphify
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.
```
Questo blocco l'ha scritto il comando `graphify install` (Fase 8), non editarlo a mano prima di aver installato graphify.

---

## Fase 6 — Language server (LSP)

I plugin `pyright-lsp`/`typescript-lsp` (Fase 3) registrano solo *quale comando lanciare* — i binari veri vanno installati a parte, altrimenti il tool `LSP` fallisce silenziosamente:

```bash
npm install -g pyright
npm install -g typescript typescript-language-server
```

Verifica che funzionino (facoltativo ma consigliato):
```bash
pyright-langserver --stdio    # deve restare in attesa, non dare errori di modulo mancante
typescript-language-server --version
```
Non serve nessuna configurazione di progetto: appena apri un file `.py`/`.ts`/`.js` ecc. in una sessione, Claude Code avvia da solo il server giusto.

---

## Fase 7 — skillOverrides (skill Anthropic native, meno invasive)

Queste skill sono già bundlate con Claude Code — qui le abbiamo solo rese "solo su richiesta esplicita" (`/pdf`, `/pptx`, ecc.) invece che auto-invocabili, per non farle pesare nel contesto quando non servono:

```json
"skillOverrides": {
  "anthropic-skills:xlsx": "user-invocable-only",
  "anthropic-skills:skill-creator": "user-invocable-only",
  "anthropic-skills:pptx": "user-invocable-only",
  "anthropic-skills:pdf": "user-invocable-only",
  "anthropic-skills:morning": "user-invocable-only",
  "anthropic-skills:import-memory": "user-invocable-only",
  "anthropic-skills:docx": "user-invocable-only",
  "anthropic-skills:docs": "user-invocable-only"
}
```
Valori possibili: `on` (default, auto-invocabile), `user-invocable-only` (solo `/nome`, mai automatica), `name-only` (resta elencata ma senza descrizione, risparmio minimo di contesto), `off` (sparisce del tutto, anche da `/`).

Questo blocco va scritto **una volta, in `~/.claude/settings.json` globale** — non nei singoli progetti, altrimenti vale solo lì.

---

## Fase 8 — graphify (non è un plugin Claude Code — tool esterno + skill)

```bash
uv tool install graphifyy
graphify install          # copia SKILL.md in ~/.claude/skills/graphify/ + scrive la sezione "# graphify" in ~/.claude/CLAUDE.md (Fase 5)
```
Verifica: `graphify --version` → dovrebbe rispondere (qui: 0.9.67).

**Non è tutto globale**: per ogni singolo progetto/repo in cui vuoi usarlo devi ripetere, dentro quella cartella:
```
/graphify .                              # prima build del grafo
graphify claude install --project        # opzionale: scrive ./CLAUDE.md + hook PreToolUse locale (nudge automatico prima di grep/read)
```
`--project` è importante: senza, il comando dell'hook viene scritto con un path assoluto legato a QUESTA macchina, non portabile se condividi il progetto.

Se vuoi anche l'hook git che ricostruisce il grafo ad ogni commit (solo repo git):
```
graphify hook install
```

---

## Fase 9 — hf CLI (Hugging Face) — tool esterno, non un plugin

```bash
uv tool install "huggingface_hub[cli]"
```
Verifica: `hf --version` → 2.0.0.

Login **solo se ti serve** toccare il tuo account (repo privati, upload, modelli gated):
```bash
hf auth login
```
Il browsing pubblico funziona anche senza login.

Nota: in questa sessione avevamo anche provato `hf skills add -g` (installa una skill `hf-cli` locale, ridondante col plugin `huggingface-skills` disattivato) — poi rimossa su richiesta. **Non è nello stato finale**, salta questo passo a meno che tu non la voglia di nuovo.

---

## Fase 10 — setup per-progetto di mattpocock-skills (facoltativo, non globale)

Il plugin (Fase 3) è globale, ma le skill legate a ticket/tracker (`to-spec`, `to-tickets`, `triage`, `wayfinder`, l'asse "Spec" di `code-review`) hanno bisogno di config **per ogni repo** in cui le usi:
```
/setup-matt-pocock-skills
```
Risponde a 3 domande (tracker issue, label di triage, layout doc dominio) e scrive `docs/agents/*.md` + un blocco `## Agent skills` nel `CLAUDE.md`/`AGENTS.md` di quel progetto. Da rifare in ogni nuovo repo dove vuoi il flusso completo.

---

## Fase 11 — cosa abbiamo valutato ma NON installato (di proposito)

Per completezza — non fanno parte dello stato finale, li abbiamo solo analizzati:

- **atomic-agents**: installato poi rimosso — framework Python di nicchia (Atomic Agents), utile solo se costruisci agenti con quello specifico framework.
- **caveman** (skill/proxy/middleware anti-verbosità): valutato, **consigliato di non installare** — la skill si sovrappone a ponytail (che già impone output corti), il proxy è un demone always-on con licenza BSL-1.1 non pienamente open source, utile solo su workload con output di tool enormi (log/CSV giganti), non il tuo caso.

---

## Fase 12 — checklist di verifica finale

Apri una sessione nuova e controlla:

- [ ] `theme` scuro, modello `opus` di default
- [ ] `/ponytail-help` risponde (conferma ponytail attivo)
- [ ] Nell'elenco skill disponibili compaiono `mattpocock-skills:*` (grilling, tdd, code-review, ecc.)
- [ ] `graphify --version` funziona da terminale
- [ ] `hf --version` e `gh --version` funzionano da terminale
- [ ] Apri un file `.py` in un progetto → nessun errore se chiedi un'operazione LSP (es. "trova dove è definito X")
- [ ] `/pdf`, `/docx` ecc. **non** vengono proposte da sole, solo se le chiami esplicitamente
- [ ] `huggingface-skills` e `superpowers` risultano installati ma spenti (verifica in `settings.json` o nel pannello plugin)
