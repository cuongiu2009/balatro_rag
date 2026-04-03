# Quickstart: Balatro RAG Assistant

This guide provides instructions to set up and run the Balatro RAG Assistant.

## Prerequisites

1.  **Balatro Game**: Installed and functional.
2.  **LM Studio**: Installed and running locally. A suitable RAG model should be downloaded and actively served on `localhost:1234`.
3.  **Python Environment**: Python 3.13.12 installed.
4.  **Love2D Environment**: Balatro's Love2D environment must support or be extended with `Luasocket`.
5.  **Operating System**: Windows.

## Setup Steps

### 1. Python Orchestrator Setup

Navigate to the `src/python_orchestrator/` directory.

```bash
cd src/python_orchestrator/
```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```
(A `requirements.txt` file will be created during implementation, containing `FastAPI`, `uvicorn`, `ChromaDB`, `requests` or an LM Studio API client library).

### 2. Lua Game Hooks Setup

This involves modifying Balatro's game files to inject the Lua hooks and `Luasocket` client.

**WARNING**: Modifying game files may lead to unexpected behavior or game instability. Proceed with caution.

1.  **Locate Balatro's `main.lua`**: This is typically found in the game's installation directory (e.g., `Balatro/main.lua`).
2.  **Integrate Lua Hooks**: Copy the files from `src/lua_game_hooks/` into a suitable location within Balatro's Lua environment. To integrate `init.lua` and enable the hooking mechanism and `Luasocket` client without modifying the game's original code structure, follow these steps:
    1.  **Locate `init.lua`**: Ensure `src/lua_game_hooks/init.lua` is copied to a location accessible by Balatro's `main.lua` (e.g., directly into the game's Lua directory or a subdirectory).
    2.  **Modify `Balatro/main.lua`**: Open Balatro's `main.lua` file (usually found in the game's installation directory). Scroll to the end of the file and add the following line:
        ```lua
        if love.filesystem.getInfo('init.lua') then
            require('init')
        end
        ```
        This code safely loads `init.lua` if it exists, integrating the hooks.
3.  **Ensure Luasocket Availability**: Verify that `Luasocket` is available to the Love2D environment. This might involve placing `luasocket` binaries in the correct Love2D `lua_modules` path or similar setup.

### 3. Run the Python Orchestrator

Start the FastAPI server for the Python orchestrator.

```bash
cd src/python_orchestrator/
uvicorn main:app --host 127.0.0.1 --port 5000 --reload
```
This will start the Python server listening for game state data from Lua.

### 4. Start Balatro

Launch the Balatro game. Ensure that the Lua hooks are active and successfully connecting to the Python orchestrator.

### 5. Verify Functionality

-   Observe the Love2D Commandline for real-time game state updates and AI suggestions.
-   Check the Python orchestrator console for incoming data from Lua and outgoing requests to LM Studio.

## Troubleshooting

-   **Connection Issues**: Ensure both the Python orchestrator and LM Studio are running on `localhost` with the correct ports. Check firewall settings.
-   **Lua Script Errors**: Review Balatro's console (if available) or log files for Lua errors.
-   **Performance**: If frame drops occur, review Lua hooking logic and the frequency of data transmission. Adjust AI response parameters in LM Studio if latency is consistently high.
