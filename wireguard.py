from prometheus_client import start_http_server, Gauge, Counter
import subprocess
import time

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

def parse_wg_show_dump(output):
    """Parse l'output de wg show all dump en un format lisible."""
    lines = output.splitlines()
    peers_info = []
    
    for line in lines:
        fields = line.split('\t')
        
        if len(fields) >= 9 and fields[0].startswith('wg'):
            peer = {
                "interface": fields[0],
                "public_key": fields[1],
                "endpoint": fields[3],
                "allowed_ips": fields[4],
                "latest_handshake": fields[6],
                "transfer_rx": int(fields[7]),
                "transfer_tx": int(fields[8])
            }
            peers_info.append(peer)
        elif len(fields) >= 8:
            peer = {
                "public_key": fields[0],
                "endpoint": fields[2],
                "allowed_ips": fields[3],
                "latest_handshake": fields[5],
                "transfer_rx": int(fields[6]),
                "transfer_tx": int(fields[7])
            }
            peers_info.append(peer)
    
    return peers_info

def monitor_wireguard(container_name, interval=10):
    """Monitor WireGuard dans le conteneur Docker depuis le host."""
    while True:
        output = run_docker_command(container_name, 'wg show all dump')
        if output:
            peers_info = parse_wg_show_dump(output)
            gauge_peers.set(len(peers_info))  # Nombre de pairs connectés
            for peer in peers_info:
                gauge_rx.labels(peer=peer['public_key']).set(peer['transfer_rx'])
                gauge_tx.labels(peer=peer['public_key']).set(peer['transfer_tx'])
                gauge_peer_ips.labels(peer=peer['public_key'], ip=peer['allowed_ips']).set(1)
                
                # Mettre à jour le statut de WireGuard
                gauge_wireguard_status.labels(interface=peer['interface']).set(1)
        
        time.sleep(interval)

if __name__ == "__main__":
    print(f"Server is running on: http://0.0.0.0:8000")
    container_name = "wireguard"  # Nom du conteneur Docker WireGuard
    start_http_server(8000, addr="0.0.0.0")  # Exposer les métriques sur toutes les interfaces, sur le port 8000
    monitor_wireguard(container_name)
