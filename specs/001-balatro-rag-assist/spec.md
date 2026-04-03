# Feature Specification: Balatro RAG Assist

**Feature Branch**: `001-balatro-rag-assist`  
**Created**: 2026-03-29  
**Status**: Draft  
**Input**: User description: "Tạo 1 dự án RAG kết nối với LMStudio, dùng model để hỗ trợ người chơi chơi game Balatro bằng cách can thiệp vào các file .lua trong thư mục @Balatro/. Dùng thông tin từ các đoạn code được can thiệp từ game để lấy thông tin về số lá bài người chơi đang giữ, lá chức năng hiện có, còn lại những lá bài nào, những lượt đánh và lượt bỏ để model local có thể tính toán được các bước tiếp theo, sau đó hiện ra ở cửa sổ love2D commandline (được engine hỗ trợ)."

## User Scenarios & Testing

### User Story 1 - Real-time Game State Update (Priority: P1)

As a Balatro player, I want to see my current game state (hand, functional cards, remaining deck) updated in real-time, so I can make informed decisions.

**Why this priority**: Providing the core game state information is fundamental for any assistance and forms the basis for more advanced features. Without it, strategic advice is impossible.

**Independent Test**: Automated test will simulate game actions by modifying a mock `G` table and verify the correct JSON payload is sent over the socket.

**Acceptance Scenarios**:

1.  **Given** a Balatro game is running, **When** the player draws a card, **Then** the love2D command line displays the updated hand and remaining deck within 2 seconds.
2.  **Given** a Balatro game is running, **When** the player gains a functional card (Joker, Planet, Tarot), **Then** the love2D command line displays the newly acquired functional card within 2 seconds.

### User Story 2 - Receive Suggested Next Moves (Priority: P2)

As a Balatro player, I want to receive suggestions for optimal next moves (what cards to play, what to discard) based on my current game state, so I can improve my gameplay.

**Why this priority**: This feature provides direct, actionable assistance to the player, significantly enhancing their experience by leveraging the RAG model's capabilities.

**Independent Test**: Can be fully tested by observing the game state, then receiving and evaluating the suggested moves against strategic principles of Balatro, without needing real-time updates. An "optimal" move is defined as the play that results in the highest `estimated_score` or, in cases of similar scores, the one that has the highest `win_chance`.

**Acceptance Scenarios**:

1.  **Given** the current game state is displayed, **When** the player requests a suggestion (implicitly or through a trigger), **Then** the love2D command line displays a recommended move (e.g., "Play Flush: 5H, 6H, 7H, 8H, 9H") within 5 seconds.
2.  **Given** a recommendation is displayed, **When** the game state changes (e.g., player plays cards), **Then** previous recommendations become invalid, and new ones can be requested if applicable.

### Edge Cases

-   What happens when a Balatro Lua file is structured unexpectedly or contains errors that prevent data extraction? The system should gracefully handle the error and notify the player, potentially by not providing assistance for that specific data point.
-   How does the system handle the LMStudio server being unavailable or returning an error? The system should report the unavailability and not provide suggestions.
-   What if the Love2D command line output is not writable or becomes full? The system should log errors internally and attempt to recover or notify the player.
-   What if the game state changes too rapidly for the model to provide timely suggestions? Prioritize delivering the latest relevant information over potentially outdated suggestions.
-   If the connection between Lua and Python is lost, the Lua script should attempt to reconnect every 5 seconds for up to 1 minute. If reconnection fails, it should stop trying and display a 'Connection Lost' message on the Love2D Commandline.
-   The Lua socket client should have a short timeout (e.g., 2 seconds) for sending data. If a timeout occurs, it should assume a network interruption and trigger the reconnection logic.
-   If the LM Studio model returns a malformed JSON or a nonsensical suggestion (e.g., suggests playing a card not in hand), the Python orchestrator will discard the response, log the error, and send a 'Suggestion failed' message to the Love2D Commandline.

## Out of Scope
- Toggling the AI assistant on or off via a command in the Love2D Commandline is out of scope for the current version.

## Requirements

### Functional Requirements

