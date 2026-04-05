import psutil
import time
import json
import asyncio
import logging
from unittest.mock import AsyncMock, patch

# Assume the Python orchestrator (main.py) is running in a separate process
# For this stress test, we will simulate interaction and monitor resource usage
# rather than actually launching and controlling the FastAPI server directly in the test.

# --- Configuration ---
LOG_FILE = "resource_usage_stress_test.log"
CPU_THRESHOLD_PERCENT = 80  # Max acceptable CPU usage for the orchestrator process
RAM_THRESHOLD_MB = 500      # Max acceptable RAM usage for the orchestrator process
STRESS_TEST_DURATION_SECONDS = 60 # Duration for the simulated stress test

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(LOG_FILE),
    logging.StreamHandler()
])

class ResourceMonitor:
    def __init__(self, process_name="uvicorn", cpu_threshold=CPU_THRESHOLD_PERCENT, ram_threshold=RAM_THRESHOLD_MB):
        self.process_name = process_name
        self.cpu_threshold = cpu_threshold
        self.ram_threshold = ram_threshold
        self.orchestrator_pid = None
        self.cpu_usages = []
        self.ram_usages = []
        logging.info("ResourceMonitor initialized.")

    def find_orchestrator_process(self):
        """
        Attempts to find the PID of the Python orchestrator process (uvicorn).
        This assumes uvicorn is running as part of the FastAPI application.
        """
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check process name or command line arguments
                if self.process_name in proc.name().lower():
                    # Further check if it's our uvicorn instance (e.g., listening on port 5000)
                    cmdline = " ".join(proc.cmdline())
                    if "main:app" in cmdline and "--port 5000" in cmdline:
                        self.orchestrator_pid = proc.pid
                        logging.info(f"Found orchestrator process: PID {self.orchestrator_pid}, CMD: {cmdline}")
                        return psutil.Process(self.orchestrator_pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        logging.warning(f"Orchestrator process '{self.process_name}' not found. Monitoring will be simulated.")
        return None

    def monitor_resources(self, process):
        """Monitors CPU and RAM usage for the given process."""
        try:
            cpu_percent = process.cpu_percent(interval=None) # Non-blocking
            ram_info = process.memory_info()
            ram_mb = ram_info.rss / (1024 * 1024) # Resident Set Size in MB

            self.cpu_usages.append(cpu_percent)
            self.ram_usages.append(ram_mb)

            logging.info(f"Monitoring PID {process.pid}: CPU: {cpu_percent:.2f}%, RAM: {ram_mb:.2f} MB")

            if cpu_percent > self.cpu_threshold:
                logging.warning(f"High CPU usage: {cpu_percent:.2f}% (above {self.cpu_threshold}%)")
            if ram_mb > self.ram_threshold:
                logging.warning(f"High RAM usage: {ram_mb:.2f}MB (above {self.ram_threshold}MB)")

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.error(f"Error monitoring process {process.pid}: {e}")

    def analyze_results(self):
        """Analyzes collected resource usage data."""
        logging.info("
--- Resource Usage Analysis Summary ---")
        
        if self.cpu_usages:
            avg_cpu = sum(self.cpu_usages) / len(self.cpu_usages)
            max_cpu = max(self.cpu_usages)
            logging.info(f"Average CPU Usage: {avg_cpu:.2f}%")
            logging.info(f"Maximum CPU Usage: {max_cpu:.2f}%")
            if max_cpu > self.cpu_threshold:
                logging.error(f"FAIL: Max CPU Usage ({max_cpu:.2f}%) exceeded threshold ({self.cpu_threshold}%)")
            else:
                logging.info(f"PASS: Max CPU Usage ({max_cpu:.2f}%) met threshold ({self.cpu_threshold}%)")
        else:
            logging.warning("No CPU usage data collected.")

        if self.ram_usages:
            avg_ram = sum(self.ram_usages) / len(self.ram_usages)
            max_ram = max(self.ram_usages)
            logging.info(f"Average RAM Usage: {avg_ram:.2f} MB")
            logging.info(f"Maximum RAM Usage: {max_ram:.2f} MB")
            if max_ram > self.ram_threshold:
                logging.error(f"FAIL: Max RAM Usage ({max_ram:.2f}MB) exceeded threshold ({self.ram_threshold}MB)")
            else:
                logging.info(f"PASS: Max RAM Usage ({max_ram:.2f}MB) met threshold ({self.ram_threshold}MB)")
        else:
            logging.warning("No RAM usage data collected.")

        # VRAM monitoring is highly platform-dependent and complex.
        # This part requires OS-specific tools (e.g., nvidia-smi on NVIDIA GPUs,
        # or DirectX/Vulkan APIs for direct integration).
        logging.info("VRAM monitoring not implemented in this script due to platform-specific complexities.")
        logging.info("For VRAM, consider using external tools like 'nvidia-smi' (NVIDIA) or vendor-specific utilities.")
        
        logging.info("--- End Resource Usage Analysis Summary ---
")


async def simulate_stress_test(monitor: ResourceMonitor, duration_seconds=STRESS_TEST_DURATION_SECONDS):
    """
    Simulates a stress test by continuously sending game state updates.
    In a real scenario, this would involve a running orchestrator and Lua client.
    """
    logging.info(f"Simulating stress test for {duration_seconds} seconds...")
    orchestrator_process = monitor.find_orchestrator_process()

    start_time = time.time()
    while (time.time() - start_time) < duration_seconds:
        # Simulate sending a game state update (e.g., from Lua client)
        # This would trigger processing in the Python orchestrator
        logging.debug("Simulating game state update...")
        # In a real test, you'd send actual data to the running server.
        # For this simulation, we just need to ensure the monitor is active.
        
        if orchestrator_process:
            monitor.monitor_resources(orchestrator_process)
        else:
            logging.info("Orchestrator process not found, skipping resource monitoring.")

        await asyncio.sleep(1) # Monitor every second

    logging.info("Stress test simulation finished.")
    monitor.analyze_results()

if __name__ == "__main__":
    monitor = ResourceMonitor()
    asyncio.run(simulate_stress_test(monitor, duration_seconds=10)) # Shorter duration for quick test

    # How to run this:
    # 1. Ensure your Python orchestrator (main.py) is running (e.g., `uvicorn main:app --port 5000`)
    # 2. Then run this script: `python tests/python/stress/test_resource_usage.py`
