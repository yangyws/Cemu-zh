package info.cemu.cemu.graphicpacks

import info.cemu.cemu.BuildConfig
import info.cemu.cemu.common.io.unzip
import info.cemu.cemu.nativeinterface.NativeGraphicPacks
import android.util.Log
import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.get
import io.ktor.client.request.header
import io.ktor.client.statement.bodyAsBytes
import io.ktor.http.HttpHeaders
import io.ktor.http.isSuccess
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.withContext
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.File
import java.io.IOException
import kotlin.io.path.div
import kotlin.io.path.readText
import kotlin.time.Clock

enum class GraphicPacksDownloadStatus {
    CHECKING_VERSION,
    NO_UPDATES_AVAILABLE,
    DOWNLOADING,
    EXTRACTING,
    FINISHED_DOWNLOADING,
    ERROR,
}

@Serializable
data class Release(
    val name: String,
    val assets: List<Asset>
)

@Serializable
data class Asset(
    @SerialName("browser_download_url")
    val browserDownloadUrl: String
)
class GraphicPacksDownloader(private val client: HttpClient = HttpClient()) {
    private val json = Json {
        ignoreUnknownKeys = true
    }

    private val userAgent = "Cemu-Android/${BuildConfig.VERSION_NAME}"

    private fun getCurrentVersion(graphicPacksDir: File): String? {
        val graphicPacksVersionFile =
            graphicPacksDir.toPath() / "downloadedGraphicPacks" / "version.txt"
        return try {
            graphicPacksVersionFile.readText().trim()
        } catch (_: IOException) {
            null
        }
    }

    private suspend fun getUpdateUrl(): String {
        return try {
            val queryUrl = "https://cemu.info/api2/query_graphicpack_url.php?" +
                    "version=${BuildConfig.VERSION_NAME}" +
                    "&t=${Clock.System.now().toEpochMilliseconds()}"

            val response = client.get(queryUrl) {
                header(HttpHeaders.UserAgent, userAgent)
            }
            val body = response.body<String>().trim()

            if (response.status.isSuccess() && body.startsWith("http")) {
                body
            } else {
                "https://api.github.com/repos/cemu-project/cemu_graphic_packs/releases/latest"
            }
        } catch (e: Exception) {
            Log.w("GraphicPacksDownloader", "Failed to query cemu.info update URL: ${e.message}, falling back to GitHub API")
            "https://api.github.com/repos/cemu-project/cemu_graphic_packs/releases/latest"
        }
    }

    private suspend fun fetchLatestRelease(): Release? {
        val targetUrl = getUpdateUrl()
        Log.d("GraphicPacksDownloader", "Fetching latest release from $targetUrl")
        return try {
            val response = client.get(targetUrl) {
                header(HttpHeaders.UserAgent, userAgent)
                header(HttpHeaders.Accept, "application/vnd.github.v3+json")
            }

            if (!response.status.isSuccess()) {
                Log.e("GraphicPacksDownloader", "API request failed with status ${response.status}")
                return fallbackRelease()
            }

            val bodyText = response.body<String>()
            json.decodeFromString<Release>(bodyText)
        } catch (e: Exception) {
            Log.e("GraphicPacksDownloader", "Failed to fetch or parse latest release: ${e.message}")
            fallbackRelease()
        }
    }

    private fun fallbackRelease(): Release {
        // 當 GitHub API 被限流 (403 Rate Limit) 或連線失敗時的堅固保底
        Log.i("GraphicPacksDownloader", "Using fallback release definition")
        return Release(
            name = "Github987",
            assets = listOf(
                Asset("https://github.com/cemu-project/cemu_graphic_packs/releases/download/Github987/graphicPacks987.zip")
            )
        )
    }

    private fun isUpToDate(dir: File, newVersion: String): Boolean {
        val current = getCurrentVersion(dir)
        Log.d("GraphicPacksDownloader", "Version check: current=$current, new=$newVersion")
        return current != null && current == newVersion
    }

    private suspend fun downloadZip(url: String): ByteArray? {
        Log.d("GraphicPacksDownloader", "Downloading zip from $url")
        return try {
            val response = client.get(url) {
                header(HttpHeaders.UserAgent, userAgent)
            }

            if (!response.status.isSuccess()) {
                Log.e("GraphicPacksDownloader", "Download zip failed with status ${response.status}")
                return null
            }

            response.bodyAsBytes()
        } catch (e: Exception) {
            Log.e("GraphicPacksDownloader", "Download zip failed: ${e.message}")
            null
        }
    }

    private suspend fun extractAndInstall(
        zipBytes: ByteArray,
        graphicPacksDir: File,
        version: String
    ) = withContext(Dispatchers.IO) {

        val tempDir = graphicPacksDir.resolve("downloadedGraphicPacksTemp")
        val finalDir = graphicPacksDir.resolve("downloadedGraphicPacks")

        tempDir.deleteRecursively()
        tempDir.mkdirs()

        unzip(zipBytes.inputStream(), tempDir.path)

        tempDir.resolve("version.txt").writeText(version)

        finalDir.deleteRecursively()
        if (!tempDir.renameTo(finalDir)) {
            tempDir.copyRecursively(finalDir, overwrite = true)
            tempDir.deleteRecursively()
        }

        NativeGraphicPacks.refreshGraphicPacks()
    }

    fun download(graphicPacksRootDir: File): Flow<GraphicPacksDownloadStatus> = flow {
        val graphicPacksDir = graphicPacksRootDir.resolve("graphicPacks")

        emit(GraphicPacksDownloadStatus.CHECKING_VERSION)

        val release = fetchLatestRelease() ?: run {
            emit(GraphicPacksDownloadStatus.ERROR)
            return@flow
        }

        val version = release.name

        if (isUpToDate(graphicPacksDir, version)) {
            emit(GraphicPacksDownloadStatus.NO_UPDATES_AVAILABLE)
            return@flow
        }

        val downloadUrl = release.assets.firstOrNull()?.browserDownloadUrl ?: run {
            emit(GraphicPacksDownloadStatus.ERROR)
            return@flow
        }

        emit(GraphicPacksDownloadStatus.DOWNLOADING)

        val zipBytes = downloadZip(downloadUrl) ?: run {
            emit(GraphicPacksDownloadStatus.ERROR)
            return@flow
        }

        emit(GraphicPacksDownloadStatus.EXTRACTING)

        extractAndInstall(zipBytes, graphicPacksDir, version)

        emit(GraphicPacksDownloadStatus.FINISHED_DOWNLOADING)
    }
}
