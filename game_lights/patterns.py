import math
from abc import ABC, abstractmethod
from dataclasses import dataclass

from rpi_ws281x import Color


def interpolate_color(start_color: int, end_color: int, step: int, total_steps: int) -> int:
    """Interpolate between two colors."""
    if total_steps <= 0:
        return end_color

    start_w = (start_color >> 24) & 0xFF
    start_r = (start_color >> 16) & 0xFF
    start_g = (start_color >> 8) & 0xFF
    start_b = start_color & 0xFF

    end_w = (end_color >> 24) & 0xFF
    end_r = (end_color >> 16) & 0xFF
    end_g = (end_color >> 8) & 0xFF
    end_b = end_color & 0xFF

    ratio = step / total_steps

    new_w = int(start_w + (end_w - start_w) * ratio)
    new_r = int(start_r + (end_r - start_r) * ratio)
    new_g = int(start_g + (end_g - start_g) * ratio)
    new_b = int(start_b + (end_b - start_b) * ratio)

    return (new_w << 24) | (new_r << 16) | (new_g << 8) | new_b

class Pattern(ABC):
    """Base class for LED patterns."""

    @abstractmethod
    def generate(self, current_color: int, num_loops: int = 1) -> list[int]:
        """Generate a sequence of color steps."""
        pass

@dataclass
class Solid(Pattern):
    color: int
    duration_frames: int = 1

    def generate(self, current_color: int, num_loops: int = 1) -> list[int]:
        steps = []
        for _ in range(num_loops):
            steps.extend([self.color] * self.duration_frames)
        return steps

@dataclass
class Fade(Pattern):
    target_color: int
    duration_frames: int

    def generate(self, current_color: int, num_loops: int = 1) -> list[int]:
        steps = []
        start = current_color
        for _ in range(num_loops):
            # If looping, subsequent loops start from the end of the previous
            # But Fade usually transitions A -> B.
            # If we loop, do we snap back?
            # For this implementation, let's assume each loop performs the fade A->B.
            # But A changes.
            # Actually, usually Fade is A->B.
            # If we loop, maybe we want A->B->A?
            # Or just A->B, A->B? (which looks like snap back)

            # Let's handle the single fade sequence.
            cycle_steps = []
            for i in range(1, self.duration_frames + 1):
                cycle_steps.append(interpolate_color(start, self.target_color, i, self.duration_frames))
            steps.extend(cycle_steps)
            start = self.target_color # Next loop starts from target

        return steps

@dataclass
class Blink(Pattern):
    color: int
    off_color: int = 0
    on_duration: int = 10
    off_duration: int = 10

    def generate(self, current_color: int, num_loops: int = 1) -> list[int]:
        steps = []
        for _ in range(num_loops):
            steps.extend([self.color] * self.on_duration)
            steps.extend([self.off_color] * self.off_duration)
        return steps

@dataclass
class Rainbow(Pattern):
    """Cycles through rainbow colors."""
    duration_frames: int = 255  # Frames to complete one full cycle

    def generate(self, current_color: int, num_loops: int = 1) -> list[int]:
        def wheel(pos):
            """Generate rainbow colors across 0-255 positions."""
            if pos < 85:
                return Color(pos * 3, 255 - pos * 3, 0)
            elif pos < 170:
                pos -= 85
                return Color(255 - pos * 3, 0, pos * 3)
            else:
                pos -= 170
                return Color(0, pos * 3, 255 - pos * 3)

        steps = []
        for _ in range(num_loops):
            for i in range(self.duration_frames):
                # Map i to 0-255
                hue = int((i / self.duration_frames) * 255)
                steps.append(wheel(hue))
        return steps
