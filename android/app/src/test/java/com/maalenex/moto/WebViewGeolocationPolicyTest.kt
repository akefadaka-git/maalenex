package com.maalenex.moto

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class WebViewGeolocationPolicyTest {
    @Test fun permitsOnlyThePackagedWebViewOrigin() {
        assertTrue(WebViewGeolocationPolicy.isTrustedOrigin("https://appassets.androidplatform.net"))
        assertTrue(WebViewGeolocationPolicy.isTrustedOrigin("https://appassets.androidplatform.net/"))
        assertFalse(WebViewGeolocationPolicy.isTrustedOrigin("https://appassets.androidplatform.net.attacker.example"))
        assertFalse(WebViewGeolocationPolicy.isTrustedOrigin("https://example.com"))
        assertFalse(WebViewGeolocationPolicy.isTrustedOrigin("http://appassets.androidplatform.net"))
        assertFalse(WebViewGeolocationPolicy.isTrustedOrigin(null))
    }

    @Test fun acceptsPreciseOrApproximateLocationGrantButNeverAnUnresolvedGrant() {
        assertTrue(WebViewGeolocationPolicy.hasLocationPermission(coarseGranted = true, fineGranted = false))
        assertTrue(WebViewGeolocationPolicy.hasLocationPermission(coarseGranted = false, fineGranted = true))
        assertFalse(WebViewGeolocationPolicy.hasLocationPermission(coarseGranted = false, fineGranted = false))
    }
}
