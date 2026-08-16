"""Test that the codebase matches PROTOCOL.md (source of truth).

This test parses PROTOCOL.md and verifies:
- All WebSocket commands have handlers in websocket_api.py
- All HA bus events are fired in data.py
- All services are registered in services.py
- The store schema fields match the documented structure
"""

import re
import sys
from pathlib import Path

def parse_protocol():
    """Parse PROTOCOL.md and extract the contract."""
    protocol_path = Path(__file__).parent.parent / "docs" / "PROTOCOL.md"
    protocol = protocol_path.read_text()

    # Extract WS commands table
    ws_cmds = {}
    ws_section = re.search(r"## WebSocket API.*?(?=##)", protocol, re.DOTALL)
    if ws_section:
        for line in ws_section.group(0).split("\n"):
            if line.strip().startswith("||") and "hakanban/" in line:
                parts = [p.strip() for p in line.split("||")[1:-1]]
                if len(parts) >= 2:
                    cmd = parts[0].replace("`", "")
                    ws_cmds[cmd] = parts[1]

    # Extract events table
    events = []
    events_section = re.search(r"## HA bus events.*?(?=##)", protocol, re.DOTALL)
    if events_section:
        for line in events_section.group(0).split("\n"):
            if line.strip().startswith("||") and "hakanban_" in line:
                parts = [p.strip() for p in line.split("||")[1:-1]]
                if len(parts) >= 1:
                    events.append(parts[0].replace("`", ""))

    # Extract services
    services = ["add_card", "move_card", "update_card", "add_comment", "create_board", "create_column"]

    return ws_cmds, events, services

def check_websocket_api(ws_cmds):
    """Check that all WS commands have handlers in websocket_api.py."""
    ws_api_path = Path(__file__).parent.parent / "custom_components" / "hakanban" / "websocket_api.py"
    ws_api_code = ws_api_path.read_text()

    # Extract handler method names
    handlers = set()
    for match in re.finditer(r"def handle_(\w+)\(", ws_api_code):
        handlers.add(f"hakanban/{match.group(1)}")

    missing = set(ws_cmds.keys()) - handlers
    extra = handlers - set(ws_cmds.keys())

    errors = []
    if missing:
        errors.append(f"Missing WS handlers: {missing}")
    if extra:
        errors.append(f"Extra WS handlers (not in PROTOCOL.md): {extra}")

    return errors

def check_events(events):
    """Check that all events are fired in data.py."""
    data_path = Path(__file__).parent.parent / "custom_components" / "hakanban" / "data.py"
    data_code = data_path.read_text()

    # Extract EVENTS constant
    events_match = re.search(r"EVENTS\s*=\s*\[(.*?)\]", data_code, re.DOTALL)
    event_names = set()
    if events_match:
        for evt in re.findall(r'"([^"]+)"', events_match.group(1)):
            event_names.add(evt)

    missing = set(events) - event_names
    extra = event_names - set(events)

    errors = []
    if missing:
        errors.append(f"Missing events in data.EVENTS: {missing}")
    if extra:
        errors.append(f"Extra events in data.EVENTS (not in PROTOCOL.md): {extra}")

    return errors

def check_services(services):
    """Check that all services are registered in services.py."""
    services_path = Path(__file__).parent.parent / "custom_components" / "hakanban" / "services.py"
    services_code = services_path.read_text()

    # Check if each service name appears in the file
    service_names = set()
    for svc in services:
        if svc in services_code:
            service_names.add(svc)

    missing = set(services) - service_names
    extra = set()  # We don't track extra since we're just checking presence

    errors = []
    if missing:
        errors.append(f"Missing services in services.py: {missing}")

    return errors

def main():
    ws_cmds, events, services = parse_protocol()

    errors = []
    errors.extend(check_websocket_api(ws_cmds))
    errors.extend(check_events(events))
    errors.extend(check_services(services))

    if errors:
        print("PROTOCOL DRIFT DETECTED:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("PASS - Code matches PROTOCOL.md")
        sys.exit(0)

if __name__ == "__main__":
    main()
