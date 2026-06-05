"""
deployer.py — Core WireGuard VPS deployment logic.

Handles SSH connection, system detection, WireGuard installation,
key generation, server configuration, and client config generation.
All operations are performed locally; no data is sent to any third party.
"""

import os
import stat
from typing import Callable, Optional

import paramiko

# ---------------------------------------------------------------------------
# Supported platforms
# ---------------------------------------------------------------------------
SUPPORTED_OS = {"ubuntu", "debian"}


# ---------------------------------------------------------------------------
# Deployment configuration
# ---------------------------------------------------------------------------
class DeployConfig:
    """Holds all user-supplied deployment parameters."""

    def __init__(
        self,
        host: str,
        ssh_port: int = 22,
        ssh_username: str = "root",
        auth_method: str = "password",
        password: str = "",
        ssh_key_path: str = "",
        wg_listen_port: int = 51820,
        client_name: str = "macbook",
        vpn_subnet: str = "10.8.0.0/24",
        server_vpn_address: str = "10.8.0.1/24",
        client_vpn_address: str = "10.8.0.2/32",
        dns: str = "1.1.1.1, 8.8.8.8",
        allowed_ips: str = "0.0.0.0/0",
        output_path: str = "",
    ):
        self.host = host.strip()
        self.ssh_port = ssh_port
        self.ssh_username = ssh_username.strip()
        self.auth_method = auth_method
        self.password = password
        self.ssh_key_path = ssh_key_path.strip()
        self.wg_listen_port = wg_listen_port
        self.client_name = client_name.strip()
        self.vpn_subnet = vpn_subnet.strip()
        self.server_vpn_address = server_vpn_address.strip()
        self.client_vpn_address = client_vpn_address.strip()
        self.dns = dns.strip()
        self.allowed_ips = allowed_ips.strip()
        self.output_path = output_path.strip()

    def validate(self) -> list[str]:
        """Return a list of validation error messages (empty = valid)."""
        errors = []
        if not self.host:
            errors.append("VPS Host / IP is required.")
        if not self.ssh_username:
            errors.append("SSH Username is required.")
        if not isinstance(self.ssh_port, int) or self.ssh_port < 1 or self.ssh_port > 65535:
            errors.append("SSH Port must be a valid port number (1-65535).")
        if not isinstance(self.wg_listen_port, int) or self.wg_listen_port < 1 or self.wg_listen_port > 65535:
            errors.append("WireGuard Listen Port must be a valid port number (1-65535).")
        if not self.client_name:
            errors.append("Client Name is required.")
        if self.auth_method == "password" and not self.password:
            errors.append("Password is required when Password authentication is selected.")
        if self.auth_method == "key":
            if not self.ssh_key_path:
                errors.append("SSH Private Key path is required when Key authentication is selected.")
            elif not os.path.isfile(os.path.expanduser(self.ssh_key_path)):
                errors.append(f"SSH Private Key file not found: {self.ssh_key_path}")
        return errors


