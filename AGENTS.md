# Repository Guidelines

## Project Structure & Module Organization
- `main.py` starts the controller loop; `config.py` stores pins, thresholds, Wi‑Fi, and webhook endpoints (treat secrets carefully).
- `core/` holds orchestration: `controller.py` coordinates sensors/actuators and uploads data; `wifi_manager.py` keeps Wi‑Fi healthy.
- `sensors/` contains DHT11, turbidity, TDS, and water-level drivers; `actuators/` controls RGB LED, buzzer, and relay.
- `lib/` ships MicroPython-friendly utilities (logging in `esplog/`, `urequests.py`, bundled Wi‑Fi helper); `fake_upload.py` generates sample payloads to a webhook; `test.py` is a simple asyncio cancellation demo.
- Assets/tests are lightweight; expect most verification to happen on the ESP32 hardware.

## Build, Test, and Development Commands
- Install host deps (for tooling and webhook generator): `uv sync --dev` (or `pip install -e .[dev]` if you prefer pip).
- Run main control loop on hardware (MicroPython/ESP32 environment only): `mpremote run main.py` after copying `config.py` with correct credentials.
- Generate sample data to a local webhook: `python fake_upload.py`.
- Quick asyncio behavior check (host Python): `python test.py`.

## Coding Style & Naming Conventions
- Use 4-space indentation, type hints where practical, and concise docstrings describing intent.
- Module/function names follow `snake_case`; configuration constants are `UPPER_SNAKE_CASE` in `config.py`.
- Keep hardware-facing code non-blocking (async-friendly); prefer logging via `lib.esplog.core.Logger` rather than print.
- Avoid committing hard-coded secrets; supply safe defaults or document required environment overrides.

## Testing Guidelines
- No formal test suite yet; verify changes on-device with real sensors/actuators and capture log output (`farm_controller.txt`).
- When modifying thresholds or control logic, exercise edge conditions (high temp/humidity, low water, turbidity/TDS spikes) and confirm actuator responses and upload behavior.
- For networking changes, watch Wi‑Fi reconnect handling and webhook status codes; keep a short run log in the PR.

## Commit & Pull Request Guidelines
- Follow the existing history pattern: `<type>: <summary>` (e.g., `feature: 新增wifi`, `chore: 整理uasyncio`); keep the summary imperative and lower-case.
- Commits should be small and hardware-tested when applicable; mention the device/firmware used.
- PRs need a brief description, linked issue (if any), and notes on hardware verification or simulated runs; include screenshots or log snippets when they clarify behavior.
- Call out breaking changes to pin mappings, thresholds, or network endpoints explicitly.

## Security & Configuration Tips
- `config.py` currently holds live credentials/endpoints; replace with deployment-specific values before flashing devices and avoid sharing real secrets in public history.
- Validate webhook targets before enabling automated uploads; prefer staging URLs while testing.
