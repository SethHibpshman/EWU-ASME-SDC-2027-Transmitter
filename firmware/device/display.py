# OLED screen: link, battery, mode

from config import OLED_W, OLED_H, i2c
import ssd1306
import gfx

oled     = ssd1306.SSD1306_I2C(OLED_W, OLED_H, i2c)
oled_gfx = gfx.GFX(OLED_W, OLED_H, oled.pixel)

def draw_centered(text, center_x, y):
    """
    Draw text centred on a given x coordinate.

    Parameters
    ----------
    text : str
        String to render.
    center_x : int
        Pixel x position to centre the text around.
    y : int
        Pixel y position (top of text).
    """
    width = len(text) * 8
    x = center_x - (width // 2)
    oled.text(text, x, y)


def draw_right_aligned(text, right_x, y):
    oled.text(text, x, y)