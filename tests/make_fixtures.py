#!/usr/bin/env python3
"""
Build sanitized fixtures for the smoke test.

Emits:
  fixtures/empty-ai-weekly.json   — page with two tables (Champion + Manager),
                                     one target-user row in each, empty cells.
  fixtures/filled-ai-weekly.json  — same, but Alex's cells have content already
                                     (tests: builder overwrites / preserves others).
  fixtures/user-alex.json         — test user config

No real names, emails, or IDs. Regenerate via `python3 tests/make_fixtures.py`.
"""

import json
from pathlib import Path


TEST_DISPLAY_NAME = "Alex Example"
OTHER_NAME = "Jordan Sample"

HERE = Path(__file__).parent
FIX = HERE / "fixtures"


def text(s, marks=None):
    n = {"type": "text", "text": s}
    if marks:
        n["marks"] = marks
    return n


def strong(s):
    return text(s, [{"type": "strong"}])


def code(s):
    return text(s, [{"type": "code"}])


def paragraph(*children):
    if not children:
        return {"type": "paragraph", "attrs": {"localId": f"empty-{id(children)}"}}
    return {"type": "paragraph", "content": list(children)}


def empty_paragraph(local_id):
    """Match the attr-only-paragraph shape used by Confluence for blank cells."""
    return {"type": "paragraph", "attrs": {"localId": local_id}}


def header_cell(*children):
    return {"type": "tableHeader",
            "attrs": {"colspan": 1, "rowspan": 1, "localId": f"th-{id(children)}"},
            "content": list(children)}


def cell(*children, local_id=None):
    return {"type": "tableCell",
            "attrs": {"colspan": 1, "rowspan": 1, "localId": local_id or f"tc-{id(children)}"},
            "content": list(children)}


def row(*cells, local_id=None):
    return {"type": "tableRow",
            "attrs": {"localId": local_id or f"tr-{id(cells)}"},
            "content": list(cells)}


def heading(level, s):
    return {"type": "heading",
            "attrs": {"level": level, "localId": f"h-{level}-{s[:6]}"},
            "content": [text(s)]}


def _build_page(fill_alex):
    # Champion Weekly Report — 5 columns.
    champ_header = row(
        header_cell(paragraph(strong("Champion"))),
        header_cell(paragraph(strong("Wins this week"))),
        header_cell(paragraph(strong("What didn't work"))),
        header_cell(paragraph(strong("Blockers"))),
        header_cell(paragraph(strong("What mentees should try next"))),
    )
    champ_divider = row(
        cell(paragraph(strong("Company A"))),
        cell(empty_paragraph("div-1")),
        cell(empty_paragraph("div-2")),
        cell(empty_paragraph("div-3")),
        cell(empty_paragraph("div-4")),
    )
    champ_other = row(
        cell(paragraph(text(OTHER_NAME))),
        cell(paragraph(text("Did unrelated work on widget foo."))),
        cell(empty_paragraph("o-1")),
        cell(empty_paragraph("o-2")),
        cell(empty_paragraph("o-3")),
    )
    champ_alex_cells = (
        [cell(paragraph(text(TEST_DISPLAY_NAME)))]
        + (
            [
                cell(paragraph(text("Shipped "), code("/demo-skill"), text(" and onboarded 2 teammates."))),
                cell(paragraph(text("Slow CI runs."))),
                cell(paragraph(text("API key pending."))),
                cell(paragraph(text("Try the new workflow."))),
            ] if fill_alex else [
                cell(empty_paragraph(f"a-{i}")) for i in range(4)
            ]
        )
    )
    champ_alex = row(*champ_alex_cells)

    champion_table = {
        "type": "table",
        "attrs": {"layout": "center", "localId": "champ-tbl"},
        "content": [champ_header, champ_divider, champ_other, champ_alex],
    }

    # Manager Weekly Report — 3 columns.
    mgr_header = row(
        header_cell(paragraph(strong("Manager"))),
        header_cell(paragraph(strong("Wins this week"))),
        header_cell(paragraph(strong("Blockers / concerns"))),
    )
    mgr_alex_cells = (
        [cell(paragraph(text(TEST_DISPLAY_NAME)))]
        + (
            [
                cell(paragraph(text("Team at 80% daily-active on Claude."))),
                cell(paragraph(text("Budget approval for API keys."))),
            ] if fill_alex else [
                cell(empty_paragraph(f"m-{i}")) for i in range(2)
            ]
        )
    )
    mgr_alex = row(*mgr_alex_cells)

    manager_table = {
        "type": "table",
        "attrs": {"layout": "default", "localId": "mgr-tbl"},
        "content": [mgr_header, mgr_alex],
    }

    return {
        "id": "fixture-ai",
        "type": "page",
        "title": "AI Weekly Report for 01 Jun - 05 Jun 2026",
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                heading(3, "Purpose"),
                paragraph(text("Example AI weekly report for testing.")),
                heading(2, "Champion Weekly Report"),
                champion_table,
                heading(2, "Manager Weekly Report"),
                manager_table,
            ],
        },
    }


def make_user_config():
    return {
        "display_name": TEST_DISPLAY_NAME,
        "display_name_overrides": [],
        "atlassian_account_id": "test-alex-001",
        "slack_user_id": "U_ALEX_TEST",
        "github_username": "alex-example",
        "email": "alex@example.test",
        "slack_search_mode": "public",
        "github": {"orgs": ["test-org"]},
        "ai_keywords": ["Claude", "Anthropic", "CLAUDE.md", "AI"],
        "jira_ai_labels": ["AI"],
        "scan_claude_logs": True,
        "claude_log_dir": "~/.claude/projects",
        "cached_at": "2026-06-01",
        "cache_source": "test_fixture",
    }


def main():
    FIX.mkdir(parents=True, exist_ok=True)
    (FIX / "empty-ai-weekly.json").write_text(json.dumps(_build_page(False), indent=2))
    (FIX / "filled-ai-weekly.json").write_text(json.dumps(_build_page(True), indent=2))
    (FIX / "user-alex.json").write_text(json.dumps(make_user_config(), indent=2))
    print(f"Wrote fixtures to {FIX}")


if __name__ == "__main__":
    main()
