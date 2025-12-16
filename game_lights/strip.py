from dataclasses import dataclass, field
from enum import Enum
from rpi_ws281x import Color, PixelStrip

from .table import TablePosition

@dataclass
class StripSegment:
  begin_led:  int
  end_led: int
  table_position: TablePosition = field(default_factory=TablePosition.NO_SEAT)
