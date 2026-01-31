import pygame
import random

WIDTH, HEIGHT = 400, 500
GRID_SIZE = 4
TILE_SIZE = 90
GAP = 10
ANIMATION_SPEED = 25
MIN_SWIPE_DISTANCE = 50

COLORS = {
    'bg': (187, 173, 160),
    'empty': (205, 193, 180),
    'text': (119, 110, 101),
    'light_text': (249, 246, 242),
    'overlay': (238, 228, 218) # Цвет полупрозрачного фона
}

TILE_COLORS = {
    2: (238, 228, 218), 4: (237, 224, 200), 8: (242, 177, 121),
    16: (245, 149, 99), 32: (246, 124, 95), 64: (246, 94, 59),
    128: (237, 207, 114), 256: (237, 204, 97), 512: (237, 200, 80),
    1024: (237, 197, 63), 2048: (237, 194, 46),
}

class Tile:
    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = self.get_coord(col)
        self.y = self.get_coord(row, y_offset=50)
        self.scale = 0
        self.growing = True
        self.merged_from = None

    def get_coord(self, index, y_offset=0):
        return index * TILE_SIZE + (index + 1) * GAP + y_offset

    def move_to(self, row, col):
        self.row = row
        self.col = col

    def update(self):
        target_x = self.get_coord(self.col)
        target_y = self.get_coord(self.row, y_offset=50)

        self.x += (target_x - self.x) / 3
        self.y += (target_y - self.y) / 3

        if abs(self.x - target_x) < 1: self.x = target_x
        if abs(self.y - target_y) < 1: self.y = target_y

        if self.growing:
            self.scale += 0.2
            if self.scale >= 1:
                self.scale = 1
                self.growing = False

    def draw(self, screen, font):
        center_x = self.x + TILE_SIZE / 2
        center_y = self.y + TILE_SIZE / 2
        
        current_size = TILE_SIZE * self.scale
        offset = current_size / 2
        
        rect = (center_x - offset, center_y - offset, current_size, current_size)
        color = TILE_COLORS.get(self.value, TILE_COLORS[2048])
        pygame.draw.rect(screen, color, rect, border_radius=5)

        if self.value > 0:
            t_color = COLORS['text'] if self.value <= 4 else COLORS['light_text']
            font_size = int(35 * self.scale)
            if font_size > 5:
                current_font = pygame.font.SysFont("arial", font_size, bold=True)
                text_surface = current_font.render(str(self.value), True, t_color)
                text_rect = text_surface.get_rect(center=(center_x, center_y))
                screen.blit(text_surface, text_rect)

class Game2048:
    def __init__(self):
        self.tiles = []
        self.score = 0
        self.over = False
        self.add_tile()
        self.add_tile()

    def get_tile_at(self, row, col):
        for tile in self.tiles:
            if tile.row == row and tile.col == col and not tile.merged_from:
                return tile
        return None

    def add_tile(self):
        empty = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.get_tile_at(r, c) is None:
                    empty.append((r, c))
        
        if empty:
            r, c = random.choice(empty)
            val = 2 if random.random() < 0.9 else 4
            self.tiles.append(Tile(val, r, c))
        
        self.check_game_over()

    def check_game_over(self):
        if len(self.tiles) < GRID_SIZE * GRID_SIZE:
            self.over = False
            return

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                current = self.get_tile_at(r, c)
                right = self.get_tile_at(r, c + 1)
                if right and right.value == current.value:
                    self.over = False
                    return
                down = self.get_tile_at(r + 1, c)
                if down and down.value == current.value:
                    self.over = False
                    return
        
        self.over = True
        print("Game Over Logic Triggered")

    def move(self, direction):
        if self.over: return

        if direction == 'UP':
            sort_key = lambda t: t.row
            dr, dc = -1, 0
        elif direction == 'DOWN':
            sort_key = lambda t: -t.row
            dr, dc = 1, 0
        elif direction == 'LEFT':
            sort_key = lambda t: t.col
            dr, dc = 0, -1
        elif direction == 'RIGHT':
            sort_key = lambda t: -t.col
            dr, dc = 0, 1
            
        moved_any = False
        for t in self.tiles: t.merged_from = None
        sorted_tiles = sorted(self.tiles, key=sort_key)
        
        for tile in sorted_tiles:
            r, c = tile.row, tile.col
            while True:
                next_r, next_c = r + dr, c + dc
                
                if not (0 <= next_r < GRID_SIZE and 0 <= next_c < GRID_SIZE):
                    break
                
                neighbor = self.get_tile_at(next_r, next_c)
                
                if neighbor is None:
                    r, c = next_r, next_c
                    moved_any = True
                elif neighbor.value == tile.value and neighbor.merged_from is None:
                    self.tiles.remove(tile)
                    self.tiles.remove(neighbor)
                    
                    new_tile = Tile(tile.value * 2, next_r, next_c)
                    new_tile.scale = 1.2
                    self.tiles.append(new_tile)
                    self.score += new_tile.value
                    moved_any = True
                    break
                else:
                    break

            tile.move_to(r, c)

        if moved_any:
            self.add_tile()

    def update(self):
        for tile in self.tiles:
            tile.update()
            if not tile.growing and tile.scale > 1:
                tile.scale -= 0.05

    def draw(self, screen, font):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x = c * TILE_SIZE + (c + 1) * GAP
                y = r * TILE_SIZE + (r + 1) * GAP + 50
                pygame.draw.rect(screen, COLORS['empty'], (x, y, TILE_SIZE, TILE_SIZE), border_radius=5)
        
        for tile in self.tiles:
            tile.draw(screen, font)
        
        score_text = font.render(f"Score: {self.score}", True, COLORS['text'])
        screen.blit(score_text, (20, 10))

        if self.over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180) 
            overlay.fill(COLORS['overlay'])
            screen.blit(overlay, (0, 0))
            
            go_text = font.render("GAME OVER", True, COLORS['text'])
            go_rect = go_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 20))
            
            restart_font = pygame.font.SysFont("arial", 25)
            restart_text = restart_font.render("Press 'R' to restart", True, COLORS['text'])
            res_rect = restart_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 30))
            
            screen.blit(go_text, go_rect)
            screen.blit(restart_text, res_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((410, 520))
    pygame.display.set_caption("2048 Animated")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 35, bold=True)
    
    game = Game2048()
    mouse_start = None
    running = True

    while running:
        game.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game.over:
                    if event.key == pygame.K_r:
                        game = Game2048() 
                else:
                    if event.key in [pygame.K_LEFT, pygame.K_a]: game.move('LEFT')
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]: game.move('RIGHT')
                    elif event.key in [pygame.K_UP, pygame.K_w]: game.move('UP')
                    elif event.key in [pygame.K_DOWN, pygame.K_s]: game.move('DOWN')
                    elif event.key == pygame.K_r: game = Game2048()

            if event.type == pygame.MOUSEBUTTONDOWN and not game.over:
                mouse_start = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and mouse_start and not game.over:
                dx = event.pos[0] - mouse_start[0]
                dy = event.pos[1] - mouse_start[1]
                if abs(dx) > MIN_SWIPE_DISTANCE or abs(dy) > MIN_SWIPE_DISTANCE:
                    if abs(dx) > abs(dy):
                        game.move('RIGHT' if dx > 0 else 'LEFT')
                    else:
                        game.move('DOWN' if dy > 0 else 'UP')
                mouse_start = None

        screen.fill(COLORS['bg'])
        game.draw(screen, font)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()