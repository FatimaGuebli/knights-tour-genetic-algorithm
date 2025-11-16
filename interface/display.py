import pygame
from typing import Tuple


def draw_background(screen: pygame.Surface, color: Tuple[int, int, int] = (30, 30, 40)) -> None:
    screen.fill(color)


def render_text_center(screen: pygame.Surface, text: str, font, color=(255, 255, 255), y_offset=0) -> None:
    # Support both pygame.font and pygame.freetype.Font-like objects
    if hasattr(font, "get_rect"):
        rect = font.get_rect(text)
        x = screen.get_width() // 2 - rect.width // 2
        y = screen.get_height() // 2 - rect.height // 2 + y_offset
        font.render_to(screen, (x, y), text, fgcolor=color)
    else:
        surf = font.render(text, True, color)
        x = screen.get_width() // 2 - surf.get_width() // 2
        y = screen.get_height() // 2 - surf.get_height() // 2 + y_offset
        screen.blit(surf, (x, y))


def render_text_at(screen: pygame.Surface, text: str, font, pos, color=(255, 255, 255)) -> None:
    if hasattr(font, "render_to"):
        font.render_to(screen, pos, text, fgcolor=color)
    else:
        surf = font.render(text, True, color)
        screen.blit(surf, pos)


def draw_button(screen: pygame.Surface, rect: pygame.Rect, text: str, font, bg=(80, 80, 120), fg=(255, 255, 255)) -> None:
    """Draw a simple rounded rectangle button with centered text.

    This implementation is intentionally minimal and compatible with older
    pygame versions (falls back when rounded rectangles are unsupported).
    """
    radius = min(rect.w, rect.h) // 8
    try:
        pygame.draw.rect(screen, bg, rect, border_radius=radius)
    except TypeError:
        pygame.draw.rect(screen, bg, rect)

    # Render centered text
    if hasattr(font, "get_rect"):
        text_rect = font.get_rect(text)
        x = rect.x + rect.w // 2 - text_rect.width // 2
        y = rect.y + rect.h // 2 - text_rect.height // 2
        font.render_to(screen, (x, y), text, fgcolor=fg)
    else:
        surf = font.render(text, True, fg)
        surf_rect = surf.get_rect(center=rect.center)
        screen.blit(surf, surf_rect)



