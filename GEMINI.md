# Project: Game Lights

## Overview
This project is a Python-based controller for WS281x LED strips, designed specifically for a gaming table setup. It allows for defining "pixels" and "strip segments" mapped to physical locations around a table (e.g., Game Master station, Wall, Window).

## Directory Structure & Key Files

### Core Logic (`game_lights/`)
*   **`game_lights/__init__.py`**: Indicates that `game_lights` is a Python package.
*   **`game_lights/pixel.py`**: Defines the `Pixel` class, representing a single LED. It manages patterns, colors, and loops for individual pixels.
*   **`game_lights/strip.py`**: Defines `StripSegment`, representing a logical grouping of LEDs (e.g., a specific side of the table).
*   **`game_lights/table.py`**: Contains the `TablePosition` enum, which maps code constants to physical locations (e.g., `GAMEMASTER`, `WALL_1`).
*   **`game_lights/animations.py`**: Defines `AnimationFrame` for orchestrating lighting effects (currently incomplete).
*   **`game_lights/objects`**: A text file containing preliminary data structure or class definitions.

### Configuration & Environment
*   **`.gitignore`**: Configured to ignore the virtual environment (`bin/`, `lib/`, etc.) and build artifacts.
*   **`bin/`, `lib/`, `pyvenv.cfg`**: The local Python Virtual Environment (ignored by git).

## Dependencies
*   **`rpi_ws281x`**: The core library used to interface with the LED hardware on a Raspberry Pi.
*   **`dataclasses`**: Used extensively for structured data storage in classes.

## Current Status & Observations
*   **Missing Dependencies**: `pixel.py` attempts to import from `patterns`, but `patterns.py` (or a `patterns` package) does not exist in the directory.
*   **Version Control**: The repository has no commits and the `.gitignore` is overly aggressive, preventing files from being tracked.
*   **Setup**: The project appears to be in the very early stages of scaffolding.

## Usage (Inferred)
The intended usage pattern seems to be:
1.  Define the physical table layout using `StripSegment` and `TablePosition`.
2.  Assign `Pattern` objects to individual `Pixel` instances.
3.  Iterate through the pixels to update their state and render them to the physical strip.
