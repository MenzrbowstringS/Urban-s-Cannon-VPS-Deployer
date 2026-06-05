# Urban's Cannon — VPS 自动部署

## 下载 Download

| 平台 Platform | 下载 Download | 版本 Version |
|:---:|---|---|
| Windows | [Urbans-Cannon-1.2-Windows-Setup.exe](https://github.com/MenzrbowstringS/Urban-s-Cannon-VPS-Deployer/releases/download/v1.2-win/Urbans-Cannon-1.2-Windows-Setup.exe) | v1.2 |
| macOS | [Urbans-Cannon-1.2.dmg](https://github.com/MenzrbowstringS/Urban-s-Cannon-VPS-Deployer/releases/download/v1.2-mac/Urbans-Cannon-1.2.dmg) | v1.2 |

---

## 中文

一款 macOS / Windows 桌面应用，帮你自动在 Ubuntu 或 Debian VPS 上部署私人VPN 服务器——无需任何命令行知识。

### 本软件的功能

- 通过 SSH 连接你的 VPS（支持密码或私钥）
- 在 VPS 上安装并配置 WireGuard VPN 服务器
- 启用 IPv4 转发并配置 NAT 伪装
- 在桌面上生成 WireGuard 客户端 `.conf` 文件
- `.conf` 文件可直接导入官方 WireGuard 应用

### 本软件不做的事

- **不会**自己连接 VPN
- **不会**使用系统 VPN 扩展
- **不包含**内置 VPN 客户端
- **不会**将你的 VPS 凭据、SSH 密钥或 WireGuard 密钥发送给任何第三方
- **不会**修改 VPS 上的 SSH 设置、防火墙规则或 SSH 端口
- **不会**禁用 root 登录或以任何方式更改 SSH 访问权限

### 使用要求

**你的电脑：**

- macOS 11+ 或 Windows 10+
- Python 3.11+（从源码运行时需要）
- [WireGuard 客户端](https://www.wireguard.com/install/)（用于导入和使用生成的配置）

**你的 VPS：**

- Ubuntu 22.04、Ubuntu 24.04 或 Debian 11+
- Root SSH 权限（或具有免密 `sudo` 的用户）
- VPS 防火墙/安全组中开放 UDP **51820** 端口（或自定义端口）

### 从源码运行

**macOS：**

```bash
cd ~/Desktop/Urban\'s\ cannon/Private-WireGuard-VPS-Deployer/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Windows：**

```bat
cd Private-WireGuard-VPS-Deployer
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 打包 macOS 版本

```bash
cd ~/Desktop/Urban\'s\ cannon/Private-WireGuard-VPS-Deployer/
chmod +x build_macos.sh
./build_macos.sh
```

`.app` 文件在 `dist/Urban's Cannon.app`

制作 DMG 安装包：

```bash
chmod +x create_dmg.sh
./create_dmg.sh
```

`.dmg` 文件在 `dist/Urbans-Cannon-1.0.dmg`

### 打包 Windows 版本

**准备条件：** Python 3.11+、[Inno Setup 6+](https://jrsoftware.org/isinfo.php)

**本地构建：**

```bat
cd Private-WireGuard-VPS-Deployer
build_windows.bat
```

构建产物在 `dist\Urban's Cannon\Urban's Cannon.exe`。

**制作安装包：**

```bat
iscc installer.iss
```

安装包在 `dist\Urbans-Cannon-1.0-Windows-Setup.exe`。

**GitHub Actions（推荐）：** 推送匹配 `v*-win` 的 tag（如 `v1.0-win`），GitHub Actions 会自动构建并将安装包发布为 Release。

### 使用步骤

1. **打开应用** — 双击 `Urban's Cannon` 或运行 `python main.py`。
2. **填写 VPS 信息：** 主机 IP（如 `1.2.3.4`）、SSH 端口（通常是 `22`）、SSH 用户名（通常是 `root`）、认证方式（密码或 SSH 私钥）。
3. **点击「连接」** — 先测试 SSH 连接，不会修改任何东西。
4. **检查 VPN 设置** — 默认值适用于大多数情况，可按需调整。
5. **点击「部署 VPN」** — 自动连接 VPS、安装 WireGuard、配置服务器、在桌面生成客户端配置。
6. **找到配置文件** — 保存在桌面，文件名为 `<客户端名称>-wireguard.conf`。
7. **导入 WireGuard** — 打开 WireGuard 应用 → 点击「从文件导入隧道…」→ 选择 `.conf` 文件 → 点击「激活」。
8. **完成！** 你现在已通过私人 VPN 上网。

### 故障排查

**SSH 连接失败：** 确认 VPS IP 正确、SSH 端口未被屏蔽、检查用户名和密码/SSH 密钥、尝试手动连接 `ssh root@your-vps-ip`。

**部署失败：** 查看应用日志、确认 VPS 运行 Ubuntu 22.04+ 或 Debian 11+、确认有 root 或 sudo 权限、在 VPS 上手动运行 `apt update`。

**WireGuard 服务无法启动：**

```bash
systemctl status wg-quick@wg0 --no-pager
wg show
ip route
```

常见修复：

```bash
systemctl restart wg-quick@wg0   # 重启服务
modprobe wireguard               # 检查内核模块
journalctl -u wg-quick@wg0 -n 50 --no-pager   # 查看日志
```

**VPN 已连接但无法上网：** 确认 IPv4 转发已启用（`sysctl net.ipv4.ip_forward` 应为 `1`）、确认 iptables 规则已生效。**最重要：检查 VPS 服务商的防火墙/安全组**，很多服务商（AWS、DigitalOcean、Vultr、阿里云、腾讯云等）默认屏蔽 UDP 端口，需手动开放 UDP 51820。

### 安全提醒

- **生成的 `.conf` 文件包含你的私钥，请勿分享给任何人。**
- 本软件完全在你的本地电脑上运行，不会向任何地方发送数据。
- SSH 密码不会保存到磁盘。
- WireGuard 私钥不会显示在界面日志中。
- 请仅在你自己的 VPS 上使用本软件。
- 永远不要分享你的 VPS root 密码。

### 许可

本项目按原样提供，仅供个人使用。使用风险自负。

---

## English

A macOS / Windows desktop application that helps you automatically configure a personal VPN server on your Ubuntu or Debian VPS — no command-line knowledge required.

### What This Software Does

- Connects to your VPS via SSH (password or private key)
- Installs and configures WireGuard VPN server on the VPS
- Enables IPv4 forwarding and configures NAT masquerading
- Generates a WireGuard client `.conf` file on your Desktop
- The `.conf` file is ready to import into the official WireGuard app

### What This Software Does NOT Do

- It does **not** connect to a VPN itself
- It does **not** use system NetworkExtension
- It does **not** include a built-in VPN client
- It does **not** send your VPS credentials, SSH keys, or WireGuard keys to any third party
- It does **not** modify SSH settings, firewall rules, or SSH ports on your VPS
- It does **not** disable root login or change SSH access in any way

### Requirements

**On Your Computer:**

- macOS 11 (Big Sur) or later, or Windows 10+
- Python 3.11 or later (if running from source)
- [WireGuard](https://www.wireguard.com/install/) (to import and use the generated config)

**On Your VPS:**

- Ubuntu 22.04, Ubuntu 24.04, or Debian 11+
- Root SSH access (or a user with passwordless `sudo`)
- UDP port **51820** (or your chosen WireGuard port) open in your VPS provider's firewall / security group

### How to Run from Source

**macOS:**

```bash
cd ~/Desktop/Urban\'s\ cannon/Private-WireGuard-VPS-Deployer/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Windows:**

```bat
cd Private-WireGuard-VPS-Deployer
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Building for macOS

```bash
cd ~/Desktop/Urban\'s\ cannon/Private-WireGuard-VPS-Deployer/
chmod +x build_macos.sh
./build_macos.sh
```

The `.app` will be at `dist/Urban's Cannon.app`

To create a DMG installer:

```bash
chmod +x create_dmg.sh
./create_dmg.sh
```

The `.dmg` will be at `dist/Urbans-Cannon-1.0.dmg`

### Building for Windows

**Prerequisites:** Python 3.11+, [Inno Setup 6+](https://jrsoftware.org/isinfo.php)

**Local Build:**

```bat
cd Private-WireGuard-VPS-Deployer
build_windows.bat
```

The `.exe` will be at `dist\Urban's Cannon\Urban's Cannon.exe`.

**Create Installer:**

```bat
iscc installer.iss
```

The installer will be at `dist\Urbans-Cannon-1.0-Windows-Setup.exe`.

**GitHub Actions (recommended):** Push a tag matching `v*-win` (e.g., `v1.0-win`) to trigger an automated build on GitHub Actions. The installer will be uploaded as a release asset.

### How to Use — Step by Step

1. **Open the app** — Double-click `Urban's Cannon` or run `python main.py`.
2. **Enter your VPS details:** VPS Host / IP (e.g., `1.2.3.4`), SSH Port (usually `22`), SSH Username (usually `root`), Authentication Method (Password or SSH Private Key).
3. **Click "Connect"** — Tests the SSH connection before making any changes.
4. **Review VPN settings** — Default values work for most users. Adjust if needed.
5. **Click "Deploy VPN"** — Automatically connects to your VPS, installs WireGuard, configures the server, and generates your client config on the Desktop.
6. **Find the `.conf` file** — Saved to your Desktop as `<client-name>-wireguard.conf`.
7. **Import into WireGuard app** — Open WireGuard → "Import tunnel(s) from file..." → Select `.conf` → "Activate".
8. **Done!** You're now connected through your private VPN.

### Troubleshooting

**SSH connection fails:** Make sure your VPS IP is correct, verify SSH port is not blocked, double-check username/password or SSH key, try `ssh root@your-vps-ip`.

**Deployment fails:** Check the app log for errors, ensure VPS runs Ubuntu 22.04+ or Debian 11+, make sure you have root/sudo access, run `apt update` manually on the VPS.

**WireGuard service won't start:**

```bash
systemctl status wg-quick@wg0 --no-pager
wg show
ip route
```

Common fixes:

```bash
systemctl restart wg-quick@wg0   # Restart service
modprobe wireguard               # Check kernel module
journalctl -u wg-quick@wg0 -n 50 --no-pager   # View logs
```

**VPN connects but websites don't load:** Ensure IPv4 forwarding is enabled (`sysctl net.ipv4.ip_forward` should be `1`), verify iptables rules are applied. **Most importantly: Check your VPS provider's firewall/security group.** Many providers (AWS, DigitalOcean, Vultr, Alibaba Cloud, Tencent Cloud) block UDP ports by default — add a rule to allow UDP 51820.

### Security Reminders

- **The generated `.conf` file contains your private key. Do not share it with anyone.**
- This software runs entirely on your local computer. No data is sent anywhere else.
- SSH passwords are never saved to disk.
- WireGuard private keys are never shown in the GUI log.
- Only use this software on your own VPS.
- Never share your VPS root password.

### License

This project is provided as-is for personal use. Use at your own risk.

---

每个人都该有选择的权利 · Everyone deserves the right to choose — MenZenithRBowstringS
