import time
import json
import logging
import asyncio

# --- Configuration ---
LOG_FILE = "performance_monitor.log"
FPS_THRESHOLD = 58  # Minimum acceptable FPS
LAG_THRESHOLD_MS = 100  # Maximum acceptable input lag in milliseconds

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(LOG_FILE),
    logging.StreamHandler()
])

class PerformanceMonitor:
    def __init__(self, fps_threshold=FPS_THRESHOLD, lag_threshold_ms=LAG_THRESHOLD_MS):
        self.fps_threshold = fps_threshold
        self.lag_threshold_ms = lag_threshold_ms
        self.fps_data = []
        self.lag_data = []
        logging.info("PerformanceMonitor initialized.")

    def record_fps(self, fps):
        """
        Records an FPS reading.
        In a real scenario, this data would be received from the Lua game hooks.
        """
        self.fps_data.append(fps)
        if fps < self.fps_threshold:
            logging.warning(f"Low FPS detected: {fps} FPS (below {self.fps_threshold})")
        else:
            logging.info(f"FPS: {fps}")

    def record_input_lag(self, lag_ms):
        """
        Records an input lag reading.
        In a real scenario, this would involve correlating input events in Lua with
        the time they are reflected in the game state received by Python.
        """
        self.lag_data.append(lag_ms)
        if lag_ms > self.lag_threshold_ms:
            logging.warning(f"High Input Lag detected: {lag_ms}ms (above {self.lag_threshold_ms}ms)")
        else:
            logging.info(f"Input Lag: {lag_ms}ms")

    def analyze_results(self):
        """
        Analyzes the collected performance data and provides a summary.
        """
        logging.info("
--- Performance Analysis Summary ---")
        if self.fps_data:
            avg_fps = sum(self.fps_data) / len(self.fps_data)
            min_fps = min(self.fps_data)
            max_fps = max(self.fps_data)
            logging.info(f"Average FPS: {avg_fps:.2f}")
            logging.info(f"Minimum FPS: {min_fps:.2f}")
            logging.info(f"Maximum FPS: {max_fps:.2f}")
            if min_fps < self.fps_threshold:
                logging.error(f"FAIL: Minimum FPS ({min_fps:.2f}) fell below threshold ({self.fps_threshold})")
            else:
                logging.info(f"PASS: Minimum FPS ({min_fps:.2f}) met threshold ({self.fps_threshold})")
        else:
            logging.warning("No FPS data recorded.")

        if self.lag_data:
            avg_lag = sum(self.lag_data) / len(self.lag_data)
            max_lag = max(self.lag_data)
            logging.info(f"Average Input Lag: {avg_lag:.2f}ms")
            logging.info(f"Maximum Input Lag: {max_lag:.2f}ms")
            if max_lag > self.lag_threshold_ms:
                logging.error(f"FAIL: Maximum Input Lag ({max_lag:.2f}ms) exceeded threshold ({self.lag_threshold_ms}ms)")
            else:
                logging.info(f"PASS: Maximum Input Lag ({max_lag:.2f}ms) met threshold ({self.lag_threshold_ms}ms)")
        else:
            logging.warning("No Input Lag data recorded.")
        logging.info("--- End Performance Analysis Summary ---
")

async def simulate_monitoring(monitor: PerformanceMonitor, duration_seconds=30):
    """
    Simulates receiving performance data over a period.
    In a real stress test, this would involve running the game and AI,
    and receiving actual data via the socket.
    """
    logging.info(f"Simulating performance monitoring for {duration_seconds} seconds...")
    start_time = time.time()
    while (time.time() - start_time) < duration_seconds:
        # Simulate receiving FPS data from Lua (e.g., love.timer.getFPS() sent via socket)
        simulated_fps = 60 - (time.time() - start_time) * 0.5 + (0.5 * (time.time() % 2)) # Simple degradation
        monitor.record_fps(simulated_fps)

        # Simulate receiving input lag data (e.g., calculated in Lua and sent via socket)
        simulated_lag = 30 + (time.time() - start_time) * 2 + (10 * (time.time() % 3)) # Simple increase
        monitor.record_input_lag(simulated_lag)
        
        await asyncio.sleep(1) # Simulate checking every second

    logging.info("Simulation finished.")
    monitor.analyze_results()

if __name__ == "__main__":
    monitor = PerformanceMonitor()
    asyncio.run(simulate_monitoring(monitor, duration_seconds=10)) # Shorter duration for quick test

    # Example of how to use it with actual data (if available)
    # monitor_actual = PerformanceMonitor()
    # while game_running:
    #     fps_from_lua = get_fps_from_lua_socket() # Hypothetical function
    #     lag_from_lua = get_lag_from_lua_socket() # Hypothetical function
    #     monitor_actual.record_fps(fps_from_lua)
    #     monitor_actual.record_input_lag(lag_from_lua)
    # monitor_actual.analyze_results()
