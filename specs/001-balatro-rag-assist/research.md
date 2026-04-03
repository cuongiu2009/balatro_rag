# Research Findings: Balatro RAG Assistant

## Technical Clarifications

### Python Version
**Decision**: Python 3.13.12
**Rationale**: User's specified version.
**Alternatives considered**: Python 3.9, 3.10, 3.11 (not chosen as user provided specific version)

### Lua Version
**Decision**: LuaJIT 2.1
**Rationale**: Targeted for maximum compatibility with Love2D engine as specified by the user.
**Alternatives considered**: Standard Lua versions (not chosen as LuaJIT is more common in Love2D).

### FastAPI Usage
**Decision**: Required (Bridge)
**Rationale**: A FastAPI server will be used to expose an endpoint for the Lua scripts to send game state to, acting as a bridge to the LM Studio RAG model. This provides a clean interface for communication between Lua and Python.
**Alternatives considered**: Not required (direct API calls) - rejected to provide a structured communication layer between Lua and Python.
