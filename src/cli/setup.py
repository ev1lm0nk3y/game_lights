from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator, NumberValidator

from led.config import ConfigManager
from led.models import Layout, SegmentDefinition, Table, TableSide


def create_table_wizard():
    print("\n--- Create New Table ---")
    name = inquirer.text(
        message="Table Name:", default="primary", validate=EmptyInputValidator()
    ).execute()

    width = inquirer.number(
        message="Width (meters):",
        float_allowed=True,
        validate=NumberValidator(float_allowed=True),
    ).execute()

    length = inquirer.number(
        message="Length (meters):",
        float_allowed=True,
        validate=NumberValidator(float_allowed=True),
    ).execute()

    ppm = inquirer.number(
        message="Pixels per Meter:",
        float_allowed=False,
        default=60,
        validate=NumberValidator(float_allowed=False),
    ).execute()

    table = Table(name, float(width), float(length), int(ppm))

    print("\nDefine Sides (Order matters! Start from where the strip connects)")

    while True:
        # Suggest length
        suggested_len = 0.0
        if len(table.sides) % 2 == 0:
            suggested_len = width
        else:
            suggested_len = length

        add_side = inquirer.confirm(
            message=f"Add side {len(table.sides) + 1}?", default=True
        ).execute()

        if not add_side:
            if len(table.sides) < 3:
                if not inquirer.confirm(
                    "Table has fewer than 3 sides. Are you sure you are done?",
                    default=False,
                ).execute():
                    continue
            break

        side_name = inquirer.text(
            message="Side Name:", validate=EmptyInputValidator()
        ).execute()

        s_len = inquirer.number(
            message=f"Side Length (meters):",
            default=float(suggested_len),
            float_allowed=True,
            validate=NumberValidator(float_allowed=True),
        ).execute()

        table.sides.append(TableSide(side_name, float(s_len), len(table.sides)))

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

    t_name = inquirer.select(
        message="Select Table:", choices=list(tables.keys())
    ).execute()

    table = tables[t_name]

    l_name = inquirer.text(
        message="Layout Name:", default="6_player", validate=EmptyInputValidator()
    ).execute()

    layout = Layout(l_name, t_name)

    while True:
        action = inquirer.select(
            message="Layout Action:", choices=["Add Segment", "Finish"]
        ).execute()

        if action == "Finish":
            break

        seg_name = inquirer.text(
            message="Segment Name:", validate=EmptyInputValidator()
        ).execute()

        side_choices = [s.name for s in table.sides]
        side = inquirer.select(message="Side Name:", choices=side_choices).execute()

        width = inquirer.number(
            message="Width (pixels):",
            validate=NumberValidator(),
        ).execute()

        strat = inquirer.select(
            message="Position Strategy:",
            choices=["center", "even", "absolute"],
            default="center",
        ).execute()

        order = 0
        offset = 0

        match strat:
            case "even":
                order = inquirer.number(
                    message="Order index (0=first, ...):", default=0
                ).execute()
            case "absolute":
                offset = inquirer.number(
                    message="Offset from start (pixels):", default=0
                ).execute()

        layout.segments.append(
            SegmentDefinition(
                seg_name, side, int(width), strat, int(order), int(offset)
            )
        )
        print(f"Added {seg_name}.")

    cm.save_layout(layout)
    print(f"Layout '{l_name}' saved.")

    if inquirer.confirm("Set as active layout?", default=True).execute():
        cm.set_active(t_name, l_name)
        print("Active configuration updated.")


def list_config():
    cm = ConfigManager()
    print("\n=== Current Configuration ===")
    print(f"Active Table: {cm.data.get('active_table')}")
    print(f"Active Layout: {cm.data.get('active_layout')}")

    print("\nTables:")
    for t in cm.get_tables().values():
        print(
            f"  {t.name}: {t.width_meters}m x {t.length_meters}m ({t.pixels_per_meter} ppm)"
        )
        print(f"    Sides: {', '.join([s.name for s in t.sides])}")

    print("\nLayouts:")
    raw_layouts = cm.data.get("layouts", {})
    for l_name, l_data in raw_layouts.items():
        print(f"  {l_name} (for {l_data['table']}): {len(l_data['segments'])} segments")
