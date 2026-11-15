package com.maalenex.moto

import android.app.Activity
import android.graphics.Color
import android.os.Bundle
import android.view.ViewGroup
import android.webkit.ConsoleMessage
import android.webkit.RenderProcessGoneDetail
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.webkit.WebViewAssetLoader
import org.json.JSONObject
import org.json.JSONTokener

class MainActivity : Activity() {
    private lateinit var webView: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = Color.TRANSPARENT
        window.navigationBarColor = Color.TRANSPARENT
        WindowCompat.setDecorFitsSystemWindows(window, false)

        val assetLoader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        webView = WebView(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.rgb(7, 27, 49))
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.mixedContentMode = android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW
            settings.setSupportZoom(false)
            webChromeClient = object : WebChromeClient() {
                override fun onConsoleMessage(consoleMessage: ConsoleMessage): Boolean {
                    val message = consoleMessage.message()
                    if (message.contains("Content Security Policy", ignoreCase = true) ||
                        message.contains("Refused to", ignoreCase = true)
                    ) {
                        android.util.Log.e(TAG, "WEBVIEW_CSP_VIOLATION $message")
                    }
                    return true
                }
            }
            webViewClient = object : WebViewClient() {
                override fun onPageStarted(view: WebView, url: String, favicon: android.graphics.Bitmap?) {
                    super.onPageStarted(view, url, favicon)
                    if (!TrustedNavigationPolicy.isTrustedDocumentUrl(url)) {
                        android.util.Log.e(TAG, "WEBVIEW_NAVIGATION_BLOCKED stage=page_started")
                        view.stopLoading()
                        return
                    }
                    android.util.Log.i(TAG, "WEBVIEW_PAGE_STARTED url=$url")
                }

                override fun onPageFinished(view: WebView, url: String) {
                    super.onPageFinished(view, url)
                    if (!TrustedNavigationPolicy.isTrustedDocumentUrl(url)) {
                        android.util.Log.e(TAG, "WEBVIEW_NAVIGATION_BLOCKED stage=page_finished")
                        view.stopLoading()
                        return
                    }
                    android.util.Log.i(TAG, "WEBVIEW_PAGE_FINISHED url=$url")
                    if (url != APP_ENTRY_URL) {
                        android.util.Log.w(TAG, "WEBVIEW_JS_PROBE_SKIPPED unexpected_document")
                        return
                    }
                    view.evaluateJavascript(
                        "JSON.stringify({schemaVersion:1,readyState:document.readyState,title:document.title,rootPresent:!!document.getElementById('root'),rootTextLength:(document.getElementById('root')?.innerText||'').trim().length})"
                    ) { result ->
                        logDecodedProbe(result)
                    }
                }

                override fun onReceivedError(
                    view: WebView,
                    request: WebResourceRequest,
                    error: android.webkit.WebResourceError
                ) {
                    super.onReceivedError(view, request, error)
                    if (request.isForMainFrame) {
                        android.util.Log.e(TAG, "WEBVIEW_MAIN_FRAME_ERROR code=${error.errorCode} description=${error.description}")
                    }
                }

                @android.annotation.TargetApi(26)
                override fun onRenderProcessGone(
                    view: WebView,
                    detail: RenderProcessGoneDetail
                ): Boolean {
                    android.util.Log.e(
                        TAG,
                        "WEBVIEW_RENDERER_GONE didCrash=${detail.didCrash()} priorityAtExit=${detail.rendererPriorityAtExit()}"
                    )
                    return true
                }

                override fun shouldInterceptRequest(
                    view: WebView,
                    request: WebResourceRequest
                ) = assetLoader.shouldInterceptRequest(request.url)

                @Suppress("DEPRECATION")
                override fun shouldOverrideUrlLoading(view: WebView, url: String): Boolean {
                    // API 23 cannot identify the requesting frame. Fail closed for all
                    // user/script navigation; the packaged SPA is loaded programmatically.
                    android.util.Log.w(TAG, "WEBVIEW_NAVIGATION_BLOCKED stage=legacy_api23")
                    return true
                }

                override fun shouldOverrideUrlLoading(
                    view: WebView,
                    request: WebResourceRequest
                ): Boolean {
                    // No frame, external URL, redirect target, or non-packaged path
                    // may become a top-level document in the app WebView.
                    if (!request.isForMainFrame) {
                        android.util.Log.w(TAG, "WEBVIEW_NAVIGATION_BLOCKED stage=subframe")
                        return true
                    }
                    val trusted = TrustedNavigationPolicy.isTrustedDocumentUrl(request.url.toString())
                    if (!trusted) {
                        android.util.Log.w(TAG, "WEBVIEW_NAVIGATION_BLOCKED stage=should_override")
                    }
                    return !trusted
                }
            }
        }
        ViewCompat.setOnApplyWindowInsetsListener(webView) { view, windowInsets ->
            val safeInsets = windowInsets.getInsets(
                WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout()
            )
            view.setPadding(safeInsets.left, safeInsets.top, safeInsets.right, safeInsets.bottom)
            windowInsets
        }
        setContentView(webView)
        ViewCompat.requestApplyInsets(webView)
        webView.loadUrl(APP_ENTRY_URL)
    }

    private fun logDecodedProbe(callbackValue: String?) {
        try {
            require(!callbackValue.isNullOrBlank() && callbackValue != "null") {
                "empty evaluateJavascript callback"
            }

            // evaluateJavascript returns a JSON-encoded string. Decode that outer
            // JSON value first; the resulting string is the actual page JSON.
            val outer = JSONTokener(callbackValue)
            val decoded = outer.nextValue() as? String
                ?: error("evaluateJavascript result was not a JSON string")
            require(outer.nextClean() == '\u0000') { "trailing data in callback result" }

            // Parse and validate the decoded page JSON without coercing types.
            val inner = JSONTokener(decoded)
            val probe = inner.nextValue() as? JSONObject
                ?: error("probe payload was not a JSON object")
            require(inner.nextClean() == '\u0000') { "trailing data in probe payload" }

            val expectedKeys = setOf(
                "schemaVersion", "readyState", "title", "rootPresent", "rootTextLength"
            )
            val actualKeys = mutableSetOf<String>()
            val keys = probe.keys()
            while (keys.hasNext()) actualKeys.add(keys.next())
            require(actualKeys == expectedKeys) { "probe schema keys did not match" }

            val schemaVersion = probe.opt("schemaVersion")
            require(schemaVersion is Number && schemaVersion.toDouble() == 1.0) {
                "unsupported probe schema"
            }
            require(probe.opt("readyState") is String) { "readyState was not a string" }
            require(probe.opt("title") is String) { "title was not a string" }
            require(probe.opt("rootPresent") is Boolean) { "rootPresent was not a boolean" }
            val rootTextLength = probe.opt("rootTextLength")
            require(
                rootTextLength is Number &&
                    rootTextLength.toDouble().isFinite() &&
                    rootTextLength.toDouble() >= 0.0 &&
                    rootTextLength.toDouble() % 1.0 == 0.0
            ) { "rootTextLength was not a non-negative integer" }

            // Log the decoded JSON string unchanged; CI parses this exact record.
            android.util.Log.i(TAG, "WEBVIEW_JS_PROBE_JSON $decoded")
        } catch (error: Exception) {
            android.util.Log.e(
                TAG,
                "WEBVIEW_JS_PROBE_DECODE_FAILED ${error.javaClass.simpleName}"
            )
        }
    }

    @Deprecated("Use system back navigation on newer Android versions")
    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }

    override fun onDestroy() {
        if (::webView.isInitialized) {
            (webView.parent as? ViewGroup)?.removeView(webView)
            webView.destroy()
        }
        super.onDestroy()
    }

    private companion object {
        const val TAG = "MaaleNexWebView"
        const val APP_ENTRY_URL = "https://appassets.androidplatform.net/assets/www/index.html"
    }
}
