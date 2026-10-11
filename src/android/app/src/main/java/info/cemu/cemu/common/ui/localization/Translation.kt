@file:Suppress("TYPEALIAS_EXPANSION_DEPRECATION")

package info.cemu.cemu.common.ui.localization

import android.content.Context
import android.util.Log
import android.view.View.LAYOUT_DIRECTION_RTL
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.unit.LayoutDirection
import androidx.core.text.layoutDirection
import info.cemu.cemu.nativeinterface.NativeLocalization
import name.kropp.kotlinx.gettext.Gettext
import name.kropp.kotlinx.gettext.Locale
import name.kropp.kotlinx.gettext.load
import java.io.IOException
import java.text.MessageFormat

private var I18n = Gettext.Fallback

private abstract class Translation(val locale: Locale) {
    abstract fun load(context: Context)
}

private class AssetTranslation(locale: Locale, private val assetFile: String) :
    Translation(locale) {
    override fun load(context: Context) {
        try {
            val poFileContent = context.assets.open(assetFile).use { source -> source.readBytes() }
            I18n = Gettext.load(locale, poFileContent.inputStream())
            NativeLocalization.setTranslations(parsePoFile(poFileContent.inputStream()))
        } catch (_: IOException) {
            Log.e("CemuTranslations", "failed to load translations from asset: $assetFile")
            return
        }
    }
}

private const val TRANSLATIONS_FOLDER = "translations"
private const val TRANSLATIONS_FILE_NAME = "cemu.po"
const val DEFAULT_LANGUAGE = "en"

const val SYSTEM_DEFAULT_LANGUAGE = "system"

private val DefaultTranslation = object : Translation(Locale(DEFAULT_LANGUAGE)) {
    override fun load(context: Context) {
        I18n = Gettext.Fallback
        NativeLocalization.setTranslations(emptyMap())
    }
}

private var Translations = listOf<Translation>(DefaultTranslation)

data class Language(val code: String, val displayName: String)

fun getAvailableLanguages(): List<Language> {
    val languages = mutableListOf<Language>()
    languages.add(Language(SYSTEM_DEFAULT_LANGUAGE, tr("System default")))
    
    val list = Translations.mapNotNull {
        val code = it.locale.language
        val full = it.locale.toString()
        val isZh = code.contains("zh", ignoreCase = true) || full.contains("zh", ignoreCase = true)
        val normalizedCode = if (isZh) "zh_TW" else code
        if (normalizedCode.equals(DEFAULT_LANGUAGE, ignoreCase = true)) return@mapNotNull null
        val name = if (normalizedCode.equals("zh_TW", ignoreCase = true)) {
            "繁體中文 (台灣)"
        } else {
            it.locale.getDisplayName(it.locale).replaceFirstChar { char -> char.uppercase() }
        }
        Language(normalizedCode, name)
    }.distinctBy { it.code }
    languages.addAll(list)
    return languages
}

fun resolveLanguageCode(languageCode: String): String {
    if (languageCode == SYSTEM_DEFAULT_LANGUAGE || languageCode.isEmpty()) {
        val defaultLocale = java.util.Locale.getDefault()
        val lang = defaultLocale.language.lowercase()
        return if (lang.startsWith("zh")) "zh_TW" else lang
    }
    return if (languageCode.lowercase().startsWith("zh")) "zh_TW" else languageCode
}

fun setLanguage(languageCode: String, context: Context) {
    val targetCode = resolveLanguageCode(languageCode)
    val translation = Translations.firstOrNull { 
        val code = it.locale.language
        val full = it.locale.toString()
        code.equals(targetCode, ignoreCase = true) || full.equals(targetCode, ignoreCase = true)
    } ?: Translations.firstOrNull { 
        targetCode.equals("zh_TW", ignoreCase = true) && 
        (it.locale.language.contains("zh", ignoreCase = true) || it.locale.toString().contains("zh", ignoreCase = true))
    } ?: Translations.firstOrNull { it.locale.language.equals(DEFAULT_LANGUAGE, ignoreCase = true) }
      ?: return

    translation.load(context)
    CurrentLocale = translation.locale
    Log.d("CemuTranslations", "Language set to $targetCode (loaded ${translation.locale}), test tr Data storage: ${tr("Data storage")}")

    if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
        try {
            val localeManager = context.getSystemService(android.app.LocaleManager::class.java)
            val tag = if (targetCode.equals("zh_TW", ignoreCase = true)) {
                "zh-TW"
            } else if (languageCode == SYSTEM_DEFAULT_LANGUAGE) {
                ""
            } else {
                targetCode
            }
            localeManager?.applicationLocales = if (tag.isEmpty()) {
                android.os.LocaleList.getEmptyLocaleList()
            } else {
                android.os.LocaleList.forLanguageTags(tag)
            }
        } catch (_: Exception) {}
    }
}

fun setTranslations(context: Context) {
    val assetTranslations = context.assets.list(TRANSLATIONS_FOLDER)?.filter { language ->
        // 略過英文與舊簡中目錄 zh，本專案一律使用 zh_TW
        if (language == DEFAULT_LANGUAGE || language.equals("zh", ignoreCase = true)) return@filter false

        context.assets.list("$TRANSLATIONS_FOLDER/$language")
            ?.contains(TRANSLATIONS_FILE_NAME)
            ?: false
    }?.map { language ->
        val locale = Locale(language)
        val assetFile = "$TRANSLATIONS_FOLDER/$language/$TRANSLATIONS_FILE_NAME"
        AssetTranslation(locale, assetFile)
    } ?: listOf()

    // 確保 zh_TW 必定納入載入清單
    val hasZhTw = assetTranslations.any { 
        it.locale.language.equals("zh_TW", ignoreCase = true) || it.locale.toString().equals("zh_tw", ignoreCase = true) 
    }
    val finalTranslations = if (!hasZhTw) {
        val zhTwAsset = "$TRANSLATIONS_FOLDER/zh_TW/$TRANSLATIONS_FILE_NAME"
        try {
            context.assets.open(zhTwAsset).close()
            assetTranslations + AssetTranslation(Locale("zh_TW"), zhTwAsset)
        } catch (_: Exception) {
            assetTranslations
        }
    } else {
        assetTranslations
    }

    Translations = listOf(DefaultTranslation).plus(finalTranslations)
}

fun trNoop(text: String) = text

fun tr(text: String) = I18n.tr(text)

fun tr(text: String, vararg args: Any): String = MessageFormat.format(I18n.tr(text), *args)

private var CurrentLocale by mutableStateOf(DefaultTranslation.locale)
val LocalLocale = staticCompositionLocalOf { Locale("en") }

@Composable
fun TranslatableContent(content: @Composable () -> Unit) {
    val currentLocale = CurrentLocale
    val layoutDirection = when (currentLocale.layoutDirection) {
        LAYOUT_DIRECTION_RTL -> LayoutDirection.Rtl
        else -> LayoutDirection.Ltr
    }

    CompositionLocalProvider(
        LocalLocale provides currentLocale,
        LocalLayoutDirection provides layoutDirection
    ) {
        content()
    }
}
