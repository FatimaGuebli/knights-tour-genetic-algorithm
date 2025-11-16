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

    # Attempt to create a blurred copy of the area under the button and
    # render a semi-transparent rounded rectangle on top so the button
    # appears translucent with a blurred background. Fall back to a
    # simple filled rect when the operations are not supported.
    try:
        # Capture area under button
        sub = screen.subsurface(rect).copy()

        # Quick blur via downscale/upsacle (simple box blur feel)
        scale_w = max(1, rect.w // 4)
        scale_h = max(1, rect.h // 4)
        small = pygame.transform.smoothscale(sub, (scale_w, scale_h))
        blurred = pygame.transform.smoothscale(small, (rect.w, rect.h))

        # Create a mask for rounded corners (white inside rounded rect, transparent outside)
        mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))
        try:
            pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
        except TypeError:
            pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect())

        # Apply mask to blurred (multiply will zero-out outside rounded rect)
        blurred.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Create overlay: blurred background inside rounded rect + semi-transparent tint
        overlay = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        overlay.blit(blurred, (0, 0))

        # Draw semi-transparent rounded rectangle tint on top
        tint = (bg[0], bg[1], bg[2], 150)  # alpha ~150 for translucency
        try:
            pygame.draw.rect(overlay, tint, overlay.get_rect(), border_radius=radius)
        except TypeError:
            # older pygame: no rounded corners, draw normal rect
            pygame.draw.rect(overlay, tint, overlay.get_rect())

        # Blit the composed overlay onto the screen at the button position
        screen.blit(overlay, rect.topleft)
    except Exception:
        # If any of the operations fail (subsurface, transform, etc.), fall back
        try:
            pygame.draw.rect(screen, bg, rect, border_radius=radius)
        except TypeError:
            pygame.draw.rect(screen, bg, rect)

    # Render centered text (unchanged)
    if hasattr(font, "get_rect"):
        text_rect = font.get_rect(text)
        x = rect.x + rect.w // 2 - text_rect.width // 2
        y = rect.y + rect.h // 2 - text_rect.height // 2
        font.render_to(screen, (x, y), text, fgcolor=fg)
    else:
        surf = font.render(text, True, fg)
        surf_rect = surf.get_rect(center=rect.center)
        screen.blit(surf, surf_rect)



