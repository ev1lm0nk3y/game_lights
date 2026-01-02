from dataclasses import dataclass, field
from enum import Enum
import sys

try:
    from rpi_ws281x import Color, PixelStrip
except ImportError:
    # Mock for non-RPi environments
    class PixelStrip:
        pass

    def Color(r, g, b, w=0):
        return 0


from .table import TablePosition


@dataclass
class StripSegment:
    begin_led: int
    end_led: int
    table_position: TablePosition = field(default_factory=lambda: TablePosition.NO_SEAT)
    pixels: list = field(default_factory=list, repr=False)

    def animate(self):
        """Advance the state of all pixels in this segment."""
        for pixel in self.pixels:
            if pixel._active:
                try:
                    next(pixel)
                    pixel.strip.setPixelColor(pixel.idx, pixel._current)
                except StopIteration:
                    pass  # Pixel finished its pattern

    def clear(self):
        """Turn off all pixels in this segment."""
        for pixel in self.pixels:
            pixel.reset()
