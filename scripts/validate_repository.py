"""Validate a standalone public Skill package without private inputs."""
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse
import yaml

ROOT = Path(__file__).resolve().parents[1]
def main():
    errors = []
    result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                            cwd=ROOT, capture_output=True, check=True)
    files = [ROOT / p.decode() for p in result.stdout.split(b"\0") if p]
    body = (ROOT / "SKILL.md").read_text()
    match = re.match(r"^---\n(.*?)\n---\n", body, re.S)
    assert match, "Skill frontmatter missing"
    frontmatter = yaml.safe_load(match[1])
    assert frontmatter["name"] == ROOT.name
    assert 0 < len(frontmatter["description"]) <= 1024
    metadata = yaml.safe_load((ROOT / "agents/openai.yaml").read_text())
    assert "$" + ROOT.name in metadata["interface"]["default_prompt"]
    assert metadata["policy"]["allow_implicit_invocation"] is True
    for key in ("icon_small", "icon_large"):
        assert (ROOT / metadata["interface"][key]).is_file()
    secret_patterns = [r"\bsk-[A-Za-z0-9_-]{20,}\b", r"\bgh[pousr]_[A-Za-z0-9]{20,}\b",
                       r"\bgithub_pat_[A-Za-z0-9_]{20,}\b", r"\borg-[A-Za-z0-9]{16,}\b",
                       re.escape("/" + "Users/") + r"[^/\s]+/",
                       "-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"]
    for path in files:
        assert not path.is_symlink(), f"Symlink: {path.relative_to(ROOT)}"
        if not path.is_file(): continue
        raw = path.read_bytes()
        if b"\0" in raw: continue
        text = raw.decode("utf8")
        for pattern in secret_patterns:
            if re.search(pattern, text):
                errors.append(f"{path.relative_to(ROOT)}: sensitive-data pattern")
        if path.suffix in (".json", ".json3"): json.loads(text)
        elif path.suffix in (".yaml", ".yml"): yaml.safe_load(text)
        elif path.suffix == ".svg": ET.fromstring(text)
        elif path.suffix == ".py": compile(text, str(path), "exec")
        elif path.suffix == ".md":
            for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
                target = target.split()[0].strip("<>")
                parsed = urlparse(target)
                if parsed.scheme or not parsed.path: continue
                if not (path.parent / unquote(parsed.path)).exists():
                    errors.append(f"{path.relative_to(ROOT)}: broken local link {target}")
    assert not errors, "\n".join(errors)
    print("PASS: Skill, metadata, YAML/JSON, SVG, local links, Python syntax and sensitive-data checks")
if __name__ == "__main__":
    main()
