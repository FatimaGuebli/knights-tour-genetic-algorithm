import sys
import os
import glob
import pygame
from .display import draw_background, render_text_center, draw_button
from population import Population


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

	# Load the explicitly named game background `game_bg.jpg` only.
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

	# Fonts: keep minimal dependencies
	try:
		title_font = pygame.font.SysFont(None, 56)
		button_font = pygame.font.SysFont(None, 28)
	except Exception:
		pygame.font.init()
		title_font = pygame.font.SysFont(None, 56)
		button_font = pygame.font.SysFont(None, 28)

	# Small font for board cell placeholders
	small_font = pygame.font.SysFont(None, 18)
	# Larger font for the visited-positions list (more readable)
	# Increased size to improve readability per user request
	list_font = pygame.font.SysFont(None, 28)
	# Scroll offset in rows for the visited list (0 = top)
	list_scroll = 0
	# Pause flag for walkthrough animation
	paused = False

	# Load knight piece image (optional)
	knight_image = None
	try:
		kp_path = os.path.join(os.path.dirname(__file__), "assets", "images", "knight_piece.png")
		if os.path.exists(kp_path):
			knight_image = pygame.image.load(kp_path).convert_alpha()
	except Exception:
		knight_image = None

	# Back button at top-left
	back_rect = pygame.Rect(20, 20, 110, 44)

	# Start position selection (1-based row/column for the user)
	start_row = 1
	start_col = 1

	# Board matrix (8x8) for the chessboard - 0 means empty tile for now
	board_size = 8
	board_matrix = [[0 for _ in range(board_size)] for _ in range(board_size)]
	# Visited/rank matrix for algorithm output (None = unvisited)
	visited_matrix = [[None for _ in range(board_size)] for _ in range(board_size)]

	running = True
	algorithm_running = False
	algorithm_path = []
	algorithm_index = 0
	last_move_time = 0
	# milliseconds between moves; increase to slow down animation
	move_delay_ms = 800
	while running:
		# Compute board drawing area (keeps square cells) at top so events
		# can reference the positions/rects.
		screen_w, screen_h = screen.get_size()
		max_board_px = int(min(screen_w, screen_h) * 0.6)
		square_px = max(8, max_board_px // board_size)
		board_px = square_px * board_size
		board_x = screen_w // 2 - board_px // 2
		# place board a bit below the title
		board_y = screen_h // 2 - board_px // 2 + 40

		# Control button rects (to use in event handling)
		controls_x = board_x + board_px + 24
		controls_y = board_y
		btn_w, btn_h = 28, 28
		row_minus = pygame.Rect(controls_x, controls_y + 22, btn_w, btn_h)
		row_plus = pygame.Rect(controls_x + btn_w + 6, controls_y + 22, btn_w, btn_h)
		col_minus = pygame.Rect(controls_x, controls_y + 90, btn_w, btn_h)
		col_plus = pygame.Rect(controls_x + btn_w + 6, controls_y + 90, btn_w, btn_h)
		start_btn = pygame.Rect(controls_x, controls_y + 140, btn_w * 2 + 6, btn_h + 6)
		# Pause/Resume button (for walkthrough)
		pause_btn = pygame.Rect(controls_x, controls_y + 180, btn_w * 2 + 6, btn_h + 6)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
			elif event.type == pygame.MOUSEWHEEL:
				# Only scroll if mouse is over the left list area
				mx, my = pygame.mouse.get_pos()
				left_panel_width = 220
				if mx < left_panel_width:
					# event.y positive => wheel up ; negative => wheel down
					list_scroll -= event.y
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				mx, my = event.pos
				# Back button
				if back_rect.collidepoint((mx, my)):
					running = False
				# Row/col +/- buttons
				elif row_minus.collidepoint((mx, my)):
					start_row = max(1, start_row - 1)
				elif row_plus.collidepoint((mx, my)):
					start_row = min(board_size, start_row + 1)
				elif col_minus.collidepoint((mx, my)):
					start_col = max(1, start_col - 1)
				elif col_plus.collidepoint((mx, my)):
					start_col = min(board_size, start_col + 1)
				# Start algorithm
				elif start_btn.collidepoint((mx, my)):
					# Run the genetic algorithm (population.py) synchronously but keep the
					# UI responsive by pumping events and drawing progress.
					population_size = 50
					max_generations = 500
					population = Population(population_size)
					# Set the start position for every knight in the population so that
					# check_moves uses the selected start from the UI without changing
					# the Population core implementation.
					start_pos = (start_row - 1, start_col - 1)
					for k in population.knights:
						k.position = start_pos
						k.path = [start_pos]
						k.fitness = 0

					best = None
					best_fitness = 0
					# Run generations
					while True:
						# Evaluate and update moves
						population.check_population()
						best_fitness, best = population.evaluate()
						# Draw a small progress indicator so the window doesn't appear frozen
						surf = pygame.Surface(screen.get_size())
						surf.set_alpha(0)
						# Render progress text
						pg_text = f"Running GA... Gen: {population.generation}  Best: {best_fitness}"
						render_text_center(screen, pg_text, button_font, color=(220, 220, 220), y_offset=screen.get_height()//2 - 10)
						pygame.display.flip()
						# Stop conditions
						if best_fitness == 64:
							break
						if population.generation >= max_generations:
							break
						# Create next generation
						population.create_new_generation()
						# Ensure new knights start from the selected start position
						for k in population.knights:
							k.position = start_pos
							k.path = [start_pos]
							k.fitness = 0
						# Keep the event queue serviced so window remains responsive
						for e in pygame.event.get():
							if e.type == pygame.QUIT:
								pygame.quit()
								sys.exit()

					# After GA finishes, animate the best knight's path if available
					algorithm_path = []
					if best is not None:
						# best.path should be a list of (row,col) positions
						algorithm_path = best.path.copy()
					algorithm_index = 0
					# reset visited matrix and mark initial position with rank 0
					visited_matrix = [[None for _ in range(board_size)] for _ in range(board_size)]
					if algorithm_path:
						# initial position
						sr, sc = algorithm_path[0]
						visited_matrix[sr][sc] = 0
						algorithm_running = True
						last_move_time = pygame.time.get_ticks()
				# Pause/Resume button
				elif pause_btn.collidepoint((mx, my)):
					# Toggle only when an animation is present
					paused = not paused
				# Click on the board sets the start position
				elif board_x <= mx < board_x + board_px and board_y <= my < board_y + board_px:
					c = (mx - board_x) // square_px
					r = (my - board_y) // square_px
					start_row = int(r) + 1
					start_col = int(c) + 1

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

		# Left-side list: show visited positions arranged in rows of 20 items
		left_x = 16
		list_y = 80
		line_h = list_font.get_linesize() if hasattr(list_font, 'get_linesize') else 20
		items_per_row = 20
		# Build positions list from algorithm_path if available else from visited_matrix
		raw_positions = []
		if algorithm_path:
			for i, (r, c) in enumerate(algorithm_path):
				raw_positions.append((i, (r + 1, c + 1)))
		else:
			for r in range(board_size):
				for c in range(board_size):
					val = visited_matrix[r][c]
					if val is not None:
						raw_positions.append((val, (r + 1, c + 1)))
		# Sort by rank/index and deduplicate by position (keep first occurrence)
		raw_positions.sort(key=lambda x: x[0])
		positions_list = []
		seen_positions = set()
		for rank, pos in raw_positions:
			if pos in seen_positions:
				continue
			seen_positions.add(pos)
			positions_list.append((rank, pos))

		# Header
		hdr = list_font.render("Visited positions:", True, (240, 240, 230))
		screen.blit(hdr, (left_x, list_y))
		y_start = list_y + line_h
		screen_h = screen.get_height()
		# How many rows fit vertically using the list font
		visible_rows = max(1, (screen_h - y_start - 20) // line_h)

		# Determine total rows and clamp scroll
		total_items = len(positions_list)
		total_rows = (total_items + items_per_row - 1) // items_per_row if total_items else 1
		max_row_scroll = max(0, total_rows - visible_rows)
		if list_scroll < 0:
			list_scroll = 0
		elif list_scroll > max_row_scroll:
			list_scroll = max_row_scroll

		# Compute available width for the left panel (space before board)
		available_w = max(120, max(0, board_x - 32))
		# Measure the widest visible item to determine column width
		max_text_w = 0
		pad_x = 8
		for rank, pos in positions_list:
			text = f"{rank}: {pos}"
			w, _h = list_font.size(text)
			if w > max_text_w:
				max_text_w = w

		# Compute how many columns fit into available_w
		col_w = max_text_w + pad_x
		if col_w <= 0:
			col_w = 80
		cols_fit = max(1, available_w // col_w)
		# We cap columns to items_per_row (user request) but never exceed cols_fit
		cols = min(items_per_row, cols_fit)
		if cols <= 0:
			cols = 1

		# Recompute total rows with the number of columns we will render
		rows_needed = (total_items + cols - 1) // cols if cols else 1
		# Clamp scroll to the number of rows
		max_row_scroll = max(0, rows_needed - visible_rows)
		if list_scroll < 0:
			list_scroll = 0
		elif list_scroll > max_row_scroll:
			list_scroll = max_row_scroll

		# Render visible rows (each row contains up to cols entries)
		for row_offset in range(visible_rows):
			row = list_scroll + row_offset
			for col in range(cols):
				idx = row * cols + col
				if idx >= total_items:
					break
				rank, pos = positions_list[idx]
				text = f"{rank}: {pos}"
				surf = list_font.render(text, True, (200, 200, 200))
				col_x = left_x + col * col_w
				screen.blit(surf, (col_x, y_start + row_offset * line_h))

		# If there are rows below the visible area, show a small indicator
		if rows_needed > visible_rows:
			below = rows_needed - (list_scroll + visible_rows)
			if below > 0:
				more = list_font.render(f"... +{below} more rows", True, (180, 180, 180))
				screen.blit(more, (left_x, y_start + visible_rows * line_h))

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


				# Center point for rendering numbers
				center = cell_rect.center
				if (r + c) % 2 == 0:
					text_color = (70, 50, 35)
				else:
					text_color = (240, 230, 210)
				# Render visited rank if available, otherwise a null placeholder
				if visited_matrix[r][c] is not None:
					val = str(visited_matrix[r][c])
					if hasattr(small_font, 'render_to'):
						rect = small_font.get_rect(val)
						tx = center[0] - rect.width // 2
						ty = center[1] - rect.height // 2
						small_font.render_to(screen, (tx, ty), val, fgcolor=text_color)
					else:
						surf = small_font.render(val, True, text_color)
						screen.blit(surf, surf.get_rect(center=center))
				else:
					placeholder = "-"
					if hasattr(small_font, 'render_to'):
						rect = small_font.get_rect(placeholder)
						tx = center[0] - rect.width // 2
						ty = center[1] - rect.height // 2
						small_font.render_to(screen, (tx, ty), placeholder, fgcolor=text_color)
					else:
						surf = small_font.render(placeholder, True, text_color)
						screen.blit(surf, surf.get_rect(center=center))

		# Draw back button
		draw_button(screen, back_rect, "Back", button_font, bg=(70, 70, 100), fg=(255, 255, 255))

		# Controls: show selection labels and +/- buttons to adjust start row/col
		# Position controls to the right of the board (rects defined earlier)
		row_label = small_font.render(f"Line: {start_row}", True, (240, 240, 230))
		screen.blit(row_label, (controls_x, controls_y))
		draw_button(screen, row_minus, "-", small_font, bg=(90, 40, 20), fg=(240, 230, 200))
		draw_button(screen, row_plus, "+", small_font, bg=(90, 40, 20), fg=(240, 230, 200))

		# Column controls
		col_label = small_font.render(f"Column: {start_col}", True, (240, 240, 230))
		screen.blit(col_label, (controls_x, controls_y + 68))
		draw_button(screen, col_minus, "-", small_font, bg=(90, 40, 20), fg=(240, 230, 200))
		draw_button(screen, col_plus, "+", small_font, bg=(90, 40, 20), fg=(240, 230, 200))

		# Start algorithm button
		draw_button(screen, start_btn, "Start algorithm", small_font, bg=(30, 120, 70), fg=(240, 240, 240))
		# Pause/Resume button: show disabled style if nothing to pause
		if algorithm_running:
			label = "Resume" if paused else "Pause"
			bg = (200, 100, 40) if paused else (30, 120, 70)
		else:
			label = "Pause"
			bg = (80, 80, 80)
		draw_button(screen, pause_btn, label, small_font, bg=bg, fg=(240, 240, 240))

		# Draw the knight image at the selected start position if available
		if knight_image is not None:
			kr = start_row - 1
			kc = start_col - 1
			if 0 <= kr < board_size and 0 <= kc < board_size:
				cell_center_x = board_x + kc * square_px + square_px // 2
				cell_center_y = board_y + kr * square_px + square_px // 2
				# scale knight image to fit inside cell
				ks = int(square_px * 0.75)
				try:
					ks_img = pygame.transform.smoothscale(knight_image, (ks, ks))
				except Exception:
					ks_img = pygame.transform.scale(knight_image, (ks, ks))
				rect = ks_img.get_rect(center=(cell_center_x, cell_center_y))
				screen.blit(ks_img, rect)

		# If algorithm running, step through path with timing (respect pause)
		if algorithm_running and algorithm_path and not paused:
			now = pygame.time.get_ticks()
			if now - last_move_time >= move_delay_ms:
				last_move_time = now
				algorithm_index += 1
				if algorithm_index < len(algorithm_path):
					rp, cp = algorithm_path[algorithm_index]
					start_row = rp + 1
					start_col = cp + 1
					# mark visited rank for this move
					visited_matrix[rp][cp] = algorithm_index
				else:
					algorithm_running = False

		pygame.display.flip()
		clock.tick(60)

	# Returning to menu


def test_algorithm(start_r: int, start_c: int, rows: int, cols: int):
	"""Test algorithm: produce a simple path where the knight (test) moves
	strictly to the right each step; when reaching the last column it jumps
	to column 0 of the next row, and continues until the last cell.

	Returns a list of `(row, col)` positions including the starting cell
	as the first element. Coordinates are 0-based.

	This function is intentionally simple and placed at the end of the
	file so you can comment it out or replace it later.
	"""
	path = []
	if start_r < 0 or start_c < 0 or start_r >= rows or start_c >= cols:
		return path
	r = start_r
	c = start_c
	path.append((r, c))
	# Continue until we reach the final cell
	while not (r == rows - 1 and c == cols - 1):
		if c < cols - 1:
			c += 1
		else:
			c = 0
			r += 1
			if r >= rows:
				break
		path.append((r, c))
	return path
