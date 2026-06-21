#!/usr/bin/env python3
"""WeWe-RSS 自动登录脚本：创建登录→等扫码→自动保存账号"""
import urllib.request, urllib.error, json, time, sys, io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API = "http://localhost:4000"

def rpc(method, path, body=None):
    url = f"{API}/trpc/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

print("📱 正在生成登录二维码...")
result = rpc("POST", "platform.createLoginUrl")
data = result["result"]["data"]
uuid = data["uuid"]
scan_url = data["scanUrl"]
print(f"   UUID: {uuid}")

# 生成二维码
import qrcode
qr = qrcode.QRCode()
qr.add_data(scan_url)
qr.make_image(fill_color='black', back_color='white').save(r"C:\Users\lxhcx\Desktop\wewe-rss-login.png")
print("   ✅ 二维码已保存到桌面: wewe-rss-login.png")
print(f"   📱 或用微信扫这个链接: {scan_url}")
print()
print("⏳ 等待扫码... (有效期 3 分钟)")

# 轮询登录结果
for i in range(90):
    time.sleep(2)
    try:
        poll = rpc("GET", f"platform.getLoginResult?input={json.dumps({'id': uuid})}")
        login_data = poll.get("result", {}).get("data", {})
        msg = login_data.get("message", "")
        if msg == "success":
            vid = login_data.get("vid")
            token = login_data.get("token")
            username = login_data.get("username", "Unknown")
            print(f"\n✅ 登录成功!")
            print(f"   用户: {username}")
            print(f"   VID: {vid}")

            # 保存账号
            account = {
                "id": str(vid),
                "token": token,
                "name": username,
                "status": 1
            }
            save = rpc("POST", "account.add", account)
            print(f"   ✅ 账号已保存")
            print(f"\n🔧 现在可以抓取文章了！")
            sys.exit(0)
        elif msg:
            print(f"\r   [{i*2}s] 状态: {msg}", end="")
    except Exception as e:
        print(f"\r   [{i*2}s] 等待中...", end="")

print("\n❌ 超时，请重新运行此脚本。")
sys.exit(1)
