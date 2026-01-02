
import time
from dataclasses import dataclass, field
from typing import List

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import NumberValidator

from led.config import ConfigManager
from led.controller import ANIMATION_MAP, COLOR_MAP, Controller


@dataclass
class Action:
    type: str  # "animation", "color"
    target: str  # segment name or "ALL" or "Range: x-y"
    details: dict = field(default_factory=dict)

    def __str__(self):
        if self.type == "animation":
            return f"Animation: {self.details['animation']} on {self.target}"
        elif self.type == "color":
            return f"Color: {self.details['color_name']} on {self.target}"
        return "Unknown Action"


class LiveControlWizard:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.cm = ConfigManager(config_path)
        self.controller: Controller
        self.pending_actions: List[Action] = []

    def setup_controller(self) -> bool:
        # 1. Select Table/Layout if needed
        tables = self.cm.get_tables()
        if not tables:
            print("No tables defined. Please run setup.")
            return False

        # If multiple tables, select one
        t_name = self.cm.data.get("active_table")
        if len(tables) > 1 or not t_name:
            t_name = inquirer.select(
                message="Select Table:", choices=list(tables.keys()), default=t_name
            ).execute()

        # Select Layout
        # We need to find layouts for this table
        layouts = self.cm.data.get("layouts", {})
        table_layouts = [l for l, d in layouts.items() if d["table"] == t_name]

        if not table_layouts:
            print(f"No layouts found for table {t_name}.")
            return False

        l_name = self.cm.data.get("active_layout")
        if len(table_layouts) > 1 or not l_name or l_name not in table_layouts:
            l_name = inquirer.select(
                message="Select Layout:", choices=table_layouts, default=l_name
            ).execute()

        # Activate and Save
        self.cm.set_active(t_name, l_name)

        # Initialize Controller
        print(f"Initializing controller with {t_name} / {l_name}...")
        self.controller = Controller(self.config_path)
        return True

    def run(self):
        if not self.setup_controller():
            return

        # Start animation loop in background
        self.controller.start_animation_thread()

        print("Controller running. Enter menu to queue commands.")

        try:
            while True:
                # Main Menu
                menu_choices = [
                    Choice("Apply Animation", "Apply Animation/Pattern"),
                    Choice("Set Color", "Set Color to Pixels"),
                    Choice("Execute", f"Execute Pending ({len(self.pending_actions)})"),
                    Choice("Clear Pending", "Clear Pending Actions"),
                    Choice("Reset Strip", "Reset/Clear Strip"),
                    Choice("Exit", "Exit"),
                ]

                choice = inquirer.select(
                    message="Live Control:", choices=menu_choices
                ).execute()

                match choice:
                    case "Apply Animation":
                        self.add_animation_action()
                    case "Set Color":
                        self.add_color_action()
                    case "Execute":
                        self.execute_pending()
                    case "Clear Pending":
                        self.pending_actions.clear()
                        print("Pending actions cleared.")
                    case "Reset Strip":
                        self.controller.clear_segment("ALL")
                        print("Strip cleared.")
                    case "Exit":
                        self.controller.running = False
                        break

        except KeyboardInterrupt:
            self.controller.running = False
        except Exception as e:
            print(f"Error: {e}")
            self.controller.running = False
        finally:
            # wait a bit for thread to clean up if needed
            time.sleep(0.5)

    def add_animation_action(self):
        # Select Segment
        segments = list(self.controller.segments.keys())
        segments.insert(0, "ALL")

        target = inquirer.select(message="Target Segment:", choices=segments).execute()

        # Select Animation
        anim = inquirer.select(
            message="Animation:", choices=list(ANIMATION_MAP.keys())
        ).execute()

        # (Optional) We could prompt for colors/params here
        # For now, just defaults or a simple color picker if the animation supports it?
        # Many animations take 'color' or 'colors'.

        self.pending_actions.append(
            Action(type="animation", target=target, details={"animation": anim})
        )
        print(f"Queued: {anim} on {target}")

    def add_color_action(self):
        # Select Mode: Segment or Range
        mode = inquirer.select(
            message="Target Type:", choices=["Segment", "Manual Range"]
        ).execute()

        target = ""
        details = {}

        if mode == "Segment":
            segments = list(self.controller.segments.keys())
            target = inquirer.select(
                message="Target Segment:", choices=segments
            ).execute()
            # We treat this as applying a "Solid" animation effectively,
            # or we could use a specific set_color method.
            # But the requirement says "Select Color to Pixels".
            # If we select a segment, we know the pixels.
            details["mode"] = "segment"

        else:
            # Manual Range
            start = inquirer.number(
                message="Start Pixel:",
                min_allowed=0,
                max_allowed=self.controller.LED_COUNT - 1,
                validate=NumberValidator(),
            ).execute()

            end = inquirer.number(
                message="End Pixel:",
                min_allowed=int(start),
                max_allowed=self.controller.LED_COUNT - 1,
                validate=NumberValidator(),
            ).execute()

            target = f"Range: {start}-{end}"
            details["mode"] = "range"
            details["start"] = int(start)
            details["end"] = int(end)

        # Select Color
        color_name = inquirer.select(
            message="Color:", choices=list(COLOR_MAP.keys())
        ).execute()

        details["color_name"] = color_name
        details["color_val"] = COLOR_MAP[color_name]

        self.pending_actions.append(
            Action(type="color", target=target, details=details)
        )
        print(f"Queued: Color {color_name} on {target}")

    def execute_pending(self):
        if not self.pending_actions:
            print("Nothing to execute.")
            return

        print(f"Executing {len(self.pending_actions)} actions...")
        for action in self.pending_actions:
            if action.type == "animation":
                # Reuse the controller's apply_animation logic
                # We might need to handle "ALL"
                if action.target == "ALL":
                    for seg_name in self.controller.segments:
                        self.controller.apply_animation(
                            seg_name, action.details["animation"]
                        )
                else:
                    self.controller.apply_animation(
                        action.target, action.details["animation"]
                    )

            elif action.type == "color":
                color_val = action.details["color_val"]
                if action.details["mode"] == "segment":
                    # Use Solid animation which is now available
                    self.controller.apply_animation(
                        action.target, "Solid", {"color": color_val}
                    )
                elif action.details["mode"] == "range":
                    self.controller.set_color_range(
                        action.details["start"], action.details["end"], color_val
                    )

        self.pending_actions.clear()
