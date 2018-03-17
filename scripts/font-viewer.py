#!/usr/bin/env python3
"""
A TTF font-viewer for creating bitmaps.

Usage: font-viewer.py [OPTIONS]

Options:
  -f, --font-name NAME   Font to use [default: Deferral-Regular]
  -o, --output PATH      Save path [default: <repo>/bitmaps]
  -p, --point-size SIZE  Initial font-point to use [default: 6]
  --help                 Show this message and exit.

Notes:
    - developed on Mac.  Untested elsewhere

Keyboard shortcuts:

    Mac OS X:

        CMD + S:  Save the current screen to the output folder
        CMD + =:  increase the font size
        CMD + -:  decrease the font size

        t: Change the text displayed
        c: Toggle colors on/off [default: on]
        space: modify colors (when colors are toggled on)
"""

import itertools
import os
import sys
import random
from pathlib import Path

import click
import pygame
from fontTools.ttLib import TTFont
from colors import colors as color_data

# pygame currently doesn't allow 32-bit unicodes
MAX_PYGAME_UNICODE = 0xFFFF


this_file = Path(__file__)
this_files_folder = this_file.parent
this_repo = this_files_folder.parent


cp437_table = [
    (0x0000, 0x263A, 0x263B, 0x2665, 0x2666, 0x2663, 0x2660, 0x2022, 0x25D8, 0x25CB, 0x25D9, 0x2642, 0x2640, 0x266A, 0x266B, 0x263C),
    (0x25BA, 0x25C4, 0x2195, 0x203C, 0x00B6, 0x00A7, 0x25AC, 0x21A8, 0x2191, 0x2193, 0x2192, 0x2190, 0x221F, 0x2194, 0x25B2, 0x25BC),
    (0x0020, 0x0021, 0x0022, 0x0023, 0x0024, 0x0025, 0x0026, 0x0027, 0x0028, 0x0029, 0x002A, 0x002B, 0x002C, 0x002D, 0x002E, 0x002F),
    (0x0030, 0x0031, 0x0032, 0x0033, 0x0034, 0x0035, 0x0036, 0x0037, 0x0038, 0x0039, 0x003A, 0x003B, 0x003C, 0x003D, 0x003E, 0x003F),

    (0x0040, 0x0041, 0x0042, 0x0043, 0x0044, 0x0045, 0x0046, 0x0047, 0x0048, 0x0049, 0x004A, 0x004B, 0x004C, 0x004D, 0x004E, 0x004F),
    (0x0050, 0x0051, 0x0052, 0x0053, 0x0054, 0x0055, 0x0056, 0x0057, 0x0058, 0x0059, 0x005A, 0x005B, 0x005C, 0x005D, 0x005E, 0x005F),
    (0x0060, 0x0061, 0x0062, 0x0063, 0x0064, 0x0065, 0x0066, 0x0067, 0x0068, 0x0069, 0x006A, 0x006B, 0x006C, 0x006D, 0x006E, 0x006F),
    (0x0070, 0x0071, 0x0072, 0x0073, 0x0074, 0x0075, 0x0076, 0x0077, 0x0078, 0x0079, 0x007A, 0x007B, 0x007C, 0x007D, 0x007E, 0x2302),

    (0x00C7, 0x00FC, 0x00E9, 0x00E2, 0x00E4, 0x00E0, 0x00E5, 0x00E7, 0x00EA, 0x00EB, 0x00E8, 0x00EF, 0x00EE, 0x00EC, 0x00C4, 0x00C5),
    (0x00C9, 0x00E6, 0x00C6, 0x00F4, 0x00F6, 0x00F2, 0x00FB, 0x00F9, 0x00FF, 0x00D6, 0x00DC, 0x00A2, 0x00A3, 0x00A5, 0x20A7, 0x0192),
    (0x00E1, 0x00ED, 0x00F3, 0x00FA, 0x00F1, 0x00D1, 0x00AA, 0x00BA, 0x00BF, 0x2310, 0x00AC, 0x00BD, 0x00BC, 0x00A1, 0x00AB, 0x00BB),
    (0x2591, 0x2592, 0x2593, 0x2502, 0x2524, 0x2561, 0x2562, 0x2556, 0x2555, 0x2563, 0x2551, 0x2557, 0x255D, 0x255C, 0x255B, 0x2510),

    (0x2514, 0x2534, 0x252C, 0x251C, 0x2500, 0x253C, 0x255E, 0x255F, 0x255A, 0x2554, 0x2569, 0x2566, 0x2560, 0x2550, 0x256C, 0x2567),
    (0x2568, 0x2564, 0x2565, 0x2559, 0x2558, 0x2552, 0x2553, 0x256B, 0x256A, 0x2518, 0x250C, 0x2588, 0x2584, 0x258C, 0x2590, 0x2580),
    (0x03B1, 0x00DF, 0x0393, 0x03C0, 0x03A3, 0x03C3, 0x00B5, 0x03C4, 0x03A6, 0x0398, 0x03A9, 0x03B4, 0x221E, 0x03C6, 0x03B5, 0x2229),
    (0x2261, 0x00B1, 0x2265, 0x2264, 0x2320, 0x2321, 0x00F7, 0x2248, 0x00B0, 0x2219, 0x00B7, 0x221A, 0x207F, 0x00B2, 0x25A0, 0x00A0),
    ]

