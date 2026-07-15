import sys
from email import mime

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QGuiApplication, QImage, QClipboard
from PyQt6.QtCore import QMimeData


def inspect_clipboard():
    clipboard = QGuiApplication.clipboard()
    mime: QMimeData = clipboard.mimeData(mode=QClipboard.Mode.Clipboard)

    print("\n=== Clipboard MIME Types ===")
    for fmt in mime.formats():
        print(" -", fmt)

    print("\n=== Decoded Content ===")

    # 1. Plain text
    if mime.hasText():
        print("\n[Text]")
        print(mime.text())

    # 2. HTML
    if mime.hasHtml():
        print("\n[HTML]")
        print(mime.html())

    # 3. URLs (files, links, etc.)
    if mime.hasUrls():
        print("\n[URLs]")
        for url in mime.urls():
            print(" -", url.toString())

    # 4. Image
    if mime.hasImage():
        print("\n[Image]")
        image = clipboard.image()
        print(f"Size: {image.width()} x {image.height()}, format: {image.format()}")
        import os
        out_path = os.path.expanduser("~/tmp/clipboard_image.png")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        image.save(out_path)
        print(f"Saved to {out_path}")

    # 5. Raw custom MIME data
    print("\n[Raw MIME payloads]")
    for fmt in mime.formats():
        print(f"\n--- {fmt} ---")
        # Qt stores images internally as QImage objects, not as raw bytes;
        # mime.data() returns empty for this format — use clipboard.image() instead.
        if fmt == "application/x-qt-image":
            image = clipboard.image()
            print(f"<QImage: {image.width()} x {image.height()}, format: {image.format()}>")
            continue
        data = mime.data(fmt)
        try:
            print(data.data().decode("utf-8"))
        except Exception:
            print(f"<binary data: {len(data)} bytes>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    inspect_clipboard()