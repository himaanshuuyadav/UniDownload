/* ========================================================================
   UniDownload — background service worker

   Minimal: the extension does not inject content scripts or intercept
   network requests.  All media extraction is handled by the local
   Python Flask backend at http://127.0.0.1:5000.
   ======================================================================== */

chrome.runtime.onInstalled.addListener(function () {
  console.log('[UniDownload] Extension installed. Ensure the backend is running at http://127.0.0.1:5000');
});
