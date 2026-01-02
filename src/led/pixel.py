"""Control one LED"""

from dataclasses import dataclass, field

try:
    from rpi_ws281x import RGBW, Color, PixelStrip
except ImportError:

    def RGBW(r=0, g=0, b=0, w=0):
        return (r << 16) | (g << 8) | b | (w << 24)

    def Color(r=0, g=0, b=0, w=0):
        return (r << 16) | (g << 8) | b | (w << 24)

    class PixelStrip:
        def __init__(self, *args, **kwargs):
            pass

        def getPixelColor(self, idx):
            return 0, 0, 0

        def getPixelColorRGBW(self, idx):
            return 0, 0, 0, 0

        def setPixelColor(self, idx, color):
            pass

        def show(self):
            pass

        def numPixels(self):
            return 0


from .patterns import Pattern


@dataclass
class Colors:
    RED: int = Color(255, 0, 0)
    ORANGE: int = Color(255, 165, 0)
    YELLOW: int = Color(255, 255, 0)
    GREEN: int = Color(0, 255, 0)
    BLUE: int = Color(0, 0, 255)
    INDIGO: int = Color(75, 0, 130)
    VIOLET: int = Color(238, 130, 238)
    PURPLE: int = Color(128, 0, 128)
    CYAN: int = Color(0, 255, 255)
    MAGENTA: int = Color(255, 0, 255)
    WHITE: int = Color(255, 255, 255)
    BLACK: int = Color(0, 0, 0)
    GOLD: int = Color(255, 215, 0)
    PINK: int = Color(255, 192, 203)
    TEAL: int = Color(0, 128, 128)
    LIME: int = Color(50, 205, 50)


@dataclass
class Pixel:
    strip: PixelStrip
    idx: int
    _current: int = field(init=False, repr=False, default=0)
    _steps: list[int] = field(init=False, repr=False, default_factory=list)
    _step_num: int = field(init=False, repr=False, default=0)
    _active: bool = field(init=False, repr=False, default=False)

    def __post_init__(self):
        self.reset()

    def add_pattern(self, pattern: Pattern, **kwargs):
        """Add the steps of a Pattern to the LED

        Args:
            pattern: A defined Pattern to use on the LED
            kwargs:
                loop_count: how many times to loop the pattern, default 1
        """
        if self._active:
            print("cannot add pattern while active")
            return
        self._steps += pattern.generate(self._current, kwargs.get("num_loops", 1))

    def reset(self):
        self._active = False
        self._steps = []
        self._step_num = 0
        self.strip.setPixelColor(self.idx, 0)

    def start(self):
        self._active = True
        self._step_num = 0

    def stop(self):
        self._active = False

    def __iter__(self):
        self.start()
        return self

    def __next__(self):
        if self._step_num >= len(self._steps):
            self.stop()
            self._step_num = 0
            raise StopIteration
        if self._active:
            self._current = self._steps[self._step_num]
            self._step_num += 1
        return self._current

    def __str__(self) -> str:
        r, g, b, w = self.strip.getPixelColorRGBW(self.idx)
        return f"LED {self.idx}: RGBW({r}, {g}, {b}, {w})"
