import urllib.request
import json
import ssl
import time
import os
import zipfile
import subprocess
import sys

def get_git_token():
    try:
        p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        out, _ = p.communicate('protocol=https\nhost=github.com\n\n')
        for line in out.splitlines():
            if line.startswith('password='):
                tok = line.split('=', 1)[1].strip()
                if len(tok) >= 20:
                    return tok
    except Exception:
        pass
    return ""

token = os.getenv("GITHUB_TOKEN", "")
if not token:
    token = get_git_token()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/vnd.github+json"
}
if token:
    headers["Authorization"] = f"token {token}"
ctx = ssl.create_default_context()

repo = "yangyws/Cemu-zh"
branch = "main-zh"
package_name = "info.cemu.cemu.zh"

print("==========================================================")
print("  Cemu-zh 掌機 / Android 自動建置與部署管線")
print(f"  套件識別碼: {package_name}")
print("==========================================================")

# 1. 尋找最新執行的工作流程 run
print(f"[*] 正在尋找 {repo} 分支 {branch} 的最新工作流程執行記錄...")
run_id = None
for attempt in range(15):
    try:
        runs_req = urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/runs?branch={branch}&per_page=5", headers=headers)
        with urllib.request.urlopen(runs_req, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            runs = data.get('workflow_runs', [])
            if runs:
                latest = runs[0]
                commit_msg = latest.get('head_commit', {}).get('message', '').split('\n')[0]
                print(f"[*] 找到最新 Run ID: {latest['id']} | 狀態: {latest['status']} | 結果: {latest['conclusion']} | Commit: {commit_msg}")
                run_id = latest['id']
                break
    except Exception as e:
        print(f"[!] 查詢工作流程記錄失敗：{e}")
    time.sleep(3)

if not run_id:
    print("[!] 未找到工作流程執行記錄，請確認是否已推送到 GitHub 並觸發 Actions。")
    sys.exit(1)

# 2. 輪詢直到完成
print(f"[*] 開始監控工作流程 {run_id} 狀態...")
start_time = time.time()
while True:
    try:
        check_req = urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/runs/{run_id}", headers=headers)
        with urllib.request.urlopen(check_req, context=ctx) as resp:
            run_data = json.loads(resp.read().decode('utf-8'))
            status = run_data.get('status')
            conclusion = run_data.get('conclusion')
            elapsed = int(time.time() - start_time)
            print(f"\r[*] [{elapsed}s] 狀態: {status} | 結果: {conclusion}   ", end="", flush=True)
            if status == "completed":
                print()
                if conclusion == "success":
                    print("[+] 建置成功！")
                    break
                else:
                    print(f"[-] 建置結束，結果為失敗: {conclusion}")
                    sys.exit(1)
    except Exception as e:
        print(f"\n[!] 檢查狀態出錯：{e}")
    time.sleep(10)

# 3. 取得 Artifact 下載連結
print("[*] 正在獲取建置產物清單...")
artifacts_req = urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts", headers=headers)
with urllib.request.urlopen(artifacts_req, context=ctx) as resp:
    art_data = json.loads(resp.read().decode('utf-8'))
    artifacts = art_data.get('artifacts', [])

if not artifacts:
    print("[!] 找不到任何建置產物 Artifact！")
    sys.exit(1)

target_artifact = None
for a in artifacts:
    if "cemu-zh" in a['name'].lower():
        target_artifact = a
        break
if not target_artifact:
    target_artifact = artifacts[0]

print(f"[+] 找到產物: {target_artifact['name']} (大小: {target_artifact['size_in_bytes']} 位元組)")
download_url = target_artifact['archive_download_url']

# 4. 下載 Artifact
print("[*] 正在下載產物 (處理 GitHub 轉址)...")
dl_headers = dict(headers)

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        new_req = urllib.request.Request(newurl)
        for h, v in req.headers.items():
            if h.lower() != 'authorization':
                new_req.add_header(h, v)
        return new_req

opener = urllib.request.build_opener(NoRedirectHandler)
req = urllib.request.Request(download_url, headers=dl_headers)
zip_path = "Cemu-zh-build.zip"

with opener.open(req) as resp, open(zip_path, 'wb') as out_f:
    out_f.write(resp.read())

print(f"[+] 產物已成功下載至 {zip_path}")

# 5. 解壓縮 APK
extracted_dir = "extracted_apk"
os.makedirs(extracted_dir, exist_ok=True)
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extracted_dir)

apk_path = None
for root, dirs, files in os.walk(extracted_dir):
    for file in files:
        if file.endswith(".apk"):
            apk_path = os.path.join(root, file)
            break

if not apk_path:
    print("[!] 解壓縮後未找到 APK 檔案！")
    sys.exit(1)

print(f"[+] 找到 APK 檔案: {apk_path}")

# 6. ADB 部署
print("==========================================================")
print("  ADB 自動安裝與部署至掌機實體設備")
print("==========================================================")

adb_devices = subprocess.check_output(['adb', 'devices'], text=True)
print(adb_devices)
lines = [l.strip() for l in adb_devices.splitlines() if l.strip()]
connected_devices = [l.split()[0] for l in lines[1:] if '\tdevice' in l]

if not connected_devices:
    print("[!] 未檢測到已連線的 ADB 設備，請檢查掌機 USB 偵錯連線。")
    sys.exit(0)

target_device = connected_devices[0]
print(f"[*] 目標掌機設備: {target_device}")

print(f"[*] 正在安裝 {apk_path} 到設備 {target_device}...")
install_res = subprocess.run(['adb', '-s', target_device, 'install', '-r', '-d', apk_path], capture_output=True, text=True)
print(install_res.stdout)
if install_res.stderr:
    print(install_res.stderr)

if "Success" in install_res.stdout:
    print(f"[+] {package_name} 安裝成功！")
    print("[*] 正在為掌機啟動應用程式...")
    subprocess.run(['adb', '-s', target_device, 'shell', 'monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1'])
    print("[+] 掌機部署完畢，Cemu-zh 已順利啟動！")
else:
    print("[-] 安裝失敗，請檢視上方錯誤訊息。")
