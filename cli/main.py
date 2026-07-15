#!/usr/bin/env python3
"""copycat CLI — copy/paste clipboard content across devices."""

import argparse
import sys

from config import Config
import clipboard
import api_client


def cmd_copy(args, config: Config):
    # Determine what to send
    if args.file or args.text or args.html:
        # Use provided values; optionally merge with current clipboard
        text = args.text
        html = args.html
        file_path = args.file

        if args.keep:
            current = clipboard.read_clipboard()
            if text is None:
                text = current.get("text")
            if html is None:
                html = current.get("html")
            if file_path is None:
                urls = current.get("urls", [])
                file_path = urls[0] if urls else None
    else:
        # Read everything from local clipboard
        current = clipboard.read_clipboard()
        text = current.get("text")
        html = current.get("html")
        urls = current.get("urls", [])
        file_path = urls[0] if urls else None

    client.post_clipboard(config, text=text, html=html, file_path=file_path)
    print("Copied to server.")


def cmd_paste(args, config: Config):
    data = client.get_clipboard(config)

    text = data.get("text") if (args.text or not any([args.file, args.html])) else None
    html = data.get("html") if (args.html or not any([args.file, args.text])) else None
    file_info = data.get("file") if (args.file or not any([args.text, args.html])) else None

    file_path = None
    if file_info:
        dest = file_info.get("name", "clipboard_file")
        client.download_file(config, dest)
        file_path = dest
        print(f"File saved: {dest}")

    clipboard.write_clipboard(text=text, html=html, file_path=file_path)
    print("Pasted from server.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="copycat",
        description="Copy and paste clipboard content across devices.",
    )
    sub = parser.add_subparsers(dest="command")

    # copy / cp
    cp = sub.add_parser("copy", aliases=["cp"], help="Send clipboard to server.")
    cp.add_argument("-f", "--file", metavar="filepath", help="Set file URI to clipboard and send.")
    cp.add_argument("-t", "--text", metavar="plain-text", help="Set plain text and send.")
    cp.add_argument("-m", "--html", metavar="html-content", help="Set HTML content and send.")
    cp.add_argument("-k", "--keep", action="store_true", help="Keep other content types when setting -f/-t/-m.")

    # paste / ps
    ps = sub.add_parser("paste", aliases=["ps"], help="Get clipboard from server.")
    ps.add_argument("-f", "--file", action="store_true", help="Get file content only.")
    ps.add_argument("-t", "--text", action="store_true", help="Get plain text only.")
    ps.add_argument("-m", "--html", action="store_true", help="Get HTML content only.")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    config = Config()

    if args.command in ("copy", "cp"):
        cmd_copy(args, config)
    elif args.command in ("paste", "ps"):
        cmd_paste(args, config)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
