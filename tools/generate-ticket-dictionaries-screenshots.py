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
OUTPUT_DIR = (
    ROOT_DIR / "docs" / "assets" / "screenshots" / "settings" / "tickets" / "dictionaries"
)


@dataclass(frozen=True)
class ScreenshotTarget:
    story_id: str
    selector: str
    filename: str
    click_selector: str | None = None
    wait_selector: str | None = None
    viewport_width: int = 1280
    viewport_height: int = 900


TARGETS = [
    ScreenshotTarget(
        story_id="settings-ticket-type-type--with-types",
        selector='[data-test="ticket-type"]',
        filename="type-list.png",
        viewport_width=1360,
        viewport_height=760,
    ),
    ScreenshotTarget(
        story_id="settings-ticket-type-type--with-types",
        selector=".p-dialog",
        filename="type-form.png",
        click_selector='tr:has-text("Инцидент") button:has(.pi-pencil)',
        wait_selector=".p-dialog",
        viewport_width=1360,
        viewport_height=900,
    ),
    ScreenshotTarget(
        story_id="settings-ticket-priority-priority--with-priorities",
        selector='[data-test="ticket-priority"]',
        filename="priority-list.png",
        viewport_width=1500,
        viewport_height=760,
    ),
    ScreenshotTarget(
        story_id="settings-ticket-priority-priority--with-priorities",
        selector=".p-dialog",
        filename="priority-form.png",
        click_selector='tr:has-text("Высокий") button:has(.pi-pencil)',
        wait_selector=".p-dialog",
        viewport_width=1360,
        viewport_height=900,
    ),
    ScreenshotTarget(
        story_id="settings-ticket-status-status--with-statuses",
        selector='[data-test="ticket-status"]',
        filename="status-list.png",
        viewport_width=1800,
        viewport_height=760,
    ),
    ScreenshotTarget(
        story_id="settings-ticket-status-status--with-statuses",
        selector=".p-dialog",
        filename="status-form.png",
        click_selector='tr:has-text("В работе") button:has(.pi-pencil)',
        wait_selector=".p-dialog",
        viewport_width=1360,
        viewport_height=1000,
    ),
    ScreenshotTarget(
        story_id="settings-ticket-status-status--with-statuses",
        selector=".p-dialog",
        filename="status-transitions.png",
        click_selector='tr:has-text("В работе") button:has-text("Переходы")',
        wait_selector='.p-dialog:has-text("Укажите, в какие статусы разрешен переход")',
        viewport_width=1360,
        viewport_height=900,
    ),
    ScreenshotTarget(
        story_id="settings-ticket-status-status--with-statuses",
        selector=".p-dialog",
        filename="status-settings.png",
        click_selector='tr:has-text("В работе") button:has-text("Настройки")',
        wait_selector='.p-dialog:has-text("Автоназначение исполнителя")',
        viewport_width=1360,
        viewport_height=1200,
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
          padding: 24px;
        }

        .p-dialog {
          max-height: none !important;
        }

        .p-dialog-content {
          max-height: none !important;
          overflow: visible !important;
        }
        """
    )

    if target.click_selector:
        page.locator(target.click_selector).first.click()

    page.wait_for_selector(target.wait_selector or target.selector)
    page.locator(target.selector).first.scroll_into_view_if_needed()


def capture_target(page: Page, base_url: str, target: ScreenshotTarget) -> None:
    prepare_page(page, base_url, target)
    output_path = OUTPUT_DIR / target.filename
    locator = page.locator(target.selector).first
    locator.screenshot(path=output_path)
    print(f"generated {output_path.relative_to(ROOT_DIR)}")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
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
