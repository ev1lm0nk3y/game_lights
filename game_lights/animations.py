from dataclasses import dataclass, field
from rpi_ws281x import Color, PixelStrip

from .strip import StripSegment

@dataclass
class AnimationFrame:
  strip: StripSegment = field(default_factory=StripSegment)
  
