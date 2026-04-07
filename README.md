# Balatro AI Strategy Assistant (RAG-based)

The Balatro AI Strategy Assistant is an innovative project designed to enhance the Balatro gameplay experience by providing real-time game state updates and strategic suggestions. It achieves this by integrating directly with the game's Love2D engine via Lua runtime hooking and leveraging a powerful local AI model through a Python orchestrator. This assistant focuses on delivering timely, context-aware advice to help players optimize their moves and improve their strategy.

## Introduction

This project implements a Retrieval Augmented Generation (RAG) based AI assistant for the popular deck-building roguelike game, Balatro. By dynamically extracting game state information directly from the running game, the assistant provides players with crucial real-time insights into their hand, active Jokers, remaining deck, and other vital statistics. Furthermore, it leverages a local Large Language Model (LLM) via LM Studio to analyze the current game situation and offer optimal strategic suggestions for upcoming moves, all displayed conveniently within the Love2D command line. The core objective is to offer a seamless, intelligent layer of support that respects game stability, standardizes data flow, and ensures low-latency AI responses.

## Architecture Diagram (Text-based)

The system architecture is composed of distinct, interacting components ensuring robust communication and processing:

```
+-------------------+        +---------------------------+        +---------------------+        +-----------------+
| Balatro Game      |        | Python Orchestrator       |        | LM Studio (LLM)     |        | ChromaDB        |
| (Love2D Engine)   |        | (FastAPI Application)     |        | (Local AI Model)    |        | (Knowledge Base)|
+-------------------+        +---------------------------+        +---------------------+        +-----------------+
        |                            ^             ^                        ^                      ^
        | (1) Lua Runtime Hooks      |             |                        |                      |
        |    - init.lua              |             | (5) AI Suggestions     |                      |
        |    - data_extractor.lua    |             |    (JSON)              | (6) RAG Query        | (7) Contextual
        |    - socket_client.lua     |             |                        |                      |     Data
        V                            |             |                        |                      |
+-------------------+        +---------------------------+        +---------------------+        +-----------------+
| Game State        |<-------| (4) Display Suggestions   |        | api_client/         |        | rag_model/      |
| Extraction (JSON) |        |    on Love2D Commandline  |        |   lm_studio_client.py |<----->|   chromadb_client.py|
+-------------------+        +---------------------------+        |                     |        |   data_processor.py   |
        | (2) TCP Socket             |             |        |    (localhost:1234)   |        |   knowledge_base_builder.py|
        |    (localhost:5000)        |             |        +---------------------+        |   rag_processor.py    |
        V                            |             |                                       +-----------------+
+-------------------+        +---------------------------+
| src/common/       |        | communication/            |
|   game_state_schema.lua    |   socket_server.py        |
|   game_state_schema.py     |<--------------------------+
+-------------------+        | rag_model/                |
                             |   rag_processor.py (RAG Logic) |
                             +---------------------------+
```

