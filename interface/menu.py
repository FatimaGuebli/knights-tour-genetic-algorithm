import pygame
from typing import Tuple
import os
import glob

from .display import draw_background, render_text_center, render_text_at, draw_button


def _find_local_font():
    """Return path to a local font file.

    Search order:
    1. Top-level files in `interface/fontsassets/fonts/` (preferred)
    2. Any .ttf/.otf found recursively under `interface/` (useful for assets folders)

    Returns the first match or None if nothing found.
    """
    base = os.path.dirname(__file__)
    # 1) Prefer the dedicated fonts folder if present
    fonts_dir = os.path.join(base, "fontsassets", "fonts")
    if os.path.isdir(fonts_dir):
        for ext in ("*.ttf", "*.otf"):
            matches = glob.glob(os.path.join(fonts_dir, ext))
            if matches:
                return matches[0]

    # 2) Fallback: search recursively under the `interface` package for any font
    for root, _, files in os.walk(base):
        for f in files:
            if f.lower().endswith((".ttf", ".otf")):
                return os.path.join(root, f)

    return None


def run_menu(width: int = 1280, height: int = 720) -> None:
    """Open a simple Pygame window showing a static "Main Menu" header.

    The window stays open until the user closes it manually.
    """
    pygame.init()
    # Initialize audio mixer and play menu soundtrack (if available).
    # Wrapped in try/except because mixer initialization can fail on some systems.
    try:
        pygame.mixer.init()
        base_sound = os.path.dirname(__file__)
        sound_path = os.path.join(base_sound, "assets", "soundtrack", "Echoes of the Fallen.mp3")
        if os.path.exists(sound_path):
            try:
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play(-1)
            except Exception:
                # If loading/playing fails, continue without audio
                pass
    except Exception:
        # Mixer init failed; ignore and continue
        pass
    # Initialize fonts; prefer freetype if available
    try:
        # pygame.freetype may be present in pygame >= 2.0
        has_freetype = hasattr(pygame, "freetype")
    except Exception:
        has_freetype = False

    pygame.font.init()

    # Use DPI-aware scaling when available (pygame 2+). Fall back to no flags.
    flags = pygame.SCALED if hasattr(pygame, "SCALED") else 0
    screen = pygame.display.set_mode((width, height), flags)
    pygame.display.set_caption("Knight's Tour - Main Menu")
    clock = pygame.time.Clock()

    # Try to load a background image from assets/images/main_menu_bg.* if present
    background_image = None
    try:
        base = os.path.dirname(__file__)
        bg_path = os.path.join(base, "assets", "images", "main_menu_bg.jpg")
        if os.path.exists(bg_path):
            background_image = pygame.image.load(bg_path).convert()
            # scale it to the initial window size (will remain static)
            if hasattr(pygame.transform, 'smoothscale'):
                background_image = pygame.transform.smoothscale(background_image, (width, height))
            else:
                background_image = pygame.transform.scale(background_image, (width, height))
    except Exception:
        background_image = None
    # Create fonts once and reuse them (prefer freetype). If there is a
    # bundled font in interface/fontsassets/fonts/, load it. Otherwise fall
    # back to system fonts.
    local_font_path = _find_local_font()

    if has_freetype:
        import pygame.freetype as freetype
        if local_font_path:
            try:
                title_font = freetype.Font(local_font_path, 48)
                button_font = freetype.Font(local_font_path, 36)
                small_font = freetype.Font(local_font_path, 18)
            except Exception:
                title_font = freetype.SysFont(None, 48)
                button_font = freetype.SysFont(None, 36)
                small_font = freetype.SysFont(None, 18)
        else:
            title_font = freetype.SysFont(None, 48)
            button_font = freetype.SysFont(None, 36)
            small_font = freetype.SysFont(None, 18)
    else:
        if local_font_path:
            try:
                title_font = pygame.font.Font(local_font_path, 48)
                button_font = pygame.font.Font(local_font_path, 36)
                small_font = pygame.font.Font(local_font_path, 18)
            except Exception:
                title_font = pygame.font.SysFont(None, 48)
                button_font = pygame.font.SysFont(None, 36)
                small_font = pygame.font.SysFont(None, 18)
        else:
            title_font = pygame.font.SysFont(None, 48)
            button_font = pygame.font.SysFont(None, 36)
            small_font = pygame.font.SysFont(None, 18)

    # Prepare buttons centered vertically; size relative to window
    btn_w = int(width * 0.35)
    btn_h = int(height * 0.09)
    spacing = int(height * 0.03)
    total_h = 3 * btn_h + 2 * spacing
    start_y = screen.get_height() // 2 - total_h // 2

    buttons = []
    labels = ["Play", "Settings", "Exit"]
    # Left-align buttons: offset from left edge as percentage of width
    left_margin = int(width * 0.14)
    for i, label in enumerate(labels):
        x = left_margin
        y = start_y + i * (btn_h + spacing)
        rect = pygame.Rect(x, y, btn_w, btn_h)
        buttons.append({"text": label, "rect": rect})

    message = ""

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for b in buttons:
                    if b["rect"].collidepoint(event.pos):
                        if b["text"] == "Exit":
                            # stop music and exit
                            try:
                                pygame.mixer.music.stop()
                            except Exception:
                                pass
                            running = False
                        elif b["text"] == "Play":
                            # stop menu music when entering the game
                            try:
                                pygame.mixer.music.stop()
                            except Exception:
                                pass
                            message = "Play pressed (GA will start here)"
                        elif b["text"] == "Settings":
                            message = "Settings pressed (open settings here)"

        # Draw background image if available, otherwise solid color
        if background_image is not None:
            screen.blit(background_image, (0, 0))
        else:
            draw_background(screen, (40, 40, 60))

        # Draw the main title at the top center
        title_text = "Knight's Tour"
        title_y = int(height * 0.06)
        # compute centered x using font metrics
        if hasattr(title_font, "get_rect"):
            rect = title_font.get_rect(title_text)
            title_x = screen.get_width() // 2 - rect.width // 2
        else:
            w, _ = title_font.size(title_text)
            title_x = screen.get_width() // 2 - w // 2
        render_text_at(screen, title_text, title_font, (title_x, title_y), color=(240, 240, 240))

        # Draw buttons and handle hover state
        mouse_pos = pygame.mouse.get_pos()
        for b in buttons:
            hover = b["rect"].collidepoint(mouse_pos)
            bg = (100, 100, 160) if hover else (70, 70, 100)
            draw_button(screen, b["rect"], b["text"], button_font, bg=bg, fg=(255, 255, 255))

        # Show small helper text below buttons (centered)
        if message:
            render_text_center(screen, message, small_font, color=(200, 200, 200), y_offset=total_h // 2 + 40)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

