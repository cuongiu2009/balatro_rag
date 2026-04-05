import json
import os
import sys

# Ensure parent directory is in path for imports
# This is a bit of a workaround for running tests directly or modules from different levels.
# In a proper package setup, this might be handled differently or by installation.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.python_orchestrator.rag_model.chromadb_client import ChromaDBClient  # Import ChromaDBClient

class RAGProcessor:
    def __init__(self, lm_studio_client, chroma_db_path="./chroma_db", collection_name="balatro_knowledge_base"):
        self.lm_studio_client = lm_studio_client
        self.chroma_client = ChromaDBClient(path=chroma_db_path, collection_name=collection_name)

    def retrieve_context(self, query_text: str, n_results: int = 5) -> list:
        """
        Retrieves relevant document chunks from ChromaDB based on the query.
        """
        if not self.chroma_client.collection:
            return []
        
        results = self.chroma_client.query(query_texts=[query_text], n_results=n_results)
        
        context = []
        if results and results.get("documents"):
            for doc_list in results["documents"]:
                context.extend(doc_list) # documents is a list of lists
        return context

    def formulate_prompt(self, game_state: dict) -> str:
        """
        Formulates a prompt for LM Studio, incorporating retrieved context and
        requesting a structured JSON output.
        """
        # Create a query for context retrieval based on the game state
        query_parts = []
        if game_state.get("player_hand"):
            card_descriptions = [f"{card.get('rank', 'Unknown Rank')} of {card.get('suit', 'Unknown Suit')}" for card in game_state['player_hand']]
            query_parts.append(f"player hand: {', '.join(card_descriptions)}")
        if game_state.get("active_jokers"):
            joker_names = [joker.get("name", "Unknown Joker") for joker in game_state["active_jokers"]]
            query_parts.append(f"active jokers: {', '.join(joker_names)}")
        if game_state.get("current_blind_name"):
            query_parts.append(f"current blind: {game_state['current_blind_name']}")
        
        query_text = " ".join(query_parts) if query_parts else "Balatro game strategy"
        
        print(f"DEBUG: formulate_prompt received FULL game_state: {json.dumps(game_state, indent=2)}")
        print(f"DEBUG: Query text for context retrieval: {query_text}")
        
        # Retrieve context from ChromaDB
        retrieved_context = self.retrieve_context(query_text)
        
        context_str = "".join(retrieved_context) if retrieved_context else "No specific context retrieved."

        # Construct the prompt with context and request for structured JSON
        prompt = f"""
        You are a Balatro strategy assistant. Analyze the current game state and the provided context about game entities to suggest the optimal next move.

        Current Game State:
        {json.dumps(game_state, indent=2)}

        Relevant Game Information (from knowledge base):
        {context_str}

        Based on this, suggest an optimal action. Your response MUST be a JSON object with the following structure:
        {{
            "action": "string", // Recommended action (e.g., 'Play', 'Discard', 'Hold')
            "card_ids": ["string"], // List of specific Card IDs involved in the action (e.g., "AH", "KS")
            "location_indices": [number], // List of 1-based indices for cards in G.hand (if applicable)
            "estimated_score": number, // Estimated score (Chips/Mult) if the action is performed
            "win_chance": number, // Percentage chance of winning the current round (0-100)
            "rationale": "string" // Brief explanation for the suggestion (optional)
        }}
        """
        return prompt
