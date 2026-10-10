import json
import os
import struct

# 214 Android-specific keys translated into strict Taiwan Traditional Chinese
ANDROID_KEYS_TW = {
    'About title': '關於標題',
    'Above': '上方',
    'AccountId missing (The account is not connected to a NNID/PNID)': '缺少 AccountId（此帳號尚未連結 NNID/PNID）',
    'Accurate barriers': '精確同步屏障',
    'Add game path': '新增遊戲路徑',
    'Are you really sure you want to delete the following entry?': '您確定要刪除以下項目嗎？',
    'Are you sure you want to delete the account {0} with id {1}?': '您確定要刪除 ID 為 {1} 的帳號 {0} 嗎？',
    'Are you sure you want to exit?': '您確定要結束嗎？',
    'Audio settings': '音訊設定',
    'Author': '作者',
    'Base': '基底',
    'Below': '下方',
    'Blow mic': '麥克風吹氣',
    'Buttons': '按鍵',
    'CPU mode': 'CPU 模式',
    'Cancel compressing title': '取消壓縮標題',
    'Cancel installing title': '取消安裝標題',
    'Cemu is a Wii U emulator.\n\nWii and Wii U are trademarks of Nintendo.\nCemu is not affiliated with Nintendo.': 'Cemu 是一款 Wii U 模擬器。\n\nWii 與 Wii U 為任天堂的註冊商標。\nCemu 與任天堂沒有任何關聯。',
    'Compressing title': '正在壓縮標題',
    'Console language': '主機語言',
    'Controller has no motion sensors': '控制器無體感感應器',
    'Controller {0}': '控制器 {0}',
    'Controls the accuracy of floating point multiplication in shaders': '控制著色器中浮點數乘法的精確度',
    'Convert to WUA': '轉換為 WUA',
    'Copied to clipboard': '已複製到剪貼簿',
    'Could not decrypt title because title.tik is missing.': '由於缺少 title.tik，無法解密標題。',
    'Could not decrypt title. Make sure that keys.txt contains the correct disc key for this title.': '無法解密標題。請確認 keys.txt 中包含該標題正確的光碟金鑰。',
    "Couldn't create shortcut for game": '無法為遊戲建立捷徑',
    'Create shortcut': '建立捷徑',
    'Current choice': '目前選擇',
    'Custom driver': '自訂驅動程式',
    'Custom drivers': '自訂驅動程式',
    'Deleted title entry': '已刪除標題項目',
    'Deleting': '正在刪除',
    'Deleting: {0}': '正在刪除：{0}',
    'Device controller': '裝置控制器',
    'Device settings': '裝置設定',
    'Dimensions Figure Mover': 'Dimensions 公仔移動器',
    'Dimensions Toypad': 'Dimensions 玩具感應座',
    'Dimensions figure': 'Dimensions 公仔',
    'Dimensions figure creator': 'Dimensions 公仔建立器',
    'Dimensions figures': 'Dimensions 公仔列表',
    'Disabling the accurate barriers option will lead to flickering graphics but may improve performance. It is highly recommended to leave it turned on': '關閉精確同步屏障選項會導致畫面閃爍，但可能提升效能。強烈建議保持開啟',
    'Do you really want to cancel compressing the title?': '您確定要取消壓縮此標題嗎？',
    'Do you really want to cancel the installation process?\n\nCanceling the process will delete the applied files.': '您確定要取消安裝程序嗎？\n\n取消程序將會刪除已套用的檔案。',
    'Done': '完成',
    'Downloaded latest graphic packs': '已下載最新圖形包',
    'Driver already installed': '驅動程式已安裝',
    'Driver installed successfully': '驅動程式安裝成功',
    'Driver version': '驅動程式版本',
    'Edit input positions': '編輯按鍵位置',
    'Edit input size': '編輯按鍵大小',
    'Edit inputs': '編輯按鍵',
    'Emulate Dimensions Toypad': '模擬 Dimensions 玩具感應座',
    'Emulated USB Devices settings': '模擬 USB 裝置設定',
    'Emulated controller: {0}': '模擬控制器：{0}',
    'Enable audio output for the Wii U Gamepad': '啟用 Wii U Gamepad 音訊輸出',
    'Enable audio output for the Wii U TV': '啟用 Wii U TV 音訊輸出',
    'Enable input overlay': '啟用虛擬按鍵覆蓋層',
    'Enable motion': '啟用體感控制',
    'Enable vibrate on touch': '啟用觸控震動',
    'Enabled': '已啟用',
    'Enables async shader and pipeline compilation. Reduces stutter at the cost of objects not rendering for a short time.\nVulkan only': '啟用非同步著色器與管線編譯。以物件短時間不渲染為代價減少畫面頓挫。\n僅限 Vulkan',
    'Error installing': '安裝時發生錯誤',
    'Error while converting': '轉換時發生錯誤',
    'Exit confirmation': '結束確認',
    'Exited input edit mode': '已退出按鍵編輯模式',
    'Extra': '額外',
    'Failed creating renderer: {0}': '建立渲染器失敗：{0}',
    'Failed creating surface: {0}': '建立介面失敗：{0}',
    'Failed to create figure': '建立公仔失敗',
    'Failed to delete title entry': '刪除標題項目失敗',
    'Failed to download graphic packs': '下載圖形包失敗',
    'Failed to initialize': '初始化失敗',
    'Failed to install driver': '安裝驅動程式失敗',
    'Failed to launch title': '啟動標題失敗',
    'Failed to load figure': '載入公仔失敗',
    'Failed to open Cemu folder': '開啟 Cemu 資料夾失敗',
    'Failed to open log file': '開啟記錄檔失敗',
    'Favorite': '最愛',
    'Figure number': '公仔編號',
    'Finished converting': '轉換完成',
    'Finished installing': '安裝完成',
    'Formats': '格式',
    'GamePad position': 'GamePad 顯示位置',
    'Gamepad channels': 'Gamepad 聲道',
    'Gamepad volume': 'Gamepad 音量',
    'Games path already added': '遊戲路徑已新增過',
    'Global': '全域',
    'Graphic packs download': '下載圖形包',
    'Graphics settings': '圖形設定',
    'Hold to confirm': '長按以確認',
    'Home': '首頁',
    'Hotkey settings': '快速鍵設定',
    'Hours: {0} Minutes: {1}': '{0} 小時 {1} 分鐘',
    'ID': 'ID',
    'Infinity figure': 'Infinity 公仔',
    'Infinity figure creator': 'Infinity 公仔建立器',
    'Infinity figures': 'Infinity 公仔列表',
    'Initializing emulation': '正在初始化模擬',
    'Input binding': '按鍵對應',
    'Input overlay': '虛擬按鍵覆蓋層',
    'Input overlay settings': '虛擬按鍵設定',
    'Input text': '輸入文字',
    'Inputs opacity': '按鍵不透明度',
    'Installed only': '僅已安裝',
    'Installing driver in progress': '正在安裝驅動程式',
    'Installing title': '正在安裝標題',
    'Invalid title': '無效的標題',
    'Kotlin libraries:': 'Kotlin 函式庫：',
    'Left': '左',
    'Left joystick': '左搖桿',
    'Left stick click': '按下左搖桿',
    'Load libraries from the cafeLibs directory': '從 cafeLibs 目錄載入函式庫',
    'Location': '位置',
    'Locations': '位置列表',
    "Log file doesn't exist": '記錄檔不存在',
    'MLC': 'MLC',
    'Makes the "show screen" button toggle between the TV and gamepad screens': '讓「切換螢幕」按鈕在 TV 與 GamePad 螢幕之間切換',
    'Manage list': '管理列表',
    'Many': '多數',
    'Min api': '最低 API',
    'Minus': '減號 (-)',
    'Minutes: {0}': '{0} 分鐘',
    'Missing certificate and key files:': '缺少憑證與金鑰檔案：',
    'Move': '移動',
    'Move here': '移至此處',
    'NUS': 'NUS',
    'Nearest neighbor': '最近鄰採樣',
    'Network service': '網路服務',
    'Never played': '從未遊玩',
    'No available figures': '沒有可用的公仔',
    'No controllers available': '沒有可用的控制器',
    'No emulated USB device is enabled': '未啟用任何模擬 USB 裝置',
    'Not enough space': '儲存空間不足',
    'Not set': '未設定',
    'OTP and SEEPROM present but no certificate files were found': '已找到 OTP 與 SEEPROM，但未找到任何憑證檔案',
    'OTP.bin or SEEPROM.bin is missing': '缺少 OTP.bin 或 SEEPROM.bin',
    'Online status': '線上狀態',
    'Open Cemu folder': '開啟 Cemu 資料夾',
    'Operation failed': '操作失敗',
    'Original authors: {0}': '原始作者：{0}',
    'Overlay controller': '虛擬控制器',
    'Overlay settings': '虛擬按鍵設定',
    'Package version': '套件版本',
    'Parsing title content...': '正在解析標題內容...',
    'Path': '路徑',
    'PersistentId': 'Persistent ID',
    'Pick a date': '選擇日期',
    'Pick up and place': '拿起並放置',
    'Plus': '加號 (+)',
    'Portuguese': '葡萄牙語',
    'Press a button': '按下任意按鈕',
    'Press a key combination': '按下組合鍵',
    'Processing...': '處理中...',
    'Quit': '結束',
    'Refreshing titles': '正在重新整理標題',
    'Remove shader caches': '清除著色器快取',
    'Remove the shader caches for {0}?': '要清除 {0} 的著色器快取嗎？',
    'Replace TV with PAD': '以 GamePad 替換 TV',
    'Requires Wii U GamePad': '需要 Wii U GamePad',
    'Reset input overlay': '重設虛擬按鍵覆蓋層',
    'Resize': '調整大小',
    'Right': '右',
    'Right joystick': '右搖桿',
    'Right stick click': '按下右搖桿',
    'Search games': '搜尋遊戲',
    'Search graphic packs': '搜尋圖形包',
    'Search titles': '搜尋標題',
    'Select': '選取',
    'Select a controller': '選擇控制器',
    'Select a figure': '選擇公仔',
    'Selected account is a valid online account': '所選帳號為有效的線上帳號',
    'Selected account is not linked to a NNID or PNID': '所選帳號未連結 NNID 或 PNID',
    'Setup all inputs': '設定所有按鍵',
    'Shader caches removed': '著色器快取已清除',
    'Share log file': '分享記錄檔',
    'Show Emulated USB Devices dialog': '顯示模擬 USB 裝置對話框',
    'Show PAD': '顯示 GamePad',
    'Show input overlay': '顯示虛擬按鍵覆蓋層',
    'Show online status': '顯示線上狀態',
    'Skylander figure': 'Skylander 公仔',
    'Skylander figure creator': 'Skylander 公仔建立器',
    'Skylanders figures': 'Skylanders 公仔列表',
    'Starting...': '正在啟動...',
    'System': '系統',
    'System driver': '系統預設驅動程式',
    'TV channels': 'TV 聲道',
    'TV volume': 'TV 音量',
    'The following content will be converted to a compressed Wii U archive file (.wua)': '以下內容將被轉換為壓縮的 Wii U 封裝檔 (.wua)',
    'The persistent id must be greater than {0}!': 'Persistent ID 必須大於 {0}！',
    'The persistent id {0} is already in use by account {1}!': 'Persistent ID {0} 已被帳號 {1} 使用！',
    'Title name': '標題名稱',
    'To use motion input, the controller type must be set to Wii U GamePad': '若要使用體感控制，控制器類型必須設為 Wii U GamePad',
    'Toggle menu': '切換選單',
    'Toggle screen': '切換螢幕',
    'Trigger an input to bind it to {0}': '按下按鍵以對應至 {0}',
    'Types': '類型',
    'Unable to launch game\nPath: {0}': '無法啟動遊戲\n路徑：{0}',
    'Used libraries:': '使用的函式庫：',
    'Variant': '款式',
    'Vendor': '廠商',
    'Version: {0}': '版本：{0}',
    'Vibrate': '震動',
    'Visible Inputs': '顯示按鍵',
    'WUHB': 'WUHB',
    'Wii U Classic Controller': 'Wii U 傳統控制器',
    'Wii U GamePad': 'Wii U GamePad',
    'Wii U Pro Controller': 'Wii U Pro 控制器',
    'Wiimote': 'Wii 遙控器',
    'otp.bin is invalid': 'otp.bin 無效',
    'otp.bin missing in Cemu directory': 'Cemu 目錄缺少 otp.bin',
    'seeprom.bin is invalid': 'seeprom.bin 無效',
    'seeprom.bin missing in Cemu directory': 'Cemu 目錄缺少 seeprom.bin',
    'External PAD screen': '外部 GamePad 螢幕',
    'Rotate external screen left': '外部螢幕向左旋轉 90 度',
    'Swap screens': '交換螢幕畫面',
    'Data storage': '資料儲存位置',
    'Choose custom root': '選擇自訂根目錄',
    'Choose where Cemu stores saves, MLC, settings and cache': '選擇 Cemu 儲存存檔、MLC、設定與快取的路徑',
    'Choose a folder for portable Cemu data. Game saves sync automatically; other data syncs manually.': '選擇便攜式 Cemu 資料資料夾。遊戲存檔會自動同步，其他資料需手動同步。',
    'Close emulation before changing data storage or importing manual data.': '在變更資料儲存位置或手動匯入資料前，請先關閉遊戲模擬。',
    'Restart Cemu to activate the configured storage location.': '請重新啟動 Cemu 以套用新設定的儲存路徑。',
    'Unsynced save changes': '未同步的存檔變更',
    'Sync saves now': '立即同步存檔',
    'Import saves from custom root': '從自訂根目錄匯入存檔',
    'Import manual data': '手動匯入資料',
    'Export manual data': '手動匯出資料',
    'Use default app storage': '使用預設應用程式儲存空間',
    'Delete previous data location': '刪除先前的資料路徑',
    'Copy the latest game saves to the custom folder.': '將最新的遊戲存檔複製到自訂資料夾。',
    'Copy game saves from the custom folder into Cemu.': '從自訂資料夾將遊戲存檔複製至 Cemu。',
    'Copy settings, controller profiles, and keys from the custom folder. Saves, games, updates, graphic packs, logs, and shader cache are not copied.': '從自訂資料夾複製設定、控制器設定檔與金鑰。存檔、遊戲、更新檔、圖形包、記錄檔與著色器快取不會被複製。',
    'Copy settings, controller profiles, and keys to the custom folder. Saves, games, updates, graphic packs, logs, and shader cache are not copied.': '將設定、控制器設定檔與金鑰複製至自訂資料夾。存檔、遊戲、更新檔、圖形包、記錄檔與著色器快取不會被複製。',
    'Migrate data back to default app-specific storage. Restart Cemu after migration.': '將資料遷移回預設應用程式專屬儲存空間。遷移後請重啟 Cemu。',
    'Only do this when emulation is closed. Cemu will migrate current local data back to default app storage.': '請僅在模擬關閉時執行此操作。Cemu 會將目前的本機資料遷移回預設應用程式空間。',
    'Only do this after restarting Cemu and confirming the new data location works.': '請僅在重啟 Cemu 並確認新資料路徑可正常運作後，再執行此操作。',
    'This updates local settings, controller profiles, and keys from the custom folder. Saves, games, updates, graphic packs, logs, account data, and shader cache are not replaced by this action.': '此操作會從自訂資料夾更新本機設定、控制器設定檔與金鑰。存檔、遊戲、更新檔、圖形包、記錄檔、帳號資料與著色器快取將不受影響。',
    'Import': '匯入',
    'Use default': '使用預設',
}

