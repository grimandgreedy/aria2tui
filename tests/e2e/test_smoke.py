"""
End-to-end tests for selection workflows.

Tests selecting items with space, select all/deselect all, visual mode,
and selection persistence.
"""
import pytest
import time


@pytest.mark.e2e
@pytest.mark.slow
def test_launch(kitty):
    """
    Test whether aria2tui launches

    Workflow:
    1. Launch aria2tui
    2. Exit to main menu
    3. Exit to console
    """
    # Launch
    kitty.launch_aria2tui()
    kitty.wait_for_text("Aria2TUI", timeout=3)
    kitty.send_text("q")
    kitty.wait_for_text("Main Menu", timeout=3)
    kitty.send_text("q")


# @pytest.mark.e2e
# @pytest.mark.slow
# def test_select_all_deselect_all(kitty, simple_data_path):
#     """
#     Test select all (m) and deselect all (M) functionality.

#     Workflow:
#     1. Launch with file (5 items)
#     2. Press 'm' to select all
#     3. Verify 5/5 selected
#     4. Press 'M' to deselect all
#     5. Verify 0/5 selected
#     6. Select some items manually
#     7. Press 'M' to deselect all
#     8. Verify 0/5 selected
#     """
#     # Launch
#     kitty.launch_aria2tui(["-i", str(simple_data_path)])
#     kitty.wait_for_text("Alice", timeout=3)

#     # Initial state - should show 0 selections
#     kitty.assert_selection_count(0)

#     # Select all with 'm'
#     kitty.select_all()
#     time.sleep(0.3)

#     # Should show all 6 items selected [6]
#     kitty.assert_selection_count(6)

#     # Deselect all with 'M'
#     kitty.deselect_all()
#     time.sleep(0.3)

#     # Should show 0 selected
#     kitty.assert_selection_count(0)

#     # Manually select 2 items
#     kitty.select_current()
#     time.sleep(0.2)
#     kitty.navigate_down(1)
#     time.sleep(0.2)
#     kitty.select_current()
#     time.sleep(0.2)

#     # Should show 2 selected
#     kitty.assert_selection_count(2)

#     # Deselect all again
#     kitty.deselect_all()
#     time.sleep(0.3)

#     # Should be back to 0
#     kitty.assert_selection_count(0)

#     # Exit
#     kitty.quit_app()


# @pytest.mark.e2e
# @pytest.mark.slow
# def test_visual_selection_mode(kitty, simple_data_path):
#     """
#     Test visual selection mode with 'v'.

#     Workflow:
#     1. Launch with file
#     2. Position on first item
#     3. Press 'v' to start visual mode
#     4. Navigate down to select range
#     5. Exit visual mode
#     6. Verify range is selected
#     """
#     # Launch
#     kitty.launch_aria2tui(["-i", str(simple_data_path)])
#     kitty.wait_for_text("Alice", timeout=3)

#     # Navigate to first data row
#     kitty.navigate_to_top()
#     time.sleep(0.2)

#     # Start visual mode with 'v'
#     kitty.send_text("v")
#     time.sleep(0.3)

#     # Navigate down 2 rows to select Alice, Bob, Charlie
#     kitty.navigate_down(2)
#     time.sleep(0.3)

#     # Exit visual mode (press 'v' again or Esc)
#     kitty.send_text("v")
#     time.sleep(0.3)

#     # Should have selected 3 items
#     kitty.assert_selection_count(3)

#     # Exit
#     kitty.quit_app()


# @pytest.mark.e2e
# @pytest.mark.slow
# def test_selection_persists_across_navigation(kitty, simple_data_path):
#     """
#     Test that selections persist when navigating.

#     Workflow:
#     1. Launch with file
#     2. Select first item
#     3. Navigate to bottom
#     4. Navigate back to top
#     5. Verify first item still selected
#     6. Select last item
#     7. Navigate to middle
#     8. Verify both selections persist
#     """
#     # Launch
#     kitty.launch_aria2tui(["-i", str(simple_data_path)])
#     kitty.wait_for_text("Alice", timeout=3)

