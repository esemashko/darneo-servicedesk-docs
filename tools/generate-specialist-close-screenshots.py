#!/usr/bin/env python3
"""Rebuild the three focused screenshots from the shipping Storybook screens."""
from __future__ import annotations

import argparse
import contextlib
import json
import socket
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ('settings-ticket-status-status--final-close-participants', '[data-test="status-settings-dialog"]',
     'settings/tickets/dictionaries/status-close-participants.png'),
    ('settings-ticket-status-status--final-close-disabled', '[data-test="status-settings-dialog"]',
     'settings/tickets/dictionaries/status-close-disabled.png'),
    ('ticket-status-transition--specialist-close-allowed', '.p-dialog',
     'tickets/statuses/ticket-specialist-close.png'),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--storybook-dir', type=Path, default=ROOT.parent / 'app/storybook-static')
    parser.add_argument('--browser-executable', type=Path)
    args = parser.parse_args()
    if not (args.storybook_dir / 'iframe.html').is_file():
        raise RuntimeError('Build Storybook first: cd ../app && yarn build-storybook')
    with contextlib.closing(socket.socket()) as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    server = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1',
                               '--directory', str(args.storybook_dir)], stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    receipt = {'pid': server.pid, 'port': port, 'stopped': False, 'screenshots': []}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=str(args.browser_executable) if args.browser_executable else None)
            try:
                page = browser.new_page(viewport={'width': 1440, 'height': 1500}, device_scale_factor=1)
                for story, selector, output in TARGETS:
                    page.goto(f'http://127.0.0.1:{port}/iframe.html?id={story}&viewMode=story')
                    page.locator(selector).wait_for(state='visible')
                    page.add_style_tag(content='*,*::before,*::after { animation:none!important; transition:none!important; }')
                    page.evaluate('document.fonts.ready')
                    target = ROOT / 'docs/assets/screenshots' / output
                    target.parent.mkdir(parents=True, exist_ok=True)
                    page.locator(selector).screenshot(path=str(target), animations='disabled')
                    receipt['screenshots'].append({'story': story, 'output': str(target.relative_to(ROOT))})
                    print(target.relative_to(ROOT))
            finally:
                browser.close()
    finally:
        server.terminate()
        server.wait(timeout=10)
        receipt['stopped'] = True
        print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
