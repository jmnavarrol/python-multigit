# AI Docs Language Policy

## Purpose
This policy ensures that AI-mediated development support documentation remains consistently written in English.

## Scope
This policy applies to Markdown files used to guide AI-assisted development workflows, including but not limited to:
- AGENTS.md
- docs/AI_DEVELOPMENT_PLAYBOOK.md
- docs/AI_DOCS_LANGUAGE_POLICY.md

## Rule
All content in scoped files must be written in English, including:
- Titles and headings
- Body text
- Action checklists and process notes
- Update notes added during refactors

## Enforcement
- Automated check script: tools/ai/check_docs_language.py
- Recommended execution: VS Code task AI: Check docs language

If the checker fails, update the affected file(s) to English before merging.

## Extending Scope
When adding a new AI support Markdown file, update the list in tools/ai/check_docs_language.py so the rule stays enforced by default.
