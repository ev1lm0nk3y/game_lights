import json
import os
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from .models import CalculatedSegment, Layout, SegmentDefinition, Table, TableSide
from .strip import StripSegment
from .table import TablePosition

CONFIG_FILE = "config.json"

class ConfigManager:
    def __init__(self, filename: str = CONFIG_FILE):
        self.filename = filename
        self.data = self._load_raw()

    def _load_raw(self) -> Dict[str, Any]:
        if not os.path.exists(self.filename):
            return {}
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)
        print(f"Configuration saved to {self.filename}")

    # --- Table Management ---
    def get_tables(self) -> Dict[str, Table]:
        tables = {}
        raw_tables = self.data.get("tables", {})
        for name, data in raw_tables.items():
            t = Table(
                name=name,
                width_meters=data["width"],
                length_meters=data["length"],
                pixels_per_meter=data["ppm"]
            )
            for s_data in data.get("sides", []):
                t.sides.append(TableSide(
                    name=s_data["name"],
                    length_meters=s_data["length"],
                    order=s_data["order"]
                ))
            t.recalculate_geometry()
            tables[name] = t
        return tables

    def save_table(self, table: Table):
        if "tables" not in self.data:
            self.data["tables"] = {}

        sides_data = []
        for s in table.sides:
            sides_data.append({
                "name": s.name,
                "length": s.length_meters,
                "order": s.order
            })

        self.data["tables"][table.name] = {
            "width": table.width_meters,
            "length": table.length_meters,
            "ppm": table.pixels_per_meter,
            "sides": sides_data
        }
        self.save()

    # --- Layout Management ---
    def get_layout(self, layout_name: str) -> Optional[Layout]:
        raw_layouts = self.data.get("layouts", {})
        if layout_name not in raw_layouts:
            return None

        l_data = raw_layouts[layout_name]
        layout = Layout(name=layout_name, table_name=l_data["table"])

        for seg_data in l_data.get("segments", []):
            layout.segments.append(SegmentDefinition(
                name=seg_data["name"],
                side_name=seg_data["side"],
                width_pixels=seg_data["width"],
                strategy=seg_data["strategy"],
                order_index=seg_data.get("order", 0),
                offset_pixels=seg_data.get("offset", 0)
            ))
        return layout

    def save_layout(self, layout: Layout):
        if "layouts" not in self.data:
            self.data["layouts"] = {}

        segs_data = []
        for s in layout.segments:
            segs_data.append({
                "name": s.name,
                "side": s.side_name,
                "width": s.width_pixels,
                "strategy": s.strategy,
                "order": s.order_index,
                "offset": s.offset_pixels
            })

        self.data["layouts"][layout.name] = {
            "table": layout.table_name,
            "segments": segs_data
        }
        self.save()

    def set_active(self, table_name: str, layout_name: str):
        self.data["active_table"] = table_name
        self.data["active_layout"] = layout_name
        self.save()

    def get_active_configuration(self) -> Optional[List[CalculatedSegment]]:
        t_name = self.data.get("active_table")
        l_name = self.data.get("active_layout")

        if not t_name or not l_name:
            return None

        tables = self.get_tables()
        if t_name not in tables:
            return None

        layout = self.get_layout(l_name)
        if not layout:
            return None

        return layout.calculate_segments(tables[t_name])

# Legacy support wrapper
def load_config(filename: str = CONFIG_FILE) -> List[StripSegment]:
    # This is kept for the old 'program' mode or simple manual edits
    # But ideally we migrate away from this.
    cm = ConfigManager(filename)
    calc_segs = cm.get_active_configuration()

    # If new config exists, return it converted to StripSegments
    if calc_segs:
        segments = []
        for cs in calc_segs:
            # Map side name to TablePosition if possible, or use a generic one
            # The old system relied heavily on TablePosition enum
            try:
                # Try exact match or upper case match
                pos = TablePosition[cs.side_name.upper()]
            except KeyError:
                pos = TablePosition.NO_SEAT # Fallback

            segments.append(StripSegment(cs.start_led, cs.end_led, pos))
        return segments

    # Fallback to loading the raw "layout" list if new config structure is missing
    return _legacy_load(filename)

def _legacy_load(filename):
    if not os.path.exists(filename): return []
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict): return [] # Should have been handled by new config
            # If it's a list, it's the very old format
            layout_list = data
            segments = []
            for item in layout_list:
                pos_name = item.get('position') or item.get('table_position')
                start = item.get('start')
                end = item.get('end')
                if pos_name:
                    segments.append(StripSegment(int(start), int(end), TablePosition[pos_name]))
            return segments
    except:
        return []

def save_config(segments: List[StripSegment], filename: str = CONFIG_FILE):
    # Backward compatibility for 'program' mode
    # This overwrites the file in the legacy way!
    # We should probably warn or update 'program' mode.
    layout_data = []
    for segment in segments:
        layout_data.append({
            "start": segment.begin_led,
            "end": segment.end_led,
            "position": segment.table_position.name
        })

    with open(filename, 'w') as f:
        json.dump({"layout": layout_data}, f, indent=4)
