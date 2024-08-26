
# 🚀 WireGuard Monitoring with Prometheus and Grafana

Welcome to the **WireGuard Monitoring** project! This project helps you monitor your WireGuard VPN server by collecting important metrics like the number of connected peers, their IPs, and the status of the WireGuard interface. The data is exposed to Prometheus, which you can visualize with Grafana.

## 📋 Table of Contents
- [Features](#-features)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Script](#running-the-script)
- [Monitoring Metrics](#-monitoring-metrics)
  - [WireGuard Metrics](#wireguard-metrics)
- [Grafana Dashboard](#-grafana-dashboard)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features
- Monitor the number of connected peers 👥
- Track the status of your WireGuard interface 🔄
- Get the IP addresses of connected peers 🌐
- Collect metrics on data transferred per peer 📊

## 🛠️ Getting Started

### Prerequisites
Before you start, make sure you have the following installed:
- Docker 🐳
- Python 3.7+ 🐍
- Prometheus 🟠
- Grafana 📊

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/VERNIERELoic/wireguard-python-monitoring.git
   cd wireguard-monitoring
   ```

2. **Install the required Python packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure your WireGuard container is running**:
   Make sure your WireGuard container is running and accessible via Docker.

### Running the Script

1. **Run the Python monitoring script**:
   ```bash
   python3 wg_monitor.py
   ```
   This will start the monitoring server on `http://0.0.0.0:8000`.

2. **Configure Prometheus**:
   Add the following job to your `prometheus.yml` configuration file:
   ```yaml
   scrape_configs:
     - job_name: 'wireguard-monitoring'
       static_configs:
         - targets: ['<host_ip>:8000']
   ```

3. **Start Prometheus**:
   Ensure Prometheus is running and correctly scrapes the metrics from the monitoring script.

## 📊 Monitoring Metrics

### WireGuard Metrics
Here’s a breakdown of the metrics monitored by this script:

- **`wireguard_rx_bytes`**: 
  - **Description**: The number of bytes received by each peer.
  - **Labels**: `peer` (public key of the peer)
  - **Example**: `wireguard_rx_bytes{peer="abc123..."} 123456`

- **`wireguard_tx_bytes`**:
  - **Description**: The number of bytes transmitted by each peer.
  - **Labels**: `peer` (public key of the peer)
  - **Example**: `wireguard_tx_bytes{peer="abc123..."} 654321`

- **`wireguard_connected_peers`**:
  - **Description**: The total number of peers currently connected to the WireGuard server.
  - **Example**: `wireguard_connected_peers 5`

- **`wireguard_peer_ips`**:
  - **Description**: The IP addresses of connected peers.
  - **Labels**: `peer` (public key of the peer), `ip` (IP address of the peer)
  - **Example**: `wireguard_peer_ips{peer="abc123...", ip="10.0.0.2"} 1`

- **`wireguard_status`**:
  - **Description**: The status of the WireGuard interface. 1 indicates that the interface is up.
  - **Labels**: `interface` (name of the WireGuard interface)
  - **Example**: `wireguard_status{interface="wg0"} 1`

## 📈 Grafana Dashboard

To visualize the metrics, you can set up a Grafana dashboard:
1. **Add Prometheus as a data source in Grafana**.
2. **Create a new dashboard** and add panels for the metrics described above.
3. **Customize your dashboard** with graphs, tables, and alerts to get a comprehensive view of your WireGuard server.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve this project.

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
