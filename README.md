# Game Lights

A Python-based controller for WS281x LED strips, designed for interactive tabletop gaming setups. This tool allows you to map physical LED strips to logical table segments (e.g., "Player 1", "Game Master", "Window Side") and control them via a CLI or scripts.

## Features

- **Table & Layout Management**: Define your physical table dimensions and map LED strips to specific sides. Create multiple layouts (e.g., "6 Player", "Warhammer Mode") for the same table.
- **Interactive CLI**:
    - **Setup Wizard**: Easily define tables and segments without editing JSON manually.
    - **Live Control**: Apply animations and colors to specific segments in real-time.
- **Animation System**: Includes built-in patterns like Rainbow, Chase, Fade, Blink, and Flare.
- **Hardware Support**: optimized for Raspberry Pi (WS281x), with a mock mode for local development on macOS/Windows.

## Installation

This project uses `uv` for dependency management.

### Prerequisites

- Python 3.13+
- `uv` (Install via `curl -LsSf https://astral.sh/uv/install.sh | sh` or `pip install uv`)
- **Hardware**: Raspberry Pi (for physical lights), WS2812B/WS2811 LED strips.

### Setup

1.  Clone the repository:
    ```bash
    git clone https://github.com/ev1lm0nk3y/game_lights.git
    cd game_lights
    ```

2.  Install dependencies:
    ```bash
    uv sync
    ```
    *Note: The `rpi_ws281x` library is only installed on Linux. On macOS/Windows, a mock implementation is used.*

## Usage

Run the CLI using `uv run`.

### 1. Initial Setup

Configure your table geometry and LED strip layout.

```bash
uv run game-lights setup
```

- **Create Table**: Define physical dimensions (e.g., 2m x 1m) and pixel density (e.g., 60 ppm).
- **Create Layout**: Map logical segments (e.g., "Player_1") to table sides. You can use strategies like:
    - `center`: Places segment in the middle of the side.
    - `even`: Distributes segments evenly along the side.
    - `absolute`: Places segment at a specific pixel offset.

### 2. Live Control

Start the light controller and interactive wizard.

```bash
uv run game-lights run
```

This launches the **Live Control** interface where you can:
- **Apply Animation**: Choose a pattern (e.g., Rainbow) and target a specific segment (e.g., "Player_1") or the whole table.
- **Set Color**: Set specific segments or pixel ranges to a solid color.
- **Queue & Execute**: Queue multiple actions and execute them simultaneously.

### 3. Systemd Service (Raspberry Pi)

To run Game Lights automatically on boot, see [systemd/README.md](systemd/README.md).

## Configuration

The configuration is stored in `config.json`. While you can edit this manually, using the `setup` wizard is recommended.

**Structure:**
- `tables`: Physical definitions of tables.
- `layouts`: Mappings of segments to table sides.
- `key_bindings`: (Legacy) Keyboard shortcuts for specific actions.

## Development

- **Build System**: Managed by `uv` with `hatchling` backend.
- **Project Structure**:
    - `src/led`: Core logic (Controller, Animations, Models).
    - `src/cli`: CLI interface and Wizards.

To add dependencies:
```bash
uv add <package_name>
```

To run formatting/linting (if configured):
```bash
uv run ruff check .
```
