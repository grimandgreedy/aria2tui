"""
End-to-end tests for selection workflows.

Tests selecting items with space, select all/deselect all, visual mode,
and selection persistence.
"""
import pytest
import time


@pytest.mark.e2e
@pytest.mark.slow
def test_download_add(kitty):
    """
    Test adding a download and pausing

    Workflow:
    1. Launch aria2tui
    2. Exit to main menu
    3. Select add download
    4. Add a download and pause
    5. Confirm that the download has been added
    6. Remove the download
    """
    # Launch
    kitty.launch_aria2tui()
    kitty.wait_for_text("Aria2TUI", timeout=3)

    # Exit to main menu
    kitty.send_text("q")
    kitty.wait_for_text("Main Menu", timeout=3)

    # Select add download via form
    kitty.navigate_to_top()
    kitty.navigate_down(2)
    kitty.send_key('return')
    kitty.wait_for_text("Basic Download Options", timeout=3)

    # Enter download information
    kitty.send_key('return')
    kitty.send_text("http://example.com/example.pdf") # set url
    kitty.send_key('return')
    kitty.send_text('j')
    kitty.send_key('return')
    kitty.send_text("this_is_a_test.pdf") # Set filename
    kitty.send_key('return')
    kitty.send_text('j')
    kitty.send_text('j')
    kitty.send_key('return')    # Pause=true
    kitty.send_text('G')
    kitty.send_text('j')
    kitty.send_key('return') # Save download

    # Wait for download to be added
    kitty.send_text('g')
    kitty.send_text('H')
    kitty.wait_for_text("this_is_a_test.pdf", timeout=3)

    # Remove download we added
    kitty.send_text('f')
    kitty.wait_for_text("Filter", timeout=3)
    kitty.send_text('this_is_a_test.pdf')
    kitty.send_key('return') # submit filter
    kitty.send_key('return') # select download
    kitty.send_text('Gkk')
    kitty.send_key('return')
    time.sleep(2)


    # Ensure that the download is deleted
    # note that the same filter is still being applied
    kitty.wait_for_text("0/0")

    kitty.send_text("q")
    kitty.send_text("q")


@pytest.mark.e2e
@pytest.mark.slow
def test_send_paused_download_to_back_of_queue(kitty):
    """Test sending a paused download to the back of the queue.

    Workflow:
    1. Launch aria2tui
    2. Add two paused downloads (A and B)
    3. Send download A to the back of the queue
    4. Switch to Paused tab (Tab x4)
    5. Jump to bottom (G) and verify A is last (below B)
    6. Remove both downloads
    """
    filename_a = "queue_back_a.pdf"
    filename_b = "queue_back_b.pdf"

    # Launch
    kitty.launch_aria2tui()
    kitty.wait_for_text("Aria2TUI", timeout=3)

    def add_paused_download(filename: str) -> None:
        # Exit to main menu
        kitty.send_text("q")
        kitty.wait_for_text("Main Menu", timeout=3)

        # Select add download via form
        kitty.navigate_to_top()
        kitty.navigate_down(2)
        kitty.send_key("return")
        kitty.wait_for_text("Basic Download Options", timeout=3)

        # Enter download information
        kitty.send_key("return")
        kitty.send_text("http://example.com/example.pdf")  # set url
        kitty.send_key("return")
        kitty.send_text("j")
        kitty.send_key("return")
        kitty.send_text(filename)  # Set filename
        kitty.send_key("return")
        kitty.send_text("j")
        kitty.send_text("j")
        kitty.send_key("return")  # Pause=true
        kitty.send_text("G")
        kitty.send_text("j")
        kitty.send_key("return")  # Save download

        # Wait for download to be added
        kitty.send_text("g")
        kitty.send_text("H")
        kitty.wait_for_text(filename, timeout=3)

    def remove_download_by_filename(filename: str) -> None:
        kitty.send_text("f")
        kitty.wait_for_text("Filter", timeout=3)
        kitty.send_text(filename)
        kitty.send_key("return")  # submit filter
        kitty.send_key("return")  # select download

        # Choose "Remove Download(s)" operation (15th item)
        kitty.navigate_to_top()
        kitty.navigate_down(14)
        kitty.send_key("return")
        time.sleep(2)

        # Ensure that the download is deleted
        kitty.wait_for_text("0/0")
        kitty.clear_filter()

    # Add two paused downloads so ordering is meaningful
    add_paused_download(filename_a)
    add_paused_download(filename_b)

    # Send A to the back of the queue
    kitty.send_text("f")
    kitty.wait_for_text("Filter", timeout=3)
    kitty.send_text(filename_a)
    kitty.send_key("return")
    kitty.send_key("return")
    kitty.wait_for_text("Select operation", timeout=3)

    # "Send to Back of Queue" is 5th item
    kitty.navigate_to_top()
    kitty.navigate_down(4)
    kitty.send_key("return")
    time.sleep(0.5)

    # Back to downloads view and clear the filter
    kitty.send_text("q")
    kitty.clear_filter()

    # Switch to Paused tab (All -> Active -> Queued -> Active+Queued -> Paused)
    for _ in range(4):
        kitty.send_key("tab")
        time.sleep(0.1)

    # Jump to bottom, then verify A is below B
    kitty.send_text("G")
    time.sleep(0.3)

    screen = kitty.get_screen_text()
    lines = screen.splitlines()

    idx_a = max((i for i, line in enumerate(lines) if filename_a in line), default=-1)
    idx_b = max((i for i, line in enumerate(lines) if filename_b in line), default=-1)

    assert idx_a != -1, f"{filename_a} not found in screen"
    assert idx_b != -1, f"{filename_b} not found in screen"
    assert idx_a > idx_b, f"Expected {filename_a} below {filename_b} in paused list"
    assert idx_a >= len(lines) - 15, f"Expected {filename_a} near bottom of screen"

    # Cleanup
    remove_download_by_filename(filename_a)
    remove_download_by_filename(filename_b)

    kitty.send_text("q")
    kitty.send_text("q")