**Workflow:**
1.  **Lua Runtime Hooks**: `init.lua` injects `data_extractor.lua` and `socket_client.lua` into the Balatro game. `data_extractor.lua` continuously monitors and extracts critical game state information (player's hand, active Jokers, deck contents, etc.) from Balatro's global Lua tables.
2.  **Game State Transmission**: `socket_client.lua` serializes the extracted game state into a standardized JSON format and sends it via a TCP socket to the Python Orchestrator running on `localhost:5000`.
3.  **Python Orchestrator (FastAPI)**: The `socket_server.py` component within the Python Orchestrator receives and deserializes the game state.
4.  **RAG Processing**: The `rag_model/rag_processor.py` uses the incoming game state to formulate a query for the local LLM. It retrieves relevant contextual information from `ChromaDB` (knowledge base of Balatro mechanics, cards, and scoring rules) to augment the query (RAG).
5.  **LLM Interaction**: The `api_client/lm_studio_client.py` sends the augmented query to the local LM Studio instance (`localhost:1234`).
6.  **AI Suggestions**: LM Studio processes the query and generates strategic suggestions, typically in a structured JSON format.
7.  **Response Handling & Display**: The Python Orchestrator receives the LLM's response, validates it, and formats it for display. The suggestions and real-time game state updates are then sent back to the Balatro game via the Love2D Commandline.

## Installation

This project requires both a Python environment for the orchestrator and modifications within your Balatro game directory for Lua hooks.

### Prerequisites

*   **Balatro Game**: Ensure Balatro is installed on your Windows machine.
*   **Python**: Version `3.13.12` is required.
*   **LM Studio**: Download and install [LM Studio](https://lmstudio.ai/). You must have LM Studio running locally on `localhost:1234` with a suitable Balatro strategy model loaded before starting the assistant.
*   **Luasocket**: This is typically bundled with Love2D. If not, you might need to install it manually for your Love2D environment.

### Python Orchestrator Setup

1.  **Navigate**: Open your terminal or command prompt and navigate to the `src/python_orchestrator/` directory:
    ```bash
    cd balatro_mod/src/python_orchestrator/
    ```
2.  **Virtual Environment**: Create and activate a Python virtual environment:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```
3.  **Install Dependencies**: Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
    (Ensure `requirements.txt` contains `FastAPI`, `uvicorn`, `ChromaDB`, `requests`).
4.  **Knowledge Base Population**:
    *   First, process any raw Balatro game data (e.g., card descriptions, joker effects) into a format suitable for ChromaDB. This is done by running:
        ```bash
        python rag_model/data_processor.py
        ```
    *   Then, build and populate the ChromaDB knowledge base:
        ```bash
        python rag_model/knowledge_base_builder.py
        ```

### Lua Game Hooks Setup

1.  **Locate Balatro `main.lua`**: Find the `main.lua` file within your Balatro game installation directory. This is usually in a path similar to `Balatro/Balatro/main.lua`.
2.  **Copy Lua Files**: Copy the contents of the `src/lua_game_hooks/` directory (specifically `init.lua`, `data_extractor.lua`, and `socket_client.lua`) into the same directory as Balatro's `main.lua`. These files will be loaded by the game at runtime.

## Usage

Once installed and configured, the Balatro AI Strategy Assistant operates by providing real-time insights and strategic advice directly within your game.

1.  **Start LM Studio**: Launch LM Studio and ensure your chosen Balatro strategy model is loaded and running, accessible at `localhost:1234`.
2.  **Start Python Orchestrator**: In your activated Python virtual environment (from the `src/python_orchestrator/` directory), start the FastAPI application:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 5000
    ```
    This will start the Python server listening for game state updates.
3.  **Launch Balatro**: Start the Balatro game as you normally would. The Lua hooks will automatically activate.

**During Gameplay:**

*   **Real-time Game State**: The Love2D Commandline (usually accessible by pressing `~` or a similar key in Love2D games) will display real-time updates of your current hand, active Jokers, remaining deck, and other relevant game information whenever significant in-game events occur (e.g., drawing cards, acquiring new Jokers, entering the shop, or ending a round).
*   **Strategic Suggestions**: Based on the updated game state, the assistant will analyze the situation and provide optimal strategic suggestions (e.g., recommended cards to play, discards) directly on the Love2D Commandline to guide your decisions.

## Technical Challenges

Developing a real-time, AI-powered assistant that deeply integrates with a running game presents several significant technical challenges, particularly in **System Integration** and **AI Engineering**.

### System Integration Challenges

*   **Runtime Hooking & Game Stability**: Intercepting and modifying a running game's Lua runtime (`Global Table G`) without causing crashes, performance degradation, or data corruption is a delicate process. Ensuring that Lua code is highly modular allows for easier adaptation to future game patches, but maintaining compatibility remains an ongoing concern.
*   **Cross-Process Communication (Lua-Python)**: Establishing and maintaining a reliable, low-latency communication bridge between the Lua-based game engine and the Python-based orchestrator via `Luasocket` over `localhost` is critical. This involves robust error handling for connection loss and managing data serialization/deserialization.
*   **Performance Overhead**: A primary goal is to prevent any noticeable frame rate drops or input lag in Balatro (below 60 FPS or above 100ms input lag, respectively) while the Python orchestrator and LM Studio are actively processing. This requires efficient data extraction, minimal processing time in Lua, and optimized Python-side operations.
*   **Error Handling and Resilience**: The system must gracefully handle unexpected Lua file structures, errors during data extraction, unavailability of the LM Studio server, malformed AI responses, and potential issues with the Love2D command line output.

### AI Engineering Challenges

*   **RAG Model Integration & Optimization**: Effectively integrating a local LLM (via LM Studio) with a Retrieval Augmented Generation (RAG) system is complex. This includes:
    *   **Knowledge Base Management**: Building and updating a comprehensive `ChromaDB` knowledge base of Balatro's intricate rules, card effects, and scoring mechanics.
    *   **Entity-Based Chunking**: Implementing an entity-based chunking strategy for the RAG knowledge base to ensure high retrieval accuracy for specific game elements (Jokers, Tarots, Planets, scoring mechanisms).
    *   **Prompt Engineering**: Formulating effective prompts that leverage both the current game state and retrieved context to elicit accurate, actionable, and structured JSON suggestions from the LLM.
*   **Low Latency AI Response**: Meeting the stringent requirement of AI suggestions being displayed within 3-5 seconds (from game event to display) demands an optimized RAG pipeline, efficient LLM inference, and minimal communication overhead.
*   **Data Standardization**: Implementing a consistent JSON schema for game state and AI suggestions is crucial for seamless data flow between Lua, Python, and the LLM, ensuring that all components "speak the same language."
*   **Actionable Suggestions**: Ensuring the AI provides truly "Actionable" strategic advice requires not only accurate data extraction and processing but also the LLM's ability to provide concrete suggestions with expected score values and in a structured, parseable format. Handling and discarding malformed or nonsensical suggestions from the LLM is also a key aspect.