-   **FR-001**: The system MUST establish a connection with a local LMStudio instance to utilize a RAG model.
-   **FR-002**: The system MUST be able to read and parse comprehensive game state information from Balatro's `.lua` files, including: player's hand, active functional cards (Jokers), remaining cards in the deck, a history of played/discarded cards, current score, current blind information, active global modifiers/challenges, contents of the shop, current stakes, and any other persistent game values.
-   **FR-003**: The system MUST transmit the extracted game state via `Luasocket` over a `localhost` connection to a Python script responsible for interacting with the LMStudio RAG model.
-   **FR-004**: The system MUST receive strategic "next step" calculations or suggestions from the LMStudio RAG model.
-   **FR-005**: The system MUST display the current game state and the received strategic suggestions, formatted as structured JSON, within the Love2D command line interface.
-   **FR-006**: The system MUST monitor for specific in-game events (e.g., after a card is played, after a card is discarded, when a new hand is drawn, when entering the shop, after buying an item, when a new round starts) and update the game state for dynamic assistance only when these events occur.
-   **FR-007**: The RAG system MUST perform entity-based chunking for data. Each Joker, Tarot, Planet card, and each scoring mechanism (Multiplier/Chips) MUST be treated as an independent chunk to ensure retrieval accuracy.
-   **FR-008**: The system MUST report critical errors from the Python orchestrator (e.g., LM Studio API failure, RAG processing error) to the Love2D Commandline as a structured JSON error message.

### Non-Functional Requirements
- **NFR-001 (Performance)**: When the AI is not actively processing a request, the Python orchestrator's CPU usage should not exceed 5% of a single core on average, and its memory footprint should remain stable.

### Key Entities

-   **Player**: Represents the user playing Balatro. Key attributes include their current hand, active Jokers, and potentially other game-relevant stats.
-   **Deck**: Represents the in-game deck of cards, primarily its remaining contents.
-   **Game State**: A comprehensive snapshot of the current game, including player's hand, active Jokers, discards, plays, current score, current blind information, active global modifiers/challenges, contents of the shop, current stakes, and any other persistent game values.
-   **LMStudio Model**: The local RAG model, responsible for processing game state and generating strategic advice.
-   **Lua Files**: The source of game state information within the Balatro game directory.
-   **Love2D Command Line**: The output interface for displaying assistance to the player.

## Success Criteria

### Measurable Outcomes

-   **SC-001**: Game state updates (hand, Jokers, deck count) are displayed in the Love2D command line within 2 seconds of the corresponding in-game action, 95% of the time.
-   **SC-002**: Strategic "next step" suggestions are displayed in the Love2D command line within 5 seconds of the model receiving the game state, 90% of the time.
-   **SC-003**: AI strategic suggestions MUST be defined as 'Actionable' when meeting 3 technical criteria: (1) Accurate extraction of Card ID and Index in G.hand; (2) Provide expected score value (Expected Chips/Mult) based on RAG formula; (3) Output Format MUST be structured JSON for neat display on Love2D Commandline instead of plain text.
-   **SC-004**: Performance error definition: The system is considered to be in violation if (1) Balatro's average FPS drops below 60 FPS during AI inference, or (2) Input lag when clicking the mouse exceeds 100ms. Monitoring tools such as RivaTuner or Love2D's Built-in FPS counter will be used for verification.

## Clarifications

### Session 2026-03-29
- Q: What additional game state information is *essential* for the LMStudio model to provide effective strategic advice? → A: Full Set
- Q: What is the primary method for extracting game state from Balatro's `.lua` files? → A: Runtime Hooking
- Clarification: Data dumping should be event-driven (player chooses cards, ends round, opens shop).
- Clarification: Use Luasocket to send data to a Python script on localhost.

## Assumptions

-   LMStudio is installed, running, and configured with a suitable Balatro strategy model on the player's local machine.
-   The Balatro game's `.lua` files contain accessible and parseable data structures for the required game state information.
-   The Love2D engine provides a mechanism for programmatic output to its command line interface.
-   The RAG model possesses sufficient knowledge of Balatro's rules and scoring mechanics to provide meaningful strategic advice.
-   The runtime hooking mechanism for `.lua` files will not corrupt game saves or cause crashes.
-   The runtime hooking will provide real-time access to game state variables in memory.
-   The Love2D environment supports or can be extended with `Luasocket` for network communication.
-   The user is playing Balatro on a Windows operating system.
-   This system is designed for the current version of Balatro. Future game patches may break the runtime hooks. The modular design of the Lua hooks is intended to simplify adaptation, but manual updates will be required.
