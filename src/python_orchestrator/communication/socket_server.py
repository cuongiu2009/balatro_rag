import asyncio
import json
import logging
import struct # Added for unpacking length prefix
from typing import Callable, Optional

logging.basicConfig(level=logging.DEBUG)

# Callback function to update game state in the main application (FastAPI)
_game_state_update_callback: Optional[Callable[[dict], None]] = None

def set_game_state_update_callback(callback: Callable[[dict], None]):
    """
    Sets the callback function that will be called when a new game state is received.
    This allows the main application (FastAPI) to register its game state update handler.
    """
    global _game_state_update_callback
    _game_state_update_callback = callback
    logging.info("Game state update callback registered.")

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    logging.info(f"Client connected: {addr}")

    message = "" # Initialize message
    message_length = 0 # Initialize for error reporting
    message_bytes = b'' # Initialize for error reporting

    try:
        # Read the 4-byte length prefix
        logging.debug(f"DEBUG: {addr} - Attempting to read 4-byte length prefix.")
        length_prefix = await reader.readexactly(4)
        message_length = struct.unpack('<I', length_prefix)[0] # <I for little-endian unsigned int
        logging.info(f"DEBUG: {addr} - Received length prefix: {message_length} bytes.")

        # Read the exact number of bytes for the message
        logging.debug(f"DEBUG: {addr} - Attempting to read {message_length} bytes for the message.")
        message_bytes = await reader.readexactly(message_length)
        message = message_bytes.decode() # Decode the message
        logging.info(f"Received raw bytes data from {addr}: {message_bytes[:200]}...") # Log raw bytes
        logging.info(f"Received raw message from {addr}: {message[:200]}...") # Log first 200 chars of raw message

        # --- Existing JSON processing and response logic starts here ---
        try: # This is the outer try block for JSON decoding and callback
            game_state = json.loads(message)
            logging.info(f"Successfully parsed JSON game state from {addr}. Keys: {game_state.keys()}")

            # --- START DEBUG DUMP LOGGING ---
            if "debug_G_GAME_dump" in game_state:
                logging.info(f"DEBUG G.GAME Dump from Lua: {game_state['debug_G_GAME_dump']}")
                del game_state["debug_G_GAME_dump"] 
            if "debug_G_dump" in game_state:
                logging.info(f"DEBUG Full G Dump from Lua (potentially large): {game_state['debug_G_dump']}")
                del game_state["debug_G_dump"]
            if "debug_path_log" in game_state:
                logging.info(f"DEBUG Path Log from Lua: {game_state['debug_path_log']}")
                del game_state["debug_path_log"] 
            # --- END DEBUG DUMP LOGGING ---

            logging.info(f"Attempting to call _game_state_update_callback for {addr}.")
            if _game_state_update_callback:
                logging.info(f"Callback registered, calling _game_state_update_callback for {addr}.")
                _game_state_update_callback(game_state)
                logging.info(f"_game_state_update_callback returned for {addr}. Preparing TCP response.")
                response_data = json.dumps({"status": "success", "message": "Game state received and updated."}).encode('utf-8')
                response_length = len(response_data)
                length_prefix_bytes = struct.pack('<I', response_length) # <I for little-endian unsigned int

                logging.info(f"Sending TCP response to {addr}: Length={response_length}, Data={response_data[:100]}...")
                writer.write(length_prefix_bytes + response_data)
                await writer.drain()
                logging.info(f"TCP response sent to {addr}.")
            else:
                logging.warning(f"No game state update callback registered for {addr}. Game state not forwarded. Sending error response.")
                response_data = json.dumps({"status": "error", "message": "Game state handler not registered."}).encode('utf-8')
                response_length = len(response_data)
                length_prefix_bytes = struct.pack('<I', response_length)

                writer.write(length_prefix_bytes + response_data)
                await writer.drain()
                logging.info(f"Error TCP response sent to {addr}.")

        except json.JSONDecodeError as e:
            logging.error(f"FATAL: JSON decoding error from {addr}: {e} - Message: {message[:200]}...")
            error_response_data = json.dumps({"status": "error", "message": "Invalid JSON"}).encode('utf-8')
            error_response_length = len(error_response_data)
            length_prefix_bytes = struct.pack('<I', error_response_length)

            writer.write(length_prefix_bytes + error_response_data)
            await writer.drain()
            logging.info(f"Error JSON decoding response sent to {addr}.")
        except Exception as e:
            logging.error(f"FATAL: Error processing message from {addr}: {e}")
            error_response_data = json.dumps({"status": "error", "message": str(e)}).encode('utf-8')
            error_response_length = len(error_response_data)
            length_prefix_bytes = struct.pack('<I', error_response_length)

            writer.write(length_prefix_bytes + error_response_data)
            await writer.drain()
            logging.info(f"Error general exception response sent to {addr}.")

    except asyncio.IncompleteReadError:
        logging.info(f"Client {addr} disconnected gracefully.")
        # Optionally, send an error response if partial data was read but not enough for full message.
        if message_length > 0 and len(message_bytes) < message_length: # Use message_length and message_bytes from outer scope
             error_response = {"status": "error", "message": "Incomplete message received."}
             writer.write(json.dumps(error_response).encode() + b'\\n')
             await writer.drain()
             logging.info(f"Error 'incomplete message' response sent to {addr}.")
    except Exception as e:
        logging.error(f"Unexpected error in handle_client for {addr}: {e}")
        error_response = {"status": "error", "message": str(e)}
        writer.write(json.dumps(error_response).encode() + b'\\n')
        await writer.drain()
        logging.info(f"Error general exception response sent to {addr}.")
    finally:
        writer.close()
        await writer.wait_closed()
        logging.info(f"Client {addr} connection closed.")
async def start_socket_server(host="127.0.0.1", port=5000):
    server = await asyncio.start_server(
        handle_client, host, port
    )

    addr = server.sockets[0].getsockname()
    logging.info(f"Socket server listening on {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    # This block is for testing the socket server independently.
    # In the actual application, this function will be called from main.py.
    logging.warning("Running socket_server.py independently. No game state callback registered.")
    asyncio.run(start_socket_server())
