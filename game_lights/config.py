import json
import os
from typing import List
from .strip import StripSegment
from .table import TablePosition

CONFIG_FILE = "config.json"

def save_config(segments: List[StripSegment], filename: str = CONFIG_FILE):
    # Load existing data to preserve other fields like "key_bindings"
    existing_data = {}
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            pass

    layout_data = []
    for segment in segments:
        layout_data.append({
            "start": segment.begin_led,
            "end": segment.end_led,
            "position": segment.table_position.name
        })
    
    existing_data["layout"] = layout_data
    
    with open(filename, 'w') as f:
        json.dump(existing_data, f, indent=4)
    print(f"Configuration saved to {filename}")

def load_config(filename: str = CONFIG_FILE) -> List[StripSegment]:
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return []
    
    # Handle both list (legacy/simple) and dict (rich) structures
    layout_list = []
    if isinstance(data, list):
        layout_list = data
    elif isinstance(data, dict):
        layout_list = data.get("layout", [])
    
    segments = []
    for item in layout_list:
        try:
            # support both naming conventions during transition if needed, 
            # but prefer existing file's "position", "start", "end"
            pos_name = item.get('position') or item.get('table_position')
            start = item.get('start') if 'start' in item else item.get('begin_led')
            end = item.get('end') if 'end' in item else item.get('end_led')
            
            if pos_name and start is not None and end is not None:
                position = TablePosition[pos_name]
                segment = StripSegment(
                    begin_led=int(start),
                    end_led=int(end),
                    table_position=position
                )
                segments.append(segment)
        except (KeyError, ValueError) as e:
            print(f"Error loading segment {item}: {e}")
            continue
            
    return segments
