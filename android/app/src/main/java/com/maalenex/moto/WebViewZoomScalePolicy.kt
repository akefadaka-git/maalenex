package com.maalenex.moto

/** Bounds persisted WebView zoom values before they are applied to a new process. */
internal object WebViewZoomScalePolicy {
    private const val MIN_SCALE = 0.5f
    private const val MAX_SCALE = 5.0f
    private const val MIN_ZOOM_FACTOR = 0.1f
    private const val MAX_ZOOM_FACTOR = 10.0f

    fun isValidScale(scale: Float): Boolean =
        scale.isFinite() && scale in MIN_SCALE..MAX_SCALE

    fun zoomFactor(currentScale: Float, savedScale: Float): Float? {
        if (!isValidScale(currentScale) || !isValidScale(savedScale)) return null
        val factor = savedScale / currentScale
        return factor.takeIf {
            it.isFinite() && it in MIN_ZOOM_FACTOR..MAX_ZOOM_FACTOR
        }
    }
}