# ---------------------------------------------------------------------------
# SSH helpers
# ---------------------------------------------------------------------------
def _create_ssh_client(config: DeployConfig) -> paramiko.SSHClient:
    """Create and connect a paramiko SSH client based on DeployConfig."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    connect_kwargs = {
        "hostname": config.host,
        "port": config.ssh_port,
        "username": config.ssh_username,
        "timeout": 15,
        "banner_timeout": 15,
    }

    if config.auth_method == "password":
        connect_kwargs["password"] = config.password
    else:
        key_path = os.path.expanduser(config.ssh_key_path)
        try:
            # Try loading various private key formats
            pkey = None
            for pkey_class in (paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey, paramiko.DSSKey):
                try:
                    pkey = pkey_class.from_private_key_file(key_path)
                    break
                except paramiko.SSHException:
                    continue
            if pkey is None:
                # Last resort: try password-protected key with empty password
                try:
                    pkey = paramiko.RSAKey.from_private_key_file(key_path, password=None)
                except paramiko.SSHException:
                    pass
            if pkey is None:
                raise ValueError(
                    "Could not load SSH private key. Verify the key is in a supported format "
                    "(RSA, Ed25519, ECDSA, DSS) and is not password-protected, or use Password login."
                )
            connect_kwargs["pkey"] = pkey
        except Exception as e:
            raise RuntimeError(f"Failed to load SSH private key: {e}") from e

    client.connect(**connect_kwargs)
    return client


def _exec_command(
    client: paramiko.SSHClient,
    command: str,
    log_callback: Optional[Callable[[str], None]] = None,
    sensitive: bool = False,
) -> tuple[int, str, str]:
    """Execute a command on the remote host.

    Returns (exit_code, stdout, stderr).  If *sensitive* is True the command
    itself is never logged (used for key-generation commands).
    """
    if log_callback and not sensitive:
        log_callback(f"  $ {command}")
    stdin, stdout, stderr = client.exec_command(command, timeout=120)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    exit_code = stdout.channel.recv_exit_status()
    return exit_code, out, err


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def test_ssh_connection(config: DeployConfig) -> str:
    """Test SSH connectivity and return a success message.

    Raises an exception with a user-friendly message on failure.
    """
    try:
        client = _create_ssh_client(config)
    except paramiko.AuthenticationException:
        raise RuntimeError(
            "SSH authentication failed. Check your username, password, or SSH key."
        )
    except paramiko.SSHException as e:
        raise RuntimeError(f"SSH connection error: {e}")
    except Exception as e:
        raise RuntimeError(f"Could not connect to {config.host}:{config.ssh_port} — {e}")

    try:
        exit_code, out, err = _exec_command(client, "echo connected && uname -a")
        if exit_code != 0:
            raise RuntimeError(f"Remote command failed: {err or out}")
        return f"SSH connection successful.\n{out}"
    finally:
        client.close()


def deploy_wireguard(
    config: DeployConfig,
    log_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """Run the full WireGuard deployment workflow on the VPS.

    Returns the path to the generated client config file on the local Mac.
    """
    def log(msg: str):
        if log_callback:
            log_callback(msg)

    # ------------------------------------------------------------------
    # Step 1 – Connect
    # ------------------------------------------------------------------
    log("Connecting to VPS...")
    try:
        client = _create_ssh_client(config)
    except paramiko.AuthenticationException:
        raise RuntimeError(
            "SSH authentication failed. Check your username, password, or SSH key."
        )
    except Exception as e:
        raise RuntimeError(f"SSH connection to {config.host}:{config.ssh_port} failed: {e}")
    log("SSH connected.")

    try:
        # ------------------------------------------------------------------
        # Step 2 – Check OS
        # ------------------------------------------------------------------
        log("Checking operating system...")
        code, os_release, err = _exec_command(client, "cat /etc/os-release")
        if code != 0:
            raise RuntimeError(f"Could not read /etc/os-release: {err}")

        os_id = ""
        for line in os_release.lower().splitlines():
            if line.startswith("id="):
                os_id = line.split("=", 1)[1].strip().strip('"')
                break
        if os_id not in SUPPORTED_OS:
            raise RuntimeError(
                f"Unsupported VPS OS: '{os_id}'. "
                "This application currently supports Ubuntu and Debian only."
            )
        log(f"  Detected: {os_id}")

        # ------------------------------------------------------------------
        # Step 3 – Install WireGuard
        # ------------------------------------------------------------------
        log("Installing WireGuard...")
        code, out, err = _exec_command(client, "apt-get update -qq")
        if code != 0:
            raise RuntimeError(f"apt-get update failed: {err or out}")

        code, out, err = _exec_command(
            client,
            "DEBIAN_FRONTEND=noninteractive apt-get install -y -qq wireguard iptables qrencode",
        )
        if code != 0:
            raise RuntimeError(f"WireGuard installation failed: {err or out}")
        log("  WireGuard installed.")

        # ------------------------------------------------------------------
        # Step 4 – Enable IPv4 forwarding
        # ------------------------------------------------------------------
        log("Enabling IPv4 forwarding...")
        _exec_command(
            client,
            "echo 'net.ipv4.ip_forward=1' > /etc/sysctl.d/99-wireguard-forward.conf",
        )
        code, out, err = _exec_command(client, "sysctl --system")
        if code != 0:
            raise RuntimeError(f"sysctl --system failed: {err or out}")
        log("  IPv4 forwarding enabled.")

        # ------------------------------------------------------------------
        # Step 5 – Detect default network interface
        # ------------------------------------------------------------------
        log("Detecting default network interface...")
        code, default_iface, err = _exec_command(
            client,
            "ip route | awk '/default/ {print $5; exit}'",
        )
        if code != 0 or not default_iface:
            raise RuntimeError(
                "Could not detect default network interface. "
                "Check that the VPS has a working network connection."
            )
        log(f"  Default interface: {default_iface}")

        # ------------------------------------------------------------------
        # Step 6 – Generate WireGuard keys
        # ------------------------------------------------------------------
        log("Generating WireGuard keys...")
        _, server_priv, _ = _exec_command(client, "wg genkey", sensitive=True)
        if not server_priv:
            raise RuntimeError("Failed to generate server private key.")
        _, server_pub, _ = _exec_command(
            client, f"echo '{server_priv}' | wg pubkey", sensitive=True
        )
        if not server_pub:
            raise RuntimeError("Failed to generate server public key.")

        _, client_priv, _ = _exec_command(client, "wg genkey", sensitive=True)
        if not client_priv:
            raise RuntimeError("Failed to generate client private key.")
        _, client_pub, _ = _exec_command(
            client, f"echo '{client_priv}' | wg pubkey", sensitive=True
        )
        if not client_pub:
            raise RuntimeError("Failed to generate client public key.")
        log("  Keys generated.")

        # ------------------------------------------------------------------
        # Step 7 – Backup existing config if present
        # ------------------------------------------------------------------
        log("Backing up existing wg0.conf if needed...")
        code, check_out, _ = _exec_command(client, "ls /etc/wireguard/wg0.conf 2>/dev/null || true")
        if check_out and "wg0.conf" in check_out:
            timestamp_cmd = 'date +%Y%m%d-%H%M%S'
            _, timestamp, _ = _exec_command(client, timestamp_cmd)
            backup_path = f"/etc/wireguard/wg0.conf.backup-{timestamp}"
            code, _, err = _exec_command(client, f"cp /etc/wireguard/wg0.conf {backup_path}")
            if code != 0:
                raise RuntimeError(f"Failed to backup existing config: {err}")
            log(f"  Backed up to: {backup_path}")
        else:
            log("  No existing config to backup.")

        # Ensure wireguard directory exists
        _exec_command(client, "mkdir -p /etc/wireguard")

        # ------------------------------------------------------------------
        # Step 8 – Write server config
        # ------------------------------------------------------------------
        log("Writing WireGuard server config...")
        server_config = (
            f"[Interface]\n"
            f"Address = {config.server_vpn_address}\n"
            f"ListenPort = {config.wg_listen_port}\n"
            f"PrivateKey = {server_priv}\n"
            f"PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; "
            f"iptables -A FORWARD -o wg0 -j ACCEPT; "
            f"iptables -t nat -A POSTROUTING -o {default_iface} -j MASQUERADE\n"
            f"PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; "
            f"iptables -D FORWARD -o wg0 -j ACCEPT; "
            f"iptables -t nat -D POSTROUTING -o {default_iface} -j MASQUERADE\n\n"
            f"[Peer]\n"
            f"PublicKey = {client_pub}\n"
            f"AllowedIPs = {config.client_vpn_address}\n"
        )

        # Write via heredoc to avoid escaping issues
        _exec_command(
            client,
            f"cat > /etc/wireguard/wg0.conf << 'WGEOCONF'\n{server_config}\nWGEOCONF",
        )
        code, _, err = _exec_command(client, "chmod 600 /etc/wireguard/wg0.conf")
        if code != 0:
            raise RuntimeError(f"Failed to set permissions on wg0.conf: {err}")
        log("  Server config written.")

        # ------------------------------------------------------------------
        # Step 9 – Start WireGuard
        # ------------------------------------------------------------------
        log("Starting WireGuard service...")
        code, out, err = _exec_command(client, "systemctl enable wg-quick@wg0")
        if code != 0:
            raise RuntimeError(f"Failed to enable WireGuard service: {err or out}")

        code, out, err = _exec_command(client, "systemctl restart wg-quick@wg0")
        if code != 0:
            raise RuntimeError(f"Failed to restart WireGuard service: {err or out}")

        code, status, err = _exec_command(client, "systemctl is-active wg-quick@wg0")
        if "active" not in status:
            # Gather diagnostics
            _, diag, _ = _exec_command(
                client, "systemctl status wg-quick@wg0 --no-pager -l"
            )
            raise RuntimeError(
                f"WireGuard service is not active (status: {status}).\n\n"
                f"Diagnostics:\n{diag}"
            )
        log("  WireGuard service is active.")

        # ------------------------------------------------------------------
        # Step 10 – Generate client config
        # ------------------------------------------------------------------
        log("Generating client config...")
        client_config = (
            f"[Interface]\n"
            f"PrivateKey = {client_priv}\n"
            f"Address = {config.client_vpn_address}\n"
            f"DNS = {config.dns}\n\n"
            f"[Peer]\n"
            f"PublicKey = {server_pub}\n"
            f"Endpoint = {config.host}:{config.wg_listen_port}\n"
            f"AllowedIPs = {config.allowed_ips}\n"
            f"PersistentKeepalive = 25\n"
        )

        # ------------------------------------------------------------------
        # Step 11 – Save client config to local Desktop
        # ------------------------------------------------------------------
        log("Saving client config to Desktop...")
        output_path = save_client_config_to_desktop(
            client_config, config.client_name, config.output_path
        )
        log(f"Config saved to: {output_path}")

        # ------------------------------------------------------------------
        # Step 12 – Reveal in file manager
        # ------------------------------------------------------------------
        log("Revealing config in file manager...")
        import subprocess as _subprocess
        import sys as _sys
        if _sys.platform == "darwin":
            _subprocess.run(["open", "-R", output_path], check=False)
        elif _sys.platform == "win32":
            _subprocess.run(["explorer", "/select,", output_path], check=False)

        log("")
        log("Deployment complete. Import the generated .conf file into the official WireGuard macOS app.")
        log("")
        log("IMPORTANT: If WireGuard cannot connect, make sure UDP port "
            f"{config.wg_listen_port} is allowed in your VPS provider firewall/security group.")

        return output_path

    finally:
        client.close()


def save_client_config_to_desktop(
    client_config: str,
    client_name: str,
    output_path: str = "",
) -> str:
    """Save the WireGuard client config to the user's Desktop.

    Handles filename collisions by appending a numeric suffix.
    """
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    if output_path:
        file_path = os.path.expanduser(output_path)
    else:
        file_path = os.path.join(desktop, f"{client_name}-wireguard.conf")

    # Handle filename collisions
    if os.path.exists(file_path):
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        stem = base_name.rsplit(".", 1)[0] if "." in base_name else base_name
        ext = "." + base_name.rsplit(".", 1)[1] if "." in base_name else ".conf"
        counter = 1
        while os.path.exists(os.path.join(dir_name, f"{stem}-{counter}{ext}")):
            counter += 1
        file_path = os.path.join(dir_name, f"{stem}-{counter}{ext}")

    with open(file_path, "w") as f:
        f.write(client_config)

    # Set restrictive permissions (private key inside)
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)

    return file_path
