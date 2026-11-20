package com.maalenex.moto

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class WebViewZoomScalePolicyTest {
    @Test fun acceptsOnlyFiniteScalesWithinSupportedBounds() {
        assertTrue(WebViewZoomScalePolicy.isValidScale(0.5f))
        assertTrue(WebViewZoomScalePolicy.isValidScale(1.0f))
        assertTrue(WebViewZoomScalePolicy.isValidScale(5.0f))
        assertFalse(WebViewZoomScalePolicy.isValidScale(0.49f))
        assertFalse(WebViewZoomScalePolicy.isValidScale(5.01f))
        assertFalse(WebViewZoomScalePolicy.isValidScale(Float.NaN))
        assertFalse(WebViewZoomScalePolicy.isValidScale(Float.POSITIVE_INFINITY))
    }

    @Test fun calculatesRelativeFactorToRestoreSavedScale() {
        assertEquals(2.0f, WebViewZoomScalePolicy.zoomFactor(1.0f, 2.0f)!!, 0.0001f)
        assertEquals(0.5f, WebViewZoomScalePolicy.zoomFactor(2.0f, 1.0f)!!, 0.0001f)
        assertEquals(1.0f, WebViewZoomScalePolicy.zoomFactor(1.0f, 1.0f)!!, 0.0001f)
    }

    @Test fun rejectsInvalidCurrentOrPersistedScales() {
        assertNull(WebViewZoomScalePolicy.zoomFactor(0.0f, 1.0f))
        assertNull(WebViewZoomScalePolicy.zoomFactor(1.0f, Float.NaN))
        assertNull(WebViewZoomScalePolicy.zoomFactor(1.0f, 6.0f))
    }
}
