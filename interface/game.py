import pygame
import os
import glob
import sys
from typing import Tuple
from .display import draw_button


def run_game(screen: pygame.Surface, clock: pygame.time.Clock, width: int = 1280, height: int = 720) -> bool:
	"""Minimal placeholder game loop.

	This function reuses the provided `screen` and `clock` so the Pygame
	window stays the same when switching from menu -> game.

	Controls:
	- Press `ESC` to return to the menu (function returns)
	- Close window to quit the application
	"""
	running = True
	# simple font for on-screen text
	try:
		has_freetype = hasattr(pygame, "freetype")
	except Exception:
		has_freetype = False

	if has_freetype:
		import pygame.freetype as freetype
		title_font = freetype.SysFont(None, 48)
		small_font = freetype.SysFont(None, 20)
	else:
		title_font = pygame.font.SysFont(None, 48)
		small_font = pygame.font.SysFont(None, 20)

	# basic animation state
	t = 0.0

	# Try to load an optional background image for the game screen. Prefer
	# Load the explicitly named game background file `game_bg.jpg` only.
	background_image = None
	try:
		base = os.path.dirname(__file__)
		images_dir = os.path.join(base, "assets", "images")
		path = os.path.join(images_dir, "game_bg.jpg")
		if os.path.exists(path):
			background_image = pygame.image.load(path).convert()
			if hasattr(pygame.transform, 'smoothscale'):
				background_image = pygame.transform.smoothscale(background_image, (width, height))
			else:
				background_image = pygame.transform.scale(background_image, (width, height))
		else:
			background_image = None
	except Exception:
		background_image = None
	while running:
		# handle events
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				# quit the whole app
				pygame.quit()
				sys.exit(0)
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					# return to menu
					running = False

		# update (dummy)
		dt = clock.tick(60) / 1000.0
		t += dt

		# draw a simple placeholder game screen (use background image if available)
		if background_image is not None:
			screen.blit(background_image, (0, 0))
		else:
			screen.fill((18, 18, 24))
		# draw a large title
		text = "Game Running - Knight's Tour"
		if hasattr(title_font, 'render_to'):
			rect = title_font.get_rect(text)
			x = screen.get_width() // 2 - rect.width // 2
			y = int(height * 0.08)
			title_font.render_to(screen, (x, y), text, fgcolor=(230, 230, 210))
		else:
			surf = title_font.render(text, True, (230, 230, 210))
			screen.blit(surf, surf.get_rect(center=(screen.get_width() // 2, int(height * 0.08) + surf.get_height() // 2)))

		# small instruction
		instr = "Press ESC to return to menu or close window to quit"
		if hasattr(small_font, 'render_to'):
			rect = small_font.get_rect(instr)
			x = screen.get_width() // 2 - rect.width // 2
			y = int(height * 0.86)
			small_font.render_to(screen, (x, y), instr, fgcolor=(200, 200, 200))
		else:
			surf = small_font.render(instr, True, (200, 200, 200))
			screen.blit(surf, surf.get_rect(center=(screen.get_width() // 2, int(height * 0.86))))

		pygame.display.flip()

	# return to caller (menu)
	return False


def _confirm_return_to_menu(screen: pygame.Surface, clock: pygame.time.Clock, width: int, height: int, title_font, small_font) -> bool:
	"""Show a translucent blurred confirmation overlay asking to return to menu.

	Returns True if user chooses to return to menu, False to resume game.
	"""
	# capture current screen and blur it
	try:
		sub = screen.copy()
		w_small = max(1, width // 16)
		h_small = max(1, height // 16)
		if hasattr(pygame.transform, 'smoothscale'):
			small = pygame.transform.smoothscale(sub, (w_small, h_small))
			blur = pygame.transform.smoothscale(small, (width, height))
		else:
			small = pygame.transform.scale(sub, (w_small, h_small))
			blur = pygame.transform.scale(small, (width, height))
	except Exception:
		blur = None

	# prepare overlay elements
	panel_w = int(width * 0.6)
	panel_h = int(height * 0.32)
	panel_x = width // 2 - panel_w // 2
	panel_y = height // 2 - panel_h // 2
	panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

	# button sizes
	btn_w = int(panel_w * 0.28)
	btn_h = int(panel_h * 0.22)
	btn_spacing = int(panel_w * 0.06)
	btn_y = panel_y + panel_h - btn_h - 20
	btn_x_left = panel_x + panel_w // 2 - btn_w - btn_spacing // 2
	btn_x_right = panel_x + panel_w // 2 + btn_spacing // 2
	btn_yes = pygame.Rect(btn_x_left, btn_y, btn_w, btn_h)
	btn_no = pygame.Rect(btn_x_right, btn_y, btn_w, btn_h)

	message = "Return to main menu?"

	paused = True
	while paused:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit(0)
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					# dismiss overlay
					return False
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				pos = event.pos
				if btn_yes.collidepoint(pos):
					return True
				if btn_no.collidepoint(pos):
					return False

		# draw blurred background or darkened fallback
		if blur:
			screen.blit(blur, (0, 0))
		else:
			screen.fill((8, 8, 10))

		# translucent panel (frosted look)
		panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
		panel.fill((30, 30, 40, 180))
		# rounded mask
		mask = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
		pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=14)
		mask.blit(panel, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
		screen.blit(mask, (panel_x, panel_y))

		# message
		if hasattr(title_font, 'render_to'):
			rect = title_font.get_rect(message)
			tx = panel_x + panel_w // 2 - rect.width // 2
			ty = panel_y + 30
			title_font.render_to(screen, (tx, ty), message, fgcolor=(240, 240, 230))
		else:
			surf = title_font.render(message, True, (240, 240, 230))
			screen.blit(surf, surf.get_rect(center=(panel_x + panel_w // 2, panel_y + 40)))

		# draw Yes / No buttons using draw_button for consistent style
		draw_button(screen, btn_yes, "Yes", small_font, bg=(90, 40, 20), fg=(240, 230, 200))
		draw_button(screen, btn_no, "No", small_font, bg=(60, 60, 80), fg=(240, 240, 240))

		pygame.display.flip()
		clock.tick(30)

	# default: resume game
	return False
