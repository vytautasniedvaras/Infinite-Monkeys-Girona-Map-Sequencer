#!/usr/bin/env python3
"""
CORINE Habitat Explorer — OSC Bridge
Bridges WebSocket messages from the browser to OSC UDP packets.

Usage:
    python3 osc_bridge.py [ws_port]
    ws_port: WebSocket port (default 8765)

The browser auto-connects to ws://localhost:{ws_port}.
Configure the OSC target (host / port) from the HTML GUI.

Message protocol from browser → bridge:
    {"type":"config", "host":"127.0.0.1", "port":57120}
    {"type":"osc",    "address":"/44",    "args":[1500.0]}
"""

import asyncio, json, sys, logging
import websockets
from pythonosc import udp_client

logging.basicConfig(
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger()

WS_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

osc_target  = {"host": "127.0.0.1", "port": 57120}
osc_extra: list[dict] = []   # [{host, port, enabled}, ...]
_clients: dict[str, udp_client.SimpleUDPClient] = {}


def get_client(host: str, port: int) -> udp_client.SimpleUDPClient:
    key = f"{host}:{port}"
    if key not in _clients:
        _clients[key] = udp_client.SimpleUDPClient(host, port)
        log.info(f"OSC client created  →  {key}")
    return _clients[key]


async def handler(websocket):
    peer = websocket.remote_address
    log.info(f"Browser connected   {peer}")
    try:
        async for raw in websocket:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            kind = data.get("type")

            if kind == "config":
                osc_target["host"] = data.get("host", "127.0.0.1").strip()
                osc_target["port"] = int(data.get("port", 57120))
                msg = f"OSC target  →  {osc_target['host']}:{osc_target['port']}"
                log.info(msg)
                await websocket.send(json.dumps({"type": "status", "ok": True, "msg": msg}))

            elif kind == "config_extra":
                osc_extra.clear()
                for t in data.get("targets", []):
                    osc_extra.append({
                        "host":    (t.get("host") or "").strip(),
                        "port":    int(t.get("port", 57120)),
                        "enabled": bool(t.get("enabled", False)),
                    })
                active = [f"{t['host']}:{t['port']}" for t in osc_extra if t["enabled"] and t["host"]]
                log.info(f"OSC extra targets: {active or '(none)'}")

            elif kind == "osc":
                address = data.get("address", "/unknown")
                args    = data.get("args", [])
                client  = get_client(osc_target["host"], osc_target["port"])
                client.send_message(address, args)
                log.info(f"OSC  {address:<14} {args}  →  {osc_target['host']}:{osc_target['port']}")
                for t in osc_extra:
                    if t["enabled"] and t["host"]:
                        get_client(t["host"], t["port"]).send_message(address, args)
                        log.info(f"OSC  {address:<14} {args}  →  {t['host']}:{t['port']}")

    except websockets.exceptions.ConnectionClosed:
        log.info(f"Browser disconnected  {peer}")


async def main():
    log.info("=" * 52)
    log.info("  CORINE Habitat Explorer — OSC Bridge")
    log.info("=" * 52)
    log.info(f"  WebSocket:     ws://localhost:{WS_PORT}")
    log.info(f"  Default OSC:   {osc_target['host']}:{osc_target['port']}")
    log.info(f"  Open explorer.html in your browser")
    log.info("=" * 52)
    async with websockets.serve(handler, "localhost", WS_PORT):
        await asyncio.Future()


asyncio.run(main())
