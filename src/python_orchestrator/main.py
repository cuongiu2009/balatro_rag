import sys
import os

# Add the project root to sys.path to allow imports from 'src'
current_dir = os.path.dirname(os.path.abspath(__file__))
# Assuming project root is two levels up from main.py (main.py is in src/python_orchestrator)
project_root = os.path.abspath(os.path.join(current_dir, "..", "..")) 
sys.path.append(project_root)

import asyncio
import logging
import threading
import json # Ensure json is imported
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
import uvicorn

from src.python_orchestrator.communication.socket_server import start_socket_server, set_game_state_update_callback
from src.python_orchestrator.rag_model.rag_processor import RAGProcessor
from src.python_orchestrator.api_client.lm_studio_client import LMStudioClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize RAG components globally
lm_studio_client = LMStudioClient()
rag_processor = RAGProcessor(lm_studio_client)

# Global variable to hold the latest game state from the socket server
latest_game_state: dict = {}
game_state_lock = threading.Lock() # For thread-safe access to latest_game_state

app = FastAPI()

# Middleware to log incoming requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Incoming Request: Method={request.method}, URL={request.url}, Headers={request.headers}")
    response = await call_next(request)
    logging.info(f"Outgoing Response: Status={response.status_code}, URL={request.url}")
    return response


def update_latest_game_state_callback(game_state_data: dict):
    """
    Callback function to update the global latest_game_state.
    Called by the socket server when new game state is received.
    """
    with game_state_lock:
        global latest_game_state
        latest_game_state = game_state_data
        logging.info(f"Global latest_game_state updated by socket server. State keys: {game_state_data.keys()}")

def run_socket_server_in_thread(loop: asyncio.AbstractEventLoop):
    """
    Runs the asyncio socket server in a separate thread with its own event loop.
    """
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_socket_server())

@app.on_event("startup")
async def startup_event():
    logging.info("FastAPI app startup event triggered.")
    
    # Set the callback for the socket server
    set_game_state_update_callback(update_latest_game_state_callback)
    logging.info("Game state update callback registered with socket_server.")

    # Create a new event loop for the socket server thread
    socket_server_loop = asyncio.new_event_loop()
    
    # Start the socket server in a separate thread
    socket_server_thread = threading.Thread(
        target=run_socket_server_in_thread, 
        args=(socket_server_loop,), 
        daemon=True # Daemon thread exits when main program exits
    )
    socket_server_thread.start()
    logging.info("Socket server started in background thread.")

@app.get("/")
async def read_root():
    return {"status": "Balatro RAG Assistant FastAPI is running and socket server is active."}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/suggestion")
async def get_ai_suggestion(request: Request):
    """
    FastAPI endpoint to trigger AI suggestion based on the latest game state.
    """
    logging.info("'/suggestion' endpoint received a request.")
    
    # Log request body (if any) - careful with large bodies
    try:
        body = await request.body()
        if body:
            logging.info(f"Request body for /suggestion: {body.decode('utf-8')}")
        else:
            logging.info("Request body for /suggestion is empty.")
    except Exception as e:
        logging.error(f"Error reading request body for /suggestion: {e}")

    current_game_state = {}
    with game_state_lock:
        current_game_state = latest_game_state.copy() # Get a copy of the latest state

    if not current_game_state:
        raise HTTPException(status_code=404, detail="No game state received yet from Lua. Cannot provide suggestion.")

    try:
        # Formulate prompt using the latest game state
        prompt = rag_processor.formulate_prompt(current_game_state)
        logging.info(f"FastAPI formulating prompt for AI suggestion: {prompt[:100]}...") # Log first 100 chars

        # Get parsed suggestion from LM Studio
        suggestion = lm_studio_client.get_suggestion(prompt)
        
        if not suggestion:
            raise HTTPException(status_code=500, detail="Failed to get a valid AI suggestion from LM Studio.")
        
        logging.info(f"FastAPI received AI suggestion: {suggestion}")
        return {"status": "success", "data": suggestion}

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error generating AI suggestion in FastAPI endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) # Run FastAPI on a different port than socket server