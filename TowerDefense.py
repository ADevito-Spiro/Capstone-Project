import random, pygame, os, math, button, TextLabel, yolo, threading, queue, json

class Game:
    def __init__(self):
        # Game constants
        self.screen_width = 1280
        self.screen_height = 720
        self.runTime = 0

        # Game variables
        self.invalid_piece_positions = []
        self.enemies = []
        self.projectiles = []
        self.defenders = []
        self.wave = 0
        self.enemy_spawn_timer = 0
        self.health = 100
        self.game_over = False
        self.game_won = False
        self.game_started = False
        self.in_space_mode = False
        self.gravity_shift_active = False
        self.gravity_scatter_triggered = False
        self.black_hole_active = False
        self.black_hole_radius = 0
        self.space_background_visible = False
        self.preparation_phase = False

        self.rounds = [
            {"enemies": 6, "color": "red", "speed_multiplier": 1.8, "spawn_delay": 60, "health": 125},
            {"enemies": 12, "color": "blue", "speed_multiplier": 2.2, "spawn_delay": 50, "health": 150},
            {"enemies": 18, "color": "yellow", "speed_multiplier": 2.4, "spawn_delay": 44, "health": 175},
            {"enemies": 21, "color": "green", "speed_multiplier": 2.6, "spawn_delay": 38, "health": 200}
        ]
        self.current_round = 0
        self.enemies_spawned_in_round = 0
        self.allowed_defenders = self.current_round + 1
        self.between_rounds = False
        self.running = True
        self.paused = False
        self.pauseLoaded = False
        self.currentMode = "MainMenu"
        self.arrow_progress = 0.0
        self.arrow_speed = 0.05
        self.invalid_defender_count = False

        # PyGame Setup
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption('Computer Vision Enhanced Game Board')
        self.clock = pygame.time.Clock()

        # Initialize assets and UI
        self.load_assets()
        self.current_screen_objects = [*self.main_menu_assets]

        # Add a queue to receive YOLO data
        self.yolo_queue = queue.Queue()
        # Store the latest detected pieces
        self.detected_pieces = {}

    def load_assets(self):
        # Declare directory and file path for all Assets
        self.directory = os.path.dirname(__file__)
        self.asset_path = os.path.join(self.directory, "Assets")

        # Declare Assets
        self.title_img = pygame.image.load(os.path.join(self.asset_path, 'title.png')).convert_alpha()
        self.title_img = pygame.transform.scale(self.title_img, (566, 164))
        self.play_img = pygame.image.load(os.path.join(self.asset_path, 'play.png')).convert_alpha()
        self.play_imgOn = pygame.image.load(os.path.join(self.asset_path, 'playOn.png')).convert_alpha()
        self.exit_img = pygame.image.load(os.path.join(self.asset_path, 'exit.png')).convert_alpha()
        self.exit_imgOn = pygame.image.load(os.path.join(self.asset_path, 'exitOn.png')).convert_alpha()
        self.pause_img = pygame.image.load(os.path.join(self.asset_path, 'pause.png')).convert_alpha()
        self.pause_imgOn = pygame.image.load(os.path.join(self.asset_path, 'pauseOn.png')).convert_alpha()
        self.arrow_img = pygame.transform.scale(pygame.image.load(os.path.join(self.asset_path, 'arrow.png')).convert_alpha(), (48, 48))
        self.background_img = pygame.image.load(os.path.join(self.asset_path, 'space_background.jpg')).convert()
        self.background_img = pygame.transform.scale(self.background_img, (self.screen_width, self.screen_height))
        self.pop_sound = pygame.mixer.Sound(os.path.join(self.asset_path, 'pop.mp3'))
        self.black_hole_sound = pygame.mixer.Sound(os.path.join(self.asset_path, 'blackhole.mp3'))

        pygame.mixer.music.load(os.path.join(self.asset_path, "main_song.mp3"))
        pygame.mixer.music.set_volume(0.1)  # Volume 10%
        pygame.mixer.music.play(-1)

        title_rect = self.title_img.get_rect(center=(self.screen_width // 2, self.screen_height // 6 + 75))
        self.title_image_data = (self.title_img, title_rect)

        self.piece_images = {
            "white-rook": pygame.image.load(os.path.join(self.asset_path, 'rook.png')).convert_alpha(),
            "white-pawn": pygame.image.load(os.path.join(self.asset_path, 'pawn.png')).convert_alpha(),
            "white-bishop": pygame.image.load(os.path.join(self.asset_path, 'bishop.png')).convert_alpha(),
            "white-queen": pygame.image.load(os.path.join(self.asset_path, 'queen.png')).convert_alpha(),
            "white-king": pygame.image.load(os.path.join(self.asset_path, 'king.png')).convert_alpha(),
            "white-knight": pygame.image.load(os.path.join(self.asset_path, 'knight.png')).convert_alpha()
        }

        self.enemy_images = {
            "red": pygame.image.load(os.path.join(self.asset_path, 'red.png')).convert_alpha(),
            "blue": pygame.image.load(os.path.join(self.asset_path, 'blue.png')).convert_alpha(),
            "yellow": pygame.image.load(os.path.join(self.asset_path, 'yellow.png')).convert_alpha(),
            "florin": pygame.image.load(os.path.join(self.asset_path, 'florin.png')).convert_alpha(),
            "green": pygame.image.load(os.path.join(self.asset_path, 'green.png')).convert_alpha(),
            "pink": pygame.image.load(os.path.join(self.asset_path, 'pink.png')).convert_alpha()
        }

        # Initialize UI assets
        button_scale = 1.5
        center_x = self.screen_width // 2
        start_y = self.screen_height // 2
        spacing = 150

        # Play Button
        play_button = button.Button(0, 0, self.play_img, self.play_imgOn, button_scale, "Play")
        play_button.rect.center = (center_x, start_y)

        # Exit Button
        exit_button = button.Button(0, 0, self.exit_img, self.exit_imgOn, button_scale, "Exit")
        exit_button.rect.center = (center_x, start_y + spacing)

        # Add to UI asset list
        self.main_menu_assets = [
            play_button,
            exit_button,
        ]

        self.game_assets = [
            button.Button((self.screen_width / 2) - 215, self.screen_height - 65, self.pause_img, self.pause_imgOn, 0.7, "Pause"),
            button.Button((self.screen_width / 2) + 125, self.screen_height - 65, self.exit_img, self.exit_imgOn, 0.7, "Exit"),
        ]

        self.pause_txt = TextLabel.TextLabel(self.screen_width // 2, self.screen_height // 2, "PAUSED", 84, "pause_label", 'bahnschrift')

    def get_board_info(self):
        board_size = 6
        box_x = self.screen.get_width() - 875
        box_y = 150
        box_width = 500
        box_height = 500
        square_size = min(box_width, box_height) // board_size
        return board_size, box_x, box_y, square_size

    # Create and draw the path that the enemies will follow
    def create_path(self):
        board_size, box_x, box_y, square_size = self.get_board_info()
        path = [(box_x - 30, box_y + square_size // 2)]

        custom_path = [
            (0, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1),
            (5, 1), (5, 2), (5, 3), (4, 3), (3, 3), (3, 4), (3, 5)
        ]

        for row, col in custom_path:
            x = box_x + (col * square_size) + square_size // 2
            y = box_y + (row * square_size) + square_size // 2
            path.append((x, y))

        last_x, last_y = path[-1]  # Last point of the path
        path.append((last_x + 50, last_y))  # Exit right from last path point
        return path

    # Draw the path highlight
    def draw_path_highlight(self, path):
        board_size, box_x, box_y, square_size = self.get_board_info()
        path_color = (255, 255, 0)
        path_alpha = 100

        for pos in path[1:-1]:
            x, y = pos
            x -= square_size // 2
            y -= square_size // 2
            highlight = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            highlight.fill((*path_color, path_alpha))
            self.screen.blit(highlight, (x, y))

    # Read the queue to get the pieces from the object detection/chessboard detection script
    def load_detected_pieces(self):
        path = "./detected_pieces.json"
        try:
            if os.path.isfile(path):
                with open(path, "r") as f:
                    data = json.load(f)
                    self.detected_pieces = data
                    return data
            else:
                try:
                    self.detected_pieces = self.yolo_queue.get_nowait()
                    return self.detected_pieces
                except queue.Empty:
                    return self.detected_pieces
        except Exception as e:
            print(f"Error loading pieces: {e}")
            return self.detected_pieces

    # Draw the chessboard on the screen, assign each box a column and row signifier to make placing pieces/images easier.
    def draw_chessboard(self):
        board_size, box_x, box_y, square_size = self.get_board_info()

        detected_pieces = self.load_detected_pieces()

        font = pygame.font.SysFont('bahnschrift', 20)

        # Draw column letters at the top
        for col in range(board_size):
            letter = chr(65 + col)  # A to G
            text = font.render(letter, True, (255, 255, 255))
            text_rect = text.get_rect(center=(box_x + col * square_size + square_size // 2, box_y - 20))
            self.screen.blit(text, text_rect)

        # Draw row numbers on the left side
        for row in range(board_size):
            number = str(row + 1)
            text = font.render(number, True, (255, 255, 255))
            text_rect = text.get_rect(center=(box_x - 20, box_y + row * square_size + square_size // 2))
            self.screen.blit(text, text_rect)

        # Draw the board squares
        for row in range(board_size):
            for col in range(board_size):
                x, y = box_x + col * square_size, box_y + row * square_size
                color = (255, 255, 255) if (row + col) % 2 == 0 else (0, 0, 0)
                pygame.draw.rect(self.screen, color, pygame.Rect(x, y, square_size, square_size))

        # Draw pieces
        for board_pos, piece in detected_pieces.items():
            col = ord(board_pos[0]) - 65  # 'A' to 0
            row = int(board_pos[1]) - 1

            x = box_x + col * square_size
            y = box_y + row * square_size

            if piece in self.piece_images:
                piece_img = pygame.transform.scale(self.piece_images[piece], (square_size, square_size))
                self.screen.blit(piece_img, (x, y))

            else:
                print(f"Error: {piece} not found in piece_images!")

    def is_position_on_path(self, col, row):
        # Match the logic from create_path and yolo.py exactly
        path_positions = [
            (0, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1),
            (5, 1), (5, 2), (5, 3), (4, 3), (3, 3), (3, 4), (3, 5)
        ]
        return (row, col) in path_positions

    def validate_defender_count(self):
        return len(self.defenders) <= self.allowed_defenders

    # Handle enemy spawning and round movement
    # Increase documentation here
    def update_defense(self):
        if self.game_over or self.paused or self.preparation_phase or self.game_won:
            return

        # Clear invalid states
        self.invalid_piece_positions = []
        self.invalid_defender_count = False
        self.defenders = []

        # Update defenders from detected pieces
        detected_pieces = self.load_detected_pieces()
        board_size, box_x, box_y, square_size = self.get_board_info()

        for board_pos, piece in detected_pieces.items():
            col = ord(board_pos[0]) - 65
            row = int(board_pos[1]) - 1

            if self.is_position_on_path(col, row):
                self.invalid_piece_positions.append(board_pos)
            else:
                x = box_x + col * square_size + square_size // 2
                y = box_y + row * square_size + square_size // 2
                self.defenders.append(Defender(x, y, piece))

        # Validate defender count
        if not self.validate_defender_count():
            self.invalid_defender_count = True

        # Stop updates if invalid pieces or defender count during preparation or between rounds
        if self.invalid_piece_positions or self.invalid_defender_count:
            return

        # Remove dead enemies and projectiles
        self.projectiles = [p for p in self.projectiles if not p.reached_target]

        # Handle enemy spawning and round progression
        if not self.between_rounds and self.game_started:
            if self.current_round < len(self.rounds):
                round_data = self.rounds[self.current_round]

                if self.enemies_spawned_in_round < round_data["enemies"]:
                    if self.enemy_spawn_timer <= 0:
                        path = self.create_path()
                        color = round_data.get("color", "red")
                        speed = round_data["speed_multiplier"]
                        health = round_data.get("health")

                        new_enemy = Enemy(path, color=color, speed_multiplier=speed, game=self)

                        if health:
                            new_enemy.health = health
                            new_enemy.max_health = health

                        self.enemies.append(new_enemy)

                        self.enemies_spawned_in_round += 1
                        self.enemy_spawn_timer = round_data["spawn_delay"]
                    else:
                        self.enemy_spawn_timer -= 1

                if self.enemies_spawned_in_round >= round_data["enemies"] and len(self.enemies) == 0:
                    self.enemies_spawned_in_round = 0
                    if self.current_round + 1 < len(self.rounds):
                        self.between_rounds = True
                        # Reset special effects for next round
                        self.gravity_shift_active = False
                        self.gravity_scatter_triggered = False
                        self.in_space_mode = False
                    else:
                        self.game_won = True

                #Trigger scatter event
                if not self.gravity_scatter_triggered: # Currently this makes a black hole for every single wave, not sure if I like this more or not yet
                    if self.enemies_spawned_in_round >= self.rounds[self.current_round]["enemies"] // 2: # Trigger gravity when all the balloons of the wave have spawned
                        self.gravity_shift_active = True
                        self.gravity_scatter_triggered = True
                        self.black_hole_active = True
                        self.black_hole_radius = 0
                        if game.black_hole_sound:
                            game.black_hole_sound.play()
                        self.in_space_mode = True
                        self.space_background_visible = True
                        for enemy in self.enemies:
                            enemy.start_gravity_scatter()    
            else:
                if len(self.enemies) == 0:
                    self.game_won = True

        # Update enemies
        new_enemies = []
        remaining_enemies = []

        for enemy in self.enemies:
            enemy.move()
            if enemy.reached_end:
                self.enemies.remove(enemy)
                self.health -= 10
                self.game_over = True

            if enemy.health <= 0:
                if game.pop_sound:
                    game.pop_sound.play()

                match enemy.color:
                    case "pink":
                        new_enemy = Enemy(enemy.path, color="green", speed_multiplier=enemy.speed, game=self)
                        new_enemy.x, new_enemy.y = enemy.x, enemy.y
                        new_enemy.path_index = enemy.path_index
                        new_enemies.append(new_enemy)
                    case "green":
                        new_enemy = Enemy(enemy.path, color="yellow", speed_multiplier=enemy.speed, game=self)
                        new_enemy.x, new_enemy.y = enemy.x, enemy.y
                        new_enemy.path_index = enemy.path_index
                        new_enemies.append(new_enemy)
                    case "yellow":
                        new_enemy = Enemy(enemy.path, color="blue", speed_multiplier=enemy.speed, game=self)
                        new_enemy.x, new_enemy.y = enemy.x, enemy.y
                        new_enemy.path_index = enemy.path_index
                        new_enemies.append(new_enemy)
                    case "blue":
                        new_enemy = Enemy(enemy.path, color="red", speed_multiplier=enemy.speed, game=self)
                        new_enemy.x, new_enemy.y = enemy.x, enemy.y
                        new_enemy.path_index = enemy.path_index
                        new_enemies.append(new_enemy)
                continue

            remaining_enemies.append(enemy)

        self.enemies = remaining_enemies + new_enemies

        # Update defenders and projectiles
        for defender in self.defenders:
            projectile = defender.update(self.enemies)
            if projectile:
                self.projectiles.append(projectile)

        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.move()

    # Handle round complete screen
    def draw_between_rounds(self):
        font_large = pygame.font.SysFont('bahnschrift', 48)
        font_medium = pygame.font.SysFont('bahnschrift', 32)

        # Semi-transparent overlay
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 64))
        self.screen.blit(s, (0, 0))

        # Round complete message
        round_text = font_large.render(f"Round {self.current_round + 1} Complete!", True, (255, 255, 0))
        self.screen.blit(round_text, (self.screen_width // 2 - round_text.get_width() // 2, self.screen_height // 2 - 100))

        # Instructions
        next_text = font_medium.render(f"Press SPACE to continue", True, (255, 255, 255))
        self.screen.blit(next_text, (self.screen_width // 2 - next_text.get_width() // 2, self.screen_height // 2))

        # Display errors if any
        if self.invalid_piece_positions:
            error_text = font_medium.render(f"Pieces on path at {', '.join(self.invalid_piece_positions)}! Move them to proceed.", True, (255, 0, 0))
            self.screen.blit(error_text, (self.screen_width // 2 - error_text.get_width() // 2, self.screen_height // 2 + 50))
        if len(self.defenders) > self.current_round + 2:
            error_text = font_medium.render(f"Need at most {self.current_round + 2} defender(s), found {len(self.defenders)}!", True, (255, 0, 0))
            self.screen.blit(error_text, (self.screen_width // 2 - error_text.get_width() // 2, self.screen_height // 2 + 100))

    # Handle preparation phase screen
    def draw_preparation_phase(self):
        font_large = pygame.font.SysFont('bahnschrift', 48)
        font_medium = pygame.font.SysFont('bahnschrift', 32)

        # Semi-transparent overlay (more transparent)
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 64))
        self.screen.blit(s, (0, 0))

        # Preparation phase message
        prep_text = font_large.render(f"Prepare for Round {self.current_round + 2}", True, (255, 255, 0))
        self.screen.blit(prep_text, (self.screen_width // 2 - prep_text.get_width() // 2, self.screen_height // 2 - 100))

        # Instructions
        instruction_text = font_medium.render(f"You may have a total of {self.current_round + 2} defenders, then press SPACE to start", True, (255, 255, 255))
        self.screen.blit(instruction_text, (self.screen_width // 2 - instruction_text.get_width() // 2, self.screen_height // 2))

        # Display errors if any
        if self.invalid_piece_positions:
            error_text = font_medium.render(f"Pieces on path at {', '.join(self.invalid_piece_positions)}! Move them to proceed.", True, (255, 0, 0))
            self.screen.blit(error_text, (self.screen_width // 2 - error_text.get_width() // 2, self.screen_height // 2 + 50))
        if len(self.defenders) > self.current_round + 2:
            error_text = font_medium.render(f"Need at most {self.current_round + 2} defender(s), found {len(self.defenders)}!", True, (255, 0, 0))
            self.screen.blit(error_text, (self.screen_width // 2 - error_text.get_width() // 2, self.screen_height // 2 + 100))

    # Handle win screen
    def draw_win_screen(self):
        font_large = pygame.font.SysFont('bahnschrift', 48)
        font_medium = pygame.font.SysFont('bahnschrift', 32)

        # Semi-transparent overlay
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 64))
        self.screen.blit(s, (0, 0))

        # Victory message
        win_text = font_large.render("Victory! You Defeated All Waves!", True, (0, 255, 0))
        self.screen.blit(win_text, (self.screen_width // 2 - win_text.get_width() // 2, self.screen_height // 2 - 100))

        # Instructions
        restart_text = font_medium.render("Press R to Restart", True, (255, 255, 255))
        exit_text = font_medium.render("Press ESC to Exit", True, (255, 255, 255))
        self.screen.blit(restart_text, (self.screen_width // 2 - restart_text.get_width() // 2, self.screen_height // 2))
        self.screen.blit(exit_text, (self.screen_width // 2 - exit_text.get_width() // 2, self.screen_height // 2 + 50))

    # Handle rendering of some UI elements, render the enemies, the path, the projectiles, and the defenders
    def draw_defense(self):
        # Draw path
        path = self.create_path()
        self.draw_path_highlight(path)

        # Clamp progress
        self.arrow_progress = min(self.arrow_progress + self.arrow_speed, len(path) - 1)

        i = int(self.arrow_progress)
        t = self.arrow_progress - i

        if i < len(path) - 1 and self.game_started is False:
            start = pygame.Vector2(path[i])
            end = pygame.Vector2(path[i + 1])
            pos = start.lerp(end, t)

            # Get direction vector for rotating the arrow
            direction = pygame.Vector2(end.x - start.x, -(end.y - start.y)).normalize()
            angle = direction.angle_to(pygame.Vector2(1, 0))

            rotated_arrow = pygame.transform.rotate(self.arrow_img, -angle)
            rect = rotated_arrow.get_rect(center=pos)
            self.screen.blit(rotated_arrow, rect.topleft)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)

        # Draw UI
        font = pygame.font.SysFont('bahnschrift', 24)
        wave_text = font.render(f"Wave: {self.current_round + 1}", True, (255, 255, 255))

        if self.current_round < len(self.rounds):
            enemies_remaining = self.rounds[self.current_round]["enemies"] - self.enemies_spawned_in_round + len(self.enemies)
            enemies_text = font.render(f"Enemies Left: {enemies_remaining}/{self.rounds[self.current_round]['enemies']}", True,
                                      (255, 255, 255))
        else:
            enemies_text = font.render("Enemies Left: 0/0", True, (255, 255, 255))

        self.screen.blit(wave_text, (600, self.screen_height / 22))
        self.screen.blit(enemies_text, (self.screen_width / 18, self.screen_height / 22))

        # Display errors during paused state or non-preparation/non-between-rounds phases
        if (self.invalid_piece_positions or self.invalid_defender_count) and not (self.preparation_phase or self.between_rounds):
            if self.invalid_piece_positions:
                error_text = font.render(f"Pieces on path at {', '.join(self.invalid_piece_positions)}! Move them to proceed.", True, (255, 0, 0))
                error_rect = error_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 200))
                self.screen.blit(error_text, error_rect)
            if self.invalid_defender_count:
                error_message = font.render(f"Need at most {self.allowed_defenders} defender(s), found {len(self.defenders)}!", True, (255, 0, 0))
                error_rect = error_message.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 150))
                self.screen.blit(error_message, error_rect)

        if self.game_won:
            self.draw_win_screen()
        elif self.preparation_phase:
            self.draw_preparation_phase()
        elif self.between_rounds:
            self.draw_between_rounds()

        if self.game_over:
            game_over_text = font.render("GAME OVER - Press R to restart", True, (255, 0, 0))
            start_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 275))
            self.screen.blit(game_over_text, start_rect)

        if not self.game_started and self.currentMode == "Game" and not self.preparation_phase:
            start_text = font.render("Press SPACE to start the game", True, (255, 255, 255))
            start_rect = start_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 275))
            self.screen.blit(start_text, start_rect)

    def reset(self):
        # Reset game state to initial values
        self.enemies.clear()
        self.projectiles.clear()
        self.defenders.clear()
        self.enemy_spawn_timer = 0
        self.health = 100
        self.game_over = False
        self.game_won = False  # Reset win state
        self.game_started = False
        self.current_round = 0
        self.allowed_defenders = self.current_round + 1
        self.enemies_spawned_in_round = 0
        self.between_rounds = False
        self.preparation_phase = False
        self.arrow_progress = 0.0
        self.gravity_shift_active = False
        self.gravity_scatter_triggered = False
        self.black_hole_active = False
        self.black_hole_radius = 0
        self.in_space_mode = False
        self.space_background_visible = False
        self.invalid_piece_positions = []
        self.invalid_defender_count = False

    # Main game loop
    def main_loop(self):
        valid_state = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and self.currentMode == "Game":
                    if event.key == pygame.K_SPACE and not self.game_won:
                        # Update defense to check for invalid pieces or defender count
                        self.update_defense()
                        # Use the defender count for the next round if between rounds or in preparation phase
                        temp_allowed_defenders = self.current_round + 2 if (self.between_rounds or self.preparation_phase) else self.allowed_defenders
                        valid_state = not (self.invalid_piece_positions or len(self.defenders) > temp_allowed_defenders)

                        if not valid_state:
                            continue

                        if not self.game_started and not self.game_over and not self.preparation_phase:
                            self.game_started = True
                        elif self.between_rounds:
                            self.between_rounds = False
                            self.preparation_phase = True
                        elif self.preparation_phase:
                            self.preparation_phase = False
                            self.current_round += 1
                            self.allowed_defenders = self.current_round + 1
                            self.enemy_spawn_timer = 0
                            self.invalid_piece_positions = []
                            self.invalid_defender_count = False
                    if event.key == pygame.K_r and (self.game_over or self.game_won):
                        self.reset()
                    if event.key == pygame.K_ESCAPE and self.game_won:
                        self.running = False

            if self.paused:
                self.screen.fill((0, 0, 0))
                if not self.pauseLoaded:
                    self.current_screen_objects.append(self.pause_txt)
                    self.pauseLoaded = True
            else:
                self.pauseLoaded = False
                # Remove pause text when unpausing
                if self.pause_txt in self.current_screen_objects:
                    self.current_screen_objects.remove(self.pause_txt)

                if self.space_background_visible:
                    self.screen.blit(self.background_img, (0, 0))  # Space themed
                else:
                    self.screen.fill((52, 61, 70))
            if self.currentMode == "MainMenu":
                self.screen.blit(*self.title_image_data)  # Draw the title image only on the main menu

            if self.currentMode == "Game":
                pygame.draw.rect(self.screen, pygame.Color(0, 0, 0), pygame.Rect(0, 0, self.screen_width, 60))
                self.draw_chessboard()
                self.draw_defense()
                self.update_defense()

                valid_state = not (self.invalid_piece_positions or self.invalid_defender_count)

            # Draw UI buttons (both in paused or game)
            for thing in self.current_screen_objects:
                if thing.draw(self.screen):
                    if thing.tag == "Exit":
                        self.running = False
                    if thing.tag == "Play":
                        self.current_screen_objects.clear()
                        self.currentMode = "Game"
                        self.current_screen_objects = [*self.game_assets]
                        self.reset()
                    if thing.tag == "Pause":
                        self.paused = not self.paused

            # Draw black hole and cover the full screen
            if self.black_hole_active:
                 center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
                 pygame.draw.circle(self.screen, (0, 0, 0), center, self.black_hole_radius)
                 self.black_hole_radius += 30
            
                 if self.black_hole_radius > max(self.screen.get_width(), self.screen.get_height()):
                    self.black_hole_active = False
                    self.in_space_mode = True

                    # 30% chance to turn each enemy into Dr. Florin
                    transformed_enemies = []
                    for enemy in self.enemies:
                        if random.random() < 0.30:
                            new_enemy = Enemy(enemy.path, color="florin", speed_multiplier=enemy.speed, game=self)
                            new_enemy.x, new_enemy.y = enemy.x, enemy.y
                            new_enemy.path_index = enemy.path_index
                            transformed_enemies.append(new_enemy)
                        else:
                            transformed_enemies.append(enemy)
                    self.enemies = transformed_enemies

            pygame.display.update()
            self.clock.tick(60)

# Define the Enemy as a class, allow various stats to be edited and defined elsewhere.
class Enemy:
    def __init__(self, path, color="red", speed_multiplier=1.0, game=None):
        self.path = path
        self.path_index = 0
        self.x, self.y = path[0]
        self.speed = speed_multiplier
        self.color = color
        self.size = 30
        self.reached_end = False
        self.alive = True
        self.distance_traveled = 0
        self.invulnerable_time = 30
        self.gravity_scatter = False
        self.gravity_target = None
        self.gravity_active = False
        self.scatter_timer = 0
        self.scatter_direction = pygame.Vector2(0, 0)
        self.game = game
        self.set_stats_by_color()

    def set_stats_by_color(self):
        match self.color:
            case "red":
                self.health = 100
                self.max_health = 100
            case "blue":
                self.health = 200
                self.max_health = 200
            case "yellow":
                self.health = 300
                self.max_health = 300
            case "green":
                self.health = 400
                self.max_health = 400
            case "pink":
                self.health = 500
                self.max_health = 500
            case "florin":
                self.health = 500
                self.max_health = 500
                self.size = 50
            case _:
                self.health = 100
                self.max_health = 100

    def clamp_to_board(self):
        board_size, box_x, box_y, square_size = self.game.get_board_info()

        board_left = box_x
        board_right = box_x + board_size * square_size
        board_top = box_y
        board_bottom = box_y + board_size * square_size

        self.x = max(board_left, min(board_right, self.x))
        self.y = max(board_top, min(board_bottom, self.y))

    def start_gravity_scatter(self):
        board_size, box_x, box_y, square_size = self.game.get_board_info()

        # Pick a random column along the top row
        random_col = random.randint(0, board_size - 1)

        # Final gravity destination after scrambling
        self.gravity_target = (
            box_x + random_col * square_size + square_size // 2,
            box_y + square_size // 2
        )

        # New: scramble mode
        self.scatter_timer = 180  # 3 seconds at 60 FPS
        angle = math.radians(random.randint(0, 360))  # Fixed: Added range for randint
        self.scatter_direction = pygame.Vector2(math.cos(angle), math.sin(angle))

        self.gravity_active = True  # Stay active until reach target

    # Handle Movement of the enemy, ensuring that the enemy follows the defined path, and setting the speed of
    # each enemy so that they aren't on top of each other, but that they can be faster in later rounds
    def move(self):
        if not self.alive:
            return

        # Count down invulnerable time
        if self.invulnerable_time > 0:
            self.invulnerable_time -= 1

        # Scatter balloons during the black hole event
        if self.scatter_timer > 0:
            self.scatter_timer -= 1

            # Wobble the direction of balloons
            wobble_angle = math.radians(random.uniform(-20, 10))
            self.scatter_direction = self.scatter_direction.rotate_rad(wobble_angle)

            # Move balloons around
            scatter_move = self.scatter_direction * self.speed
            self.x += scatter_move.x
            self.y += scatter_move.y

            # Make balloons bounce of the edges if they hit them
            board_left = game.screen.get_width() - 875
            board_top = 150
            board_right = board_left + 500
            board_bottom = board_top + 500

            if self.x <= board_left or self.x >= board_right:
                self.scatter_direction.x *= -1
                self.x = max(board_left, min(board_right, self.x))

            if self.y <= board_top or self.y >= board_bottom:
                self.scatter_direction.y *= -1
                self.y = max(board_top, min(board_bottom, self.y))

            # Skip the normal path following while scattering
            return

        # Normal path movement
        if self.path_index < len(self.path) - 1:
            target_x, target_y = self.path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance < self.speed:
                self.path_index += 1
            else:
                self.x += dx / distance * self.speed
                self.y += dy / distance * self.speed
        else:
            self.reached_end = True

    # Render the enemy image on the screen, leaving the ability to add other types of enemies to render with different color balloons to use.
    def draw(self, screen):
        image = game.enemy_images.get(self.color, game.enemy_images["red"])
        scaled = pygame.transform.scale(image, (self.size * 2, self.size * 2))
        screen.blit(scaled, (int(self.x) - self.size, int(self.y) - self.size))

# Define a projectile class, to handle the actual motion of attacking.
class Projectile:
    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 8
        self.damage = 25
        self.size = 5
        self.reached_target = False

    def move(self):
        if self.target.reached_end:
            self.reached_target = True
            return

        # Respect invulnerability logic
        if self.target.invulnerable_time > 0:
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < self.speed:
            self.reached_target = True
            if not self.target.reached_end:
                self.target.health -= self.damage
                if self.target.health <= 0:
                    self.target.health = 0
        else:
            self.x = self.x + dx / distance * self.speed
            self.y = self.y + dy / distance * self.speed

    # Render the attack projectile, needs to be adjusted
    def draw(self, screen):
        pygame.draw.line(screen, (255, 0, 0), (int(self.x), int(self.y)), (int(self.target.x), int(self.target.y)), 4)

# Class for player-based defenders, placed on the physical chessboard, loaded from the load_detected_pieces() method,
# Leaves ability for other pieces to be used for high tier defenders
class Defender:
    def __init__(self, x, y, piece_type):
        self.x = x
        self.y = y
        self.piece_type = piece_type
        self.size = 30
        self.range = 150
        self.cooldown = 0
        self.cooldown_max = 30

        # Will primarily use Pawn's for this but has the ability to use other types.
        # If using other types need to find and add images for them as currently only using white pawn images
        # We should stick to only using the white pieces as they are easier to detect than the black ones.
        if "queen" in piece_type or "king" in piece_type:
            self.damage = 70
            self.range = 175
        elif "rook" in piece_type or "bishop" in piece_type:
            self.damage = 60
            self.range = 150
        else:  # pawn, knight
            self.damage = 40
            self.range = 90

    def update(self, enemies):
        if self.cooldown > 0:
            self.cooldown -= 1
            return None

        # Find the closest enemy in range
        closest_enemy = None
        min_distance = float('inf')

        for enemy in enemies:
            distance = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
            if distance < self.range and distance < min_distance:
                min_distance = distance
                closest_enemy = enemy

        if closest_enemy:
            self.cooldown = self.cooldown_max
            return Projectile(self.x, self.y, closest_enemy)

        return None

    # Render the defenders using the preloaded images, should be able to detect what type of defender was placed and chose right image
    def draw(self, screen):
        if self.piece_type in game.piece_images:
            piece_img = pygame.transform.scale(game.piece_images[self.piece_type], (self.size * 2, self.size * 2))
            screen.blit(piece_img, (int(self.x) - self.size, int(self.y) - self.size))

# Instantiate and run the game
if __name__ == "__main__":
    # Create a Game instance
    game = Game()

    # Define function to run yolo.main
    def run_yolo(yolo_queue):
        try:
            yolo.main(yolo_queue)
        except Exception as e:
            print(f"YOLO thread error: {e}")

    # Create a thread for yolo.main
    yolo_thread = threading.Thread(target=run_yolo, args=(game.yolo_queue,))

    # Start the YOLO thread
    yolo_thread.start()

    # Run the game main loop in the main thread
    try:
        game.main_loop()
    except Exception as e:
        print(f"Game loop error: {e}")
    finally:
        # Signal YOLO thread to stop and join
        game.running = False  # Signal YOLO to exit
        yolo_thread.join()