#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

try:
    from playwright.sync_api import Page, sync_playwright
except ImportError:
    print(
        "Playwright is not installed. Run: pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise


ROOT_DIR = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = ROOT_DIR.parent
STORYBOOK_DIR = WORKSPACE_DIR / "app" / "storybook-static"
OUTPUT_DIR = ROOT_DIR / "docs" / "assets" / "screenshots" / "objects"


@dataclass(frozen=True)
class ScreenshotTarget:
    story_id: str
    selector: str
    filename: str
    wait_selector: str | None = None
    viewport_width: int = 1500
    viewport_height: int = 980


TARGETS = [
    ScreenshotTarget(
        story_id="docs-objects-pages--clients-list",
        selector='[data-test="objects-clients-list-story"]',
        filename="clients/list.png",
        wait_selector='[data-test="objects-clients-list-story"] .p-datatable-tbody',
    ),
    ScreenshotTarget(
        story_id="docs-objects-pages--clients-card",
        selector='[data-test="objects-clients-card-story"]',
        filename="clients/card.png",
        wait_selector='[data-test="objects-clients-card-story"]:has-text("Анна")',
        viewport_height=1050,
    ),
    ScreenshotTarget(
        story_id="docs-objects-pages--companies-list",
        selector='[data-test="objects-companies-list-story"]',
        filename="companies/list.png",
        wait_selector='[data-test="objects-companies-list-story"] .p-datatable-tbody',
    ),
    ScreenshotTarget(
        story_id="docs-objects-pages--companies-card",
        selector='[data-test="objects-companies-card-story"]',
        filename="companies/card.png",
        wait_selector='[data-test="objects-companies-card-story"]:has-text("ООО")',
    ),
    ScreenshotTarget(
        story_id="docs-objects-pages--contracts-list",
        selector='[data-test="objects-contracts-list-story"]',
        filename="contracts/list.png",
        wait_selector='[data-test="objects-contracts-list-story"] .p-datatable-tbody',
    ),
    ScreenshotTarget(
        story_id="docs-objects-pages--contracts-card",
        selector='[data-test="objects-contracts-card-story"]',
        filename="contracts/card.png",
        wait_selector='[data-test="objects-contracts-card-story"]:has-text("Договор обслуживания")',
        viewport_height=860,
    ),
    ScreenshotTarget(
        story_id="docs-objects-pages--service-objects-list",
        selector='[data-test="objects-service-objects-list-story"]',
        filename="service-objects/list.png",
        wait_selector='[data-test="objects-service-objects-list-story"] .p-datatable-tbody',
    ),
    ScreenshotTarget(
        story_id="docs-objects-pages--service-objects-card",
        selector='[data-test="objects-service-objects-card-story"]',
        filename="service-objects/card.png",
        wait_selector='[data-test="objects-service-objects-card-story"]:has-text("Магазин N12")',
    ),
    ScreenshotTarget(
        story_id="docs-objects-pages--equipment-list-story",
        selector='[data-test="objects-equipment-list-story"]',
        filename="equipment/list.png",
        wait_selector='[data-test="objects-equipment-list-story"] .p-datatable-tbody',
        viewport_width=1900,
    ),
    ScreenshotTarget(
        story_id="docs-objects-pages--equipment-card",
        selector='[data-test="objects-equipment-card-story"]',
        filename="equipment/card.png",
        wait_selector='[data-test="objects-equipment-card-story"]:has-text("Кассовый узел")',
        viewport_width=1600,
        viewport_height=1020,
    ),
]


def find_free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as server:
        server.bind(("127.0.0.1", 0))
        return int(server.getsockname()[1])


def start_storybook_server(port: int) -> subprocess.Popen[str]:
    if not (STORYBOOK_DIR / "iframe.html").exists():
        raise RuntimeError(
            f"Storybook build was not found at {STORYBOOK_DIR}. "
            "Run `cd ../app && yarn build-storybook` first."
        )

    return subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=STORYBOOK_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def wait_for_server(port: int) -> None:
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            if client.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise RuntimeError("Storybook static server did not start in time.")


def prepare_page(page: Page, base_url: str, target: ScreenshotTarget) -> None:
    page.set_viewport_size({"width": target.viewport_width, "height": target.viewport_height})
    page.goto(f"{base_url}/iframe.html?id={target.story_id}&viewMode=story")
    page.wait_for_selector("#storybook-root")
    page.add_style_tag(
        content="""
        *,
        *::before,
        *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
          caret-color: transparent !important;
        }

        body {
          background: #ffffff !important;
        }

        #storybook-root {
          box-sizing: border-box;
          padding: 0;
        }

        .p-datatable-wrapper,
        .p-treetable-wrapper {
          max-height: none !important;
        }
        """
    )
    page.wait_for_selector(target.wait_selector or target.selector)
    page.locator(target.selector).first.scroll_into_view_if_needed()


def capture_target(page: Page, base_url: str, target: ScreenshotTarget) -> None:
    prepare_page(page, base_url, target)
    output_path = OUTPUT_DIR / target.filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    page.locator(target.selector).first.screenshot(path=output_path)
    print(f"generated {output_path.relative_to(ROOT_DIR)}")


def main() -> int:
    port = find_free_port()
    server = start_storybook_server(port)
    base_url = f"http://127.0.0.1:{port}"

    try:
        wait_for_server(port)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            for target in TARGETS:
                capture_target(page, base_url, target)
            browser.close()
    finally:
        server.terminate()
        with contextlib.suppress(subprocess.TimeoutExpired):
            server.wait(timeout=5)
        if server.poll() is None:
            server.kill()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
