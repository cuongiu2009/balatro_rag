# RAG Knowledge Base: Entity-Based Chunking Strategy

## Goal
The primary goal of the entity-based chunking strategy for the Balatro RAG knowledge base is to organize information in a way that maximizes retrieval relevance for queries about specific game elements. This ensures that when a user asks about a particular Joker, a poker hand, or a game mechanic, the RAG model receives a comprehensive and focused set of facts related to that entity.

## Core Entities for Chunking

Information will be chunked around the following key game entities:

### 1. Joker Cards
- **Description**: Each unique Joker card in Balatro.
- **Content to Extract**:
    - **Name**: The official name of the Joker (e.g., "Joker", "Abstract Joker").
    - **Text Description**: The in-game text describing its effect.
    - **Detailed Mechanics**: A more detailed explanation of how the Joker's effect functions, including any triggers, scaling, or conditions.
    - **Synergies**: How this Joker interacts positively or negatively with other Jokers, cards, poker hands, or game mechanics.
    - **Drawbacks/Conditions**: Any negative effects, specific conditions for activation, or situations where it might be less effective.
    - **Categorization**: Broad categories of effect (e.g., Multiplier, Chips, Money, Hand Size, Discard Modification, Card Creation, etc.).
- **Metadata**:
    - `entity_type: "joker"`
    - `name: "Joker Name"`
    - `categories: ["category1", "category2"]` (e.g., ["Multiplier", "Money"])
    - `rarity: "common | uncommon | rare | holo | foil | polychrome"`

### 2. Tarot Cards
- **Description**: Each unique Tarot card.
- **Content to Extract**:
    - **Name**: The official name of the Tarot card (e.g., "The Fool", "The Magician").
    - **Text Description**: The in-game text describing its effect.
    - **Detailed Mechanics**: How the Tarot card modifies specific cards or the game state.
    - **Strategic Use**: Common situations or cards where this Tarot card is most effective.
- **Metadata**:
    - `entity_type: "tarot"`
    - `name: "Tarot Name"`

### 3. Planet Cards
- **Description**: Each unique Planet card.
- **Content to Extract**:
    - **Name**: The official name of the Planet card (e.g., "Jupiter", "Neptune").
    - **Text Description**: The in-game text describing its effect.
    - **Affected Poker Hand**: The specific poker hand whose level is increased by this Planet card.
- **Metadata**:
    - `entity_type: "planet"`
    - `name: "Planet Name"`
    - `poker_hand_affected: "Poker Hand Name"`

### 4. Voucher Items
- **Description**: Each unique Voucher that can be purchased in the shop.
- **Content to Extract**:
    - **Name**: The official name of the Voucher.
    - **Text Description**: The in-game text describing its persistent effect.
    - **Detailed Mechanics**: How the Voucher alters gameplay.
- **Metadata**:
    - `entity_type: "voucher"`
    - `name: "Voucher Name"`

### 5. Poker Hands
- **Description**: Each unique standard poker hand recognized by Balatro.
- **Content to Extract**:
    - **Name**: The official name of the poker hand (e.g., "Pair", "Flush", "Straight Flush").
    - **Rules**: The combination of cards required to form the hand.
    - **Base Scoring**: Base Chips and Multiplier values for the hand at Level 1.
    - **Level Scaling**: How Chips and Multiplier increase with each level.
    - **Strategic Importance**: General strategic value of the hand (e.g., early game, synergy with specific card types).
- **Metadata**:
    - `entity_type: "poker_hand"`
    - `name: "Poker Hand Name"`

### 6. Mechanics/Keywords
- **Description**: Important game mechanics, conditions, or keywords that are not specific to a single card but affect gameplay broadly.
- **Examples**: "Debuffed", "Glass Card" (as a card effect keyword), "Edition" (Foil, Holographic, Polychrome), "Seal" (Red, Blue, Gold, Lucky), "Eternal", "Perishable", "Negative", "Bonus Card", "Enhancement" (e.g., Stone, Mult, Lucky).
- **Content to Extract**:
    - **Name**: The term or keyword (e.g., "Debuffed", "Red Seal").
    - **Explanation**: A detailed description of what the mechanic does, how it's applied, and its impact on cards or gameplay.
    - **Interactions**: How this mechanic interacts with other mechanics, Jokers, or cards.
- **Metadata**:
    - `entity_type: "mechanic"`
    - `name: "Mechanic Name"`

### 7. Boss Blinds
- **Description**: Each unique Boss Blind.
- **Content to Extract**:
    - **Name**: The official name of the Boss Blind (e.g., "The Hook", "The Needle").
    - **Text Description**: The in-game text describing its special modifier or debuff.
    - **Detailed Mechanics**: How the Boss Blind alters the game rules for that round.
    - **Strategic Considerations**: Advice for dealing with this specific Boss Blind.
- **Metadata**:
    - `entity_type: "boss_blind"`
    - `name: "Boss Blind Name"`

## Chunking Process Workflow

1.  **Source Data Collection**: Gather raw information from various sources (Balatro game files, official wiki, community-driven data, manual entry). This data is often semi-structured or unstructured.
2.  **Entity Identification & Segmentation**: Use parsing techniques (regular expressions, keyword matching, or manual annotation) to identify boundaries for each core entity within the raw data.
3.  **Content Extraction & Normalization**: Extract the relevant content for each entity. Normalize text (e.g., remove redundant formatting, standardize terminology) to improve consistency.
4.  **Metadata Generation**: Programmatically or manually assign the defined metadata to each extracted entity chunk. This metadata is crucial for targeted retrieval.
5.  **Vectorization Preparation**: The cleaned content and metadata for each chunk will be prepared for embedding by the chosen vectorization model.

## Retrieval Strategy (Conceptual)

When a user query is received by the RAG system:

1.  **Query Analysis**: The query will be analyzed to identify explicit and implicit entities (e.g., "best Jokers for a Flush deck" -> identifies "Joker", "Flush").
2.  **Targeted Retrieval**: The RAG system will leverage the `entity_type` and other metadata fields to perform a more targeted retrieval from the vector database. For instance, if "Joker" and "Flush" are identified, it will prioritize chunks with `entity_type: "joker"` and potentially those with `poker_hand_affected: "Flush"` (from Planet cards) or a metadata tag indicating "Flush synergy".
3.  **Context Assembly**: The retrieved chunks, which are already entity-focused, provide a rich context to the Language Model for generating a precise and helpful response.

This strategy ensures that the RAG model can access highly relevant and non-redundant information, leading to more accurate and concise strategic suggestions for the player.