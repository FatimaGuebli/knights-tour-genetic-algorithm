import sys
import os
import glob
import pygame
from .display import draw_background, render_text_center, draw_button


def run_play(width: int = 1280, height: int = 720) -> None:
	"""Simple play screen showing the Knights Tour board title.

	This function takes control of the event loop and returns when the
	user clicks the Back button or presses Escape. Closing the window
	will exit the process.
	"""
	screen = pygame.display.get_surface()
	if screen is None:
		# If no display exists, create one sized to the provided values
		flags = pygame.SCALED if hasattr(pygame, "SCALED") else 0
		screen = pygame.display.set_mode((width, height), flags)

	clock = pygame.time.Clock()

	# Try to load a background image for the play screen (optional).
	# If `play_bg.jpg` isn't present, pick the first image found in
	# `interface/assets/images/` (supports jpg/png/etc.).
	background_image = None
	try:
		base = os.path.dirname(__file__)
		images_dir = os.path.join(base, "assets", "images")
		candidates = []
		preferred = os.path.join(images_dir, "play_bg.jpg")
		if os.path.exists(preferred):
			candidates.append(preferred)
		if os.path.isdir(images_dir):
			for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp"):
				for p in glob.glob(os.path.join(images_dir, ext)):
					if p not in candidates:
						candidates.append(p)

		if candidates:
			path = candidates[0]
			background_image = pygame.image.load(path).convert()
			if hasattr(pygame.transform, 'smoothscale'):
				background_image = pygame.transform.smoothscale(background_image, (width, height))
			else:
				background_image = pygame.transform.scale(background_image, (width, height))
	except Exception:
		background_image = None

	# Fonts: keep minimal dependencies
	try:
		title_font = pygame.font.SysFont(None, 56)
		button_font = pygame.font.SysFont(None, 28)
	except Exception:
		pygame.font.init()
		title_font = pygame.font.SysFont(None, 56)
		button_font = pygame.font.SysFont(None, 28)

	# Back button at top-left
	back_rect = pygame.Rect(20, 20, 110, 44)

	# Board matrix (8x8) for the chessboard - 0 means empty tile for now
	board_size = 8
	board_matrix = [[0 for _ in range(board_size)] for _ in range(board_size)]

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if back_rect.collidepoint(event.pos):
					running = False

		# Draw background image if available, otherwise a solid color.
		if background_image is not None:
			screen.blit(background_image, (0, 0))
			# Dim the image slightly so the board and UI remain readable
			dim = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
			dim.fill((0, 0, 0, 64))
			screen.blit(dim, (0, 0))
		else:
			draw_background(screen, (30, 30, 35))

		# Title
		render_text_center(screen, "Knight's Tour Board", title_font, color=(240, 240, 240), y_offset=-40)

		# Compute board drawing area (keeps square cells)
		screen_w, screen_h = screen.get_size()
		max_board_px = int(min(screen_w, screen_h) * 0.6)
		square_px = max(8, max_board_px // board_size)
		board_px = square_px * board_size
		board_x = screen_w // 2 - board_px // 2
		# place board a bit below the title
		board_y = screen_h // 2 - board_px // 2 + 40

		# Draw chessboard squares from the matrix
		# Colors: charcoal dark brown and boken latte white approximations
		light = (238, 224, 200)   # boken latte white
		dark = (60, 45, 35)       # charcoal dark brown
		for r in range(board_size):
			for c in range(board_size):
				col = light if (r + c) % 2 == 0 else dark
				cell_rect = pygame.Rect(board_x + c * square_px, board_y + r * square_px, square_px, square_px)
				pygame.draw.rect(screen, col, cell_rect)
				# optional thin border for clarity
				pygame.draw.rect(screen, (30, 30, 30), cell_rect, 1)

		# Draw back button
		draw_button(screen, back_rect, "Back", button_font, bg=(70, 70, 100), fg=(255, 255, 255))

		pygame.display.flip()
		clock.tick(60)

	# Returning to menu
