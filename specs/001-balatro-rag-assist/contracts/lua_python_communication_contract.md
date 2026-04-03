# Lua-Python Communication Contract

## 1. Lua to Python (Game State Transmission)

**Purpose**: Transmit current game state from the Love2D game (Lua) to the Python orchestrator.

**Method**: TCP Socket communication using `Luasocket`.

**Endpoint**:
-   **Lua Client**: Connects to `localhost` on a predefined port (e.g., `5000`).
-   **Python Server**: Listens on `localhost` on the same predefined port (`5000`).

**Data Format**: JSON string, conforming to the `GameState JSON Schema` defined in `data-model.md`.

**Transmission Trigger**: Event-driven, on specific in-game events (player choosing cards, ending a round, opening the shop).

**Example Data (JSON)**:
```json
{
  "player_hand": ["AH", "KS", "QC"],
  "active_jokers": [{"name": "Joker 1", "effect": "Multiply by 2"}],
  "discard_pile": ["2S", "3D"],
  "played_cards_history": ["4C", "5H"],
  "current_score": 1200,
  "current_blind_info": {"name": "Small Blind", "chips_required": 300, "reward": 10},
  "active_global_modifiers_challenges": [],
  "shop_contents": [{"item_type": "card", "name": "5D", "cost": 3}],
  "current_stakes": 1
}
```

## 2. Python to Lua (Analysis Results/Suggestions)

**Purpose**: Display strategic advice and analysis results from the Python orchestrator to the player within the Love2D game.

**Method**: Love2D Commandline output. The Python script will likely write to stdout, which is then captured by the Love2D Commandline (or a mechanism Love2D exposes for external input).

**Data Format**: JSON string, conforming to a defined schema for AI suggestions.

**Transmission Trigger**: When the Python RAG model generates a suggestion based on the received game state.

**Example Output (Love2D Commandline)**:
```json
{
  "action": "Play",
  "cards": ["AH", "4H", "5H", "6H", "7H"],
  "estimated_score": 1500,
  "win_chance": 85.5
}
```

## 3. Python to LM Studio (RAG Model Interaction)

**Purpose**: Send structured queries to the local LM Studio RAG model and receive responses.

**Method**: HTTP POST requests to the LM Studio API endpoint.

**Endpoint**: `http://localhost:1234/v1/chat/completions` (or similar, as configured by LM Studio).

**Data Format (Request)**: JSON payload conforming to LM Studio's Chat Completions API specification (e.g., messages array, model name, temperature).

**Data Format (Response)**: JSON payload conforming to LM Studio's Chat Completions API response specification.

**Transmission Trigger**: When the Python orchestrator needs to query the RAG model for strategic advice based on the current game state.
