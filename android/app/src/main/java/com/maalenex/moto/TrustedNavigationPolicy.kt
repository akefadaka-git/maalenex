package com.maalenex.moto

import java.net.URI

/**
 * Exact top-level document boundary for the packaged WebView application.
 *
 * This intentionally rejects query strings, fragments and percent-encoded paths:
 * the app is a packaged single-page application and does not need URL-based routing.
 */
internal object TrustedNavigationPolicy {
    private const val TRUSTED_HOST = "appassets.androidplatform.net"
    private const val TRUSTED_PATH_PREFIX = "/assets/"

    fun isTrustedDocumentUrl(rawUrl: String): Boolean {
        val uri = try {
            URI(rawUrl)
        } catch (_: Exception) {
            return false
        }

        if (!uri.isAbsolute || uri.isOpaque) return false
        if (!uri.scheme.equals("https", ignoreCase = true)) return false
        if (!TRUSTED_HOST.equals(uri.host, ignoreCase = true)) return false
        if (uri.rawUserInfo != null) return false
        if (uri.port != -1 && uri.port != 443) return false

        val authority = uri.rawAuthority ?: return false
        if (!authority.equals(TRUSTED_HOST, ignoreCase = true) &&
            !authority.equals("$TRUSTED_HOST:443", ignoreCase = true)
        ) return false

        // The packaged SPA does not use query- or fragment-based document routing.
        if (uri.rawQuery != null || uri.rawFragment != null) return false

        val path = uri.rawPath ?: return false
        if (!path.startsWith(TRUSTED_PATH_PREFIX)) return false
        if ('%' in path || '\\' in path || "//" in path) return false
        if (path.split('/').any { it == "." || it == ".." }) return false

        return true
    }
}
