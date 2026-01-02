from led.config import ConfigManager
from led.models import Layout, SegmentDefinition, Table, TableSide


def input_float(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")

def input_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a valid integer.")

def create_table_wizard():
    print("\n--- Create New Table ---")
    name = input("Table Name (e.g., 'primary'): ").strip()
    if not name: return

    width = input_float("Width (meters): ")
    length = input_float("Length (meters): ")
    ppm = input_int("Pixels per Meter (e.g., 30, 60): ")

    table = Table(name, width, length, ppm)

    print("\nDefine Sides (Order matters! Start from where the strip connects)")

    # Suggested default sides?
    print("Standard rectangular table has 4 sides.")

    while True:
        side_name = input(f"Side {len(table.sides) + 1} Name (or 'done'): ").strip()
        if side_name.lower() == 'done':
            break

        # Auto-suggest length based on count?
        # 0->width, 1->length, 2->width, 3->length
        suggested_len = 0.0
        if len(table.sides) % 2 == 0:
            suggested_len = width
        else:
            suggested_len = length

        s_len_in = input(f"Side Length [default: {suggested_len}]: ").strip()
        s_len = float(s_len_in) if s_len_in else suggested_len

        table.sides.append(TableSide(side_name, s_len, len(table.sides)))

    cm = ConfigManager()
    cm.save_table(table)
    print(f"Table '{name}' saved.")

def create_layout_wizard():
    print("\n--- Create New Layout ---")
    cm = ConfigManager()
    tables = cm.get_tables()
    if not tables:
        print("No tables defined. Create a table first.")
        return

    print("Available Tables:")
    for t_name in tables:
        print(f"- {t_name}")

    t_name = input("Select Table: ").strip()
    if t_name not in tables:
        print("Invalid table.")
        return

    table = tables[t_name]
    l_name = input("Layout Name (e.g., '6_player'): ").strip()
    layout = Layout(l_name, t_name)

    while True:
        print(f"\nCurrent Segments: {len(layout.segments)}")
        print("Sides:", ", ".join(s.name for s in table.sides))

        cmd = input("Action (add/done): ").lower().strip()
        if cmd == 'done':
            break

        if cmd == 'add':
            seg_name = input("Segment Name: ").strip()
            side = input("Side Name: ").strip()

            if not table.get_side(side):
                print(f"Side '{side}' does not exist on table '{t_name}'.")
                continue

            width = input_int("Width (pixels): ")

            print("Strategies: center, even, absolute")
            strat = input("Position Strategy [center]: ").strip().lower() or "center"

            order = 0
            offset = 0
            match strat:
                case "even":
                    order = input_int("Order index (0=first, 1=second...): ")
                case "absolute":
                    offset = input_int("Offset from start of side (pixels): ")

            layout.segments.append(SegmentDefinition(
                seg_name, side, width, strat, order, offset
            ))
            print(f"Added {seg_name}.")

    cm.save_layout(layout)
    print(f"Layout '{l_name}' saved.")

    activate = input("Set as active layout? (y/n): ").lower()
    if activate == 'y':
        cm.set_active(t_name, l_name)
        print("Active configuration updated.")

def list_config():
    cm = ConfigManager()
    print("\n=== Current Configuration ===")
    print(f"Active Table: {cm.data.get('active_table')}")
    print(f"Active Layout: {cm.data.get('active_layout')}")

    print("\nTables:")
    for t in cm.get_tables().values():
        print(f"  {t.name}: {t.width_meters}m x {t.length_meters}m ({t.pixels_per_meter} ppm)")
        print(f"    Sides: {', '.join([s.name for s in t.sides])}")

    print("\nLayouts:")
    raw_layouts = cm.data.get("layouts", {})
    for l_name, l_data in raw_layouts.items():
        print(f"  {l_name} (for {l_data['table']}): {len(l_data['segments'])} segments")
