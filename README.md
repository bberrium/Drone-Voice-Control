# Drone Voice Control

An object-oriented Python application designed to control drone flight paths and operations using natural language voice commands. 

This repository demonstrates practical implementations of **Python scripting**, **Object-Oriented Programming (OOP)**, and containerized deployment via **Docker**—developed and tested in a Linux environment.

## Key Features
- **Voice Recognition Integration:** Translates spoken language into mapped drone commands (e.g., takeoff, land, move forward).
- **Object-Oriented Architecture:** Cleanly separates the drone hardware interface, the voice processing engine, and the command mapper into modular Python classes.
- **Containerized:** Fully deployable via Docker to ensure cross-platform compatibility and network isolation.
- **Automated Startup:** Includes a Bash shell script for easy environment setup and execution on Linux systems.

## Tech Stack & Requirements
- **Language:** Python 3.x
- **Containerization:** Docker
- **Version Control:** Git
- **OS:** Linux (Tested on Fedora)

## Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/bberrium/Drone-Voice-Control.git](https://github.com/bberrium/Drone-Voice-Control.git)
cd Drone-Voice-Control

```

### 2. Local Linux Setup (Fedora/RHEL)

If you prefer running this natively on your Linux machine rather than in a container, ensure your system packages are up to date:

```bash
sudo dnf update
sudo dnf install python3-pip portaudio-devel 
pip install -r requirements.txt

```

### 3. Running with Bash

A convenient Bash script is provided to check dependencies and launch the application seamlessly.

```bash
chmod +x run_drone.sh
./run_drone.sh

```

## Docker Deployment

To ensure consistent environments across different hypervisors and network setups, this project can be run inside a Docker container.

1. **Build the image:**

```bash
docker build -t drone-voice-control .

```

2. **Run the container:**
*(Note: Running hardware-linked containers requires passing device networks. Adjust `--device` as needed for your specific drone's network interface).*

```bash
docker run -it --network host --device /dev/snd drone-voice-control

```

## Architecture Overview (OOP)

The codebase relies heavily on OOP principles to maintain modularity and scale:

* `DroneController`: Manages the direct networking, IP allocation, and API connections to the drone hardware.
* `VoiceProcessor`: Handles microphone streaming and intent parsing from audio to text.
* `CommandRouter`: Maps the parsed text to the appropriate `DroneController` methods (e.g., mapping "fly up" to `drone.ascend()`).

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/NewCommand`)
3. Commit your changes (`git commit -m 'Add a backflip command'`)
4. Push to the branch (`git push origin feature/NewCommand`)
5. Open a Pull Request