cp850_table = cp437_table[0:8] + [
    (0x00C7, 0x00FC, 0x00E9, 0x00E2, 0x00E4, 0x00E0, 0x00E5, 0x00E7, 0x00EA, 0x00EB, 0x00E8, 0x00EF, 0x00EE, 0x00EC, 0x00C4, 0x00C5),
    (0x00C9, 0x00E6, 0x00C6, 0x00F4, 0x00F6, 0x00F2, 0x00FB, 0x00F9, 0x00FF, 0x00D6, 0x00DC, 0x00F8, 0x00A3, 0x00D8, 0x00D7, 0x0192),
    (0x00E1, 0x00ED, 0x00F3, 0x00FA, 0x00F1, 0x00D1, 0x00AA, 0x00BA, 0x00BF, 0x00AE, 0x00AC, 0x00BD, 0x00BC, 0x00A1, 0x00AB, 0x00BB),
    (0x2591, 0x2592, 0x2593, 0x2502, 0x2524, 0x00C1, 0x00C2, 0x00C0, 0x00A9, 0x2563, 0x2551, 0x2557, 0x255D, 0x00A2, 0x00A5, 0x2510),

    (0x2514, 0x2534, 0x252C, 0x251C, 0x2500, 0x253C, 0x00E3, 0x00C3, 0x255A, 0x2554, 0x2569, 0x2566, 0x2560, 0x2550, 0x256C, 0x00A4),
    (0x00F0, 0x00D0, 0x00CA, 0x00CB, 0x00C8, 0x0131, 0x00CD, 0x00CE, 0x00CF, 0x2518, 0x250C, 0x2588, 0x2584, 0x00A6, 0x00CC, 0x2580),
    (0x00D3, 0x00DF, 0x00D4, 0x00D2, 0x00F5, 0x00D5, 0x00B5, 0x00FE, 0x00DE, 0x00DA, 0x00DB, 0x00D9, 0x00FD, 0x00DD, 0x00AF, 0x00B4),
    (0x00AD, 0x00B1, 0x2017, 0x00BE, 0x00B6, 0x00A7, 0x00F7, 0x00B8, 0x00B0, 0x00A8, 0x00B7, 0x00B9, 0x00B3, 0x00B2, 0x25A0, 0x00A0),
    ]


TesterText = """
iIl1L
oO0
s52Zz
<[({})]>
+tT
pqga
mnh
"""

code_text = """
def get_max_point_size(resolution, dimensions, max_point_size=72):
    line_offset = 2
    dimensions = dimensions[0], dimensions[1] + line_offset
    for point_size in range(max_point_size, 1, -1):
        if all(d * point_size < r for d, r in zip(dimensions, resolution)):
            break
    return point_size or 14
"""


# colors
black = (0, 0, 0)


