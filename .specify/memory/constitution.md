<!--
  Sync Impact Report:
  Version change: None → 1.0.0
  List of modified principles: All new
  Added sections: None
  Removed sections: PRINCIPLE_5, SECTION_2, SECTION_3 placeholders removed
  Templates requiring updates:
    - .specify/templates/plan-template.md: ⚠ pending
    - .specify/templates/spec-template.md: ⚠ pending
    - .specify/templates/tasks-template.md: ⚠ pending
    - .specify/templates/commands/*.md: ⚠ pending
  Follow-up TODOs: Ensure dependent templates are updated to reflect these principles.
-->
# Balatro RAG Assistant Constitution

## Core Principles

### I. Game Engine Stability & Local-first Processing
Prioritize Love2D Game Engine stability. Lua file intervention MUST use Runtime Hooking/Global Table G to prevent frame drops. Processing MUST be 100% local-first on RTX 5060 via LM Studio API (localhost:1234).

### II. Data Standardization & AI Performance
Extracted data (hand cards, Jokers, played/discarded moves) MUST be standardized as JSON. RAG system MUST implement chunking by card/game mechanism for accurate retrieval. AI response latency MUST NOT exceed 3 seconds.

### III. In-Game Communication
Analysis results and action suggestions MUST be communicated back and displayed directly on the game's Love2D Commandline.

### IV. Modularity & Orchestration
Python MUST be used as the central orchestrator. Lua intervention code MUST be highly modular to facilitate easy updates during game patches.

## Governance
This Constitution supersedes all other practices. Amendments require a documented proposal, team approval, and a plan for migration. All code changes and feature implementations MUST adhere to these principles. Compliance will be verified during code reviews.

**Version**: 1.0.0 | **Ratified**: 2026-03-29 | **Last Amended**: 2026-03-29
