# Data Model: Balatro RAG Assistant

## Key Entities

### Player
- **Description**: Represents the user playing Balatro.
- **Attributes**:
    - `current_hand`: List of cards the player currently holds.
    - `active_jokers`: List of active Joker cards and their effects.
    - `other_stats`: Various game-relevant statistics (e.g., chips, multiplier).

### Deck
- **Description**: Represents the in-game deck of cards.
- **Attributes**:
    - `remaining_cards_count`: Number of cards left in the deck.
    - `discard_pile`: List of cards in the discard pile.

### Game State
- **Description**: A comprehensive snapshot of the current game, transmitted from Lua to Python. The specific variables extracted depend on the game phase.
- **Attributes by Phase (to be included in JSON schema)**:

    **1. In-Round (During a hand)**
    *   `G.hand`: The player's current hand of cards.
    *   `G.jokers`: All active Joker cards.
    *   `G.consumeables`: All active consumable cards (e.g., Tarot, Planet).
    *   `G.GAME.round_resets.hands`: Number of hands remaining.
    *   `G.GAME.round_resets.discards`: Number of discards remaining.
    *   `G.GAME.dollars`: Current amount of money.
    *   `G.GAME.blind`: Information on the current blind.
    *   `G.GAME.round`: Current round number.

    **2. Shop Phase (Between rounds)**
    *   All variables from the "In-Round" phase.
    *   `G.shop.cards`: All cards available for purchase in the shop.
    *   `G.pack_context`: Information about available booster packs.

    **3. Post-Round Summary**
    *   `G.GAME.dollars`: Final money count.
    *   `G.jokers`: Final state of all Jokers.
    *   Any newly acquired cards or items.

- **Relationships**:
    - Aggregates data from various global game tables (`G`).

### LMStudio Model
- **Description**: The local RAG model, responsible for processing `Game State` and generating strategic advice.
- **Attributes**: None directly, as it's an external service.

### Lua Files
- **Description**: Source of real-time game state information, accessed via Runtime Hooking.
- **Attributes**: None directly.

### Love2D Command Line
- **Description**: Output interface for displaying assistance.
- **Attributes**: None directly.

## GameState JSON Schema (Conceptual)

The `Game State` data MUST be standardized as JSON for transmission from Lua to Python. A conceptual schema includes:

```json
{
  "type": "object",
  "properties": {
    "player_hand": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of cards in the player's hand (e.g., 'AH', 'KS')"
    },
    "active_jokers": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "value": { "type": "number", "optional": true },
          "effect": { "type": "string", "optional": true }
        }
      },
      "description": "List of active Jokers with names and effects"
    },
    "discard_pile": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of cards in the discard pile"
    },
    "played_cards_history": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of cards played in previous rounds/hands"
    },
    "current_score": {
      "type": "number",
      "description": "Player's current score"
    },
    "current_blind_info": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "chips_required": { "type": "number" },
        "reward": { "type": "number" }
      },
      "description": "Information about the current blind"
    },
    "active_global_modifiers_challenges": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of active global modifiers or challenge rules"
    },
    "shop_contents": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "item_type": { "type": "string" },
          "name": { "type": "string" },
          "cost": { "type": "number" }
        }
      },
      "description": "Items currently available in the shop"
    },
    "current_stakes": {
      "type": "number",
      "description": "Current stake level"
    },
    "other_persistent_game_values": {
      "type": "object",
      "properties": {},
      "additionalProperties": true,
      "description": "Placeholder for any other relevant game variables"
    }
  },
  "required": [
    "player_hand", "active_jokers", "discard_pile", "played_cards_history",
    "current_score", "current_blind_info", "active_global_modifiers_challenges",
    "shop_contents", "current_stakes"
  ]
}
```

## Suggestion JSON Schema (Conceptual)

The AI suggestion data MUST be standardized as JSON for transmission from Python to Lua. A conceptual schema includes:

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "description": "Recommended action (e.g., 'Play', 'Discard', 'Hold')"
    },
    "card_ids": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of specific Card IDs involved in the action"
    },
    "location_indices": {
      "type": "array",
      "items": { "type": "number" },
      "description": "List of 1-based indices for cards in G.hand (if applicable)"
    },
    "estimated_score": {
      "type": "number",
      "description": "Estimated score (Chips/Mult) if the action is performed"
    },
    "win_chance": {
      "type": "number",
      "description": "Percentage chance of winning the current round (0-100)"
    },
    "rationale": {
      "type": "string",
      "optional": true,
      "description": "Brief explanation for the suggestion"
    }
  },
  "required": [
    "action", "card_ids", "location_indices", "estimated_score", "win_chance"
  ]
}
```