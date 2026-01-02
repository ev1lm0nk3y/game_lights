import argparse

from InquirerPy import inquirer

from cli import setup
from cli.live_control import LiveControlWizard
from led import config
from led.controller import Controller
from led.strip import StripSegment
from led.table import TablePosition


def program_mode():
    print("=== LED Strip Configuration Mode ===")
    segments = config.load_config()
    if segments:
        print(f"Loaded {len(segments)} existing segments.")
    else:
        print("No existing configuration found. Starting fresh.")

    while True:
        print("\n--- Add New Segment ---")
        try:
            start_led = int(input("Start LED ID: "))
            end_led = int(input("End LED ID: "))

            if start_led > end_led:
                print("Error: Start LED must be less than or equal to End LED.")
                continue

            print("\nAvailable Positions:")
            for pos in TablePosition:
                if pos != TablePosition.NO_SEAT:
                    print(f"{pos.value}: {pos.name}")

            pos_input = input("Enter Position Name or ID: ").upper()

            selected_pos = TablePosition.NO_SEAT
            try:
                # Try parsing as integer ID first
                pos_id = int(pos_input)
                selected_pos = TablePosition(pos_id)
            except ValueError:
                # Try parsing as name
                try:
                    selected_pos = TablePosition[pos_input]
                except KeyError:
                    print("Invalid position. Please try again.")
                    continue

            segment = StripSegment(begin_led=start_led, end_led=end_led, table_position=selected_pos)
            segments.append(segment)
            print(f"Segment added: {segment}")

            cont = input("Add another segment? (y/N): ").lower()
            if cont != 'y':
                break

        except ValueError:
            print("Invalid input. Please enter numbers for LEDs.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return

    save = input("\nSave configuration? (Y/n): ").lower()
    if save != 'n':
        config.save_config(segments)
    else:
        print("Configuration NOT saved.")

def setup_mode():
    while True:
        choice = inquirer.select(
            message="Setup Menu",
            choices=[
                "Create/Update Table",
                "Create/Update Layout",
                "List Configuration",
                "Legacy Program Mode",
                "Exit"
            ]
        ).execute()

        match choice:
            case "Create/Update Table":
                setup.create_table_wizard()
            case "Create/Update Layout":
                setup.create_layout_wizard()
            case "List Configuration":
                setup.list_config()
            case "Legacy Program Mode":
                program_mode()
            case "Exit":
                break

def main():
    parser = argparse.ArgumentParser(description="Game Lights Controller")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command
    _ = subparsers.add_parser("setup", help="Interactive setup for tables and layouts")

    # Program command (Legacy)
    _ = subparsers.add_parser("program", help="Legacy: Configure LED strip segments")

    # Run command
    _ = subparsers.add_parser("run", help="Run the light show")

    args = parser.parse_args()

    match args.command:
        case "setup":
            setup_mode()
        case "program":
            program_mode()
        case "run":
            wizard = LiveControlWizard("config.json")
            wizard.run()
        case _:
            parser.print_help()

if __name__ == "__main__":
    main()
