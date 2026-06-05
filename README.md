# Private WireGuard VPS Deployer

A macOS desktop application that helps you automatically configure a personal WireGuard VPN server on your Ubuntu or Debian VPS — no command-line knowledge required.

## What This Software Does

- Connects to your VPS via SSH (password or private key)
- Installs and configures WireGuard VPN server on the VPS
- Enables IPv4 forwarding and configures NAT masquerading
- Generates a WireGuard client `.conf` file on your Mac Desktop
- The `.conf` file is ready to import into the official [WireGuard macOS app](https://apps.apple.com/app/wireguard/id1451685025)

## What This Software Does NOT Do

- It does **not** connect to a VPN itself
- It does **not** use macOS NetworkExtension
- It does **not** include a built-in VPN client
- It does **not** send your VPS credentials, SSH keys, or WireGuard keys to any third party
- It does **not** modify SSH settings, firewall rules, or SSH ports on your VPS
- It does **not** disable root login or change SSH access in any way

## Requirements

### On Your Mac

- macOS 11 (Big Sur) or later
- Python 3.11 or later (if running from source)
- [WireGuard for macOS](https://apps.apple.com/app/wireguard/id1451685025) (to import and use the generated config)

### On Your VPS

- Ubuntu 22.04, Ubuntu 24.04, or Debian 11+
- Root SSH access (or a user with passwordless `sudo`)
- UDP port **51820** (or your chosen WireGuard port) open in your VPS provider's firewall / security group

## How to Run from Source

Open **Terminal** on your Mac and run:

```bash
cd ~/Desktop/Urban\'s\ cannon/Private-WireGuard-VPS-Deployer/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## How to Package as a macOS App

```bash
cd ~/Desktop/Urban\'s\ cannon/Private-WireGuard-VPS-Deployer/
chmod +x build_macos.sh
./build_macos.sh
```

The `.app` will be created at:
```
dist/Private WireGuard VPS Deployer.app
```

## Building for Windows

### Prerequisites (Windows machine or VM)
- Python 3.11+
- [Inno Setup 6+](https://jrsoftware.org/isinfo.php)

### Local Build
```bat
cd Private-WireGuard-VPS-Deployer
build_windows.bat
```
The `.exe` will be at `dist\Urban's Cannon\Urban's Cannon.exe`.

### Create Installer
```bat
iscc installer.iss
```
The installer will be at `dist\Urbans-Cannon-1.0-Windows-Setup.exe`.

### GitHub Actions (recommended)
Push a tag matching `v*-win` (e.g., `v1.0-win`) to trigger an automated build on GitHub Actions. The installer will be uploaded as a release asset.

## How to Create a DMG Installer

```bash
cd ~/Desktop/Urban\'s\ cannon/Private-WireGuard-VPS-Deployer/
chmod +x create_dmg.sh
./create_dmg.sh
```

The `.dmg` will be created at:
```
dist/Private-WireGuard-VPS-Deployer.dmg
```

## How to Use — Step by Step

1. **Open the app** — Double-click `Private WireGuard VPS Deployer.app` or run `python main.py`.

2. **Enter your VPS details:**
   - **VPS Host / IP** — Your server's IP address (e.g., `1.2.3.4`)
   - **SSH Port** — Usually `22`
   - **SSH Username** — Usually `root`
   - **Authentication Method** — Choose Password or SSH Private Key

3. **Click "Test SSH Connection"** — This verifies your Mac can reach the VPS before making any changes.

4. **Review VPN settings** — Default values work for most users. You can adjust the port, VPN addresses, or client name if needed.

5. **Click "Deploy VPN"** — The app will:
   - Connect to your VPS
   - Install WireGuard
   - Configure the server
   - Generate your client config on the Desktop

6. **Find the `.conf` file** — It will be saved to your Desktop as `macbook-wireguard.conf` (or your chosen client name). Finder will open automatically.

7. **Import into WireGuard app:**
   - Open the WireGuard macOS app
   - Click "Import tunnel(s) from file..."
   - Select your `.conf` file from the Desktop
   - Click "Activate"

8. **Done!** Your Mac is now connected through your private VPN.

## Troubleshooting

### SSH connection fails

- Make sure your VPS IP address is correct
- Verify that SSH port 22 (or your custom port) is not blocked
- Double-check your username and password / SSH key
- Try connecting manually: `ssh root@your-vps-ip`

### Deployment fails

- Check the Progress Log in the app for specific error messages
- Ensure your VPS runs Ubuntu 22.04+, Ubuntu 24.04, or Debian 11+
- Make sure you have root access or passwordless sudo
- Run `apt update` manually on the VPS to check for issues

### WireGuard service won't start

Check on the VPS:
```bash
systemctl status wg-quick@wg0 --no-pager
wg show
ip route
```

Common fixes:
```bash
# Restart WireGuard
systemctl restart wg-quick@wg0

# Check kernel module
modprobe wireguard

# View logs
journalctl -u wg-quick@wg0 -n 50 --no-pager
```

### VPN connects but websites don't load

- Make sure IPv4 forwarding is enabled: `sysctl net.ipv4.ip_forward` should show `1`
- Verify the PostUp/PostDown iptables rules are applied
- Check that the default network interface was detected correctly
- **Most importantly: Check your VPS provider's firewall / security group.**
  Many providers (AWS, DigitalOcean, Vultr, Alibaba Cloud, Tencent Cloud) have an
  external firewall that blocks UDP ports by default. You must add a rule to allow
  UDP port 51820 (or your custom WireGuard port).

## Security Reminders

- **The generated `.conf` file contains your private key. Do not share it with anyone.**
- This software runs entirely on your local Mac. No data is sent anywhere else.
- SSH passwords are never saved to disk.
- WireGuard private keys are never shown in the GUI log.
- Only use this software on your own VPS.
- Never share your VPS root password.

## License

This project is provided as-is for personal use. Use at your own risk.
