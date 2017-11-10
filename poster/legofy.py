"""poster.legofy
Simplified version of https://github.com/JuanPotato/Legofy"""

import os
from math import ceil

from PIL import Image


def dims(total, chop):
    for a in range(int(ceil(total / chop))):
        offset = a * chop
        diff = total - offset
        if diff <= chop:
            size = diff
        else:
            size = chop

        yield offset, size


def overlay_effect(color, overlay):
    """Actual overlay effect function
    """
    if color < 33:
        return overlay - 100
    elif color > 233:
        return overlay + 100
    else:
        return overlay - 133 + color


def apply_color_overlay(image, color):
    """Small function to apply an effect over an entire image
    """
    overlay_red, overlay_green, overlay_blue = color
    channels = image.split()

    r = channels[0].point(lambda color: overlay_effect(color, overlay_red))
    g = channels[1].point(lambda color: overlay_effect(color, overlay_green))
    b = channels[2].point(lambda color: overlay_effect(color, overlay_blue))

    channels[0].paste(r)
    channels[1].paste(g)
    channels[2].paste(b)

    return Image.merge(image.mode, channels)


def legofy(img_path, chop_width=80, chop_height=80):
    """Get an image (Path of PIL Image Object) and apply legofy filter
    """
    brick_path = os.path.join(os.path.dirname(__file__), 'assets', f'{chop_width}x{chop_height}.png')
    brick_image = Image.open(brick_path)
    brick_width, brick_height = brick_image.size

    try:
        img_path = os.path.realpath(img_path)
        if not os.path.isfile(img_path):
            src = Image.open(img_path)
    except:
        src = img_path

    base_width, base_height = src.size
    lego_image = Image.new("RGB", (base_width, base_height), "white")

    for xoff, xsize in dims(base_width, chop_width):
        for yoff, ysize in dims(base_height, chop_height):
            img = src.crop((xoff, yoff, xoff+xsize, yoff+ysize))
            img_width, img_height = img.size

            im = img.resize((1, 1), Image.ANTIALIAS)
            color = im.getpixel((0, 0))
            im = img = None

            if img_width != brick_width or img_height != brick_height:
                bk = brick_image.crop((0, 0, img_width, img_height))
                img = apply_color_overlay(bk, color)
                bk = None
            else:
                img = apply_color_overlay(brick_image, color)

            lego_image.paste(img, (xoff, yoff))
            img = None

    return lego_image
