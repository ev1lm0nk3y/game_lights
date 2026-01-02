import json
import select
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Handle hardware dependency for local dev
try:
    from rpi_ws281x import Color, PixelStrip
except ImportError:
    print("Warning: rpi_ws281x not found. Using Mock objects.")
    class PixelStrip:
        def __init__(self, num, pin, freq_hz=800000, dma=10, invert=False, brightness=255, channel=0):
            self.num = num
        def begin(self): pass
        def show(self): pass
        def setPixelColor(self, n, color): pass
        def getPixelColorRGBW(self, n): return (0,0,0,0)

    def Color(r, g, b, w=0):
        return (w << 24) | (r << 16) | (g << 8) | b

from .animations import Animation, Blink, Chase, FadeInOut, Flare, Rainbow
from .pixel import Colors, Pixel
from .strip import StripSegment
from .table import TablePosition

# Map string names to classes/enums
ANIMATION_MAP = {
    "Chase": Chase,
    "FadeInOut": FadeInOut,
    "Flare": Flare,
    "Blink": Blink,
    "Rainbow": Rainbow
}

COLOR_MAP = {
    "RED": Colors.RED,
    "ORANGE": Colors.ORANGE,
    "YELLOW": Colors.YELLOW,
    "GREEN": Colors.GREEN,
    "BLUE": Colors.BLUE,
    "INDIGO": Colors.INDIGO,
    "VIOLET": Colors.VIOLET,
    "PURPLE": Colors.PURPLE,
    "CYAN": Colors.CYAN,
    "MAGENTA": Colors.MAGENTA,
    "WHITE": Colors.WHITE,
    "BLACK": Colors.BLACK,
    "GOLD": Colors.GOLD,
    "PINK": Colors.PINK,
    "TEAL": Colors.TEAL,
    "LIME": Colors.LIME
}

class Controller:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # LED Strip Configuration (Defaults, could be in config)
        self.LED_COUNT = 300      # Number of LED pixels.
        self.LED_PIN = 18      # GPIO pin connected to the pixels (18 uses PWM!).
        self.LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
        self.LED_DMA = 10      # DMA channel to use for generating signal (try 10)
        self.LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
        self.LED_INVERT = False   # True to invert the signal (when using NPN transistor level shift)
        self.LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

        self.strip = PixelStrip(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ,
                                self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL)
        self.strip.begin()

        self.segments: Dict[str, StripSegment] = {}
        self.queues: Dict[str, List[Animation]] = {} # Target -> List of queued animations
        self.running = True

        self._setup_segments()

    def _setup_segments(self):
        """Initialize segments from config."""
        for item in self.config['layout']:
            pos_name = item['position']
            start = item['start']
            end = item['end']

            # Map string to Enum
            try:
                table_pos = TablePosition[pos_name]
            except KeyError:
                print(f"Unknown TablePosition: {pos_name}")
                continue

            segment = StripSegment(start, end, table_pos)

            # Initialize Pixels for this segment
            for i in range(start, end + 1):
                p = Pixel(self.strip, i)
                segment.pixels.append(p)

            self.segments[pos_name] = segment
            self.queues[pos_name] = []

    def _parse_params(self, params: dict):
        """Convert string color names to int values in params."""
        parsed = {}
        for k, v in params.items():
            if k == "color" or k.startswith("color"):
                if v in COLOR_MAP:
                    parsed[k] = COLOR_MAP[v]
                else:
                    parsed[k] = v # Assume raw int or handled elsewhere
            else:
                parsed[k] = v
        return parsed

    def handle_command(self, key: str):
        """Execute command based on key binding."""
        if key not in self.config['key_bindings']:
            return

        cmd = self.config['key_bindings'][key]
        action = cmd.get('action')
        target_name = cmd.get('target')

        if action == "quit":
            self.running = False
            return

        if action == "clear":
            if target_name == "ALL":
                for seg in self.segments.values():
                    seg.clear()
            elif target_name in self.segments:
                self.segments[target_name].clear()
            return

        if action == "trigger_all":
            # Trigger the next queued item for all segments
            for name, queue in self.queues.items():
                if queue:
                    anim = queue.pop(0)
                    if name in self.segments:
                        print(f"Triggering {type(anim).__name__} on {name}")
                        anim.apply(self.segments[name].pixels)
            return

        if action == "trigger":
            if target_name in self.queues and self.queues[target_name]:
                 anim = self.queues[target_name].pop(0)
                 if target_name in self.segments:
                     print(f"Triggering {type(anim).__name__} on {target_name}")
                     anim.apply(self.segments[target_name].pixels)
            return

        if action in ["queue", "immediate"]:
            anim_name = cmd.get('animation')
            params = self._parse_params(cmd.get('params', {}))

            if anim_name not in ANIMATION_MAP:
                print(f"Unknown animation: {anim_name}")
                return

            anim_class = ANIMATION_MAP[anim_name]
            animation = anim_class(**params)

            if action == "immediate":
                if target_name in self.segments:
                    print(f"Applying {anim_name} immediately to {target_name}")
                    animation.apply(self.segments[target_name].pixels)

            elif action == "queue":
                if target_name in self.queues:
                    print(f"Queueing {anim_name} for {target_name}")
                    self.queues[target_name].append(animation)

    def input_loop(self):
        """Listen for keyboard input."""
        print("Starting Input Loop. Press keys defined in config. 'q' to quit.")
        # Simple non-blocking input for demo/dev (requires 'enter' in standard terminal)
        # For true single-keystroke in terminal, we'd need tty/termios magic
        # But this suffices for 'commands'

        while self.running:
            # Check for input without blocking indefinitely
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                line = sys.stdin.readline()
                if line:
                    key = line.strip()
                    self.handle_command(key)
            time.sleep(0.1)

    def animation_loop(self):
        """Main loop to update LEDs."""
        print("Starting Animation Loop.")
        while self.running:
            # Update all segments
            for segment in self.segments.values():
                segment.animate()

            # Push updates to physical strip
            self.strip.show()

            # Control framerate (e.g., 50ms = 20fps)
            time.sleep(0.05)

    def run(self):
        # Start input listener in separate thread so animation doesn't block
        input_thread = threading.Thread(target=self.input_loop)
        input_thread.daemon = True
        input_thread.start()

        try:
            self.animation_loop()
        except KeyboardInterrupt:
            self.running = False

        print("Exiting...")
        # Cleanup
        for seg in self.segments.values():
            seg.clear()
        self.strip.show()

if __name__ == "__main__":
    c = Controller("config.json")
    c.run()
