package com.maalenex.moto

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class TrustedNavigationPolicyTest {
    @Test fun acceptsOnlyPackagedHttpsAssetDocuments() {
        assertTrue(TrustedNavigationPolicy.isTrustedDocumentUrl(
            "https://appassets.androidplatform.net/assets/www/index.html"
        ))
        assertTrue(TrustedNavigationPolicy.isTrustedDocumentUrl(
            "https://appassets.androidplatform.net:443/assets/www/chunk.js"
        ))
    }

    @Test fun rejectsNonHttpsAndUnexpectedPorts() {
        assertFalse(TrustedNavigationPolicy.isTrustedDocumentUrl(
            "http://appassets.androidplatform.net/assets/www/index.html"
        ))
        assertFalse(TrustedNavigationPolicy.isTrustedDocumentUrl(
            "https://appassets.androidplatform.net:444/assets/www/index.html"
        ))
    }

    @Test fun rejectsUserInfoLookalikeAndTrailingDotHosts() {
        assertFalse(TrustedNavigationPolicy.isTrustedDocumentUrl(
            "https://attacker@appassets.androidplatform.net/assets/www/index.html"
        ))
        assertFalse(TrustedNavigationPolicy.isTrustedDocumentUrl(
            "https://appassets.androidplatform.net.attacker.example/assets/www/index.html"
        ))
        assertFalse(TrustedNavigationPolicy.isTrustedDocumentUrl(
            "https://appassets.androidplatform.net./assets/www/index.html"
        ))
    }

    @Test fun rejectsExternalAndNonAssetPaths() {
        assertFalse(TrustedNavigationPolicy.isTrustedDocumentUrl(
            "https://example.com/assets/www/index.html"
        ))
        assertFalse(TrustedNavigationPolicy.isTrustedDocumentUrl(
            "https://appassets.androidplatform.net/private/index.html"
        ))
    }

    @Test fun rejectsEncodedTraversalAndAmbiguousPaths() {
        listOf(
            "https://appassets.androidplatform.net/assets/%2e%2e/private.html",
            "https://appassets.androidplatform.net/assets/a/../private.html",
            "https://appassets.androidplatform.net/assets//www/index.html",
            "https://appassets.androidplatform.net/assets\\\\www/index.html"
        ).forEach { assertFalse(TrustedNavigationPolicy.isTrustedDocumentUrl(it)) }
    }

    @Test fun rejectsQueryFragmentsAndMalformedUrls() {
        assertFalse(TrustedNavigationPolicy.isTrustedDocumentUrl(
            "https://appassets.androidplatform.net/assets/www/index.html?next=https://evil.example"
        ))
        assertFalse(TrustedNavigationPolicy.isTrustedDocumentUrl(
            "https://appassets.androidplatform.net/assets/www/index.html#external"
        ))
        assertFalse(TrustedNavigationPolicy.isTrustedDocumentUrl("not a URL"))
        assertFalse(TrustedNavigationPolicy.isTrustedDocumentUrl("https:///assets/www/index.html"))
    }
}
