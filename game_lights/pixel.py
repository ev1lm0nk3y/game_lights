"""Control one LED"""

from dataclasses import dataclass, field
from rpi_ws281x import PixelStrip, Color, RGBW

from patterns import Pattern

@dataclass
class Pixel:
    strip: PixelStrip
    idx: int
    _current: int = field(init=False, repr=False, default=0)
    _steps: list[RGBW] = field(init=False, repr=False, default=[])
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
            print('cannot add pattern while active')
            return
        self._steps += pattern.generate(self._current, 
                                        kwargs.get('num_loops', 1))
        
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
        return f'LED {self.idx}: RGBW({r}, {g}, {b}, {w})'
