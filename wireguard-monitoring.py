from prometheus_client import start_http_server, Gauge
import subprocess
import time
import re

# Créer des métriques pour Prometheus
gauge_rx = Gauge('wireguard_rx_bytes', 'Bytes received per peer', ['peer'])
gauge_tx = Gauge('wireguard_tx_bytes', 'Bytes transmitted per peer', ['peer'])
gauge_peers = Gauge('wireguard_connected_peers', 'Number of connected peers')
gauge_peer_ips = Gauge('wireguard_peer_ips', 'IP addresses of connected peers', ['peer', 'ip'])
gauge_wireguard_status = Gauge('wireguard_status', 'Status of the WireGuard interface', ['interface'])

def run_docker_command(container_name, command):
    """Exécute une commande dans le conteneur Docker et retourne la sortie."""
    docker_command = f"docker exec {container_name} {command}"
    result = subprocess.run(docker_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Erreur lors de l'exécution de la commande: {result.stderr.decode('utf-8')}")
        return None
    return result.stdout.decode('utf-8')

def parse_handshake_time(time_str):
    """Convertit une chaîne de temps en secondes."""
    units = {
        "second": 1,
        "seconds": 1,
        "minute": 60,
        "minutes": 60,
        "hour": 3600,
        "hours": 3600,
    }
    total_seconds = 0
    parts = time_str.split(",")
    for part in parts:
        amount, unit = part.strip().split()[0], part.strip().split()[1]
        total_seconds += int(amount) * units[unit]
    return total_seconds

def parse_wg_show(output):
    """Parse l'output de wg show en un format lisible."""
    peers_info = []
    
    peer_block = None
    for line in output.splitlines():
        if line.startswith("peer:"):
            if peer_block:
                peers_info.append(peer_block)
            peer_block = {}
            peer_block["public_key"] = line.split()[1]
        elif line.strip().startswith("endpoint:"):
            peer_block["endpoint"] = line.split()[1]
        elif line.strip().startswith("allowed ips:"):
            peer_block["allowed_ips"] = line.split()[2]
        elif line.strip().startswith("latest handshake:"):
            time_str = ' '.join(line.split()[2:])
            peer_block["latest_handshake"] = parse_handshake_time(time_str)
        elif line.strip().startswith("transfer:"):
            rx, tx = re.findall(r'([\d\.]+ \w+)', line)
            peer_block["transfer_rx"] = parse_size(rx)
            peer_block["transfer_tx"] = parse_size(tx)
    if peer_block:
        peers_info.append(peer_block)

    return peers_info

def parse_size(size_str):
    """Convertir une taille avec unité en bytes."""
    number, unit = size_str.split()
    number = float(number)
    if unit == "KiB":
        return number * 1024
    elif unit == "MiB":
        return number * 1024 * 1024
    elif unit == "GiB":
        return number * 1024 * 1024 * 1024
    return number

def monitor_wireguard(container_name, interval=30):
    """Monitor WireGuard dans le conteneur Docker depuis le host."""
    existing_peers = set()

    while True:
        output = run_docker_command(container_name, 'wg show')
        if output:
            peers_info = parse_wg_show(output)
            connected_peers = 0
            current_peers = set()
            
            for peer in peers_info:
                print(f"Peer: {peer['public_key']}, Handshake: {peer['latest_handshake']}, RX: {peer['transfer_rx']}, TX: {peer['transfer_tx']}")
                connected_peers += 1
                gauge_rx.labels(peer=peer['public_key']).set(peer['transfer_rx'])
                gauge_tx.labels(peer=peer['public_key']).set(peer['transfer_tx'])
                gauge_peer_ips.labels(peer=peer['public_key'], ip=peer['allowed_ips']).set(1)
                current_peers.add((peer['public_key'], peer['allowed_ips']))
            
            gauge_peers.set(connected_peers)  # Nombre de pairs connectés
            
            # Mettre à jour les peers existants
            for peer in existing_peers - current_peers:
                gauge_peer_ips.remove(peer[0], peer[1])
            existing_peers = current_peers
        
        time.sleep(interval)

if __name__ == "__main__":
    print(f"Server is running on: http://0.0.0.0:8000")
    container_name = "wireguard"  # Nom du conteneur Docker WireGuard
    start_http_server(8000, addr="0.0.0.0")  # Exposer les métriques sur toutes les interfaces, sur le port 8000
    monitor_wireguard(container_name)
