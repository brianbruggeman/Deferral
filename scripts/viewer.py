#!/usr/bin/env python3
import itertools
import os
import sys
from pathlib import Path

import pygame


class Viewer(object):

    def calculate_max_font_point(self, point_size, dimensions=None, resolution=None, font_path=None):
        # Set dimensions
        default_dimensions = (80, 50)
        dimensions = dimensions or default_dimensions

        # Set resolution
        info = pygame.display.Info()
        resolution = resolution or (info.current_w, info.current_h)

    def get_font_path(self, font_name):
        standards = ['', '-Square', '-Normal', '-Regular', '-Narrow']
        extensions = ['', '.ttf', '.otf']
        for font_home in self.find_font_homes():
            for fragments in itertools.product([font_name], standards, extensions):
                name = ''.join(fragments)
                test_path = font_home / name
                if test_path.exists():
                    yield test_path

    def find_font_homes(self, platform=None):
        repo_path = Path(__file__).absolute().parent.parent
        home = os.getenv('HOME')
        sysroot = os.getenv('SYSROOT')  # windows only
        platform = platform or sys.platform
        mapping = {
            'darwin': [f'{home}/Library/Fonts', '/Library/Fonts/', '/Network/Library/Fonts/', '/System/Library/Fonts/'],
            'win32': [f'{sysroot}\\Fonts'],
            'linux': [f'{home}/.fonts/truetype', f'{home}/.local/share/fonts/truetype', '/usr/local/share/fonts/truetype', '/usr/share/fonts/truetype'],
        }

        # TODO: Add this
        project = [str(path) for path in [
            repo_path,
            repo_path / 'fonts',
        ] if path.exists()]
        return map(Path, project + mapping[platform])

    def handle_keyboard_input(self):
        shift = lambda m: (m & pygame.KMOD_SHIFT) and (m & ~(pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT | pygame.KMOD_SHIFT) == 0)
        meta = lambda m: (m & pygame.KMOD_META) and (m & ~(pygame.KMOD_LMETA | pygame.KMOD_RMETA | pygame.KMOD_META) == 0)
        shift_meta = lambda m: (m & pygame.KMOD_META & pygame.KMOD_SHIFT) and (m & ~(pygame.KMOD_LMETA | pygame.KMOD_RMETA | pygame.KMOD_META | pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT | pygame.KMOD_SHIFT) == 0)

        for event in pygame.event.get():
            mods = pygame.key.get_mods()

            mapping = {
                # Resize
                (pygame.VIDEORESIZE, None, None): (self.handle_video_resize, [], {}),

                # Exit
                (pygame.QUIT, None, None): (sys.exit, [0], {}),
                (pygame.KEYDOWN, pygame.K_q, None): (sys.exit, [0], {}),
                (pygame.KEYDOWN, pygame.K_ESCAPE, None): (sys.exit, [0], {}),

                # Colors
                (pygame.KEYDOWN, pygame.K_c, None): (self.toggle_colors, [], {}),

                # Fonts
                (pygame.KEYDOWN, pygame.K_f, None): (self.toggle_colors, [], {}),

                # Text
                (pygame.KEYDOWN, pygame.K_t, None): (self.cycle_text, [], {}),
            }

            data = mapping.get((event.type, None, mods))
            if not data:
                data = mapping.get((event.type, event.key))

            if data:
                func, args, kwds = data
                func(*args, **kwds)
                continue
