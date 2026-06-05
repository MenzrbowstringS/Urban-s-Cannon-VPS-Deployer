# Private WireGuard VPS Deployer · 私有 WireGuard VPS 部署器

A macOS / Windows desktop application that helps you automatically configure a personal WireGuard VPN server on your Ubuntu or Debian VPS — no command-line knowledge required.

一款 macOS / Windows 桌面应用，帮你自动在 Ubuntu 或 Debian VPS 上部署私人 WireGuard VPN 服务器——无需任何命令行知识。

---

## What This Software Does · 本软件的功能

- Connects to your VPS via SSH (password or private key)
- Installs and configures WireGuard VPN server on the VPS
- Enables IPv4 forwarding and configures NAT masquerading
- Generates a WireGuard client `.conf` file on your Desktop
- The `.conf` file is ready to import into the official WireGuard app

---

- 通过 SSH 连接你的 VPS（支持密码或私钥）
- 在 VPS 上安装并配置 WireGuard VPN 服务器
- 启用 IPv4 转发并配置 NAT 伪装
- 在你的桌面上生成 WireGuard 客户端 `.conf` 文件
- `.conf` 文件可直接导入官方 WireGuard 应用使用

## What This Software Does NOT Do · 本软件不做的事

- It does **not** connect to a VPN itself
- It does **not** use macOS NetworkExtension
- It does **not** include a built-in VPN client
- It does **not** send your VPS credentials, SSH keys, or WireGuard keys to any third party
- It does **not** modify SSH settings, firewall rules, or SSH ports on your VPS
- It does **not** disable root login or change SSH access in any way

---

- **不会**自己连接 VPN
- **不会**使用系统 VPN 扩展
- **不包含**内置 VPN 客户端
- **不会**将你的 VPS 凭据、SSH 密钥或 WireGuard 密钥发送给任何第三方
- **不会**修改 VPS 上的 SSH 设置、防火墙规则或 SSH 端口
- **不会**禁用 root 登录或以任何方式更改 SSH 访问权限

## Requirements · 使用要求

### On Your Computer · 你的电脑

