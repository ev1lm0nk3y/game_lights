import math
from dataclasses import dataclass, field
from typing import List

from .patterns import Blink as BlinkPattern
from .patterns import Fade, Pattern, Solid
from .patterns import Rainbow as RainbowPattern
from .pixel import Colors, Pixel
from .strip import StripSegment

try:
    from rpi_ws281x import Color
except ImportError:

    def Color(r=0, g=0, b=0, w=0):
        return (r << 16) | (g << 8) | b | (w << 24)


@dataclass
class Animation:
    """Base class for Strip Animations."""

    def apply(self, pixels: List[Pixel]):
        """Apply the animation to the given pixels."""
        pass


@dataclass
class Chase(Animation):
    color: int = Colors.RED
    direction: int = 1  # 1 for forward, -1 for backward
    tail_length: int = 5
    speed_delay: int = 2  # Frames between steps

    def apply(self, pixels: List[Pixel]):
        n = len(pixels)
        for i, pixel in enumerate(pixels):
            # Calculate start delay based on position
            if self.direction == 1:
                delay = i * self.speed_delay
            else:
                delay = (n - 1 - i) * self.speed_delay

            # Initial delay
            if delay > 0:
                pixel.add_pattern(Solid(0, duration_frames=delay))

            # The "Head" (fade in quickly)
            pixel.add_pattern(Fade(self.color, duration_frames=2))

            # The "Tail" (fade out)
            pixel.add_pattern(
                Fade(0, duration_frames=self.tail_length * self.speed_delay)
            )


@dataclass
class FadeInOut(Animation):
    color: int = Colors.BLUE
    duration: int = 30  # Frames for full fade in

    def apply(self, pixels: List[Pixel]):
        for pixel in pixels:
            # Fade In
            pixel.add_pattern(Fade(self.color, duration_frames=self.duration))
            # Fade Out
            pixel.add_pattern(Fade(0, duration_frames=self.duration))


@dataclass
class Flare(Animation):
    """
    Flare from center to edges.
    Starts with color1, transitions to color2 spreading from center.
    """

    color1: int = Colors.RED
    color2: int = Colors.YELLOW
    speed_delay: int = 2
    transition_duration: int = 10

    def apply(self, pixels: List[Pixel]):
        n = len(pixels)
        center = n // 2

        for i, pixel in enumerate(pixels):
            dist = abs(i - center)
            delay = dist * self.speed_delay

            # Start with Color 1 (assuming currently 0 or we set it)
            # If we assume the strip is already Color 1, we just wait then fade.
            # If not, we set it to Color 1 first.
            pixel.add_pattern(
                Solid(self.color1, duration_frames=1)
            )  # Set initial state

            if delay > 0:
                pixel.add_pattern(Solid(self.color1, duration_frames=delay))

            # Transition to Color 2
            pixel.add_pattern(
                Fade(self.color2, duration_frames=self.transition_duration)
            )


@dataclass
class Blink(Animation):
    color: int = Colors.GREEN
    duration: int = 10

    def apply(self, pixels: List[Pixel]):
        for pixel in pixels:
            pixel.add_pattern(
                BlinkPattern(
                    self.color, off_duration=self.duration, on_duration=self.duration
                )
            )


@dataclass
class Rainbow(Animation):
    speed: int = 10

    def apply(self, pixels: List[Pixel]):
        # Apply Rainbow pattern to all.
        # Can optionally shift phase for a "moving" rainbow if RainbowPattern supported it.
        # Current RainbowPattern is a cycle over time.
        # To make it a "Rainbow transition across the entire strip", we might want
        # pixels to be out of phase.

        # Updating RainbowPattern in patterns.py to support phase would be better,
        # but for now we apply the temporal rainbow.
        for pixel in pixels:
            pixel.add_pattern(RainbowPattern(duration_frames=255))
