"""
i18n.py — Chinese / English translation for Urban's Cannon.

Usage:
    from i18n import tr, set_lang, LANG
    label.setText(tr("host_ip"))
    set_lang("zh")  # switch to Chinese
"""

LANG = "en"  # default

_translations = {
    "en": {},
    "zh": {},
}

def add(key: str, en: str, zh: str):
    _translations["en"][key] = en
    _translations["zh"][key] = zh

def tr(key: str) -> str:
    return _translations.get(LANG, _translations["en"]).get(key, key)

def set_lang(lang: str):
    global LANG
    if lang in ("en", "zh"):
        LANG = lang

# ============================================================
# All UI strings
# ============================================================

add("app_title",       "Urban's Cannon",            "Urban's Cannon")
add("app_subtitle",    "Private VPS Deployer",       "私有 VPS 部署器")

# Segmented tabs (legacy keys, kept for compatibility)
add("tab_connection",  "Connection",    "连接")
add("tab_vpn",         "VPN Config",    "VPN 配置")
add("tab_log",         "Log",           "日志")

# Stepper step labels
add("step_connect",    "Connect",       "连接")
add("step_configure",  "Configure",     "配置")
add("step_deploy",     "Deploy",        "部署")

# Connect button states
add("connect",         "Connect",       "连接")
add("connecting",      "Connecting…",   "正在连接…")
add("connected",       "✓ Connected",   "✓ 已连接")
add("connect_failed",  "Connection failed", "连接失败")

# Connection page
add("vps_connection",  "VPS Connection",     "VPS 连接")
add("host_ip",         "Host / IP:",         "主机 / IP：")
add("ssh_port",        "SSH Port:",          "SSH 端口：")
add("username",        "Username:",          "用户名：")
add("auth_method",     "Auth Method:",       "认证方式：")
add("password",        "Password:",          "密码：")
add("ssh_key",         "SSH Key:",           "SSH 密钥：")
add("browse",          "Browse...",          "浏览...")
add("test_ssh",        "Test SSH Connection","测试 SSH 连接")
add("placeholder_host","1.2.3.4",            "1.2.3.4")
add("placeholder_password", "Enter SSH password", "输入 SSH 密码")
add("placeholder_key", "~/.ssh/id_rsa",      "~/.ssh/id_rsa")
add("auth_password",   "Password",           "密码")
add("auth_key",        "SSH Private Key",    "SSH 私钥")

# VPN Config page
add("wg_settings",     "WireGuard Settings",  "WireGuard 设置")
add("listen_port",     "Listen Port:",        "监听端口：")
add("vpn_subnet",      "VPN Subnet:",         "VPN 子网：")
add("server_addr",     "Server Address:",     "服务器地址：")
add("client_addr",     "Client Address:",     "客户端地址：")
add("dns",             "DNS:",                "DNS：")
add("allowed_ips",     "Allowed IPs:",        "允许的 IP：")
add("client_section",  "Client",              "客户端")
add("client_name",     "Client Name:",        "客户端名称：")
add("output",          "Output:",             "输出路径：")
add("deploy_vpn",      "Deploy VPN",          "部署 VPN")

# Log page
add("show_finder",     "Show in Folder",      "在文件夹中显示")
add("clear_log",       "Clear Log",           "清空日志")

# Status messages
add("status_ready",    "Ready",               "就绪")
add("status_testing",  "Testing SSH connection...", "正在测试 SSH 连接...")
add("status_ssh_ok",   "SSH connection successful.", "SSH 连接成功。")
add("status_ssh_fail", "SSH connection failed.", "SSH 连接失败。")
add("status_connecting", "Connecting to VPS…",       "正在连接 VPS…")
add("status_connected",  "Connected — opening VPN config", "已连接 — 正在打开 VPN 配置")
add("status_connect_first", "Connect to your VPS first", "请先连接到你的 VPS")
# Footer connection-status indicator
add("footer_disconnected", "Not connected",          "未连接")
add("footer_connecting",   "Connecting…",            "正在连接…")
add("footer_connected",    "Connected",              "已连接")
add("status_validation_failed", "Validation failed", "输入校验失败")
add("status_deploying", "Deploying WireGuard VPN...", "正在部署 WireGuard VPN...")
add("status_deploy_ok", "Deployment complete.", "部署完成。")
add("status_deploy_fail", "Deployment failed. See log for details.", "部署失败，详见日志。")

# Dialog titles
add("dlg_select_key",  "Select SSH Private Key", "选择 SSH 私钥")
add("dlg_save_config", "Save Config As",         "保存配置文件为")
add("dlg_all_files",   "All Files (*)",          "所有文件 (*)")
add("dlg_wg_conf",     "WireGuard Config (*.conf);;All Files (*)", "WireGuard 配置 (*.conf);;所有文件 (*)")

