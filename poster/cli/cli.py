"""poster.cli.cli"""

import json

import click
from urllib.request import urlopen

from poster.poster import create as poster_create

POSTER_API_URL = 'https://api.remotepixel.ca/poster_uuid'


@click.command(short_help="Create poster")
@click.argument('poster_id', type=click.UUID, nargs=1)
@click.option('--preview/--full', default=True, help='Create high resolution poster or preview')
def create(poster_id, preview):
    """
    """
    click.echo(f'Order: {poster_id}')

    r = urlopen(f'{POSTER_API_URL}?uuid={poster_id}')
    metadata = json.loads(r.read())
    metadata = metadata.get('results').get('_source')

    mapid = metadata['overlay']
    lyr_desc = metadata['lyr_desc']
    date = metadata['date']
    style = metadata['style']
    filters = metadata['filters']
    rotation = metadata.get('rot', 0)

    bounds = list(eval(str(metadata['aoi'])))
    bounds[0] = ((bounds[0] + 180) % 360) - 180
    bounds[2] = ((bounds[2] + 180) % 360) - 180

    click.echo(f'Layer: {lyr_desc}')
    click.echo(f'Date: {date}')
    click.echo(f'Size: {style.get("size")}')
    click.echo(f'Orientation: {style.get("orient")}')
    click.echo(f'Preview: {preview}')

    img = poster_create(mapid, date, bounds, filters, style, rotation, preview=preview)

    outfile = f'./{poster_id}.jpg'
    with open(outfile, 'wb') as f:
        f.write(img.getvalue())