- macOS 11 (Big Sur) or later, or Windows 10+
- Python 3.11 or later (if running from source)
- [WireGuard](https://www.wireguard.com/install/) (to import and use the generated config)

### On Your VPS · 你的 VPS

- Ubuntu 22.04, Ubuntu 24.04, or Debian 11+
- Root SSH access (or a user with passwordless `sudo`)
- UDP port **51820** (or your chosen WireGuard port) open in your VPS provider's firewall / security group

---

### 你的电脑

- macOS 11+ 或 Windows 10+
- Python 3.11+（从源码运行时需要）
- [WireGuard 客户端](https://www.wireguard.com/install/)（用于导入和使用生成的配置）

### 你的 VPS

- Ubuntu 22.04、Ubuntu 24.04 或 Debian 11+
- Root SSH 权限（或具有免密 `sudo` 的用户）
- VPS 防火墙/安全组中开放 UDP **51820** 端口（或你选择的自定义端口）

## How to Run from Source · 从源码运行

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

## Building for macOS · 打包 macOS 版本

```bash
cd ~/Desktop/Urban\'s\ cannon/Private-WireGuard-VPS-Deployer/
chmod +x build_macos.sh
./build_macos.sh
```

The `.app` will be created at `dist/Urban's Cannon.app`

To create a DMG installer:

```bash
chmod +x create_dmg.sh
./create_dmg.sh
```

The `.dmg` will be at `dist/Urbans-Cannon-1.0.dmg`

## Building for Windows · 打包 Windows 版本

### Prerequisites · 准备条件
- Python 3.11+
- [Inno Setup 6+](https://jrsoftware.org/isinfo.php)

### Local Build · 本地构建
```bat
cd Private-WireGuard-VPS-Deployer
build_windows.bat
```

The `.exe` will be at `dist\Urban's Cannon\Urban's Cannon.exe`.

构建产物在 `dist\Urban's Cannon\Urban's Cannon.exe`。

### Create Installer · 制作安装包
```bat
iscc installer.iss
```

The installer will be at `dist\Urbans-Cannon-1.0-Windows-Setup.exe`.

安装包在 `dist\Urbans-Cannon-1.0-Windows-Setup.exe`。

### GitHub Actions (recommended · 推荐)
Push a tag matching `v*-win` (e.g., `v1.0-win`) to trigger an automated build on GitHub Actions. The installer will be uploaded as a release asset.

推送匹配 `v*-win` 的 tag（如 `v1.0-win`），GitHub Actions 会自动构建并将安装包发布为 Release。

## How to Use — Step by Step · 使用步骤

1. **Open the app · 打开应用** — Double-click `Urban's Cannon` or run `python main.py`.

2. **Enter your VPS details · 填写 VPS 信息：**
   - **VPS Host / IP · 主机 IP** — Your server's IP address (e.g., `1.2.3.4`)
   - **SSH Port · SSH 端口** — Usually `22`（通常是 `22`）
   - **SSH Username · SSH 用户名** — Usually `root`（通常是 `root`）
   - **Authentication Method · 认证方式** — Password or SSH Private Key（密码或 SSH 私钥）

3. **Click "Connect" · 点击「连接」** — Tests the SSH connection before making any changes.（先测试连接，不会修改任何东西。）

4. **Review VPN settings · 检查 VPN 设置** — Default values work for most users. Adjust if needed.（默认值适用于大多数情况，可按需调整。）

5. **Click "Deploy VPN" · 点击「部署 VPN」** — The app will automatically:
   - Connect to your VPS（连接 VPS）
   - Install WireGuard（安装 WireGuard）
   - Configure the server（配置服务器）
   - Generate your client config on the Desktop（在桌面生成客户端配置）

6. **Find the `.conf` file · 找到配置文件** — Saved to your Desktop as `<client-name>-wireguard.conf`.

7. **Import into WireGuard app · 导入 WireGuard：**
   - Open the WireGuard app（打开 WireGuard 应用）
   - Click "Import tunnel(s) from file..."（点击「从文件导入隧道…」）
   - Select your `.conf` file（选择你的 `.conf` 文件）
   - Click "Activate"（点击「激活」）

8. **Done! · 完成！** You're now connected through your private VPN.（你现在已通过私人 VPN 上网。）

## Troubleshooting · 故障排查

### SSH connection fails · SSH 连接失败

- Make sure your VPS IP address is correct · 确认 VPS IP 地址正确
- Verify that SSH port is not blocked · 确认 SSH 端口未被屏蔽
- Double-check your username and password / SSH key · 再次检查用户名和密码/SSH 密钥
- Try connecting manually: `ssh root@your-vps-ip` · 尝试手动连接

### Deployment fails · 部署失败

- Check the Progress Log in the app for specific error messages · 查看应用中的日志
- Ensure your VPS runs Ubuntu 22.04+, Ubuntu 24.04, or Debian 11+ · 确认 VPS 系统版本
- Make sure you have root access or passwordless sudo · 确认有 root 或 sudo 权限
- Run `apt update` manually on the VPS to check for issues · 手动运行 `apt update`

### WireGuard service won't start · WireGuard 服务无法启动

Check on the VPS · 在 VPS 上检查：
```bash
systemctl status wg-quick@wg0 --no-pager
wg show
ip route
```

Common fixes · 常见修复：
```bash
systemctl restart wg-quick@wg0   # Restart WireGuard · 重启服务
modprobe wireguard               # Check kernel module · 检查内核模块
journalctl -u wg-quick@wg0 -n 50 --no-pager   # View logs · 查看日志
```

### VPN connects but websites don't load · VPN 已连接但无法上网

- Make sure IPv4 forwarding is enabled: `sysctl net.ipv4.ip_forward` should show `1`
- 确认 IPv4 转发已启用
- Verify the PostUp/PostDown iptables rules are applied · 确认 iptables 规则已生效
- **Most importantly · 最重要的一点：Check your VPS provider's firewall / security group.**
  Many providers (AWS, DigitalOcean, Vultr, Alibaba Cloud, Tencent Cloud) have an
  external firewall that blocks UDP ports by default. You must add a rule to allow
  UDP port 51820 (or your custom WireGuard port).
  很多 VPS 服务商（AWS、DigitalOcean、Vultr、阿里云、腾讯云等）有外部防火墙，默认屏蔽 UDP 端口。你需要手动添加规则开放 UDP 51820（或自定义端口）。

## Security Reminders · 安全提醒

- **The generated `.conf` file contains your private key. Do not share it with anyone.**
  **生成的 `.conf` 文件包含你的私钥，请勿分享给任何人。**
- This software runs entirely on your local computer. No data is sent anywhere else.
  本软件完全在你的本地电脑上运行，不会向任何地方发送数据。
- SSH passwords are never saved to disk. · SSH 密码不会保存到磁盘。
- WireGuard private keys are never shown in the GUI log. · WireGuard 私钥不会显示在界面日志中。
- Only use this software on your own VPS. · 请仅在你自己的 VPS 上使用本软件。
- Never share your VPS root password. · 永远不要分享你的 VPS root 密码。

## License · 许可

This project is provided as-is for personal use. Use at your own risk.

本项目按原样提供，仅供个人使用。使用风险自负。

---

**Everyone deserves the right to choose — MenZenithRBowstringS · 每个人都该有选择的权利**
