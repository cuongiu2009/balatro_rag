import json
import os

# Placeholder for raw game data. In a real scenario, this would be loaded from
# game files, a database, or external sources.
# For demonstration, we'll use a simplified structure based on Balatro entities.
RAW_GAME_DATA = {
    "jokers": [
        {
            "name": "Joker",
            "description": "Playing card types give X0.5 Mult.",
            "mechanics": "Each distinct playing card type (e.g., Spades, Hearts, Clubs, Diamonds) present in your hand gives X0.5 Multiplier.",
            "synergies": ["High Card strategy", "diverse hands"],
            "drawbacks": ["less effective with mono-suit hands"],
            "category": ["Multiplier"],
            "rarity": "common"
        },
        {
            "name": "Abstract Joker",
            "description": "Gives X0.1 Mult for each card in hand.",
            "mechanics": "Multiplier scales with the number of cards currently in your hand.",
            "synergies": ["large hand size", "hand size modifiers"],
            "drawbacks": ["small hand sizes"],
            "category": ["Multiplier", "Hand Size"],
            "rarity": "uncommon"
        }
    ],
    "tarot_cards": [
        {
            "name": "The Fool",
            "description": "Generates a random Joker.",
            "mechanics": "Upon use, adds a random Joker to your hand.",
            "strategic_use": ["early game joker acquisition", "desperation for a good joker"],
        },
        {
            "name": "The Magician",
            "description": "Upgrade a random card to a bonus card.",
            "mechanics": "Upgrades one of your existing playing cards to a Bonus Card, giving it +30 Chips.",
            "strategic_use": ["boosting score of key cards"],
        }
    ],
    "planet_cards": [
        {
            "name": "Jupiter",
            "description": "Upgrades Straight.",
            "poker_hand_affected": "Straight"
        }
    ],
    "vouchers": [
        {
            "name": "Honeypot",
            "description": "Start each run with $5.",
            "mechanics": "Grants an additional $5 at the start of every new run.",
        }
    ],
    "poker_hands": [
        {
            "name": "Pair",
            "rules": "Two cards of the same rank.",
            "base_chips": 20,
            "base_mult": 2,
            "level_scaling": "Chips +10, Mult +1 per level.",
            "strategic_importance": "Basic scoring hand, easy to make."
        },
        {
            "name": "Flush",
            "rules": "Five cards of the same suit.",
            "base_chips": 35,
            "base_mult": 4,
            "level_scaling": "Chips +15, Mult +1.5 per level.",
            "strategic_importance": "Good mid-game hand, strong scaling."
        }
    ],
    "mechanics": [
        {
            "name": "Debuffed",
            "explanation": "Cards are Debuffed by certain Boss Blinds or effects, making them worth 0 Chips and X1 Mult.",
            "interactions": "Negates scoring from chips and multipliers on affected cards."
        },
        {
            "name": "Glass Card",
            "explanation": "A playing card that has a chance to shatter when scored.",
            "interactions": "Can be destroyed after being played; provides X2 Mult while in hand."
        }
    ],
    "boss_blinds": [
        {
            "name": "The Hook",
            "description": "Playing cards with face values are debuffed.",
            "mechanics": "All Face Cards (J, Q, K) become Debuffed, scoring 0 Chips and X1 Mult.",
            "strategic_considerations": "Avoid playing Face Cards, focus on number cards or Jokers that ignore card values."
        }
    ]
}


def process_joker_data(joker_raw: dict) -> dict:
    """Processes raw Joker data into an entity-based chunk."""
    content = (
        f"Name: {joker_raw['name']}
"
        f"Description: {joker_raw['description']}
"
        f"Mechanics: {joker_raw.get('mechanics', 'N/A')}
"
        f"Synergies: {', '.join(joker_raw.get('synergies', ['N/A']))}
"
        f"Drawbacks: {', '.join(joker_raw.get('drawbacks', ['N/A']))}"
    )
    return {
        "content": content,
        "metadata": {
            "entity_type": "joker",
            "name": joker_raw["name"],
            "categories": joker_raw.get("category", []),
            "rarity": joker_raw.get("rarity", "unknown")
        }
    }

def process_tarot_data(tarot_raw: dict) -> dict:
    """Processes raw Tarot card data into an entity-based chunk."""
    content = (
        f"Name: {tarot_raw['name']}
"
        f"Description: {tarot_raw['description']}
"
        f"Mechanics: {tarot_raw.get('mechanics', 'N/A')}
"
        f"Strategic Use: {', '.join(tarot_raw.get('strategic_use', ['N/A']))}"
    )
    return {
        "content": content,
        "metadata": {
            "entity_type": "tarot",
            "name": tarot_raw["name"]
        }
    }

