#!/usr/bin/env python3
"""Import CareGraph story documents into GitHub Issues.

The story documents in ``docs/pm/stories/epic-*/e*-s*.md`` are the source of
truth for *content*. GitHub is the source of truth for *state* (open/closed,
assignee, project column).

The import is idempotent: the story identifier (e.g. ``E1-S4``) is the join key
and lives in the issue title. Re-running updates existing issues instead of
creating duplicates.

Examples
--------
    # Preview (writes nothing)
    python scripts/import_stories.py --repo LWSNLab/caregraph --epics 1,2 --dry-run

    # Create / update issues
    python scripts/import_stories.py --repo LWSNLab/caregraph --epics 1,2

    # Specific stories, and add them to a project board
    python scripts/import_stories.py --repo LWSNLab/caregraph --ids E1-S4,E2-S1 \\
        --project-owner LWSNLab --project-number 3
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STORIES_DIR = REPO_ROOT / "docs" / "pm" / "stories"

ID_PATTERN = re.compile(r"E\d+-S\d+")
# Title line:  "# E1-S1 — GKV insurer list"
TITLE_PATTERN = re.compile(r"^#\s+(E\d+-S\d+)\s+[—-]\s+(.*)$")
# Header-table row:  "| **Story Points** | 5 |"
TABLE_FIELD_PATTERN = re.compile(r"^\|\s*\*\*(?P<key>[^*|]+?)\*\*\s*\|\s*(?P<value>.*?)\s*\|\s*$", re.MULTILINE)


# --------------------------------------------------------------------------- #
# Model
# --------------------------------------------------------------------------- #


@dataclass
class Story:
    story_id: str          # E1-S4
    name: str              # "CareGraph-native loader"
    points: str            # "5"
    priority: str          # "High"
    epic: str              # "E1 — Ingestion & ETL"
    status: str            # "✅ Done" / "⏳ Planned"
    kind: str              # "Story" / "Bug" — from the optional **Type** row
    path: Path
    body_source: str = field(repr=False)

    @property
    def epic_key(self) -> str:
        return self.story_id.split("-", 1)[0].lower()  # "e1"

    @property
    def title(self) -> str:
        return f"{self.story_id} — {self.name}"

    @property
    def labels(self) -> list[str]:
        # A bug and a story are read differently: one describes work to plan, the
        # other something that is wrong now. Labelling both "story" hides that.
        labels = [slug(self.kind) or "story", f"epic:{self.epic_key}"]
        if self.points.isdigit():
            labels.append(f"points:{self.points}")
        if self.priority:
            labels.append(f"priority:{slug(self.priority)}")
        return labels

    @property
    def is_done(self) -> bool:
        return "✅" in self.status or "done" in self.status.lower()

    @property
    def is_abandoned(self) -> bool:
        """Decided against, rather than finished — e.g. "❌ Won't do"."""
        return "❌" in self.status or "won\u0027t do" in self.status.lower()

    @property
    def is_closed(self) -> bool:
        return self.is_done or self.is_abandoned

    @property
    def close_reason(self) -> str:
        """GitHub distinguishes the two, and for an abandoned story that
        distinction is the whole content: it was decided, not delivered."""
        return "not planned" if self.is_abandoned else "completed"

    def body(self, source_repo: str | None) -> str:
        """Issue body: the story without its title, breadcrumb and Status row.

        Status is deliberately dropped — in GitHub the issue state is the truth.
        """
        lines = []
        for line in self.body_source.splitlines():
            if TITLE_PATTERN.match(line):          # drop the "# E1-S1 — …" heading
                continue
            if line.lstrip().startswith("> ←"):    # drop the breadcrumb line
                continue
            if re.match(r"^\|\s*\*\*Status\*\*\s*\|", line):  # drop the Status table row
                continue
            lines.append(line)

        body = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()

        rel = self.path.relative_to(REPO_ROOT).as_posix()
        if source_repo:
            link = f"https://github.com/{source_repo}/blob/main/{rel}"
            footer = f"Source of truth for this description: [`{rel}`]({link})"
        else:
            footer = f"Source of truth for this description: `{rel}`"
        return f"{body}\n\n---\n\n_{footer}_\n"


def slug(value: str) -> str:
    value = value.lower().replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def sort_key(story_id: str) -> tuple[int, int]:
    epic, story = re.findall(r"\d+", story_id)[:2]
    return int(epic), int(story)


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #


def parse_story(path: Path) -> Story | None:
    text = path.read_text(encoding="utf-8")

    title_match = next(
        (TITLE_PATTERN.match(line) for line in text.splitlines() if TITLE_PATTERN.match(line)),
        None,
    )
    if title_match is None:
        return None

    fields = {m.group("key").strip(): m.group("value").strip() for m in TABLE_FIELD_PATTERN.finditer(text)}

    return Story(
        story_id=title_match.group(1),
        name=title_match.group(2).strip(),
        points=fields.get("Story Points", "?"),
        priority=fields.get("Priority", ""),
        epic=fields.get("Epic", "unknown"),
        status=fields.get("Status", ""),
        kind=fields.get("Type", "Story"),
        path=path,
        body_source=text,
    )


def load_stories(stories_dir: Path) -> dict[str, Story]:
    stories: dict[str, Story] = {}
    for path in sorted(stories_dir.glob("epic-*/e*-s*.md")):
        story = parse_story(path)
        if story is None:
            print(f"  skipped (no valid story title): {path}", file=sys.stderr)
            continue
        if story.story_id in stories:
            raise SystemExit(f"Duplicate story id {story.story_id}: {path}")
        stories[story.story_id] = story
    return stories


# --------------------------------------------------------------------------- #
# GitHub (via the `gh` CLI)
# --------------------------------------------------------------------------- #


def gh(*args: str, check: bool = True) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        raise SystemExit(f"gh {' '.join(args)}\n{result.stderr.strip()}")
    return result.stdout.strip()


def ensure_auth() -> None:
    result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit("gh is not authenticated. Run 'gh auth login' first.")


def existing_issues(repo: str) -> dict[str, dict]:
    """Map story id -> issue, based on the id prefix in the title."""
    raw = gh("issue", "list", "--repo", repo, "--state", "all",
             "--limit", "1000", "--json", "number,title,url,state")
    found: dict[str, dict] = {}
    for issue in json.loads(raw or "[]"):
        match = ID_PATTERN.match(issue["title"])
        if match:
            found[match.group(0)] = issue
    return found


def ensure_labels(repo: str, labels: set[str], dry_run: bool) -> None:
    raw = gh("label", "list", "--repo", repo, "--limit", "300", "--json", "name")
    have = {item["name"] for item in json.loads(raw or "[]")}
    missing = sorted(labels - have)
    if not missing:
        return

    print(f"Creating labels ({len(missing)}): {', '.join(missing)}")
    if dry_run:
        return

    palette = {"story": "1d76db", "epic": "5319e7", "points": "c5def5", "priority": "d93f0b"}
    for name in missing:
        colour = palette.get(name.split(":", 1)[0], "ededed")
        gh("label", "create", name, "--repo", repo, "--color", colour, "--force")


def add_to_project(owner: str, number: str, url: str) -> None:
    gh("project", "item-add", number, "--owner", owner, "--url", url)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True, help="Target repo for the issues, e.g. LWSNLab/caregraph")
    parser.add_argument("--stories-dir", type=Path, default=STORIES_DIR, help="Directory holding the epic folders")
    parser.add_argument("--epics", help="Comma list of epic numbers, e.g. 1,2")
    parser.add_argument("--ids", help="Comma list of concrete story ids, e.g. E1-S4,E2-S1")
    parser.add_argument("--all", action="store_true", help="All stories")
    parser.add_argument("--project-owner", help="Project owner (user or org)")
    parser.add_argument("--project-number", help="Project number")
    parser.add_argument("--source-repo", default="LWSNLab/CareGraph_Doc",
                        help="Repo of the story docs, for the source link in the issue body")
    parser.add_argument("--close-done", action="store_true",
                        help="Close issues whose story status is ✅ Done")
    parser.add_argument("--dry-run", action="store_true", help="Show only, write nothing")
    args = parser.parse_args()

    if sum(bool(x) for x in (args.epics, args.ids, args.all)) != 1:
        raise SystemExit("Pick exactly one selection: --epics, --ids or --all")

    stories = load_stories(args.stories_dir)
    if not stories:
        raise SystemExit(f"No stories found under {args.stories_dir}")

    if args.all:
        wanted = list(stories)
    elif args.ids:
        wanted = [s.strip() for s in args.ids.split(",") if s.strip()]
    else:
        epics = {int(e) for e in args.epics.split(",")}
        wanted = [sid for sid in stories if sort_key(sid)[0] in epics]

    wanted = sorted(dict.fromkeys(wanted), key=sort_key)

    unknown = [i for i in wanted if i not in stories]
    if unknown:
        raise SystemExit(f"Unknown story ids: {', '.join(unknown)}")

    selected = [stories[i] for i in wanted]
    points = sum(int(s.points) for s in selected if s.points.isdigit())

    mode = "DRY RUN — nothing is written" if args.dry_run else "WRITE MODE"
    print(f"{mode}\n")
    print(f"Repo:    {args.repo}")
    print(f"Stories: {len(selected)}  ({points} story points)")
    if args.project_number:
        print(f"Project: {args.project_owner}/{args.project_number}")
    print()

    ensure_auth()

    labels = {label for story in selected for label in story.labels}
    ensure_labels(args.repo, labels, args.dry_run)
    print()

    known = existing_issues(args.repo)
    created = updated = 0

    for story in selected:
        issue = known.get(story.story_id)
        body = story.body(args.source_repo)

        if issue:
            print(f"  update  #{issue['number']:<5} {story.title}")
            updated += 1
            url = issue["url"]
            if not args.dry_run:
                gh("issue", "edit", str(issue["number"]), "--repo", args.repo,
                   "--title", story.title, "--body", body,
                   *sum((["--add-label", label] for label in story.labels), []))
                if args.close_done and story.is_closed and issue.get("state") == "OPEN":
                    gh("issue", "close", str(issue["number"]), "--repo", args.repo,
                       "--reason", story.close_reason)
        else:
            print(f"  create  {'':<6} {story.title}")
            created += 1
            url = ""
            if not args.dry_run:
                url = gh("issue", "create", "--repo", args.repo,
                         "--title", story.title, "--body", body,
                         *sum((["--label", label] for label in story.labels), []))
                if args.close_done and story.is_closed:
                    gh("issue", "close", url, "--repo", args.repo,
                       "--reason", story.close_reason)

        if args.project_number and args.project_owner and url and not args.dry_run:
            add_to_project(args.project_owner, args.project_number, url)

    print()
    print(f"to create: {created}")
    print(f"to update: {updated}")
    if args.dry_run:
        print("\nNothing written. Re-run without --dry-run to apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
