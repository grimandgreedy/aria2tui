"""
Unit tests for formatting utilities in aria2c_utils.py

Tests for size formatting, time conversion, and display utilities.
"""
import pytest
from aria2tui.utils.aria2c_utils import bytes_to_human_readable


# ============================================================================
# Tests for bytes_to_human_readable
# ============================================================================

class TestBytesToHumanReadable:
    """Test the bytes_to_human_readable function."""

    def test_zero_bytes(self):
        """Test formatting zero bytes."""
        assert bytes_to_human_readable(0) == "0 B"

    def test_bytes_only(self):
        """Test formatting byte values under 1024."""
        assert bytes_to_human_readable(1) == "1 B"
        assert bytes_to_human_readable(100) == "100 B"
        assert bytes_to_human_readable(1023) == "1023 B"

    def test_kilobytes(self):
        """Test formatting kilobytes."""
        assert bytes_to_human_readable(1024) == "1.0 KB"
        assert bytes_to_human_readable(1536) == "1.5 KB"
        assert bytes_to_human_readable(2048) == "2.0 KB"
        assert bytes_to_human_readable(102400) == "100.0 KB"

    def test_megabytes(self):
        """Test formatting megabytes."""
        assert bytes_to_human_readable(1024 * 1024) == "1.0 MB"
        assert bytes_to_human_readable(1024 * 1024 * 5) == "5.0 MB"
        assert bytes_to_human_readable(1024 * 1024 * 50) == "50.0 MB"
        assert bytes_to_human_readable(1024 * 1024 * 100) == "100.0 MB"

    def test_gigabytes(self):
        """Test formatting gigabytes."""
        assert bytes_to_human_readable(1024 * 1024 * 1024) == "1.0 GB"
        assert bytes_to_human_readable(1024 * 1024 * 1024 * 2.5) == "2.5 GB"
        assert bytes_to_human_readable(1024 * 1024 * 1024 * 100) == "100.0 GB"

    def test_terabytes(self):
        """Test formatting terabytes."""
        assert bytes_to_human_readable(1024 * 1024 * 1024 * 1024) == "1.0 TB"
        assert bytes_to_human_readable(1024 * 1024 * 1024 * 1024 * 5.5) == "5.5 TB"

    def test_terabytes_max(self):
        """Test that terabytes is the maximum unit."""
        # Should not go beyond TB
        huge_value = 1024 * 1024 * 1024 * 1024 * 1024 * 10  # 10 PB in bytes
        result = bytes_to_human_readable(huge_value)
        assert "TB" in result
        assert "PB" not in result

    def test_string_input(self):
        """Test that string inputs are converted to float."""
        assert bytes_to_human_readable("1024") == "1.0 KB"
        assert bytes_to_human_readable("1048576") == "1.0 MB"

    def test_float_input(self):
        """Test float inputs."""
        assert bytes_to_human_readable(1024.0) == "1.0 KB"
        assert bytes_to_human_readable(1536.5) == "1.5 KB"

    def test_custom_separator(self):
        """Test custom separator between value and unit."""
        assert bytes_to_human_readable(1024, sep="") == "1.0KB"
        assert bytes_to_human_readable(1024, sep="-") == "1.0-KB"
        assert bytes_to_human_readable(1024, sep="  ") == "1.0  KB"

    def test_round_at_zero(self):
        """Test rounding with round_at=0 (always show decimals)."""
        # round_at=0 means always show decimals, even for bytes
        assert bytes_to_human_readable(0, round_at=0) == "0.0 B"
        assert bytes_to_human_readable(100, round_at=0) == "100.0 B"
        assert bytes_to_human_readable(1024, round_at=0) == "1.0 KB"

    def test_round_at_one(self):
        """Test rounding with round_at=1 (default, round bytes)."""
        # round_at=1 means round integers for B, show decimals for KB+
        assert bytes_to_human_readable(0, round_at=1) == "0 B"
        assert bytes_to_human_readable(100, round_at=1) == "100 B"
        assert bytes_to_human_readable(1024, round_at=1) == "1.0 KB"
        assert bytes_to_human_readable(1048576, round_at=1) == "1.0 MB"

    def test_round_at_two(self):
        """Test rounding with round_at=2 (round B and KB)."""
        # round_at=2 means round integers for B and KB, show decimals for MB+
        assert bytes_to_human_readable(0, round_at=2) == "0 B"
        assert bytes_to_human_readable(1024, round_at=2) == "1 KB"
        assert bytes_to_human_readable(1536, round_at=2) == "1 KB"  # Rounds down
        assert bytes_to_human_readable(2048, round_at=2) == "2 KB"
        assert bytes_to_human_readable(1048576, round_at=2) == "1.0 MB"

    def test_real_world_sizes(self):
        """Test with realistic file sizes."""
        # Small file: 500 KB
        assert bytes_to_human_readable(512000) == "500.0 KB"

        # CD image: ~700 MB
        assert bytes_to_human_readable(734003200) == "700.0 MB"

        # DVD image: ~4.7 GB
        result = bytes_to_human_readable(5046586572.8)
        assert "GB" in result
        assert result.startswith("4.7")

        # Large download: 50 GB
        assert bytes_to_human_readable(53687091200) == "50.0 GB"

    def test_partial_downloads(self):
        """Test sizes commonly seen in partial downloads."""
        # 50% of 100MB
        assert bytes_to_human_readable(52428800) == "50.0 MB"

        # 25% of 1GB
        assert bytes_to_human_readable(268435456) == "256.0 MB"

        # 75% of 2GB
        result = bytes_to_human_readable(1610612736)
        assert "GB" in result or "MB" in result

    def test_edge_case_1023_bytes(self):
        """Test edge case right below 1 KB."""
        assert bytes_to_human_readable(1023) == "1023 B"

    def test_edge_case_1024_bytes(self):
        """Test edge case exactly 1 KB."""
        assert bytes_to_human_readable(1024) == "1.0 KB"

    def test_edge_case_near_boundaries(self):
        """Test values near unit boundaries."""
        # Just under 1 MB
        result = bytes_to_human_readable(1048575)
        assert "KB" in result

        # Exactly 1 MB
        assert bytes_to_human_readable(1048576) == "1.0 MB"

        # Just over 1 MB
        result = bytes_to_human_readable(1048577)
        assert "MB" in result

    def test_decimal_precision(self):
        """Test that decimal precision is one decimal place."""
        # 1.5 KB = 1536 bytes
        result = bytes_to_human_readable(1536)
        assert result == "1.5 KB"

        # 2.3 MB
        result = bytes_to_human_readable(2411724.8)
        assert result.startswith("2.3")
        assert "MB" in result

    def test_negative_size(self):
        """Test handling of negative sizes (edge case)."""
        # Function doesn't explicitly handle negatives,
        # but let's verify it doesn't crash
        result = bytes_to_human_readable(-100)
        assert isinstance(result, str)

    def test_very_large_float(self):
        """Test with very large float values."""
        large_value = 1024.0 ** 4 * 100.5  # 100.5 TB
        result = bytes_to_human_readable(large_value)
        assert "TB" in result
        assert "100.5" in result or "100.4" in result or "100.6" in result


# ============================================================================
# Placeholder for future tests
# ============================================================================

# TODO: Add tests for other formatting functions once they are identified:
# - Time formatting (if exists)
# - Progress bar formatting (if exists)
# - Speed formatting (if exists)
# - Percentage formatting (if exists)
