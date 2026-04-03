import unittest
import subprocess
import threading
import time
import uvicorn
from src.python_orchestrator.main import app

class TestLuaPythonIntegration(unittest.TestCase):

    def setUp(self):
        self.server_thread = threading.Thread(target=uvicorn.run, args=(app,), kwargs={"host": "127.0.0.1", "port": 5000, "log_level": "info"})
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(2)  # Give the server a moment to start

    def test_data_flow(self):
        # Path to the Lua script
        lua_script_path = "tests/lua/unit/send_test_data.lua"

        # Execute the Lua script as a subprocess
        result = subprocess.run(["lua", lua_script_path], capture_output=True, text=True)
        
        # Check if the Lua script ran without errors
        self.assertEqual(result.returncode, 0, f"Lua script failed with error: {result.stderr}")
        
        # Check the output from the Lua script to see if it successfully sent data
        self.assertIn("Data sent successfully.", result.stdout)
        
        # In a more advanced test, we would capture the logs from the FastAPI server
        # and assert that the correct data was received and logged.
        # For now, we are just verifying the connection and send status.
        print("Integration test passed: Lua script executed and reported successful data send.")

    def tearDown(self):
        # The server is a daemon thread, so it will shut down when the main thread exits.
        # In a more robust setup, you would have a proper shutdown mechanism.
        pass

if __name__ == '__main__':
    unittest.main()
