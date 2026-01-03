"""
Pytest configuration and shared fixtures for aria2tui tests.
"""
import pytest
from pathlib import Path


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture
def fixtures_dir():
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def config_fixtures_dir(fixtures_dir):
    """Return the path to config fixtures directory."""
    return fixtures_dir / "configs"


@pytest.fixture
def rpc_fixtures_dir(fixtures_dir):
    """Return the path to RPC response fixtures directory."""
    return fixtures_dir / "rpc_responses"


@pytest.fixture
def torrent_fixtures_dir(fixtures_dir):
    """Return the path to torrent fixtures directory."""
    return fixtures_dir / "torrents"


@pytest.fixture
def input_fixtures_dir(fixtures_dir):
    """Return the path to input file fixtures directory."""
    return fixtures_dir / "input_files"


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def default_config():
    """Return default aria2tui configuration dict."""
    return {
        "general": {
            "port": 6800,
            "token": "test-token",
            "url": "http://localhost",
            "global_stats_timer": 1,
            "refresh_timer": 2,
            "paginate": False
        },
        "appearance": {
            "theme": 3,
            "show_right_pane_default": False,
            "right_pane_default_index": 0
        }
    }


# ============================================================================
# Sample Download Data Fixtures
# ============================================================================

@pytest.fixture
def sample_download():
    """Return sample direct download dict from aria2 RPC."""
    return {
        "gid": "2089b05ecca3d829",
        "status": "active",
        "totalLength": "104857600",  # 100 MB
        "completedLength": "52428800",  # 50 MB
        "uploadLength": "0",
        "downloadSpeed": "1048576",  # 1 MB/s
        "uploadSpeed": "0",
        "infoHash": "",
        "numSeeders": "0",
        "seeder": "false",
        "pieceLength": "1048576",
        "numPieces": "100",
        "connections": "16",
        "errorCode": "",
        "errorMessage": "",
        "followedBy": [],
        "following": "",
        "belongsTo": "",
        "dir": "/downloads",
        "files": [{
            "index": "1",
            "path": "/downloads/file.zip",
            "length": "104857600",
            "completedLength": "52428800",
            "selected": "true",
            "uris": [{
                "uri": "http://example.com/file.zip",
                "status": "used"
            }]
        }],
        "bittorrent": {}
    }


@pytest.fixture
def sample_torrent_download():
    """Return sample torrent download dict from aria2 RPC."""
    return {
        "gid": "3089b05ecca3d830",
        "status": "active",
        "totalLength": "3774873600",  # ~3.5 GB
        "completedLength": "1887436800",  # ~1.75 GB (50%)
        "uploadLength": "524288000",
        "downloadSpeed": "524288",  # 512 KB/s
        "uploadSpeed": "131072",  # 128 KB/s
        "infoHash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
        "numSeeders": "15",
        "seeder": "false",
        "pieceLength": "1048576",
        "numPieces": "3600",
        "connections": "45",
        "errorCode": "",
        "errorMessage": "",
        "followedBy": [],
        "following": "",
        "belongsTo": "",
        "dir": "/downloads/torrents",
        "files": [
            {
                "index": "1",
                "path": "/downloads/torrents/ubuntu-22.04.iso",
                "length": "3774873600",
                "completedLength": "1887436800",
                "selected": "true",
                "uris": []
            }
        ],
        "bittorrent": {
            "announceList": [
                ["http://tracker.example.com:6969/announce"]
            ],
            "comment": "Ubuntu 22.04 LTS",
            "creationDate": 1650000000,
            "mode": "single",
            "info": {
                "name": "ubuntu-22.04.iso"
            }
        }
    }


@pytest.fixture
def sample_stopped_download():
    """Return sample stopped/completed download."""
    return {
        "gid": "4089b05ecca3d831",
        "status": "complete",
        "totalLength": "10485760",  # 10 MB
        "completedLength": "10485760",  # 100% complete
        "uploadLength": "0",
        "downloadSpeed": "0",
        "uploadSpeed": "0",
        "infoHash": "",
        "numSeeders": "0",
        "seeder": "false",
        "pieceLength": "1048576",
        "numPieces": "10",
        "connections": "0",
        "errorCode": "",
        "errorMessage": "",
        "followedBy": [],
        "following": "",
        "belongsTo": "",
        "dir": "/downloads",
        "files": [{
            "index": "1",
            "path": "/downloads/small_file.txt",
            "length": "10485760",
            "completedLength": "10485760",
            "selected": "true",
            "uris": [{
                "uri": "http://example.com/small_file.txt",
                "status": "used"
            }]
        }],
        "bittorrent": {}
    }


@pytest.fixture
def sample_error_download():
    """Return sample download with error."""
    return {
        "gid": "5089b05ecca3d832",
        "status": "error",
        "totalLength": "52428800",  # 50 MB
        "completedLength": "5242880",  # 10% complete before error
        "uploadLength": "0",
        "downloadSpeed": "0",
        "uploadSpeed": "0",
        "infoHash": "",
        "numSeeders": "0",
        "seeder": "false",
        "pieceLength": "1048576",
        "numPieces": "50",
        "connections": "0",
        "errorCode": "3",
        "errorMessage": "Resource not found",
        "followedBy": [],
        "following": "",
        "belongsTo": "",
        "dir": "/downloads",
        "files": [{
            "index": "1",
            "path": "/downloads/missing_file.zip",
            "length": "52428800",
            "completedLength": "5242880",
            "selected": "true",
            "uris": [{
                "uri": "http://example.com/missing_file.zip",
                "status": "used"
            }]
        }],
        "bittorrent": {}
    }


# ============================================================================
# RPC Response Fixtures
# ============================================================================

@pytest.fixture
def sample_files_response():
    """Return sample getFiles RPC response."""
    return [
        {
            "index": "1",
            "path": "/downloads/file.zip",
            "length": "104857600",
            "completedLength": "52428800",
            "selected": "true",
            "uris": [{
                "uri": "http://example.com/file.zip",
                "status": "used"
            }]
        }
    ]


@pytest.fixture
def sample_options_response():
    """Return sample getOption RPC response."""
    return {
        "dir": "/downloads",
        "out": "file.zip",
        "max-connection-per-server": "16",
        "split": "16",
        "min-split-size": "1M",
        "continue": "true",
        "max-concurrent-downloads": "5"
    }


@pytest.fixture
def sample_global_stats():
    """Return sample getGlobalStat RPC response."""
    return {
        "downloadSpeed": "2097152",  # 2 MB/s
        "uploadSpeed": "524288",  # 512 KB/s
        "numActive": "3",
        "numWaiting": "5",
        "numStopped": "12",
        "numStoppedTotal": "12"
    }
