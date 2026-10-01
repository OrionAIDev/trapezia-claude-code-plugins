# trapezia-claude-code-plugins

A Claude Code plugin marketplace: commands, skills and plugins for working with Claude Code.

## Install

```
/plugin marketplace add OrionAIDev/trapezia-claude-code-plugins
/plugin install bro@trapezia-claude-code-plugins
```

## Plugins

| Plugin | What it does |
| --- | --- |
| `bro` | When Claude's last reply was a wall of text or unclear, `/bro` makes it restate the point as a short update to a non-technical boss: what's going on, the decision needed (if any), and its recommendation. Runs at low effort for a fast reply. |

### Use without the plugin system

Copy `plugins/bro/commands/bro.md` into `~/.claude/commands/`.

## Layout

```
.claude-plugin/marketplace.json   # marketplace catalog
plugins/<name>/                   # one plugin per folder
  .claude-plugin/plugin.json
  commands/  skills/  agents/  hooks/
```

## Checks

CI runs `python scripts/validate.py` on every push and pull request; run it locally before committing.

## License

MIT
