#!/usr/bin/env python3
"""
Script to fetch a raw payload from the database and print its JSON schema.

Usage:
    python scripts/print_payload_schema.py [--channel CHANNEL_ID] [--message-id MESSAGE_ID] [--db-path DB_PATH]

If no channel/message-id is specified, the script will fetch the first available message.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path to import osintagency modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from osintagency.storage import fetch_messages, resolve_db_path


def infer_json_schema(obj: Any, path: str = "$") -> dict[str, Any]:
    """
    Recursively infer a JSON schema from a Python object.

    Args:
        obj: The object to infer schema from
        path: Current path in the object (for nested objects)

    Returns:
        A JSON schema representation
    """
    if obj is None:
        return {"type": "null", "path": path}

    if isinstance(obj, bool):
        return {"type": "boolean", "path": path, "example": obj}

    if isinstance(obj, int):
        return {"type": "integer", "path": path, "example": obj}

    if isinstance(obj, float):
        return {"type": "number", "path": path, "example": obj}

    if isinstance(obj, str):
        return {
            "type": "string",
            "path": path,
            "example": obj[:50] + ("..." if len(obj) > 50 else ""),
            "length": len(obj),
        }

    if isinstance(obj, list):
        if len(obj) == 0:
            return {"type": "array", "path": path, "items": "unknown (empty array)"}

        # Infer schema from first element (assuming homogeneous array)
        item_schema = infer_json_schema(obj[0], f"{path}[0]")

        # Check if all items have the same type
        all_same_type = all(
            type(item) == type(obj[0]) for item in obj
        )

        return {
            "type": "array",
            "path": path,
            "length": len(obj),
            "items": item_schema,
            "homogeneous": all_same_type,
        }

    if isinstance(obj, dict):
        properties = {}
        for key, value in obj.items():
            properties[key] = infer_json_schema(value, f"{path}.{key}")

        return {
            "type": "object",
            "path": path,
            "properties": properties,
            "required": list(obj.keys()),
        }

    # Fallback for unknown types
    return {
        "type": f"unknown ({type(obj).__name__})",
        "path": path,
        "example": str(obj)[:50],
    }


def format_schema_tree(schema: dict[str, Any], indent: int = 0) -> str:
    """
    Format the schema as a readable tree structure.

    Args:
        schema: The schema dictionary to format
        indent: Current indentation level

    Returns:
        Formatted string representation
    """
    prefix = "  " * indent
    result = []

    schema_type = schema.get("type", "unknown")
    path = schema.get("path", "")

    if schema_type == "object":
        result.append(f"{prefix}object {{")
        properties = schema.get("properties", {})
        for key, prop_schema in properties.items():
            prop_type = prop_schema.get("type", "unknown")
            result.append(f"{prefix}  {key}: {prop_type}")

            if prop_type == "object":
                # Recursively format nested objects
                nested = format_schema_tree(prop_schema, indent + 2)
                result.append(nested)
            elif prop_type == "array":
                items = prop_schema.get("items", {})
                items_type = items.get("type", "unknown") if isinstance(items, dict) else items
                length = prop_schema.get("length", 0)
                result.append(f"{prefix}    (length: {length}, items: {items_type})")
            elif prop_type == "string":
                length = prop_schema.get("length", 0)
                example = prop_schema.get("example", "")
                result.append(f'{prefix}    (length: {length}, example: "{example}")')
            elif "example" in prop_schema:
                example = prop_schema.get("example")
                result.append(f"{prefix}    (example: {example})")

        result.append(f"{prefix}}}")
    elif schema_type == "array":
        items = schema.get("items", {})
        length = schema.get("length", 0)
        result.append(f"{prefix}array[{length}] {{")
        if isinstance(items, dict):
            nested = format_schema_tree(items, indent + 1)
            result.append(nested)
        else:
            result.append(f"{prefix}  items: {items}")
        result.append(f"{prefix}}}")
    else:
        # Primitive type
        if "example" in schema:
            result.append(f"{prefix}{schema_type} (example: {schema['example']})")
        else:
            result.append(f"{prefix}{schema_type}")

    return "\n".join(result)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch a raw payload from the database and print its JSON schema"
    )
    parser.add_argument(
        "--channel",
        type=str,
        help="Channel ID to fetch message from (optional)",
    )
    parser.add_argument(
        "--message-id",
        type=int,
        help="Specific message ID to fetch (requires --channel)",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        help="Path to the database file (default: from environment or data/messages.sqlite3)",
    )
    parser.add_argument(
        "--format",
        choices=["tree", "json", "compact"],
        default="tree",
        help="Output format: tree (readable), json (full schema), or compact (summary)",
    )

    args = parser.parse_args()

    # Resolve database path
    db_path = resolve_db_path(args.db_path) if args.db_path else resolve_db_path(None)

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}", file=sys.stderr)
        print("Run message collection first to populate the database.", file=sys.stderr)
        sys.exit(1)

    # Fetch messages
    try:
        messages = fetch_messages(channel_id=args.channel, db_path=db_path)
    except Exception as e:
        print(f"Error fetching messages: {e}", file=sys.stderr)
        sys.exit(1)

    if not messages:
        print("No messages found in the database.", file=sys.stderr)
        sys.exit(1)

    # Find specific message or use first one
    target_message = None
    if args.message_id is not None:
        if not args.channel:
            print("Error: --message-id requires --channel", file=sys.stderr)
            sys.exit(1)

        target_message = next(
            (m for m in messages if m["message_id"] == args.message_id),
            None,
        )
        if not target_message:
            print(
                f"Error: Message {args.message_id} not found in channel {args.channel}",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        target_message = messages[0]

    # Extract raw payload
    raw_payload = target_message["raw_payload"]

    # Print message info
    print(f"Channel: {target_message['channel_id']}")
    print(f"Message ID: {target_message['message_id']}")
    print(f"Posted at: {target_message['posted_at']}")
    print(f"Text preview: {target_message['text'][:100]}...")
    print("\n" + "=" * 80 + "\n")

    # Infer and print schema
    schema = infer_json_schema(raw_payload)

    if args.format == "json":
        print("JSON Schema:")
        print(json.dumps(schema, indent=2, ensure_ascii=False))
    elif args.format == "compact":
        print("Compact Schema:")
        print(f"Type: {schema['type']}")
        if schema["type"] == "object":
            print(f"Properties: {len(schema.get('properties', {}))}")
            print("Fields:")
            for key in schema.get("properties", {}).keys():
                print(f"  - {key}")
    else:  # tree format (default)
        print("Raw Payload Schema (Tree View):")
        print(format_schema_tree(schema))

    print("\n" + "=" * 80 + "\n")
    print("Raw Payload (JSON):")
    print(json.dumps(raw_payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
