# Skills OpenCode in uso

## Skills locali (`~\.config\opencode\skills\`)

| Skill | Provenienza | Repo |
|-------|-------------|------|
| **simplify** | Bundled con oh-my-opencode-slim | [alvinunreal/oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim) |
| **codemap** | Bundled con oh-my-opencode-slim | [alvinunreal/oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim) |
| **clonedeps** | Built-in di OpenCode | [anomalyco/opencode](https://github.com/anomalyco/opencode) |

## Skill aggiuntive

| Skill | Installata in | Repo |
|-------|---------------|------|
| **agent-browser** | `~\.agents\skills\` | [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) |

`agent-browser` si installa globalmente con npm e poi configura la skill:

```bash
npm i -g agent-browser && agent-browser install
```

## Plugin

| Plugin | Repo |
|--------|------|
| **oh-my-opencode-slim** | [alvinunreal/oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim) |

## Come vengono caricate le skills

Le skills sono dichiarate nei preset di `oh-my-opencode-slim.json`. Ogni agente può avere un set specifico di skills abilitate:

| Agente | Skills |
|--------|--------|
| **Orchestrator** | `*` (tutte) |
| **Oracle** | `simplify` |
| **Designer** | `agent-browser` |
| **Librarian, Explorer, Fixer, Observer** | nessuna |

## Comandi utili per le skills

```bash
# Elenca tutte le skills installate
opencode skill list

# Installa una nuova skill
opencode skill install <nome-skill>

# Rimuovi una skill
opencode skill remove <nome-skill>

# Installa agent-browser (globale + skill)
npm i -g agent-browser && agent-browser install
```
