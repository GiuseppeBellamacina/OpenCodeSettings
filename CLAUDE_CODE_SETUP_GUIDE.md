# Guida: replicare questa configurazione di Claude Code da zero

Guida passo-passo per portare un'installazione appena fatta di Claude Code allo stato esatto di questa (aggiornata al 2026-10-07). Le fasi sono in ordine di esecuzione: ognuna dipende solo da quelle precedenti.

Convenzione: dove possibile do **due strade** — il comando/percorso UI "ufficiale", e la scorciatoia "modifica diretta di `settings.json`" (più affidabile e verificabile).

Indice: 0. Prerequisiti di sistema

1. Installare Claude Code e login
2. Impostazioni base globali
3. Marketplace
4. Plugin
5. Language server (binari per i plugin LSP)
6. Tool esterni: graphify e hf CLI
7. CLAUDE.md globale
8. skillOverrides
9. Setup per-progetto (facoltativo)
10. Valutati ma NON installati + catalogo di altri tool noti
11. Checklist di verifica finale

---

## Fase 0 — Prerequisiti di sistema

Installa questi PRIMA di toccare Claude Code — molti plugin/tool ne dipendono e falliscono silenziosamente senza:

| Strumento               | Perché serve                                                   | Versione di riferimento (questa macchina)                      |
| ----------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- |
| **Node.js + npm**       | LSP (Fase 5), npm-installed tools                              | `node -v` → v24.18.0, `npm -v` → 11.16.0                       |
| **Python 3.11+**        | graphify, hf CLI                                               | —                                                              |
| **uv** (`astral-sh/uv`) | installer isolato per graphify e hf                            | `uv --version` → 0.11.29                                       |
| **git**                 | requisito base                                                 | —                                                              |
| **gh** (GitHub CLI)     | usato da mattpocock-skills se scegli GitHub come issue tracker | `gh --version` → 2.96.0. Se manca: `winget install GitHub.cli` |

Installazione uv (se manca):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Fase 1 — Installare Claude Code e fare login