def escape_po_string(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def generate_po_content(catalog):
    lines = [
        'msgid ""',
        'msgstr ""',
        '"Project-Id-Version: Cemu-zh\\n"',
        '"Report-Msgid-Bugs-To: \\n"',
        '"POT-Creation-Date: 2026-09-21 23:00+0800\\n"',
        '"PO-Revision-Date: 2026-09-21 23:00+0800\\n"',
        '"Last-Translator: yangyws <yangyws@users.noreply.github.com>\\n"',
        '"Language-Team: Traditional Chinese (Taiwan) <zh-TW>\\n"',
        '"Language: zh_TW\\n"',
        '"MIME-Version: 1.0\\n"',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        '"Content-Transfer-Encoding: 8bit\\n"',
        '"Plural-Forms: nplurals=1; plural=0;\\n"',
        ''
    ]
    for k in sorted(catalog.keys()):
        v = catalog[k]
        escaped_k = escape_po_string(k)
        escaped_v = escape_po_string(v)
        lines.append(f'msgid "{escaped_k}"')
        lines.append(f'msgstr "{escaped_v}"')
        lines.append('')
    return '\n'.join(lines)

def generate_mo_binary(catalog):
    # Standard GNU MO binary format
    msgs = {
        '': 'Content-Type: text/plain; charset=UTF-8\nContent-Transfer-Encoding: 8bit\n',
    }
    msgs.update(catalog)

    keys = sorted(msgs.keys())
    offsets = []
    ids = b''
    strs = b''
    for k in keys:
        v = msgs[k]
        k_b = k.encode('utf-8') + b'\x00'
        v_b = v.encode('utf-8') + b'\x00'
        offsets.append((len(ids), len(k_b) - 1, len(strs), len(v_b) - 1))
        ids += k_b
        strs += v_b

    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    for o1, l1, o2, l2 in offsets:
        koffsets.extend([l1, o1 + keystart])
        voffsets.extend([l2, o2 + valuestart])

    header = [
        0x950412de, # magic
        0,          # version
        len(keys),  # number of strings
        7 * 4,      # start of key index
        7 * 4 + len(keys) * 8, # start of value index
        0, 0        # hash table size and offset
    ]
    data = struct.pack(f'<{len(header)}I', *header)
    data += struct.pack(f'<{len(koffsets)}I', *koffsets)
    data += struct.pack(f'<{len(voffsets)}I', *voffsets)
    data += ids
    data += strs
    return data

def main():
    # 1. Load converted MO dictionary (766 keys)
    mo_dict = json.load(open('cemu_tw_mo_converted.json', encoding='utf-8'))
    
    # 2. Merge Android keys (214 keys)
    full_catalog = dict(mo_dict)
    full_catalog.update(ANDROID_KEYS_TW)

    print(f"Total entries in unified Taiwan Traditional Chinese catalog: {len(full_catalog)}")

    # 3. Generate PO content and MO binary
    po_content = generate_po_content(full_catalog)
    mo_binary = generate_mo_binary(full_catalog)

    # Output targets
    po_targets = [
        'src/android/app/src/main/assets/translations/zh_TW/cemu.po',
    ]
    mo_targets = [
        'bin/resources/zh_TW/cemu.mo',
        'bin/resources/zh/cemu.mo',
    ]

    for p in po_targets:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(po_content)
        print(f"Wrote {p} ({len(po_content)} bytes)")

    for p in mo_targets:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as f:
            f.write(mo_binary)
        print(f"Wrote {p} ({len(mo_binary)} bytes)")

if __name__ == '__main__':
    main()