# Log messages
add("log_ssh_test",    "--- Test SSH Connection ---", "--- 测试 SSH 连接 ---")
add("log_deploy_start","Starting WireGuard VPN Deployment", "开始部署 WireGuard VPN")
add("log_separator",   "=" * 50,                      "=" * 50)
add("log_error_prefix","Error: ",                     "错误：")
add("log_troubleshooting",
    "Troubleshooting:\n"
    "  1. Verify VPS runs Ubuntu 22.04+ or Debian 11+.\n"
    "  2. Confirm root/sudo access.\n"
    "  3. Check no other WireGuard instance is running.\n"
    "  4. Ensure UDP port is open in VPS firewall/security group.",
    "故障排查：\n"
    "  1. 确认 VPS 运行 Ubuntu 22.04+ 或 Debian 11+。\n"
    "  2. 确认有 root/sudo 权限。\n"
    "  3. 检查没有其他 WireGuard 实例在运行。\n"
    "  4. 确保 VPS 防火墙/安全组已开放 UDP 端口。")
add("log_file_missing", "Config file no longer exists.", "配置文件已不存在。")

# Language switch
add("lang_label",      "EN",          "中")

# ============================================================
# Help / Instructions dialog
# ============================================================
add("help_title",     "How to Use",                   "使用说明")
add("help_tooltip",   "How to use",                   "使用说明")
add("help_got_it",    "Got it",                       "知道了")
add("help_dont_show", "Don't show this on startup",   "启动时不再自动显示")

_HELP_EN = """
<div style="color:#E8E2D6; font-size:13px;">
<p style="color:#A89C8B;">This tool automatically deploys your Ubuntu VPS as a private VPN
server and, by default, generates a WireGuard-importable
<span style="color:#C5854C;"><b>.conf</b></span> file on your Mac Desktop.</p>

<p style="color:#F2ECE0;"><b>Before you start, prepare</b></p>
<ul style="color:#A89C8B;">
<li>The VPS Public IPv4</li>
<li>SSH username (usually <b>root</b>)</li>
<li>SSH port (usually <b>22</b>)</li>
<li>SSH password or SSH private key</li>
<li>A VPS running Ubuntu 22.04 / 24.04</li>
</ul>

<p style="color:#F2ECE0;"><b>Steps</b></p>
<ol style="color:#A89C8B;">
<li>Enter the VPS IP, SSH port, username, and auth method.</li>
<li>Click <span style="color:#C5854C;"><b>Connect</b></span> to test and connect to the VPS.</li>
<li>Once connected it opens the config page &mdash; click
    <span style="color:#C5854C;"><b>Deploy VPN</b></span> to start the automatic deployment.</li>
<li>When finished, the app generates the WireGuard
    <span style="color:#C5854C;"><b>.conf</b></span> file on your Desktop by default.</li>
<li>Open WireGuard and import the .conf file to enable the connection.</li>
</ol>

<p style="color:#F2ECE0;"><b>Note</b></p>
<p style="color:#A89C8B;">Do not share the generated .conf file &mdash; it contains your VPN
private key. If the VPN can't connect, check whether your VPS provider's
firewall has opened <span style="color:#57B89A;"><b>UDP port 51820</b></span>.</p>

<p style="color:#C5854C;"><i>Everyone deserves the right to choose &mdash; MenZenithRBowstringS</i></p>
</div>
"""

_HELP_ZH = """
<div style="color:#E8E2D6; font-size:13px;">
<p style="color:#A89C8B;">本工具用于将你的 Ubuntu VPS 自动部署为私人 VPN 服务器，并默认在
Mac 桌面生成可导入 WireGuard 的 <span style="color:#C5854C;"><b>.conf</b></span> 配置文件。</p>

<p style="color:#F2ECE0;"><b>使用前请准备</b></p>
<ul style="color:#A89C8B;">
<li>VPS 的 Public IPv4</li>
<li>SSH 用户名（通常为 <b>root</b>）</li>
<li>SSH 端口（通常为 <b>22</b>）</li>
<li>SSH 密码 或 SSH Private Key</li>
<li>Ubuntu 22.04 / 24.04 系统的 VPS</li>
</ul>

<p style="color:#F2ECE0;"><b>使用步骤</b></p>
<ol style="color:#A89C8B;">
<li>输入 VPS IP、SSH 端口、用户名和登录方式。</li>
<li>点击 <span style="color:#C5854C;"><b>Connect</b></span> 测试并连接 VPS。</li>
<li>连接成功后会自动进入配置页，点击
    <span style="color:#C5854C;"><b>Deploy VPN</b></span> 开始自动部署。</li>
<li>部署完成后，软件默认在桌面生成 WireGuard
    <span style="color:#C5854C;"><b>.conf</b></span> 文件。</li>
<li>打开 WireGuard，导入该 .conf 文件即可启用连接。</li>
</ol>

<p style="color:#F2ECE0;"><b>注意</b></p>
<p style="color:#A89C8B;">请不要分享生成的 .conf 文件，它包含你的 VPN 私钥。若 VPN 无法连接，
请检查 VPS 服务商防火墙是否已开放 <span style="color:#57B89A;"><b>UDP 51820</b></span> 端口。</p>

<p style="color:#C5854C;"><i>每个人都该有选择的权利 —— MenZenithRBowstringS</i></p>
</div>
"""

add("help_html", _HELP_EN, _HELP_ZH)