@click.command()
@click.argument('font-name', metavar='FONT', required=False, default='Deferral-Regular')
@click.option('-o', '--output', metavar='PATH', help='Save path')
@click.option('-p', '--point-size', metavar='SIZE', help='Font-point to use', default=16, type=int)
def main(font_name, point_size, output):
    output = output or this_repo / 'bitmaps'

    pygame.init()
    info = pygame.display.Info()

    font_path = find_font(font_name)
    font = load_font(font_path, point_size)
    font_height = get_font_height(font_path, point_size)

    glyphs = sorted(set(get_font_glyphs(font_path)))
    symbols, font_dimensions = get_font_dimensions(font, point_size, glyphs)

    texts = {
        'cp437': layout_text(
            text=''.join(chr(code) if code != 0 else ' ' for row in cp437_table for code in row),
            width=16
        ),
        'cp850': layout_text(
            text=''.join(chr(code) if code != 0 else ' ' for row in cp850_table for code in row),
            width=16
        ),
        'glyphs': layout_text(
            text=''.join(symbol for symbol, code, name in glyphs if 0x0000 < code < MAX_PYGAME_UNICODE),
            width=32
        ),
        'test': layout_text(text=TesterText),
        'code': layout_text(text=code_text),
    }

    text_name = 'glyphs'
    random_color_generator = get_random_color()
    colors = None
    # colors = {
    #     symbol: next(random_color_generator)
    #     for symbol, code, name in glyphs
    # }

    dimensions = sum(1 for character in texts[text_name].split('\n')[0]), sum(1 for line in texts[text_name].split('\n'))
    monitor_resolution = info.current_w, info.current_h
    font_size, font_width, font_height = font_dimensions
    screen_flags = (pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
    screen = pygame.display.set_mode((dimensions[0] * font_width, dimensions[1] * font_height), screen_flags)
    resolution = screen.get_size()

    text_surface = render_text_surface(texts[text_name], font, font_dimensions, colors=colors, ignore_whitespace=True)
    screen.blit(text_surface, (0, 0))
    pygame.display.flip()

    # Event loop
    while True:
        dimensions = sum(1 for character in texts[text_name].split('\n')[0]), sum(1 for line in texts[text_name].split('\n'))
        monitor_resolution = info.current_w, info.current_h
        max_point_size = get_max_point_size(monitor_resolution, dimensions)

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_SPACE]:
            if colors:
                colors = {
                    symbol: next(random_color_generator)
                    for symbol, code, name in glyphs
                }
            text_surface = render_text_surface(texts[text_name], font, font_dimensions, colors=colors, ignore_whitespace=True)
            screen.fill(black)

        for event in pygame.event.get():
            mods = pygame.key.get_mods()
            meta_only = (mods & pygame.KMOD_META) and (mods & ~(pygame.KMOD_LMETA | pygame.KMOD_RMETA | pygame.KMOD_META) == 0)

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key in [pygame.K_q, pygame.K_ESCAPE]):
                return

            elif event.type == pygame.VIDEORESIZE:
                resolution = event.dict['size']
                dimensions = sum(1 for character in texts[text_name].split('\n')[0]), sum(1 for line in texts[text_name].split('\n'))
                max_point_size = get_max_point_size(resolution, dimensions)
                point_size = min(max_point_size, point_size)

                font = load_font(font_path, point_size)
                symbols, font_dimensions = get_font_dimensions(font, point_size, glyphs)
                text_surface = render_text_surface(texts[text_name], font, font_dimensions, colors=colors, ignore_whitespace=True)
                screen = pygame.display.set_mode(resolution, screen_flags)
                screen.fill(black)
                pygame.display.flip()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    if not colors:
                        colors = {
                            symbol: next(random_color_generator)
                            for symbol, code, name in glyphs
                        }
                    else:
                        colors = None
                    text_surface = render_text_surface(texts[text_name], font, font_dimensions, colors=colors, ignore_whitespace=True)
                    screen.fill(black)

                elif event.key == pygame.K_g:
                    font = load_font(font_path, point_size)
                    glyphs = sorted(set(get_font_glyphs(font_path)))
                    symbols, font_dimensions = get_font_dimensions(font, point_size, glyphs)

                    texts = {
                        'cp437': layout_text(
                            text=''.join(chr(code) if code != 0 else ' ' for row in cp437_table for code in row),
                            width=16
                        ),
                        'cp850': layout_text(
                            text=''.join(chr(code) if code != 0 else ' ' for row in cp850_table for code in row),
                            width=16
                        ),
                        'glyphs': layout_text(
                            text=''.join(symbol for symbol, code, name in glyphs if 0x0000 < code < MAX_PYGAME_UNICODE),
                            width=32
                        ),
                        'test': layout_text(text=TesterText),
                        'code': layout_text(text=code_text),
                    }

                    dimensions = sum(1 for character in texts[text_name].split('\n')[0]), sum(1 for line in texts[text_name].split('\n'))
                    max_point_size = get_max_point_size(screen.get_size(), dimensions)
                    point_size = min(max_point_size, point_size)

                    text_surface = render_text_surface(texts[text_name], font, font_dimensions, colors=colors, ignore_whitespace=True)
                    screen.fill(black)

                elif event.key == pygame.K_t:
                    dimensions = sum(1 for character in texts[text_name].split('\n')[0]), sum(1 for line in texts[text_name].split('\n'))
                    max_point_size = get_max_point_size(screen.get_size(), dimensions)
                    point_size = min(max_point_size, point_size)

                    text_names = [k for k in texts]
                    text_name_index = text_names.index(text_name) + 1
                    if not 0 <= text_name_index < len(text_names):
                        text_name_index = 0
                    text_name = text_names[text_name_index]
                    text_surface = render_text_surface(texts[text_name], font, font_dimensions, colors=colors, ignore_whitespace=True)
                    screen.fill(black)

                elif meta_only:
                    if event.key == pygame.K_e:
                        if not output.exists():
                            output.mkdir(parents=True, exist_ok=True)
                        filepath = output / f'{font_name}-{point_size:>02}-{text_name}.png'
                        pygame.image.save(text_surface, str(filepath))

                    elif event.key == pygame.K_x:
                        remove_bitmaps()

                    elif event.key == pygame.K_EQUALS:
                        point_size = min(point_size + 1, max_point_size)
                        font = load_font(font_path, point_size)
                        symbols, font_dimensions = get_font_dimensions(font, point_size, glyphs)
                        text_surface = render_text_surface(texts[text_name], font, font_dimensions, colors=colors, ignore_whitespace=True)
                        screen.fill(black)

                    elif event.key == pygame.K_MINUS:
                        point_size = max(point_size - 1, 1)
                        font = load_font(font_path, point_size)
                        symbols, font_dimensions = get_font_dimensions(font, point_size, glyphs)
                        text_surface = render_text_surface(texts[text_name], font, font_dimensions, colors=colors, ignore_whitespace=True)
                        screen.fill(black)

        pygame.display.set_caption(f'{point_size}-point {text_name} {font_name} ')
        # scaled_surface = pygame.transform.scale(text_surface, resolution, screen)
        # screen.blit(scaled_surface, (0, 0))
        screen.blit(text_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(1)


def find_font(font_name):
    font_filenames = map(''.join, itertools.product([font_name], ['.ttf', '.otf', '.png', '.bmp']))
    found = []

    # Allow for an actual path
    if Path(font_name).exists():
        return Path(font_name)

    # Otherwise look for a name
    for font_filename in font_filenames:
        for fonts_home in [this_repo] + [h for h in get_fonts_homes()]:
            fonts_path = fonts_home / font_filename
            if not fonts_path.exists():
                continue
            modified = fonts_path.stat().st_mtime
            found.append((modified, fonts_path))
    found = list(reversed(sorted(found)))
    found = found[0][-1] if found else None
    return found


def glyph_is_visible(symbol, name, code):
    symbol_repr = repr(symbol)
    if symbol_repr.startswith("'\\x"):
        return False
    else:
        return True


def get_font(font):
    if not isinstance(font, TTFont):
        font = TTFont(font)
    return font


def get_font_glyphs(font, visible=None):
    font = get_font(font)
    glyphs = {
        name: code
        for table in font['cmap'].tables
        for code, name in table.cmap.items()
    }
    for name, code in glyphs.items():
        code = glyphs[name]
        symbol = chr(code)
        if visible and not glyph_is_visible(symbol, name, code):
            continue
        yield symbol, code, name


def get_font_height(font, point_size=None):
    font = get_font(font)
    head = font['head']
    hhea = font['hhea']
    units_per_em = head.unitsPerEm
    height = (hhea.ascent - hhea.descent + hhea.lineGap) / units_per_em
    if point_size:
        height = int(height * point_size)
    return height


def get_font_size_data(font, point_size=None):
    font = get_font(font)
    head = font['head']
    units_per_em = head.unitsPerEm

    # Assumes .notdef is available
    glyph_set = font.getGlyphSet()
    standard_width = glyph_set['.notdef'].width / units_per_em
    if point_size:
        standard_width = standard_width * point_size
    yield '.notdef', standard_width
    for glyph_name in glyph_set.keys():
        glyph = glyph_set[glyph_name]
        glyph_width = (glyph.width * point_size if point_size else glyph.width) / units_per_em
        if glyph_width != standard_width:
            yield (glyph_name, glyph_width)


def get_font_dimensions(font_path, point_size, glyphs):
    """Renders every glyph to a surface and then finds max character
    height and width"""
    font = load_font(font_path, point_size)
    antialias = True
    color = (255, 255, 255)  # RGB, white
    background = black  # RGB, black
    fonts = {}
    max_width = 0
    max_height = 0
    for symbol, code, name in glyphs:
        if code > MAX_PYGAME_UNICODE or code == 0x0000:
            continue
        elif len(str(symbol)) == 0:
            continue
        try:
            surface = font.render(symbol, antialias, color, background)
        except pygame.error:
            continue
        width, height = surface.get_size()
        max_width = max(width, max_width)
        max_height = max(height, max_height)
        fonts[code] = (symbol, width, height, surface)
    return fonts, (point_size, width, height)


# def get_font_glyphs(font_path):
#     font = TTFont(font_path)
#     for table in font['cmap'].tables:
#         for code, name in table.cmap.items():
#             if code > MAX_PYGAME_UNICODE:
#                 continue
#             symbol = chr(code)
#             yield symbol, code, name


def get_fonts_homes(platform=None):
    home = os.getenv('HOME')
    sysroot = os.getenv('SYSROOT')
    platform = platform or sys.platform
    # Order here matters less because search is not short-circuted; instead
    #  the font that matches with the most recent modified time is taken
    mapping = {
        'darwin': [f'{home}/Library/Fonts', '/Library/Fonts/', '/Network/Library/Fonts/', '/System/Library/Fonts/'],
        'win32': [f'{sysroot}\\Fonts'],
        'linux': [f'{home}/.fonts/truetype', f'{home}/.local/share/fonts/truetype', '/usr/local/share/fonts/truetype', '/usr/share/fonts/truetype'],
    }

    # TODO: Add this
    project = []
    return map(Path, mapping[platform] + project)


def get_max_point_size(resolution, dimensions, max_point_size=72):
    line_offset = 2
    dimensions = dimensions[0], dimensions[1] + line_offset
    for point_size in range(max_point_size, 1, -1):
        if all(d * point_size < r for d, r in zip(dimensions, resolution)):
            break
    return point_size or 14


def get_random_color():
    color_names = list(color_data.keys())
    while True:
        random.shuffle(color_names)
        for name in color_names:
            raw_color = color_data[name]
            try:
                color = tuple(raw_color)
                yield color
            except Exception as e:
                print(e)
                import pdb; pdb.set_trace()
                pass


def remove_bitmaps():
    bitmap_path = Path(__file__).absolute().parent.parent / 'bitmaps'
    for root, folders, files in os.walk(bitmap_path):
        for filename in files:
            if filename.endswith('.png'):
                path = Path(root) / filename
                os.remove(path)


def layout_text(text, width=None):
    wrapped_text = text
    if '\n' in text and width is None:
        pass
    elif width and len(text) > width:
        table = []
        row = []
        for index, character in enumerate(text):
            if repr(character).lstrip("'").startswith('\\x') or character in ['\t', '\r']:
                character = ' '
            if index and index % width == 0:
                table.append(''.join(row))
                row = []
            row.append(character)
        table.append(''.join(row))
        wrapped_text = '\n'.join(table)
    return wrapped_text


def load_font(font_filepath, point_size):
    # Handle truetype/opentype and bitmap/png fonts
    if isinstance(font_filepath, pygame.font.Font):
        return font_filepath
    supported_filetypes = ('.ttf', 'otf', '.png', '.bmp')
    if font_filepath.suffix in supported_filetypes:
        font = pygame.font.Font(str(font_filepath), point_size)
    else:
        raise ValueError('Font, {font_filepath}, must be one of: TTF/OTF/PNG/BMP.')
    return font


def render_text_surface(text, font, font_dimensions, antialias=None, colors=None, background=None, ignore_whitespace=None):
    antialias = True if antialias is None else antialias
    color = (255, 255, 255)
    background = black if background is None else background

    rows = len(text.split('\n'))
    cols = max(len(row) for row in text.split('\n'))

    point_size, font_width, font_height = font_dimensions

    offset = 1
    font_height = font_height - offset

    # H is used for determining the "average" glyph space
    space = font.render('H', antialias, color, background)
    space_width, space_height = space.get_size()

    text_pixel_width = cols * font_width
    text_pixel_height = rows * font_height

    text_surface = pygame.Surface((text_pixel_width, text_pixel_height))
    text_surface = text_surface.convert()
    text_surface.fill(background)

    max_width, max_height = text_surface.get_size()
    y = 0
    for line in text.splitlines():
        x = 0
        for character in line:

            if colors:
                color = colors.get(character, black)

            if character in ['\n']:
                y += font_height
                x = 0
                continue

            if character in ['\r', '\t']:
                character = ' '
            elif ignore_whitespace and character in ['\t']:
                character = ' '
            elif character in ['\t']:
                for character in range(4):
                    text_surface.blit(space, (x, y))
                    x += (space_width or point_size)
            else:
                try:
                    character_surface = font.render(character, antialias, color, background)
                except pygame.error:
                    continue
                except TypeError:
                    import pdb; pdb.set_trace()
                    pass
                cwidth, cheight = character_surface.get_size()
                text_surface.blit(character_surface, (x, y))
                x += (cwidth or point_size)
        y += font_height

    return text_surface


if __name__ == '__main__':
    main()
