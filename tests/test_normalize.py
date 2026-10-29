from clihax.utils.helpers import normalize_tool


def test_valid_entry_gets_defaults():
    result = normalize_tool({"tool": "nmap", "command": "nmap -sV <target>"})
    assert result["tool"] == "nmap"
    assert result["command"] == "nmap -sV <target>"
    assert result["description"] == ""
    assert result["category"] == ""
    assert result["tags"] == []
    assert result["created_at"] and result["updated_at"]


def test_missing_tool_or_command_is_rejected():
    assert normalize_tool({"tool": "nmap"}) is None
    assert normalize_tool({"command": "ls"}) is None
    assert normalize_tool({"tool": "  ", "command": "ls"}) is None


def test_non_dict_is_rejected():
    assert normalize_tool("nmap") is None
    assert normalize_tool(None) is None
    assert normalize_tool(["tool", "command"]) is None


def test_tags_string_is_split_and_cleaned():
    result = normalize_tool({"tool": "a", "command": "b", "tags": "scan, nmap,,"})
    assert result["tags"] == ["scan", "nmap"]


def test_bad_tags_type_becomes_empty_list():
    assert normalize_tool({"tool": "a", "command": "b", "tags": 5})["tags"] == []


def test_existing_timestamps_are_kept():
    result = normalize_tool(
        {"tool": "a", "command": "b", "created_at": "2025-01-01T00:00:00"}
    )
    assert result["created_at"] == "2025-01-01T00:00:00"
    assert result["updated_at"] == "2025-01-01T00:00:00"
