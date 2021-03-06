from multiprocessing import Lock
from typing import Tuple
import pygame as py

from graphics.objects.sprite import Sprite


MUTEX = Lock()


class BaseWindow:

    QUIT = py.QUIT

    def __init__(self, window_size: Tuple[int, int], draw_area: Tuple[int, int] = None, frame_rate: int = 60, flags: int = 0) -> None:
        """This class structurizes a game and the corresponding GUI for 
        it. The main loop will block the main thread, so be sure to 
        specify all callbacks before.

        Args:
            window_size (Tuple[int, int]): The size of the window in pixels (width, height)
            draw_area (Tuple[int, int], optional): The area in which sprites are drawn. Defaults to None.
            frame_rate (int, optional): The framerate at which the scene is rendered. Defaults to 60.
            flags (int, optional): Flags like fullscreen or hardware acceleration. Defaults to 0.
        """
        py.init()
        py.font.init()

        # set the screen size and draw area
        self._width, self._height = self._window_size = window_size
        self._draw_area = draw_area
        if not self._draw_area:
            self._draw_area = self._window_size

        # define the screen on which all sprites are rendered
        self._flags = flags#py.FULLSCREEN | py.HWSURFACE | py.DOUBLEBUF# | py.SCALED 
        self._screen = py.display.set_mode(self._window_size, self._flags)
        self._font = py.font.SysFont("Times New Roman", 14)

        # define a clock to limit the frames per second
        self._clock = py.time.Clock()
        self._frame_rate = frame_rate

        # set up everything else
        self._running = False
        self._callbacks = dict()

        # sprite containers
        self._sprites = {}
        self._sprite_list = []
    
    def get_surface(self) -> py.Surface:
        """Returns the surface which is used to create sprites.

        Returns:
            py.Surface: The pygames surface of this window.
        """
        return self._screen
    
    def get_window_size(self) -> Tuple[int, int]:
        """The window's size.

        Returns:
            Tuple[int, int]: width and height in pixels.
        """
        return self._window_size
  
    def get_flags(self):
        return self._flags

    def get_font(self):#
        return self._font

    @property
    def frame_rate(self) -> int:
        return self._frame_rate
    
    @frame_rate.setter
    def frame_rate(self, frame_rate) -> None:
        if frame_rate < 1 or frame_rate > 60:
            raise ValueError("The frame rate has to be between 1 and 60.")
        self._frame_rate = frame_rate
    
    def add_sprite(self, name: str, sprite: Sprite, zindex: int = 0) -> None:
        """This method adds a sprite to the window. For easier handling, give a name to the sprite.

        Args:
            name (str): Name of the sprite.
            sprite (Sprite): The sprite object.
            zindex (int, optional): Layering the sprites (higher values = send to back). Defaults to 0.
        """
        self._sprites[name] = (zindex, sprite)

        # convert to list and sort
        self._update_sprite_list()

    def remove_sprite(self, name: str) -> None:
        """This method removes a registered sprite based on the name.

        Args:
            name (str): The name of the sprite to remove.
        """
        self._sprites.pop(name, "")

        # convert to list and sort
        self._update_sprite_list()
    
    def _update_sprite_list(self) -> None:
        # the sprite list is used to sort sprites corresponding to their 
        # zindex value.
        comp = lambda sprite: sprite[0]
        self._sprite_list = list(self._sprites.values())
        self._sprite_list.sort(key=comp, reverse=True)

    def on_callback(self, type, func) -> None:
        """
        Using this method, callbacks can be registered. If the 
        defined event occurs, then the given function is executed.
        """
        self._callbacks[type] = func
    
    def remove_callback(self, type) -> None:
        """
        This method removes a registered callback
        """
        del self._callbacks[type]

    def start(self) -> None:
        """
        This method holds the main loop that updates the GUI. Be 
        aware that this blocks the main thread.
        """
        self._running = True
        while self._running:
            for event in py.event.get():
                self.event(event)
            
            # draw all registered sprites first
            for _, sprite in self._sprite_list:
                sprite.draw()
                
            self.draw()
        
            # cap at the given frame rate
            self._clock.tick(self._frame_rate)
            py.display.flip()

        print("Graphics has stopped.")
    
    def event(self, event) -> None:
        """
        This method is used to handle GUI events.
        """
        if event.type == py.QUIT:
            self._running = False
            if BaseWindow.QUIT in self._callbacks.keys():
                self._callbacks[BaseWindow.QUIT]()
    
    def draw(self) -> None:
        """
        This method can be used to draw elements on the GUI.
        """
        pass