def process_planet_data(planet_raw: dict) -> dict:
    """Processes raw Planet card data into an entity-based chunk."""
    content = (
        f"Name: {planet_raw['name']}
"
        f"Description: {planet_raw['description']}
"
        f"Poker Hand Affected: {planet_raw.get('poker_hand_affected', 'N/A')}"
    )
    return {
        "content": content,
        "metadata": {
            "entity_type": "planet",
            "name": planet_raw["name"],
            "poker_hand_affected": planet_raw.get("poker_hand_affected")
        }
    }

def process_voucher_data(voucher_raw: dict) -> dict:
    """Processes raw Voucher data into an entity-based chunk."""
    content = (
        f"Name: {voucher_raw['name']}
"
        f"Description: {voucher_raw['description']}
"
        f"Mechanics: {voucher_raw.get('mechanics', 'N/A')}"
    )
    return {
        "content": content,
        "metadata": {
            "entity_type": "voucher",
            "name": voucher_raw["name"]
        }
    }

def process_poker_hand_data(poker_hand_raw: dict) -> dict:
    """Processes raw Poker Hand data into an entity-based chunk."""
    content = (
        f"Name: {poker_hand_raw['name']}
"
        f"Rules: {poker_hand_raw['rules']}
"
        f"Base Chips: {poker_hand_raw['base_chips']}
"
        f"Base Multiplier: {poker_hand_raw['base_mult']}
"
        f"Level Scaling: {poker_hand_raw.get('level_scaling', 'N/A')}
"
        f"Strategic Importance: {poker_hand_raw.get('strategic_importance', 'N/A')}"
    )
    return {
        "content": content,
        "metadata": {
            "entity_type": "poker_hand",
            "name": poker_hand_raw["name"]
        }
    }

def process_mechanic_data(mechanic_raw: dict) -> dict:
    """Processes raw Mechanic data into an entity-based chunk."""
    content = (
        f"Name: {mechanic_raw['name']}
"
        f"Explanation: {mechanic_raw['explanation']}
"
        f"Interactions: {mechanic_raw.get('interactions', 'N/A')}"
    )
    return {
        "content": content,
        "metadata": {
            "entity_type": "mechanic",
            "name": mechanic_raw["name"]
        }
    }

def process_boss_blind_data(boss_blind_raw: dict) -> dict:
    """Processes raw Boss Blind data into an entity-based chunk."""
    content = (
        f"Name: {boss_blind_raw['name']}
"
        f"Description: {boss_blind_raw['description']}
"
        f"Mechanics: {boss_blind_raw.get('mechanics', 'N/A')}
"
        f"Strategic Considerations: {boss_blind_raw.get('strategic_considerations', 'N/A')}"
    )
    return {
        "content": content,
        "metadata": {
            "entity_type": "boss_blind",
            "name": boss_blind_raw["name"]
        }
    }

def process_raw_data(raw_data: dict) -> list:
    """
    Orchestrates the processing of raw game data into a list of entity-based chunks.
    """
    chunks = []

    for joker in raw_data.get("jokers", []):
        chunks.append(process_joker_data(joker))
    
    for tarot in raw_data.get("tarot_cards", []):
        chunks.append(process_tarot_data(tarot))

    for planet in raw_data.get("planet_cards", []):
        chunks.append(process_planet_data(planet))

    for voucher in raw_data.get("vouchers", []):
        chunks.append(process_voucher_data(voucher))

    for poker_hand in raw_data.get("poker_hands", []):
        chunks.append(process_poker_hand_data(poker_hand))

    for mechanic in raw_data.get("mechanics", []):
        chunks.append(process_mechanic_data(mechanic))

    for boss_blind in raw_data.get("boss_blinds", []):
        chunks.append(process_boss_blind_data(boss_blind))

    return chunks

if __name__ == "__main__":
    print("Processing Balatro raw game data into entity-based chunks...")
    processed_chunks = process_raw_data(RAW_GAME_DATA)
    
    # Example of printing processed chunks
    for i, chunk in enumerate(processed_chunks):
        print(f"
--- Chunk {i+1} ---")
        print(f"Content:
{chunk['content']}")
        print(f"Metadata: {json.dumps(chunk['metadata'], indent=2)}")

    print(f"
Total chunks processed: {len(processed_chunks)}")
