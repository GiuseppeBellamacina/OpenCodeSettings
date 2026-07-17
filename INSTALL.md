# Installazione di OpenCode

- **Repo ufficiale:** <https://github.com/anomalyco/opencode>
- **Versione installata:** v1.17.7 (globale via npm)

## Prerequisiti

- **Node.js** (versione 18+ consigliata)
- **npm** (incluso con Node.js)

## Installazione globale via npm

```bash
npm i -g opencode-ai
```

Verifica l'installazione:

```bash
opencode --version
```

## Dipendenze del plugin

Nella directory `~\.config\opencode\` è presente un `package.json` con le dipendenze del plugin:

```json
{
  "dependencies": {
    "@opencode-ai/plugin": "1.15.3"
  }
}
```

Per installarle:

```bash
cd ~\.config\opencode
npm install
```

## oh-my-opencode-slim

Plugin per la gestione di preset multi-modello e configurazione degli agenti.

- **Repo:** <https://github.com/alvinunreal/oh-my-opencode-slim>
- **Schema:** `https://unpkg.com/oh-my-opencode-slim@latest/oh-my-opencode-slim.schema.json`

### Installazione

```bash
# Metodo consigliato — installazione interattiva
bunx oh-my-opencode-slim install

# Installazione non interattiva con preset
bunx oh-my-opencode-slim install --no-tui --preset=cosmic

# O in alternativa da npm
npm install -g oh-my-opencode-slim
```

### Configurazione

Abilitato in `opencode.json` tramite:

```json
{
  "plugin": ["oh-my-opencode-slim"]
}
```

Il file di configurazione `oh-my-opencode-slim.json` contiene i preset per diversi provider (cosmic, openai, opencode-go).

## Configurazione directory

OpenCode legge la configurazione da:

- **Windows:** `%USERPROFILE%\.config\opencode\` → `C:\Users\<utente>\.config\opencode\`
- **Linux/macOS:** `~/.config/opencode/`

### Struttura della directory di configurazione

```
~\.config\opencode\
├── opencode.json              # Configurazione principale
├── tui.json                   # Configurazione TUI (plugin)
├── oh-my-opencode-slim.json   # Plugin oh-my-opencode-slim
├── package.json               # Dipendenze npm del plugin
├── package-lock.json
├── .gitignore
└── skills/                    # Skills locali
    ├── clonedeps/             # Skill built-in di OpenCode
    ├── codemap/               # Skill bundled con oh-my-opencode-slim
    └── simplify/              # Skill bundled con oh-my-opencode-slim
```

## Skills

Le skills sono caricate da `~\.config\opencode\skills\`. Skills aggiuntive (come `agent-browser`) possono essere installate da `~\.agents\skills\`.

Per installare una skill:

```bash
opencode skill install <nome-skill>
```

## Comandi utili

| Comando                            | Descrizione                                |
| ---------------------------------- | ------------------------------------------ |
| `opencode`                         | Avvia OpenCode in modalità TUI             |
| `opencode --version`               | Mostra la versione                         |
| `opencode skill list`              | Elenca le skills disponibili               |
| `opencode skill install <nome>`    | Installa una skill                         |
| `opencode config`                  | Apre la configurazione                     |
| `bunx oh-my-opencode-slim install` | (Re)installa/configura oh-my-opencode-slim |
| `bunx oh-my-opencode-slim doctor`  | Diagnostica del plugin                     |