#     # Select first item (Alice)
#     kitty.select_current()
#     time.sleep(0.2)
#     kitty.assert_selection_count(1)

#     # Navigate to bottom
#     kitty.navigate_to_bottom()
#     time.sleep(0.2)

#     # Should still show 1 selected
#     kitty.assert_selection_count(1)

#     # Select last item (Eve)
#     kitty.select_current()
#     time.sleep(0.2)

#     # Should show 2 selected
#     kitty.assert_selection_count(2)

#     # Navigate to middle
#     kitty.navigate_to_top()
#     time.sleep(0.2)
#     kitty.navigate_down(2)
#     time.sleep(0.2)

#     # Should still show 2 selected
#     kitty.assert_selection_count(2)

#     # Exit
#     kitty.quit_app()


# @pytest.mark.e2e
# @pytest.mark.slow
# def test_selection_with_filtering(kitty, simple_data_path):
#     """
#     Test that selections work correctly with filtering.

#     Workflow:
#     1. Launch with file
#     2. Select some items
#     3. Apply filter
#     4. Verify selection count updates (only visible items counted)
#     5. Clear filter
#     6. Verify original selections restored
#     """
#     # Launch
#     kitty.launch_aria2tui(["-i", str(simple_data_path)])
#     kitty.wait_for_text("Alice", timeout=3)

#     # Select first two items (Alice and Bob)
#     kitty.select_current()
#     time.sleep(0.2)
#     kitty.navigate_down(1)
#     time.sleep(0.2)
#     kitty.select_current()
#     time.sleep(0.2)

#     # Should show 2 selected
#     kitty.assert_selection_count(2)

#     # Apply filter for "Alice" only
#     kitty.open_filter()
#     time.sleep(0.3)
#     kitty.send_text("Alice")
#     kitty.send_key("return")
#     time.sleep(0.3)

#     # Should show filtered results - Alice is selected, Bob is hidden
#     # Footer should show 1 selected out of 1 visible
#     screen = kitty.get_screen_text()
#     assert "Alice" in screen, "Alice should be visible after filter"
#     assert "Bob" not in screen, "Bob should be hidden after filter"

#     # Clear filter with backslash
#     kitty.send_key("escape")
#     time.sleep(0.3)

#     # Should show all items again, with 2 still selected
#     kitty.assert_selection_count(2)
#     kitty.assert_text_present("Alice")
#     kitty.assert_text_present("Bob")

#     # Exit
#     kitty.quit_app()


# @pytest.mark.e2e
# @pytest.mark.slow
# def test_toggle_selection(kitty, simple_data_path):
#     """
#     Test that space toggles selection on and off.

#     Workflow:
#     1. Launch with file
#     2. Press space on item (select)
#     3. Verify selected (count = 1)
#     4. Press space on same item again (deselect)
#     5. Verify deselected (count = 0)
#     """
#     # Launch
#     kitty.launch_aria2tui(["-i", str(simple_data_path)])
#     kitty.wait_for_text("Alice", timeout=3)

#     # Initial state
#     kitty.assert_selection_count(0)

#     # Select first item
#     kitty.select_current()
#     time.sleep(0.2)
#     kitty.assert_selection_count(1)

#     # Toggle off (deselect)
#     kitty.navigate_up(1)
#     kitty.select_current()
#     time.sleep(0.2)

#     # Should be back to 0
#     kitty.assert_selection_count(0)

#     # Toggle on again
#     kitty.select_current()
#     time.sleep(0.2)
#     kitty.assert_selection_count(1)

#     # Toggle off again
#     kitty.navigate_up(1)
#     kitty.select_current()
#     time.sleep(0.2)
#     kitty.assert_selection_count(0)

#     # Exit
#     kitty.quit_app()
