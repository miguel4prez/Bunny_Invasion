# Bunny Invasion Game

Welcome to **Bunny Invasion**, a simple 2D platformer game created using the Pygame library. In this game, you'll control a character, Mask Dude, who must navigate through levels, avoid obstacles, defeat enemies, and collect items.

Feel Free to Fork and Clone this project. To use, make sure to "pipenv install pygame" and run the code.

## How to Play

- **Movement:** Use the **A** key to move left and the **D** key to move right.
- **Jump:** Press the **W** key to make Mask Dude jump.
- **Shoot:** Press the **Spacebar** to shoot bullets and defeat enemies.
- **Objective:** Reach the exit at the end of each level while overcoming obstacles and enemies.
- **Health:** Watch out for your health. Collect health items to restore health.
- **Ammo:** Collect ammo boxes to replenish your ammunition.
- **Score:** Keep track of your kills and deaths. The game will display the number of kills and deaths on the screen.

## Game Elements

### Characters

- **Mask Dude:** Your main character, equipped with the ability to jump and shoot.
- **Bunny:** Enemy character. Defeat them to progress through levels.

Charaters are being loaded by their action and their animations are displayed on screen based on file index number.

```python
 # load all images for players
    animation_types = ['Idle', 'Run', 'Jump', 'Death', 'Hit']
    for animation in animation_types:
      # reset temporary list of images
      temp_list = []
      num_of_frames = len(os.listdir(f'Sprites/Main_Characters/{self.char_type}/{animation}'))
      for i in range(num_of_frames):
        img = pygame.image.load(f'Sprites/Main_Characters/{self.char_type}/{animation}/{i}.png').convert_alpha()
        img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        temp_list.append(img)
      self.animation_list.append(temp_list)
```

### Items

- **Health Box:** Restores Mask Dude's health.
- **Ammo Box:** Provides additional ammunition.

### Obstacles

- **Water:** Avoid falling into the water, as it will damage Mask Dude.

### Decorations

- **Boxes, Trees, Grass:** Boxes scattered through the map

## Levels

The game consists of multiple levels, each with its own challenges. Progress through the levels by reaching the exit.

The levels are being rendered by the csv files that are in the root directory

```python
# CREATE EMPTY TILE LIST
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

# load in data
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)
```

- Creates an empty 2D list (world_data) representing the game world.
- Loads level data from a CSV file (level{level}\_data.csv) and populates world_data.
- Initializes a World instance and processes the data, creating game elements based on the loaded information.
- The World class is responsible for handling and rendering the game world.

```python
class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    # More conditions for different tile types...
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
```

- World class manages the game world, specifically the obstacles and elements within it.
- process_data method processes the loaded level data, creating various game elements based on different tile types.
- The draw method renders the obstacles on the screen, adjusting their positions with the screen scroll.

## Health

You can track your health as the game progresses. Once your hit a minimum of 0 health, your death count will go up by one and will have to restart that level.

```python
class HealthBar():
  def __init__(self, x, y, health, max_health):
    self.x = x
    self.y = y
    self.health = health
    self.max_health = max_health

  def draw(self, health):
    # update with new health
    self.health = health
    ratio = self.health / self.max_health

    pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
    pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
    pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20) )

```

## Controls

- **Start Game:** Click the "Start" button on the main menu.
- **Exit Game:** Click the "Exit" button on the main menu or press **ESC** during gameplay.
- **Restart Level:** If Mask Dude dies, you can restart the level by clicking the "Restart" button.

The buttons are being programmed by the Button class imported from Button.

```python
import pygame

#button class
class Button():
	def __init__(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.smoothscale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action
```

This allows whatever image I use as a button to execute the code I want to accomplish.

## Game Over

You are able to see the stats once the game ends, viewing how many deaths and kills you had all throughout the 3 levels

```python
   if level > MAX_LEVELS:
          screen.fill('#211F30')
          screen.blit(game_over_img, (200,0))
          draw_text('STATS', font, WHITE, 335, 450)
          draw_text(f'Deaths: {death_counter}', font, WHITE, 320, 500)
          draw_text(f'Kills: {total_kills}', font, WHITE, 320, 550)
          if exit_button.draw(screen):
            run = False
```

Have fun playing **Bunny Invasion**!

# Credits

World Sprties by https://free-game-assets.itch.io/free-exclusion-zone-tileset-pixel-art

Character Sprites by https://pixelfrog-assets.itch.io/pixel-adventure-1