1. Installa l'app desktop Claude Code / la CLI `claude` (a seconda di come la usi).
2. Avvia una sessione e fai login con lo stesso account Anthropic (`/login`). **Non copiare mai `.credentials.json` da un'altra macchina** — rigeneralo sempre col login.
3. Verifica che si sia creato `~/.claude/` (su Windows: `C:\Users\<utente>\.claude\`).

---

## Fase 2 — Impostazioni base globali

Apri (o crea) `~/.claude/settings.json` e imposta questi campi base (non legati a plugin/skill):

```json
{
  "model": "sonnet",
  "effortLevel": "low",
  "advisorModel": "opus",
  "autoUpdatesChannel": "latest",
  "theme": "dark",
  "agentPushNotifEnabled": true,
  "modelSettings": {
    "claude-sonnet-5": { "effortLevel": "high" },
    "claude-sonnet-5-5": { "effortLevel": "medium" },
    "claude-opus-5": { "effortLevel": "medium" },
    "claude-opus-5-5": { "effortLevel": "medium" }
  },
  "attribution": {
    "commit": "",
    "pr": ""
  }
}
```

Equivalente da comando: `/config` per model/theme; il resto (advisorModel, effortLevel, attribution) è più semplice da scrivere direttamente nel file.

Cosa significano:

- `model: sonnet` — modello di default della sessione
- `effortLevel: low` — ragionamento di default per i modelli senza override
- `modelSettings.<modello>.effortLevel` — override per modello: Sonnet 5 a `high`, Sonnet 5.5 e Opus 5/5.5 a `medium`
- `advisorModel: opus` — modello usato dal tool `advisor`
- `attribution` vuoto — niente riga "Co-authored-by" o simili nei commit/PR generati

Le sezioni `enabledPlugins`, `extraKnownMarketplaces` e `skillOverrides` si aggiungono nelle fasi successive, nello stesso file.

---

## Fase 3 — Marketplace

Servono prima dei plugin (Fase 4).

- **`claude-plugins-official`** (`anthropics/claude-plugins-official`): è quello di default, non c'è nulla da aggiungere.
- **`ponytail`** (`DietrichGebert/ponytail`): non è nel marketplace ufficiale, va aggiunto a parte:

```
/plugin marketplace add DietrichGebert/ponytail
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

---

## Fase 4 — Plugin

Per ognuno: da sessione interattiva `/plugin install <nome>@<marketplace>`, oppure aggiungi direttamente la riga nel blocco `enabledPlugins` di `settings.json` (Claude Code lo scarica da solo alla prossima sessione).

### Attivi

| Plugin              | Cosa fa (riassunto)                                                                                                   |
| ------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `frontend-design`   | linee guida design UI/frontend                                                                                        |
| `code-review`       | skill di code review PR/branch                                                                                        |
| `code-simplifier`   | agente che semplifica/rifinisce codice mantenendo la funzionalità                                                     |
| `commit-commands`   | `/commit`, `/commit-push-pr`, `/clean_gone`                                                                           |
| `context7`          | MCP per doc aggiornate di librerie/framework                                                                          |
| `supabase`          | MCP + skill per Supabase (DB, auth, edge functions, ecc.)                                                             |
| `vercel`            | MCP + skill per deploy/gestione progetti Vercel                                                                       |
| `playwright`        | MCP per automazione browser                                                                                           |
| `claude-security`   | scan di sicurezza del codice e patch verificate                                                                       |
| `claude-code-setup` | raccomanda automazioni (hook, subagent, skill, MCP) per un progetto                                                   |
| `mattpocock-skills` | metodologia ingegneristica: grilling, TDD, code review a 2 assi, domain modeling, ecc. — setup per-progetto in Fase 9 |
| `pyright-lsp`       | LSP Python (richiede binario esterno, Fase 5)                                                                         |
| `typescript-lsp`    | LSP TypeScript/JS (richiede binario esterno, Fase 5)                                                                  |
| `ponytail@ponytail` | "sviluppatore senior pigro": YAGNI, stdlib prima di dipendenze, diff minimo (vedi sotto)                              |

### Installati ma disattivati

| Plugin                 | Note                                                                                            |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| `superpowers`          | non esplorato                                                                                   |
| `skill-creator`        | spento (la skill nativa`anthropic-skills:skill-creator` è comunque presente, Fase 8)            |
| `claude-md-management` | spento                                                                                          |
| `huggingface-skills`   | riattivalo solo se lavori con l'ecosistema HuggingFace/ML; serve poi autorizzare l'MCP da`/mcp` |

### Blocco `enabledPlugins` finale da incollare in `settings.json`

```json
"enabledPlugins": {
  "frontend-design@claude-plugins-official": true,
  "superpowers@claude-plugins-official": false,
  "code-review@claude-plugins-official": true,
  "context7@claude-plugins-official": true,
  "skill-creator@claude-plugins-official": false,
  "code-simplifier@claude-plugins-official": true,
  "claude-md-management@claude-plugins-official": false,
  "supabase@claude-plugins-official": true,
  "typescript-lsp@claude-plugins-official": true,
  "pyright-lsp@claude-plugins-official": true,
  "mattpocock-skills@claude-plugins-official": true,
  "huggingface-skills@claude-plugins-official": false,
  "claude-security@claude-plugins-official": true,
  "ponytail@ponytail": true,
  "playwright@claude-plugins-official": true,
  "commit-commands@claude-plugins-official": true,
  "vercel@claude-plugins-official": true,
  "claude-code-setup@claude-plugins-official": true
}
```

### Dettaglio ponytail

Attivo su ogni sessione via hook `SessionStart`. Default livello **full**; cambialo con `/ponytail lite|full|ultra`, disattivalo con "stop ponytail".

Facoltativo — statusline che mostra `[PONYTAIL:FULL]` (te lo propone da solo al primo avvio se manca; al momento **non** configurata):

```json
"statusLine": { "type": "command", "command": "powershell -ExecutionPolicy Bypass -File \"<percorso-plugin>\\hooks\\ponytail-statusline.ps1\"" }
```

### Plugin mods e `/plugin-authoring`

`/plugin-authoring` **non è un plugin da installare**: è una skill built-in di Claude Code (richiede v2.1.287+) che ti fa creare dei **mod**. Un mod è un plugin con un file "hooks module" (JS/TS, caricato direttamente, senza Node/bundler/build) le cui funzioni Claude Code chiama quando succedono eventi. Serve a personalizzare il comportamento di Claude Code:

- pannelli/viste live, righe sopra il prompt, voci di status line, toast
- slash command custom
- bloccare, riscrivere o reagire alle tool call e ai prompt
- modificare il system prompt, riprodurre suoni, timer

Come si usa: lanci `/plugin-authoring`, descrivi a Claude il mod che vuoi, e lui lo scrive in `~/.claude/dev-mods/<id-sessione>/<nome-mod>/` (con `.claude-plugin/plugin.json`, `hooks/hooks.json` con la chiave `modules`, e `hooks/register.tsx`). Al primo file scritto Claude Code ti chiede _"Enable hot reloading for this session?"_: rispondendo sì il mod si carica a fine turno e si ricarica a ogni modifica. Controlli utili: `claude plugin validate <cartella>` e `claude plugin test <cartella>`. Per condividerlo basta un repo GitHub usato come marketplace: `/plugin install <mod> --marketplace <owner>/<repo>`.

Documentazione ufficiale: [https://code.claude.com/docs/en/plugins/mods/create](https://code.claude.com/docs/en/plugins/mods/create)

---

## Fase 5 — Language server (LSP)

I plugin `pyright-lsp`/`typescript-lsp` (Fase 4) registrano solo _quale comando lanciare_ — i binari veri vanno installati a parte, altrimenti il tool `LSP` fallisce silenziosamente:

```bash
npm install -g pyright
npm install -g typescript typescript-language-server
```

Versioni di riferimento: pyright 1.1.414, typescript 7.0.2, typescript-language-server 6.0.1.

Verifica (facoltativa ma consigliata):

```bash
pyright-langserver --stdio    # deve restare in attesa, non dare errori di modulo mancante
typescript-language-server --version
```

Nessuna configurazione di progetto: appena apri un file `.py`/`.ts`/`.js` ecc., Claude Code avvia da solo il server giusto.

---

## Fase 6 — Tool esterni (non sono plugin Claude Code)

### graphify — tool + skill

```bash
uv tool install graphifyy
graphify install          # copia SKILL.md in ~/.claude/skills/graphify/ + scrive la sezione "# graphify" in ~/.claude/CLAUDE.md (vedi Fase 7)
```

Verifica: `graphify --version` → 0.9.69.

Non è tutto globale: per l'uso per-progetto vedi Fase 9.

### hf CLI (Hugging Face)

```bash
uv tool install "huggingface_hub[cli]"
```

Verifica: `hf --version` → 2.0.0 (potrebbe suggerire un aggiornamento, non necessario).

Login **solo se ti serve** toccare il tuo account (repo privati, upload, modelli gated):

```bash
hf auth login
```

Il browsing pubblico funziona anche senza login.

Nota: `hf skills add -g` (skill `hf-cli` locale) **non** è nello stato finale — ridondante col plugin `huggingface-skills`. Salta il passo.

---

## Fase 7 — CLAUDE.md globale

`~/.claude/CLAUDE.md` contiene solo il blocco scritto da `graphify install` (Fase 6) — non editarlo a mano prima di aver installato graphify:

```markdown
# graphify

- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
  When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.
```

---

## Fase 8 — skillOverrides (skill Anthropic native, meno invasive)

Queste skill sono già bundlate con Claude Code — qui le rendiamo "solo su richiesta esplicita" (`/pdf`, `/pptx`, ecc.) invece che auto-invocabili, per non farle pesare nel contesto:

```json
"skillOverrides": {
  "anthropic-skills:google-workspace": "user-invocable-only",
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

Valori possibili: `on` (default, auto-invocabile), `user-invocable-only` (solo `/nome`, mai automatica), `name-only` (resta elencata senza descrizione), `off` (sparisce del tutto, anche da `/`).

Va scritto **una volta, nel `~/.claude/settings.json` globale** — non nei singoli progetti, altrimenti vale solo lì.

---

## Fase 9 — Setup per-progetto (facoltativo, non globale)

### mattpocock-skills

Il plugin (Fase 4) è globale, ma le skill legate a ticket/tracker (`to-spec`, `to-tickets`, `triage`, `wayfinder`, l'asse "Spec" di `code-review`) hanno bisogno di config **per ogni repo**:

```
/setup-matt-pocock-skills
```

Risponde a 3 domande (tracker issue, label di triage, layout doc dominio) e scrive `docs/agents/*.md` + un blocco `## Agent skills` nel `CLAUDE.md`/`AGENTS.md` del progetto. Da rifare in ogni nuovo repo dove vuoi il flusso completo.

### graphify

Dentro la cartella del progetto:

```
/graphify .                              # prima build del grafo
graphify claude install --project        # opzionale: scrive ./CLAUDE.md + hook PreToolUse locale (nudge prima di grep/read)
```

`--project` è importante: senza, il comando dell'hook viene scritto con un path assoluto legato a QUESTA macchina, non portabile.

Hook git che ricostruisce il grafo ad ogni commit (solo repo git):

```
graphify hook install
```

---

## Fase 10 — Valutati ma NON installati

- **caveman** (skill/proxy/middleware anti-verbosità): **sconsigliato** — la skill si sovrappone a ponytail (già output corti), il proxy è un demone always-on con licenza BSL-1.1, utile solo con output di tool enormi.

### Altri tool/plugin noti (catalogo, non installati)

Verificati con ricerca web il 2026-10-07 (stelle e numeri sono quelli riportati dalle fonti, cambiano in fretta):

- **[Agent Reach](https://github.com/panniantong/agent-reach)** — "livello di capacità" che dà all'agente accesso a internet: installa, configura e instrada backend di terze parti (CLI, API, MCP) per leggere/cercare su Twitter/X, Reddit, YouTube, Bilibili, Xiaohongshu, GitHub, RSS e web (Jina Reader, yt-dlp, Exa, `gh`…). Funziona con Claude Code, Cursor, Windsurf e altri agenti con shell. Per Claude Code: `npx skills add Panniantong/Agent-Reach@agent-reach`. Utile se ti serve far leggere all'agente social/video; attenzione che installa molti tool di terze parti.
- **[OmniRoute](https://github.com/diegosouzapw/OmniRoute)** — gateway AI self-hosted (TypeScript, MIT, dashboard Next.js) che unifica 200+ provider dietro un solo endpoint compatibile OpenAI/Anthropic/Gemini: routing intelligente, fallback automatico, load balancing, cache, osservabilità, compressione token. Si collega a Claude Code, Cursor, Cline, ecc. Serve per gestire costi/limiti o sfruttare tier gratuiti; è un servizio da far girare, e instradare il traffico verso provider non ufficiali ha rischi di affidabilità e privacy.
- **[Strix](https://github.com/usestrix/strix)** — pentester AI open source (Apache-2.0): team di agenti autonomi che eseguono l'app, trovano vulnerabilità e le **validano con proof-of-concept reali** (proxy HTTP, browser, shell, runtime exploit, OSINT, analisi statica/dinamica). Si integra in GitHub Actions/CI. Da usare **solo su sistemi di tua proprietà o con autorizzazione scritta**. Complementare a `claude-security` (che fa analisi del codice, non attacchi dinamici).

Altri noti, descritti **a memoria** (non verificati ora, controlla il repo prima di installare):

- **claude-mem** — plugin di memoria persistente: cattura cosa fa Claude nelle sessioni, lo comprime e lo reinietta nelle sessioni successive.
- **Serena** — server MCP di coding semantico basato su LSP: ricerca e modifica simboli invece di leggere file interi; si sovrappone in parte al tool `LSP` e a graphify.
- **ccusage** — CLI che analizza i log locali di Claude Code e mostra consumo di token e costi per giorno/sessione.
- **Repomix** — impacchetta un repo in un singolo file ottimizzato per LLM; utile per dare contesto a modelli senza accesso al filesystem.
- **Firecrawl** (MCP/CLI) — scraping e crawling web che restituisce markdown pulito; alternativa più robusta a WebFetch su siti dinamici.

---

## Fase 11 — Checklist di verifica finale

Apri una sessione nuova e controlla:

- [ ] `theme` scuro, modello `sonnet` di default
- [ ] `/ponytail-help` risponde (ponytail attivo)
- [ ] Tra le skill compaiono `mattpocock-skills:*`, `vercel:*`, `supabase:*`, `commit-commands:*`
- [ ] `graphify --version` funziona da terminale
- [ ] `hf --version` e `gh --version` funzionano da terminale
- [ ] Apri un file `.py` in un progetto → nessun errore se chiedi un'operazione LSP (es. "trova dove è definito X")
- [ ] `/pdf`, `/docx` ecc. **non** vengono proposte da sole, solo se le chiami esplicitamente
- [ ] `huggingface-skills`, `superpowers`, `skill-creator`, `claude-md-management` risultano installati ma spenti (`settings.json` o pannello plugin)
