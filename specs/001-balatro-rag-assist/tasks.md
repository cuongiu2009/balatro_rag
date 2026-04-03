# Tasks: Balatro RAG Assistant

**Input**: Design documents from `/specs/001-balatro-rag-assist/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The plan includes dedicated test tasks as part of each user story phase and the final phase.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create the project directory structure as per `plan.md`'s "Source Code (repository root)" section.
- [X] T002 Initialize Python virtual environment and `requirements.txt` in `src/python_orchestrator/`. `src/python_orchestrator/requirements.txt`
- [X] T003 Add initial Python dependencies to `requirements.txt` (`FastAPI`, `uvicorn`, `ChromaDB`, `requests` or LM Studio API client). `src/python_orchestrator/requirements.txt`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Define the `GameState JSON Schema` in `src/common/game_state_schema.py` (Python representation) and `src/common/game_state_schema.lua` (Lua representation).
- [X] T005 Create Python FastAPI server `main.py` in `src/python_orchestrator/` to listen for Lua connections on `localhost:5000`. `src/python_orchestrator/main.py`
- [X] T006 Implement basic Lua `Luasocket` client in `src/lua_game_hooks/socket_client.lua` to connect to `localhost:5000`. `src/lua_game_hooks/socket_client.lua`
- [X] T007 Implement a Python communication module `src/python_orchestrator/communication/socket_server.py` to handle incoming JSON game state. `src/python_orchestrator/communication/socket_server.py`
- [X] T008 Set up initial ChromaDB client and connection in `src/python_orchestrator/rag_model/chromadb_client.py`. `src/python_orchestrator/rag_model/chromadb_client.py`
- [X] T009 Implement a basic LM Studio API client in `src/python_orchestrator/api_client/lm_studio_client.py` and verify successful connection to the `localhost:1234` endpoint. `src/python_orchestrator/api_client/lm_studio_client.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Real-time Game State Update (Priority: P1) 🎯 MVP

**Goal**: As a Balatro player, I want to see my current game state (hand, functional cards, remaining deck) updated in real-time, so I can make informed decisions.

**Independent Test**: Starting a game, performing actions, verifying that the displayed game state reflects the in-game reality.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Create a unit test for Lua `data_extractor.lua` to ensure correct extraction and JSON serialization. `tests/lua/unit/test_data_extractor.lua`
- [X] T011 [US1] Create an integration test to verify real-time data flow from Lua to Python and successful logging. `tests/python/integration/test_lua_python_data_flow.py`

### Implementation for User Story 1

- [X] T012 [P] [US1] Implement Lua `data_extractor.lua` to hook into Love2D global tables and extract comprehensive game state data. `src/lua_game_hooks/data_extractor.lua`
- [X] T013 [P] [US1] Integrate Lua `init.lua` into Balatro's `main.lua` to load `data_extractor.lua` and `socket_client.lua` for event-driven data extraction.
- [X] T014 [P] [US1] Modify `src/lua_game_hooks/socket_client.lua` to serialize extracted game state into JSON and send it to the Python server. `src/lua_game_hooks/socket_client.lua`
- [X] T015 [US1] Update Python `socket_server.py` to receive and deserialize JSON game state, and log it to verify. `src/python_orchestrator/communication/socket_server.py`
- [X] T016 [US1] Implement a basic display mechanism in Love2D Commandline via Lua `init.lua` to show a confirmation of data transmission. `src/lua_game_hooks/init.lua`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Receive Suggested Next Moves (Priority: P2)

**Goal**: As a Balatro player, I want to receive suggestions for optimal next moves based on my current game state.

**Independent Test**: Observing game state, then receiving and evaluating the suggested moves against strategic principles of Balatro, without needing real-time updates.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T017 [US2] Create a unit test for `rag_processor.py` to verify prompt formulation and that the response is parsed into the required JSON suggestion format, strictly matching the Suggestion JSON Schema in `data-model.md`. `tests/python/unit/test_rag_processor.py`
- [X] T018 [US2] Create an integration test to verify the full AI suggestion pipeline returns a structured JSON suggestion that is correctly displayed by Lua, strictly matching the Suggestion JSON Schema in `data-model.md`. `tests/python/integration/test_ai_suggestion_pipeline.py`
- [X] T018a [US2] Create a unit test for `lm_studio_client.py`'s `get_suggestion` method to verify its interaction with the LM Studio API and its parsing/error handling of responses. `tests/python/unit/test_lm_studio_client.py`

### Implementation for User Story 2

- [X] T019 [P] [US2] Design the entity-based chunking strategy for the RAG knowledge base. `docs/rag_chunking_strategy.md`
- [X] T020 [P] [US2] Develop a Python script to process raw Balatro game data into entity-based chunks (Joker, Tarot, Planet, etc.), preparing it for vectorization. `src/python_orchestrator/rag_model/data_processor.py`
- [X] T021 [P] [US2] Update the knowledge base builder (`knowledge_base_builder.py`) to use the processed entity chunks, vectorize them, and populate ChromaDB. `src/python_orchestrator/rag_model/knowledge_base_builder.py`
- [X] T022 [P] [US2] Implement RAG logic in `rag_processor.py` to use the entity-chunked ChromaDB and formulate prompts that request structured JSON output for LM Studio. `src/python_orchestrator/rag_model/rag_processor.py`
- [X] T023 [US2] Update `lm_studio_client.py` to parse responses and format them into the required JSON structure for suggestions (as per SC-003 and Suggestion JSON Schema), with robust error handling for malformed responses. `src/python_orchestrator/api_client/lm_studio_client.py`
- [X] T024 [US2] Integrate RAG logic into the `main.py` FastAPI endpoint to trigger AI suggestions and return the JSON response conforming to the Suggestion JSON Schema. `src/python_orchestrator/main.py`
- [X] T025 [US2] Implement a mechanism in Lua `init.lua` to receive and parse the JSON suggestion, then display it neatly on the Love2D Commandline. `src/lua_game_hooks/init.lua`

**Checkpoint**: All user stories should now be independently functional

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T026 [P] Refine error handling and logging across Lua and Python components.
- [ ] T027 [P] Define and implement the monitoring methodology for FPS and input lag using RivaTuner or Love2D's built-in counter. `tests/python/stress/performance_monitor.py`
- [ ] T028 [P] Conduct stress tests to verify performance against SC-004 thresholds. `tests/python/stress/test_resource_usage.py`
- [ ] T029 [P] Review and optimize code for performance in both Lua and Python components.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3+)**: Depend on Foundational completion
- **Polish (Final Phase)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories
- **User Story 2 (P2)**: No dependencies on other stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Entity/Data processing tasks before RAG logic
- RAG logic before API integration

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2
2. Complete Phase 3: User Story 1
3. Test User Story 1 independently

### Incremental Delivery

1. Complete Setup + Foundational
2. Add User Story 1 → Test → Deploy/Demo (MVP!)
3. Add User Story 2 → Test → Deploy/Demo
4. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks can run in parallel.
- [Story] label maps a task to a user story.
- Each user story is independently completable and testable.
