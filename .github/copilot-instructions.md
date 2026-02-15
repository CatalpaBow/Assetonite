# Assetonite Copilot Instructions

## Project Overview
Assetonite bridges AssettoCorsaSim telemetry data to Resonite via a reactive message pipeline. It reads shared memory data from AssettoCorsaSim, transforms it through a layered architecture, and transmits via OSC.

## Architecture: Reactive Layered Pipeline

Data flows through strict dependency layers (bottom-up):
1. **RawData** (`src/msg/raw_data/`): Reads AssettoCorsaSim shared memory (`pyaccsharedmemory.py`) and INI configs
2. **MessageSource** (`src/msg/message_source/`): Transforms raw telemetry using whitelists into structured data
3. **Message** (`src/msg/message/`): Calculates derived values (analog gauges, tire rotation angles)
4. **Sender** (`src/msg/send/`): Serializes and sends via OSC

The pipeline is orchestrated in `MessageServerRxPy` using **ReactiveX** (`reactivex==4.0.4`) with `rx.interval()` at configurable tick rates.

## Critical Patterns

### Telemetry Data Whitelisting
All AssettoCorsaSim properties are filtered through whitelists in `telemetry_reader_implement.py`:
- Only whitelisted fields from `Physics`, `Graphics`, `Static` are included
- Add new telemetry: extend whitelists, not raw data structures
- Example: `'rpm', 'speed_kmh', 'fuel'` in Physics whitelist

### Reactive Subscriptions
Never block the main loop. Use ReactiveX operators:
```python
rx.interval(tick_rate).pipe(
    ops.map(lambda _ : self.telemetry_reader.read()),
    ops.filter(lambda tele : tele != None),
    ops.map(lambda tele : self.msg_src_prvdr.create(tele))
).subscribe(on_next=handler, on_error=error_handler)
```

### Logging Setup
Use centralized logger from `src/utils/logger_getter.py`:
```python
from src.utils.logger_getter import get_logger
logger = get_logger('module_name')
```
Log config in `config/log_config.json` controls all output.

### FBX Material Processing
Material fixing happens in two stages:
1. **Texture conversion** (`convert_to_non_alpha`): Uses `ezTexConv.exe` to strip alpha channels via channel mapping
2. **Material property fixing** (`material_fixer.py`): FBX SDK to update shader properties and texture references

Key: DDS format detection (`is_r8g8`) determines channel mapping strategy (`'rg'` vs `'rgb'`).

## Developer Workflows

### Running the Server
```bash
# Activate venv and launch
.venv\Scripts\activate && python src\main.py
# Press 'q' + Enter to graceful shutdown
```
Task: `launch_sever` (note: typo in task name)

### Project Dependencies
- **ReactiveX** 4.0.4: Core async/streaming
- **python-osc** 1.9.3: OSC protocol
- **PyQt5/6**: GUI (for plotting/debugging)
- **numpy-quaternion**: Physics calculations
- **FBX SDK**: Material/model manipulation
- **matplotlib**: Data visualization

### Testing
Uses `pytest` with async support (`pytest-asyncio`). Tests in `tests/` verify:
- Shared memory reading (`test_shared_memory.py`)
- OSC message transmission (`test_rxpy_osc.py`)

## File Organization

- `src/main.py`: Entry point, async server setup
- `src/msg/server_builder.py`: Dependency injection—modify to alter pipeline composition
- `src/fbx_fixer/`: AssettoCorsaSim asset processing (separate from telemetry pipeline)
- `config/log_config.json`: Logging control
- `data/input/`, `data/output/`: FBX and texture directories

## Common Tasks

**Add new telemetry field**: Update whitelists in `telemetry_reader_implement.py` (no schema changes needed)

**Change OSC tick rate**: Modify `tick_rate` in `main.py` (currently 1/160 = ~160Hz)

**Debug message flow**: Enable log level `DEBUG` in `config/log_config.json`

**Handle new message types**: Extend `MessageBuilder` and `message/message_builder.py`

## External Context
- Resonite VR platform (consumer) at IP/port configured in `server_builder.py`
- AssettoCorsaSim writes shared memory continuously; app crashes cleanly if sim exits
