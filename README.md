# FDDOS

# DDoS Attack Script

This Python script is designed to perform Distributed Denial of Service (DDoS) attacks using two different flooding techniques:

## Flooding Techniques

1. **HTTP Flood**: Sends massive and repeated HTTP requests to overwhelm targeted servers.
2. **UDP Flood**: Sends large data packets over the UDP protocol to flood and exhaust the target.

## Script Description and Workflow

### Key Components

- **Setup and Configuration**: The script utilizes the `argparse` library to specify the required options for execution:
  - `--target`: The target address (IP or domain name).
  - `--port`: The port to attack (default: 443).
  - `--threads`: Number of threads (default: 1000).
  - `--flood-type`: Type of attack (http or udp).
  - `--mode`: Specifies the mode used (default: HTTP).

- **Customizing Traffic**: The script employs a list of user agents to simulate multiple traffic sources and uses a set of random paths to mimic diverse traffic flows.

- **HTTP Flood Attack**: Utilizes the `http.client` library to send large POST requests with massive payloads. It keeps the connection open (keep-alive) to reduce reconnection time and maximize the load.

Funk Sec team.
