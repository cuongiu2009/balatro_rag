# Implementation Plan: Balatro RAG Assistant

**Branch**: `001-balatro-rag-assist` | **Date**: 2026-03-29 | **Spec**: specs/001-balatro-rag-assist/spec.md
**Input**: Feature specification from `/specs/001-balatro-rag-assist/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement a Balatro RAG Assistant to provide real-time game state updates and strategic suggestions via the Love2D Commandline. It will use a Python orchestrator to interact with Love2D via Lua runtime hooking and an LM Studio RAG model for AI analysis, focusing on game stability, JSON data standardization, and low AI response latency. The development will proceed in four phases: Infiltration (Lua Hooking), The Brain (Python RAG & LM Studio), The Messenger (Love2D Commandline display), and Testing & Validation.

## Technical Context

**Language/Version**:
- Python: 3.13.12
- Lua: LuaJIT 2.1 (Love2D engine's embedded Lua version)
**Primary Dependencies**:
- Lua: Luasocket
- Python: LM Studio API client library, ChromaDB client library, FastAPI (for bridging communication between Lua and LM Studio)
**Storage**: ChromaDB (for RAG knowledge base of card/game mechanics)
**Testing**:
- Unit testing: For JSON data serialization/deserialization and RAG logic.
- Integration testing: To measure latency between Lua game and Python orchestrator, and correctness of data flow.
- Stress testing: To monitor VRAM/RAM usage when game and AI run concurrently, ensure no OOM and no Love2D engine freezes (Async Handling).
**Target Platform**: Windows operating system, Love2D environment (Balatro game)
**Project Type**: Game modification (Lua scripts), CLI/Service (Python orchestrator)
**Performance Goals**:
- AI response latency: MUST NOT exceed 3 seconds (from Constitution)
- Game state updates: Displayed within 2 seconds of in-game action (from Spec SC)
- No noticeable frame rate drop or input lag in Balatro (from Spec SC)
**Constraints**:
- Local-first processing: 100% on RTX 5060 via LM Studio API (localhost:1234) (from Constitution)
- Lua intervention: MUST use Runtime Hooking/Global Table G (from Constitution)
- Lua code: MUST be highly modular for easy updates during game patches (from Constitution)
- Data dumping: Event-driven (player choosing cards, ending a round, opening shop) (from Spec Clarifications)
**Scale/Scope**: Single-player game assistance; comprehensive game state extraction and strategic advice.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Result**: Passed

- **I. Game Engine Stability & Local-first Processing**: The plan adheres to prioritizing Love2D stability and local-first processing using Runtime Hooking/Global Table G and LM Studio on RTX 5060.
- **II. Data Standardization & AI Performance**: The plan incorporates JSON data standardization and targets an AI response latency not exceeding 3 seconds.
- **III. In-Game Communication**: The plan ensures analysis results and suggestions are displayed directly on the Love2D Commandline.
- **IV. Modularity & Orchestration**: The plan designates Python as the orchestrator and emphasizes modular Lua intervention code for patch compatibility.

## Project Structure

### Documentation (this feature)

```text
specs/001-balatro-rag-assist/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── python_orchestrator/ # Python project for RAG, LM Studio interaction, and overall control
│   ├── main.py          # Entry point for the Python application
│   ├── rag_model/       # Components related to RAG (ChromaDB, retrieval logic)
│   ├── api_client/      # Code for interacting with LM Studio API
│   └── communication/   # Socket communication with Lua
├── lua_game_hooks/      # Lua scripts for runtime hooking and data extraction
│   ├── init.lua         # Entry point for Lua modifications
│   ├── data_extractor.lua # Logic to extract game state from global tables
│   └── socket_client.lua  # Luasocket client to send data to Python
└── common/              # Shared data structures, constants (e.g., JSON schema for game state)

tests/
├── python/
│   ├── unit/            # Unit tests for Python modules
│   ├── integration/     # Integration tests for Lua-Python communication and AI latency
│   └── stress/          # Stress tests for resource monitoring
├── lua/
│   └── unit/            # Unit tests for Lua hooking and data extraction logic
└── contracts/           # Tests for JSON data standardization
```

**Structure Decision**: A single project structure is chosen, separating Python orchestration and Lua game hooking into distinct subdirectories under `src/`. A dedicated `common/` directory will hold shared data structures like JSON schemas. Testing is organized by language and type (unit, integration, stress, contracts).

## Knowledge Base Management Strategy
The knowledge base (ChromaDB) will be updated when new Balatro cards or mechanics are released. This will be done by re-running the `data_processor.py` and `knowledge_base_builder.py` scripts. A versioning scheme for the knowledge base will be implemented to ensure compatibility.

## Lua Development Guidelines
Lua code must be organized into separate files based on functionality (e.g., `data_extractor.lua`, `socket_client.lua`, `config.lua`). Global variable usage should be minimized, and functions should be self-contained where possible.

## Error Handling Strategy
Lua-side errors (e.g., socket failure) will be logged to the Love2D Commandline. Python-side errors will be logged to a file (`python_orchestrator.log`) and a simplified error message will be sent back to the Love2D Commandline.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
