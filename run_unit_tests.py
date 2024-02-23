import subprocess

# Define the command to run
commands = [
    ["python3", "apis/Utility.py"],
    ["python3", "apis/Sensors/TemperatureSensorSim.py"],
    ["python3", "apis/Relays/RelayControllerSim.py"],
    ["python3", "apis/DatabaseAccess/DbInterface.py"],
]

try:
    for command in commands:
        subprocess.run(command, check=True)
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
