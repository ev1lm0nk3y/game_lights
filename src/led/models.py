from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional


@dataclass
class TableSide:
    name: str
    length_meters: float
    order: int  # 0, 1, 2, 3... defining the sequence around the table

    # These will be calculated
    start_pixel_index: int = 0
    end_pixel_index: int = 0
    total_pixels: int = 0

@dataclass
class SegmentDefinition:
    name: str
    side_name: str
    width_pixels: int
    # positioning: "center", "even", "absolute" (start_offset)
    strategy: Literal["center", "even", "absolute"] = "center"
    order_index: int = 0 # For "even" distribution relative order
    offset_pixels: int = 0 # For "absolute" strategy

@dataclass
class CalculatedSegment:
    name: str
    start_led: int
    end_led: int
    side_name: str

@dataclass
class Layout:
    name: str
    table_name: str
    segments: List[SegmentDefinition] = field(default_factory=list)

    def calculate_segments(self, table: 'Table') -> List[CalculatedSegment]:
        calculated = []

        # Group segments by side
        by_side: Dict[str, List[SegmentDefinition]] = {}
        for s in self.segments:
            if s.side_name not in by_side:
                by_side[s.side_name] = []
            by_side[s.side_name].append(s)

        for side_name, seg_defs in by_side.items():
            side = table.get_side(side_name)
            if not side:
                continue

            side_len = side.total_pixels
            side_start = side.start_pixel_index

            # Sort by order_index
            seg_defs.sort(key=lambda x: x.order_index)

            if not seg_defs:
                continue

            # Check strategies
            # Simplified logic: Assumes all segments on a side use compatible strategies
            # or processes them individually if absolute.

            # Handle "even" spacing
            even_segs = [s for s in seg_defs if s.strategy == "even"]
            if even_segs:
                count = len(even_segs)
                total_seg_width = sum(s.width_pixels for s in even_segs)
                available_space = side_len - total_seg_width
                if available_space < 0:
                    print(f"Warning: Segments on {side_name} are too wide for the side.")
                    available_space = 0

                # Gap calculation
                # gap | seg | gap | seg | gap
                gap = available_space // (count + 1)

                current_offset = gap
                for seg in even_segs:
                    start = side_start + current_offset
                    end = start + seg.width_pixels - 1 # inclusive
                    calculated.append(CalculatedSegment(seg.name, start, end, side_name))
                    current_offset += seg.width_pixels + gap

            # Handle "center"
            center_segs = [s for s in seg_defs if s.strategy == "center"]
            for seg in center_segs:
                # Center single item for now
                mid_point = side_len // 2
                half_width = seg.width_pixels // 2
                start = side_start + (mid_point - half_width)
                end = start + seg.width_pixels - 1
                calculated.append(CalculatedSegment(seg.name, start, end, side_name))

            # Handle "absolute"
            abs_segs = [s for s in seg_defs if s.strategy == "absolute"]
            for seg in abs_segs:
                start = side_start + seg.offset_pixels
                end = start + seg.width_pixels - 1
                calculated.append(CalculatedSegment(seg.name, start, end, side_name))

        return calculated

@dataclass
class Table:
    name: str
    width_meters: float
    length_meters: float
    pixels_per_meter: int
    sides: List[TableSide] = field(default_factory=list)

    def __post_init__(self):
        # Sort sides by order if provided
        self.sides.sort(key=lambda x: x.order)
        self.recalculate_geometry()

    def get_side(self, name: str) -> Optional[TableSide]:
        for s in self.sides:
            if s.name == name:
                return s
        return None

    def recalculate_geometry(self):
        current_pixel = 0
        for side in self.sides:
            side.start_pixel_index = current_pixel
            # Rounding to nearest pixel
            px_count = int(side.length_meters * self.pixels_per_meter)
            side.total_pixels = px_count
            side.end_pixel_index = current_pixel + px_count - 1
            current_pixel += px_count

    @property
    def total_pixels(self) -> int:
        return sum(s.total_pixels for s in self.sides)
