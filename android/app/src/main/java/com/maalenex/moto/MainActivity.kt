package com.maalenex.moto

import android.app.Activity
import android.graphics.Color
import android.os.Bundle
import android.view.ViewGroup
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.webkit.WebViewAssetLoader

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
            webViewClient = object : WebViewClient() {
                override fun onPageStarted(view: WebView, url: String, favicon: android.graphics.Bitmap?) {
                    super.onPageStarted(view, url, favicon)
                    android.util.Log.i(TAG, "WEBVIEW_PAGE_STARTED url=$url")
                }

                override fun onPageFinished(view: WebView, url: String) {
                    super.onPageFinished(view, url)
                    android.util.Log.i(TAG, "WEBVIEW_PAGE_FINISHED url=$url")
                    view.evaluateJavascript(
                        "JSON.stringify({readyState:document.readyState,title:document.title,rootPresent:!!document.getElementById('root'),rootTextLength:(document.getElementById('root')?.innerText||'').trim().length})"
                    ) { result ->
                        android.util.Log.i(TAG, "WEBVIEW_JS_PROBE $result")
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

                override fun shouldInterceptRequest(
                    view: WebView,
                    request: WebResourceRequest
                ) = assetLoader.shouldInterceptRequest(request.url)

                override fun shouldOverrideUrlLoading(
                    view: WebView,
                    request: WebResourceRequest
                ): Boolean = request.url.host != APP_ASSET_HOST || !request.url.path.orEmpty().startsWith("/assets/")
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
        const val APP_ASSET_HOST = "appassets.androidplatform.net"
        const val APP_ENTRY_URL = "https://appassets.androidplatform.net/assets/www/index.html"
    }
}
