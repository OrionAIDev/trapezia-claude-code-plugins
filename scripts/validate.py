"""Validate the marketplace catalog, plugin manifests, and command/skill frontmatter."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
errors = []


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"{path.relative_to(ROOT)}: {e}")
        return None


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        errors.append(f"{path.relative_to(ROOT)}: missing frontmatter")
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return fields


def check_markdown(path):
    fm = frontmatter(path)
    rel = path.relative_to(ROOT)
    if fm and not fm.get("description"):
        errors.append(f"{rel}: frontmatter needs a description")
    effort = fm.get("effort")
    if effort and effort not in EFFORTS and not effort.isdigit():
        errors.append(f"{rel}: invalid effort '{effort}'")


catalog = load_json(ROOT / ".claude-plugin" / "marketplace.json")
if catalog:
    for key in ("name", "owner", "plugins"):
        if key not in catalog:
            errors.append(f"marketplace.json: missing '{key}'")
    names = [p.get("name") for p in catalog.get("plugins", [])]
    if len(names) != len(set(names)):
        errors.append("marketplace.json: duplicate plugin names")
    listed = set()
    for entry in catalog.get("plugins", []):
        name, source = entry.get("name"), entry.get("source")
        if not name or not source:
            errors.append(f"marketplace.json: plugin entry needs name and source: {entry}")
            continue
        pdir = (ROOT / source).resolve()
        listed.add(pdir)
        manifest = load_json(pdir / ".claude-plugin" / "plugin.json")
        if manifest is not None and manifest.get("name") != name:
            errors.append(f"{source}: plugin.json name '{manifest.get('name')}' != catalog name '{name}'")
        md = list(pdir.glob("commands/*.md")) + list(pdir.glob("skills/*/SKILL.md")) + list(pdir.glob("agents/*.md"))
        if not md and not (pdir / "hooks").exists() and not (pdir / ".mcp.json").exists():
            errors.append(f"{source}: plugin has no commands, skills, agents, hooks or MCP servers")
        for f in md:
            check_markdown(f)
    for pdir in (ROOT / "plugins").glob("*/"):
        if pdir.resolve() not in listed:
            errors.append(f"plugins/{pdir.name}: not listed in marketplace.json")

if errors:
    print("\n".join(f"ERROR: {e}" for e in errors))
    sys.exit(1)
print("OK: marketplace and plugins are valid")
