"""poster.poster"""

import math
from io import BytesIO

import numpy as np

from PIL import Image
from wand.image import Image as WImage

from rasterio.io import MemoryFile
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds

from poster.legofy import legofy

POSTER_SIZES = {
    's': {'landscape': [5400, 3600], 'portrait': [3600, 5400]},
    'l': {'landscape': [7200, 5400], 'portrait': [5400, 7200]},
    'xl': {'landscape': [10800, 7200], 'portrait': [7200, 10800]}}


def getImage(xml, bounds, out_shape):
    """Fetch tiles and create image
    """
    bounds = transform_bounds(*['epsg:4326', 'epsg:3857'] + list(bounds), densify_pts=21)
    w, s, e, n = bounds

    with MemoryFile(xml) as memfile:
        with memfile.open() as src:
            with WarpedVRT(src, dst_crs='EPSG:3857', resampling=Resampling.bilinear, num_threads=8) as vrt:
                window = vrt.window(w, s, e, n, precision=21)
                return vrt.read(window=window,
                                boundless=True,
                                resampling=Resampling.bilinear,
                                out_shape=out_shape,
                                indexes=(1, 2, 3))


def create_req_xml(layer, date):
    """Create XML string representing the WMS-TMS gibs service
    """
    xml = f"""<GDAL_WMS>
        <Service name="TMS">
            <ServerUrl>http://gibs.earthdata.nasa.gov/wmts/epsg4326/best/{layer}/default/{date}/250m/${{z}}/${{y}}/${{x}}.jpg</ServerUrl>
        </Service>
        <DataWindow>
            <UpperLeftX>-180.0</UpperLeftX>
            <UpperLeftY>90</UpperLeftY>
            <LowerRightX>396.0</LowerRightX>
            <LowerRightY>-198</LowerRightY>
            <TileLevel>8</TileLevel>
            <TileCountX>2</TileCountX>
            <TileCountY>1</TileCountY>
            <YOrigin>top</YOrigin>
        </DataWindow>
        <Projection>EPSG:4326</Projection>
        <BlockSizeX>512</BlockSizeX>
        <BlockSizeY>512</BlockSizeY>
        <BandsCount>3</BandsCount>
    </GDAL_WMS>"""

    return xml.encode()


def create(layer, date, bounds, filters, style, rotation, preview=False):
    """Create poster from GIBS imagery layers (MODIS, SUOMI...) designed on https://poster.remotepixel.ca
    More info on gibs layer: https://wiki.earthdata.nasa.gov/display/GIBS/

    Parameters
    -----------
    layer: string
        Imagery layer name (https://wiki.earthdata.nasa.gov/display/GIBS/GIBS+Available+Imagery+Products?src=contextnavpagetreemode)
    date: string
        layer date (e.g. 2014-07-7)
    bounds: list
        4 elemets list describing poster bounds
        [w, s, e, n] in WGS84 system (epsg:4326)
    filters: dict
        - hue-rotate: integer
            hue rotation angle (0-360)
        - saturate: integer
            saturation percentage (0-200)
        - brightness: integer
            brightness percentage (0-100)
        more info: http://www.imagemagick.org/script/command-line-options.php?#modulate

    style: dict
        - size: string
            "s", "l" or "xl" defining poster size
        - orient: string
            "landscape" or "portrait" defining poster orientation
        - legofy: bool
            weither or not to apply legofy transformation
    rotation: float
        rotation angle (-180 to 180)
    preview: bool
        if true, poster size will be 10x smaller

    Returns
    --------
    object: buffer
        BytesIO buffer of the image
    """

    select_size = style['size']
    select_orient = style['orient']
    sz = POSTER_SIZES.get(select_size).get(select_orient)

    if preview:
        sz[0] = int(sz[0] / 10)
        sz[1] = int(sz[1] / 10)

    angle = math.radians(abs(rotation))

    if (rotation < -90):
        angle = math.radians(abs(rotation + 180))

    if (rotation > 90):
        angle = math.radians(abs(rotation - 180))

    bx = sz[0]
    by = sz[1]
    if (rotation != 0):
        bx = abs(int(sz[0] * math.cos(angle) + sz[1] * math.sin(angle)))
        by = abs(int(sz[0] * math.sin(angle) + sz[1] * math.cos(angle)))

    xml = create_req_xml(layer, date)
    arr = getImage(xml, bounds, (3, by, bx))

    img = Image.fromarray(np.stack(arr, axis=2))

    if style.get('legofy'):
        block_size = 80 if not preview else 8
        img = legofy(img, block_size, block_size)

    if rotation != 0:
        img = img.rotate(rotation, expand=True)
        w, h = img.size
        midX = w / 2
        midY = h / 2
        midW = sz[0] / 2
        midH = sz[1] / 2
        bbox = (midX - midW, midY - midH, midX + midW, midY + midH)
        bbox = map(int, bbox)
        img = img.crop(tuple(bbox))

    hue = (float(filters['hue-rotate']) * 100/180) + 100
    satu = float(filters['saturate'])
    lum = float(filters['brightness'])

    sio = BytesIO()
    img.save(sio, 'jpeg', subsampling=0, quality=100)
    sio.seek(0)
    img = None

    with WImage(file=sio, format='jpeg') as img:
        img.modulate(saturation=satu, brightness=lum, hue=hue)
        sio = BytesIO()
        img.save(file=sio)
        sio.seek(0)

    return sio
