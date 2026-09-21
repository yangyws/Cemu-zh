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

private val DefaultTranslation = object : Translation(Locale(DEFAULT_LANGUAGE)) {
    override fun load(context: Context) {
        I18n = Gettext.Fallback
        NativeLocalization.setTranslations(emptyMap())
    }
}

private var Translations = listOf<Translation>(DefaultTranslation)

data class Language(val code: String, val displayName: String)

fun getAvailableLanguages() =
    Translations.map {
        val name = if (it.locale.language == "zh" || it.locale.language == "zh_tw") {
            "繁體中文 (台灣)"
        } else {
            it.locale.getDisplayName(it.locale).replaceFirstChar { char -> char.uppercase() }
        }
        Language(it.locale.language, name)
    }.distinctBy { it.code }

fun setLanguage(languageCode: String, context: Context) {
    val translation = Translations.firstOrNull { it.locale.language == languageCode } ?: return
    translation.load(context)
    CurrentLocale = translation.locale

    if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
        try {
            val localeManager = context.getSystemService(android.app.LocaleManager::class.java)
            val tag = if (languageCode == "zh" || languageCode == "zh_tw") "zh-TW" else languageCode
            localeManager?.applicationLocales = android.os.LocaleList.forLanguageTags(tag)
        } catch (_: Exception) {}
    }
}

fun setTranslations(context: Context) {
    val assetTranslations = context.assets.list(TRANSLATIONS_FOLDER)?.filter { language ->
        if (language == DEFAULT_LANGUAGE) return@filter false

        context.assets.list("$TRANSLATIONS_FOLDER/$language")
            ?.contains(TRANSLATIONS_FILE_NAME)
            ?: false
    }?.map { language ->
        val locale = Locale(language)
        val assetFile = "$TRANSLATIONS_FOLDER/$language/$TRANSLATIONS_FILE_NAME"
        AssetTranslation(locale, assetFile)
    } ?: listOf()

    Translations = listOf(DefaultTranslation).plus(assetTranslations)
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
