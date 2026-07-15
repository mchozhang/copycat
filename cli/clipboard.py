"""Local OS clipboard read/write via PyQt6."""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QGuiApplication, QClipboard
from PyQt6.QtCore import QMimeData, QUrl

qt_app = None


def _init_app():
    """
    initialize Qt app instance
    """
    global qt_app
    if qt_app is None:
        qt_app = QApplication.instance() or QApplication(sys.argv)


def read_clipboard() -> dict:
    """
    Return current clipboard contents as a dict with keys: text, html, file.
    """
    _init_app()
    clipboard = QGuiApplication.clipboard()
    mime: QMimeData = clipboard.mimeData(mode=QClipboard.Mode.Clipboard)

    result = {}
    if mime.hasText():
        result["text"] = mime.text()
    if mime.hasHtml():
        result["html"] = mime.html()

    # only process the first file url, e.g. file://<filepath>
    # save image to local file if clipboard has image and no file url
    if mime.hasUrls() and mime.urls()[0].toLocalFile():
        result["file_path"] = mime.urls()[0].toLocalFile()
    elif mime.hasImage():
        # Save image to a temporary file and return the path
        image = clipboard.image()
        out_path = os.path.expanduser("~/tmp/copycat/image.png")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        image.save(out_path)
        result["file_path"] = out_path
    return result


def write_clipboard(text=None, html=None, file_path=None):
    """Write content to the local OS clipboard."""
    _init_app()
    clipboard = QGuiApplication.clipboard()
    mime = QMimeData()

    if text is not None:
        mime.setText(text)
    if html is not None:
        mime.setHtml(html)
    if file_path is not None:
        mime.setUrls([QUrl.fromLocalFile(file_path)])

    clipboard.setMimeData(mime)

