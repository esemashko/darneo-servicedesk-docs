#!/usr/bin/env python3
"""Capture only the production column-width dialog from a built Storybook."""
from __future__ import annotations

import argparse
import functools
import http.server
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--storybook-dir', type=Path, default=root.parent / 'app' / 'storybook-static')
    args = parser.parse_args()
    if not (args.storybook_dir / 'index.html').is_file():
        raise SystemExit('Build Storybook before capturing screenshots')
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(args.storybook_dir.resolve()))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    output = root / 'docs/assets/screenshots/interface/grid-column-widths.png'
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
                page.goto(f'http://127.0.0.1:{server.server_port}/iframe.html?id=table-grid-column-widths--locked-system-tab&viewMode=story')
                page.add_style_tag(content='*, *::before, *::after { animation: none !important; transition: none !important; }')
                page.get_by_role('button', name='Ширина столбцов', exact=True).click()
                dialog = page.get_by_role('dialog', name='Ширина столбцов', exact=True)
                dialog.wait_for(state='visible')
                dialog.get_by_role('spinbutton').nth(1).fill('540')
                dialog.get_by_role('spinbutton').nth(1).press('Tab')
                dialog.screenshot(path=output)
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    print(output)


if __name__ == '__main__':
    main()
