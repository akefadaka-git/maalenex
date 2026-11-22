package com.maalenex.moto

internal object WebViewGeolocationPolicy {
    private const val APP_ORIGIN = "https://appassets.androidplatform.net"

    fun isTrustedOrigin(origin: String?): Boolean =
        origin == APP_ORIGIN || origin == "$APP_ORIGIN/"

    fun hasLocationPermission(coarseGranted: Boolean, fineGranted: Boolean): Boolean =
        coarseGranted || fineGranted
}
