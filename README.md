# Infinite Monkeys Girona Map Sequencer

An interactive map sequencer for exploring CORINE habitat data around Girona. Click polygons and points on the map to trigger OSC messages to any OSC-capable software (SuperCollider, Max/MSP, Pure Data, etc.).

## Requirements

- Python 3.8+
- `websockets` — WebSocket server
- `python-osc` — OSC UDP client

Install dependencies:

```bash
pip install websockets python-osc
```

## Running the OSC Bridge

The OSC bridge relays messages from the browser to any OSC target over UDP.

```bash
python3 osc_bridge.py
```

By default it listens on WebSocket port **8765** and sends OSC to **127.0.0.1:57120** (SuperCollider default). You can override the WebSocket port:

```bash
python3 osc_bridge.py 9000
```

Once the bridge is running, open **`explorer.html`** in your browser. The page will auto-connect to `ws://localhost:8765`.

## Configuring OSC Target

The OSC target host and port can be changed live from the HTML GUI — no restart needed. You can also add multiple extra OSC targets from the interface.

## OSC Message Format

Each map feature click sends:

```
/HABITAT_CODE  [float: value]
```

For example, clicking a polygon with habitat code `44` sends `/44 1500.0`.

## Files

| File | Description |
|---|---|
| `explorer.html` | Main map interface |
| `viewer.html` | Viewer-only map |
| `osc_bridge.py` | WebSocket → OSC bridge server |
| `hab_poligons_CORINE_2023.*` | CORINE habitat polygon shapefile |
| `hab_punts_CORINE_2023.*` | CORINE habitat points shapefile |
| `hab_poligons.geojson` | Habitat polygons in GeoJSON format |
