local GAME_STATE_SCHEMA = {
    type = "object",
    properties = {
        player_hand = {
            type = "array",
            items = {type = "string"},
            description = "List of cards in the player's hand (e.g., 'AH', 'KS')"
        },
        active_jokers = {
            type = "array",
            items = {
                type = "object",
                properties = {
                    name = {type = "string"},
                    value = {type = "number", optional = true},
                    effect = {type = "string", optional = true}
                }
            },
            description = "List of active Jokers with names and effects"
        },
        discard_pile = {
            type = "array",
            items = {type = "string"},
            description = "List of cards in the discard pile"
        },
        played_cards_history = {
            type = "array",
            items = {type = "string"},
            description = "List of cards played in previous rounds/hands"
        },
        current_score = {
            type = "number",
            description = "Player's current score"
        },
        current_blind_info = {
            type = "object",
            properties = {
                name = {type = "string"},
                chips_required = {type = "number"},
                reward = {type = "number"}
            },
            description = "Information about the current blind"
        },
        active_global_modifiers_challenges = {
            type = "array",
            items = {type = "string"},
            description = "List of active global modifiers or challenge rules"
        },
        shop_contents = {
            type = "array",
            items = {
                type = "object",
                properties = {
                    item_type = {type = "string"},
                    name = {type = "string"},
                    cost = {type = "number"}
                }
            },
            description = "Items currently available in the shop"
        },
        current_stakes = {
            type = "number",
            description = "Current stake level"
        },
        other_persistent_game_values = {
            type = "object",
            properties = {},
            additionalProperties = true,
            description = "Placeholder for any other relevant game variables"
        }
    },
    required = {
        "player_hand", "active_jokers", "discard_pile", "played_cards_history",
        "current_score", "current_blind_info", "active_global_modifiers_challenges",
        "shop_contents", "current_stakes"
    }
}

return GAME_STATE_SCHEMA
