"""
Pytest configuration and fixtures for unit tests.
"""
import pytest


# ============================================================================
# RPC Response Builders
# ============================================================================

@pytest.fixture
def mock_rpc_response():
    """Builder for mock RPC responses."""
    def _builder(result=None, error=None, method="aria2.test", rpc_id="qwer"):
        """
        Build a mock JSON-RPC 2.0 response.

        Args:
            result: The result to include in response
            error: The error to include in response (if any)
            method: The RPC method name
            rpc_id: The RPC request ID

        Returns:
            Dict representing a JSON-RPC response
        """
        response = {
            "jsonrpc": "2.0",
            "id": rpc_id
        }
        if error:
            response["error"] = error
        else:
            response["result"] = result
        return response
    return _builder


@pytest.fixture
def sample_files_response():
    """Mock getFiles RPC response."""
    return [
        {
            "index": "1",
            "path": "/downloads/file.zip",
            "length": "104857600",
            "completedLength": "52428800",
            "selected": "true",
            "uris": [
                {
                    "uri": "http://example.com/file.zip",
                    "status": "used"
                }
            ]
        }
    ]


@pytest.fixture
def sample_multi_files_response():
    """Mock getFiles response with multiple files (torrent)."""
    return [
        {
            "index": "1",
            "path": "/downloads/torrent/file1.mkv",
            "length": "1073741824",  # 1 GB
            "completedLength": "536870912",  # 512 MB
            "selected": "true",
            "uris": []
        },
        {
            "index": "2",
            "path": "/downloads/torrent/file2.mkv",
            "length": "2147483648",  # 2 GB
            "completedLength": "1073741824",  # 1 GB
            "selected": "true",
            "uris": []
        },
        {
            "index": "3",
            "path": "/downloads/torrent/subtitle.srt",
            "length": "102400",  # 100 KB
            "completedLength": "102400",  # Complete
            "selected": "false",  # Not selected
            "uris": []
        }
    ]


@pytest.fixture
def sample_options_response():
    """Mock getOption RPC response."""
    return {
        "dir": "/downloads",
        "out": "file.zip",
        "max-connection-per-server": "16",
        "split": "16",
        "min-split-size": "1M",
        "continue": "true",
        "max-concurrent-downloads": "5",
        "max-download-limit": "0",
        "max-upload-limit": "0"
    }


# ============================================================================
# Data Transformation Fixtures
# ============================================================================

@pytest.fixture
def sample_downloads_list():
    """Sample list of downloads for dataToPickerRows testing."""
    return [
        {
            "gid": "abc123",
            "status": "active",
            "totalLength": "104857600",
            "completedLength": "52428800",
            "downloadSpeed": "1048576",
            "files": [{
                "path": "/downloads/file1.zip",
                "length": "104857600",
                "completedLength": "52428800",
                "selected": "true",
                "uris": [{"uri": "http://example.com/file1.zip"}]
            }]
        },
        {
            "gid": "def456",
            "status": "complete",
            "totalLength": "10485760",
            "completedLength": "10485760",
            "downloadSpeed": "0",
            "files": [{
                "path": "/downloads/file2.txt",
                "length": "10485760",
                "completedLength": "10485760",
                "selected": "true",
                "uris": [{"uri": "http://example.com/file2.txt"}]
            }]
        }
    ]


@pytest.fixture
def sample_options_batch():
    """Sample batch of getOption responses."""
    return [
        {
            "id": "qwer1",
            "jsonrpc": "2.0",
            "result": {
                "dir": "/downloads",
                "out": "file1.zip"
            }
        },
        {
            "id": "qwer2",
            "jsonrpc": "2.0",
            "result": {
                "dir": "/downloads",
                "out": "file2.txt"
            }
        }
    ]


@pytest.fixture
def sample_files_batch():
    """Sample batch of getFiles responses."""
    return [
        {
            "id": "qwer1",
            "jsonrpc": "2.0",
            "result": [{
                "path": "/downloads/file1.zip",
                "length": "104857600",
                "completedLength": "52428800",
                "selected": "true"
            }]
        },
        {
            "id": "qwer2",
            "jsonrpc": "2.0",
            "result": [{
                "path": "/downloads/file2.txt",
                "length": "10485760",
                "completedLength": "10485760",
                "selected": "true"
            }]
        }
    ]


# ============================================================================
# Operation Class Fixtures
# ============================================================================

@pytest.fixture
def sample_operation_args():
    """Sample arguments for Operation class."""
    return {
        "name": "Test Operation",
        "key": "t",
        "description": "A test operation",
        "function": lambda: None,
        "args": ["arg1", "arg2"],
        "meta_args": {"key": "value"}
    }
