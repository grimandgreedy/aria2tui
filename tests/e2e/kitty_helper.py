"""
Kitty terminal controller for E2E testing.

Provides a helper class to control kitty terminal via remote control protocol
for end-to-end testing of the aria2tui TUI application.
"""
import subprocess
import time
import os
import signal
from pathlib import Path
from datetime import datetime


class KittyController:
    """Controller for kitty terminal using remote control protocol."""

    def __init__(self, socket_path="/tmp/aria2tui_test_kitty", cleanup=True, delay=0.1):
        """
        Initialize the KittyController.

        Args:
            socket_path: Unix socket path for kitty remote control
            cleanup: Whether to cleanup on exit
            delay: Default delay between commands (seconds)
        """
        self.socket_path = socket_path
        self.should_cleanup = cleanup
        self.delay = delay
        self.kitty_process = None
        self.launched = False

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        if self.should_cleanup:
            self.cleanup()

    def launch_kitty(self):
        """Launch kitty terminal with remote control enabled."""
        if self.launched:
            return

        # Kill any existing kitty on this socket
        self.cleanup()

        # Launch kitty in background with remote control
        self.kitty_process = subprocess.Popen(
            ["kitty", f"--listen-on=unix:{self.socket_path}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Wait for kitty to start
        time.sleep(1)
        self.launched = True

    def cleanup(self):
        """Kill kitty process and clean up socket."""
        # Kill kitty process if we have it
        if self.kitty_process:
            try:
                self.kitty_process.terminate()
                self.kitty_process.wait(timeout=2)
            except:
                try:
                    self.kitty_process.kill()
                except:
                    pass
            self.kitty_process = None

        # Also try to kill by socket path
        try:
            subprocess.run(
                ["pkill", "-f", f"kitty --listen-on=unix:{self.socket_path}"],
                capture_output=True,
                timeout=2
            )
        except:
            pass

        # Remove socket file
        socket_file = Path(self.socket_path)
        if socket_file.exists():
            try:
                socket_file.unlink()
            except:
                pass

        self.launched = False

    def send_text(self, text):
        """
        Send text to kitty as if typed.

        Args:
            text: Text to send
        """
        subprocess.run(
            ["kitten", "@", "--to", f"unix:{self.socket_path}", "send-text", "--", text],
            check=True,
            capture_output=True
        )
        time.sleep(self.delay)

    def send_key(self, key):
        """
        Send a special key to kitty.

        Args:
            key: Key name (e.g., 'return', 'F5', 'ctrl+c', 'escape')
        """
        subprocess.run(
            ["kitten", "@", "--to", f"unix:{self.socket_path}", "send-key", key],
            check=True,
            capture_output=True
        )
        time.sleep(self.delay)

    def send_keys(self, keys):
        """
        Send a sequence of characters.

        Args:
            keys: String of characters to send
        """
        for char in keys:
            self.send_text(char)

    def get_screen_text(self):
        """
        Capture current terminal content.

        Returns:
            Terminal content as string
        """
        result = subprocess.run(
            ["kitten", "@", "--to", f"unix:{self.socket_path}", "get-text"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

    def wait_for_text(self, text, timeout=5, interval=0.1):
        """
        Wait for text to appear in terminal.

        Args:
            text: Text to wait for
            timeout: Maximum time to wait (seconds)
            interval: Polling interval (seconds)

        Returns:
            True if text appeared, False if timeout

        Raises:
            AssertionError: If text doesn't appear within timeout
        """
        start = time.time()
        while time.time() - start < timeout:
            screen = self.get_screen_text()
            if text in screen:
                return True
            time.sleep(interval)

        # Timeout - raise assertion error with helpful message
        screen = self.get_screen_text()
        raise AssertionError(
            f"Text '{text}' not found after {timeout}s timeout.\n"
            f"Screen content:\n{screen[:500]}..."
        )

    def assert_text_present(self, text):
        """
        Assert that text is present in terminal.

        Args:
            text: Text that should be present

        Raises:
            AssertionError: If text is not present
        """
        screen = self.get_screen_text()
        assert text in screen, f"Text '{text}' not found in terminal.\nScreen:\n{screen[:500]}..."

    def assert_text_absent(self, text):
        """
        Assert that text is NOT present in terminal.

        Args:
            text: Text that should not be present

        Raises:
            AssertionError: If text is present
        """
        screen = self.get_screen_text()
        assert text not in screen, f"Text '{text}' unexpectedly found in terminal"

    def get_footer_text(self):
        """
        Extract footer content from screen.

        Returns:
            Footer text (last non-empty line)
        """
        screen = self.get_screen_text()
        lines = screen.split('\n')
        # Get last few non-empty lines (footer is typically at bottom)
        for line in reversed(lines):
            if line.strip():
                return line.strip()
        return ""

    def save_screenshot(self, filename):
        """
        Save current terminal state to file for debugging.

        Args:
            filename: Path to save screenshot
        """
        content = self.get_screen_text()
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)

    def on_failure(self, test_name):
        """
        Called when test fails - save screenshot for debugging.

        Args:
            test_name: Name of the failing test
        """
        screenshot_dir = Path("tests/test_screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = screenshot_dir / f"{test_name}_{timestamp}.txt"
        self.save_screenshot(filename)

    # High-level utility methods

    def launch_aria2tui(self, args = []):
        """
        Launch aria2tui with given arguments.

        Args:
            args: List of command-line arguments
        """
        if not self.launched:
            self.launch_kitty()

        # Build command
        cmd = "aria2tui " + " ".join(str(arg) for arg in args)
        self.send_text(cmd)
        self.send_key("return")
        time.sleep(0.5)  # Wait for app to launch

    def navigate_down(self, count=1):
        """Navigate down N times."""
        for _ in range(count):
            self.send_text("j")

    def navigate_up(self, count=1):
        """Navigate up N times."""
        for _ in range(count):
            self.send_text("k")

    def navigate_to_bottom(self):
        """Navigate to bottom."""
        self.send_text("G")

    def navigate_to_top(self):
        """Navigate to top."""
        self.send_text("g")

    def select_current(self):
        """Select current item (space)."""
        self.send_key("space")

    def select_all(self):
        """Select all items (m)."""
        self.send_text("m")

    def deselect_all(self):
        """Deselect all items (M)."""
        self.send_text("M")

    def open_filter(self):
        """Open filter prompt (f)."""
        self.send_text("f")
        time.sleep(0.2)  # Wait for prompt

    def open_search(self):
        """Open search prompt (/)."""
        self.send_text("/")
        time.sleep(0.2)  # Wait for prompt

    def clear_filter(self):
        """Clear filter (backslash)."""
        self.send_text("\\")

    def next_match(self):
        """Go to next search match (n)."""
        self.send_text("n")

    def prev_match(self):
        """Go to previous search match (N)."""
        self.send_text("N")

    def cycle_sort(self):
        """Cycle to next sort method (s)."""
        self.send_text("s")

    def quit_app(self):
        """Quit application (q)."""
        self.send_text("q")
        self.send_text("q")
        time.sleep(0.3)  # Wait for exit

    def assert_footer_contains(self, text):
        """
        Assert footer contains specific text.

        Args:
            text: Text that should be in footer
        """
        footer = self.get_footer_text()
        assert text in footer, f"Footer doesn't contain '{text}'. Footer: {footer}"

    def assert_selection_count(self, expected):
        """
        Assert specific number of items selected.

        Args:
            expected: Expected selection count
        """
        screen = self.get_screen_text()
        # Selection is shown as "[N]" in format: "[2] 3/5 | C"
        # This appears in the second-to-last line, not in the actual footer
        assert f"[{expected}]" in screen, \
               f"Selection count [{expected}] not found in screen"
