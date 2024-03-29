import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bunny Invasion')

#set framerate
clock  = pygame.time.Clock()
FPS = 60

# Game Variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
death_counter = 0
total_kills = 0
music_paused = True
keep_playing = False

## action variables
moving_left = False
moving_right = False
shoot = False

# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
  img = pygame.image.load(f'Tiles/{x}.png')
  img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
  img_list.append(img)

# Load Music
pygame.mixer.music.load('audio/Cloudy_Sleeze.wav')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.3)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.2)
water_fx = pygame.mixer.Sound('audio/water_splash.wav')
water_fx.set_volume(0.3)
falling_fx = pygame.mixer.Sound('audio/falling_fx.wav')
falling_fx.set_volume(0.2)
walking_fx = pygame.mixer.Sound('audio/walking.wav')
walking_fx.set_volume(0.3)

# load images
game_over_img = pygame.image.load('Sprites/Menu/Buttons/game_over.png').convert_alpha()
game_over_img = pygame.transform.scale(game_over_img, (400, 320))

#button images
start_img = pygame.image.load('Sprites/Menu/Buttons/start_btn.png').convert_alpha()
exit_img = pygame.image.load('Sprites/Menu/Buttons/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('Sprites/Menu/Buttons/restart_btn.png').convert_alpha()
audio_img = pygame.image.load('Sprites/audio_logo.png').convert_alpha()

# background
pine1_img = pygame.image.load('Sprites/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('Sprites/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('Sprites/background/mountains.png').convert_alpha()
sky_img = pygame.image.load('Sprites/background/sky_cloud.png').convert_alpha()

main_menu_background = pygame.image.load('BG.png').convert_alpha()
  
# bullet
bullet_img = pygame.image.load('Sprites/Fire/fire_bullet.png').convert_alpha()

#items
health_box_img = pygame.image.load('Sprites/Fruits/Apple_Animation/0.png').convert_alpha()
ammo_box_img = pygame.image.load('Sprites/Fire/Fire_Ammo/0.png').convert_alpha()

item_boxes = {
  'Health': health_box_img,
  'Ammo': ammo_box_img
}

# define colors
BG= (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN =(0, 255, 0)
BLACK = (0, 0, 0)

# define font
font = pygame.font.SysFont('Futura', 30)
sub_font = pygame.font.SysFont('Futura', 15)
sub_text = sub_font.render('https://github.com/miguel4prez', False, WHITE, None)

def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))


def draw_bg():
  screen.fill(BG)
  width = mountain_img.get_width()
  for x in range(5):
    screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
    screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
    screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
    screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))
    
  
# fucntion to reset level
def reset_level():
  enemy_group.empty()
  bullet_group.empty()
  item_box_group.empty()
  decoration_group.empty()
  water_group.empty()
  exit_group.empty()
  flame_group.empty()

  data = []
  for row in range(ROWS):
    r = [-1] * COLS
    data.append(r)

  return data

#################################################################################################

class Soldier(pygame.sprite.Sprite):
  def __init__(self, char_type, x, y, scale, speed, ammo):
    pygame.sprite.Sprite.__init__(self)
    self.alive = True
    self.char_type = char_type 
    self.speed = speed
    self.ammo = ammo
    self.start_ammo = ammo
    self.shoot_cooldown = 0
    self.max_ammo = 20
    self.health = 100
    self.max_health = self.health
    self.direction = 1
    self.vel_y = 0
    self.jump = False
    self.in_air = True
    self.flip = False
    self.animation_list = []
    self.frame_index = 0
    self.action = 0
    self.update_time = pygame.time.get_ticks()

    #AI specific variables
    self.move_counter = 0
    self.vision = pygame.Rect(0, 0, 150, 20)
    self.idiling = False
    self.idiling_counter = 0

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

    self.img = self.animation_list[self.action][self.frame_index]
    self.rect = self.img.get_rect()
    self.rect.center = (x, y)
    self.width = self.img.get_width()
    self.height = self.img.get_height()

  def update(self):
    self.update_animation()
    self.check_alive()
    # update cooldown
    if self.shoot_cooldown > 0:
      self.shoot_cooldown -= 1

  def move(self, moving_left, moving_right):
    screen_scroll = 0
    # reset movement
    dx = 0
    dy = 0

    #movement function
    if moving_left:
      dx = -self.speed
      self.flip = True
      self.direction = -1
    if moving_right:
      dx = self.speed
      self.flip = False
      self.direction = 1

    # jump
    if self.jump == True and self.in_air == False:
      self.vel_y = -12
      self.jump = False
      self.in_air = True
    
    #gravity  
    self.vel_y += GRAVITY
    if self.vel_y > 10:
      self.vel_y
    dy += self.vel_y  

    # check collision 
    if player.alive:
      # checking collision in the x direction
      for tile in world.obstacle_list:
        if tile [1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
          dx = 0
        
      # checking collision in the y direction
        if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
          # check if below the ground by jumping
          if self.vel_y < 0:
            self.vel_y = 0
            dy = tile[1].bottom - self.rect.top
          #check above ground
          elif self.vel_y >= 0:
            self.vel_y = 0
            self.in_air = False
            dy = tile[1].top - self.rect.bottom
    else:
      dy = 5
      falling_fx.play()
    
    if self.char_type == 'Mask_Dude':
      if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
        dx = 0

    # update rectangle position
    self.rect.x += dx
    self.rect.y += dy

    # check collision with water
    if pygame.sprite.spritecollide(self, water_group, False):
      self.health = 0
      water_fx.play()
      falling_fx.play()

    level_complete = False
    if pygame.sprite.spritecollide(self, exit_group, False):
      level_complete = True
    
    if self.rect.bottom > SCREEN_HEIGHT:
      self.health = 0
      player.alive = False
      falling_fx.play()

    # update scroll
    if self.char_type == 'Mask_Dude':
      if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
        or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
        self.rect.x -= dx
        screen_scroll = -dx
    return screen_scroll, level_complete


  def shoot(self):
      if self.shoot_cooldown == 0 and self.ammo > 0:
        self.shoot_cooldown = 20
        bullet = Bullet(self.rect.centerx + (0.7 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
        bullet_group.add(bullet)
        #reduce ammo
        self.ammo -= 1
        shot_fx.play()

  def ai(self):
    if self.alive and player.alive:
      if self.idiling == False and random.randint(1, 200) == 1:
        self.update_action(0) # idle action
        self.idiling = True
        self.idiling_counter = 50

      # check if ai near the player
      if self.vision.colliderect(player.rect):
        #stop player
        self.update_action(0)
        self.shoot()
      else:
          if self.idiling == False:
            if self.direction == 1:
              ai_moving_right = True
            else:
              ai_moving_right = False
            ai_moving_left = not ai_moving_right
            self.move(ai_moving_left, ai_moving_right)
            self.update_action(1) #1 is running
            self.move_counter += 1
            #update ai vision
            self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

            if self.move_counter > TILE_SIZE:
              self.direction *= -1
              self.move_counter *= -1
          else: 
            self.idiling_counter -= 1
            if self.idiling_counter <= 0:
              self.idiling = False

    #scroll
    self.rect.x += screen_scroll


  def update_animation(self):
    #update animation
    ANIMATION_COOLDOWN = 100
    # update image depending on current frame
    self.img = self.animation_list[self.action][self.frame_index]
    # check if enough time has passed since last update
    if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
      self.update_time = pygame.time.get_ticks()
      self.frame_index += 1
    # loop animation
    if self.frame_index >= len(self.animation_list[self.action]):
      if self.action == 3:
        self.frame_index = len(self.animation_list[self.action]) -1
        self.rect.y += 50
      else:
        self.frame_index = 0

  def update_action(self, new_action):
    # check if the new action is different from the previous one
    if new_action != self.action:
      self.action = new_action
      # update the animation settings
      self.frame_index = 0
      self.update_time = pygame.time.get_ticks()

  def check_alive(self):
    if self.health <= 0:
      self.health = 0
      self.speed = 0
      self.alive = False
      self.update_action(3)
      # falling_fx.play()

  def draw(self):
    screen.blit(pygame.transform.flip(self.img, self.flip, False),  self.rect)

##################################################################################################

class Flame(pygame.sprite.Sprite):
  def __init__(self, x, y, scale):
    pygame.sprite.Sprite.__init__(self)
    self.images = []
    for num in range(1, 4):
      img = pygame.image.load(f'Sprites/Fire/Flame/{num}.png').convert_alpha()
      img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
      self.images.append(img)
    self.frame_index = 0
    self.image = self.images[self.frame_index]
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.counter = 0

  def update(self):
    FIRE_SPEED = 4
    #update fire animation
    self.counter += 1
    
    if self.counter >= FIRE_SPEED:
      self.counter = 0
      self.frame_index += 1
      #if the animation is complete then delete flame
      if self.frame_index >= len(self.images):
        self.kill()
      else:
        self.image = self.images[self.frame_index]

########################################################################################

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
          elif tile >= 9 and tile <= 10:
            water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
            water_group.add(water)
          elif tile >= 11 and tile <= 14:
            decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
            decoration_group.add(decoration)
          elif tile == 15:
            player = Soldier('Mask_Dude', x * TILE_SIZE, y * TILE_SIZE, 1.65, 6, 20)
            health_bar = HealthBar(10, 10, player.health, player.health)
          elif tile == 16:
            enemy = Soldier('Bunny', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20)
            enemy_group.add(enemy)
          elif tile == 17:
            item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
            item_box_group.add(item_box)
          elif tile == 18:
            item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
            item_box_group.add(item_box)
          elif tile == 19:
            pass
          elif tile == 20:
            exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
            exit_group.add(exit)
    return player, health_bar

  def draw(self):
    for tile in self.obstacle_list:
      tile[1][0] += screen_scroll
      screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
  def __init__(self, img, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = img
    self.rect = self.image.get_rect()
    self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

  def update(self):
    self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
  def __init__(self, img, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = img
    self.rect = self.image.get_rect()
    self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
  
  def update(self):
    self.rect.x += screen_scroll
    

class Exit(pygame.sprite.Sprite):
  def __init__(self, img, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = img
    self.rect = self.image.get_rect()
    self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
  
  def update(self):
    self.rect.x += screen_scroll

########################################################################################

class ItemBox(pygame.sprite.Sprite):
  def __init__(self, item_type, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.item_type = item_type
    self.image = item_boxes[self.item_type]
    self.rect = self.image.get_rect()
    self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

  def update(self):
    self.rect.x += screen_scroll
    ## check for collision against the player
    if pygame.sprite.collide_rect(self, player):
      # check what kind of box it was
      if self.item_type == 'Health':
        player.health += 25
        if player.health > player.max_health:
          player.health = player.max_health
      elif self.item_type == 'Ammo':
        player.ammo += 15
        if player.ammo > player.max_ammo:
          player.ammo = player.max_ammo
      self.kill()

#################################################################################################

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

#################################################################################################

class Bullet(pygame.sprite.Sprite):
  def __init__(self, x, y, direction):
    pygame.sprite.Sprite.__init__(self)
    self.speed = 10
    self.image = bullet_img
    self.timer = 100
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.direction = direction

  def update(self):
    #move bullet
    self.rect.x += (self.direction * self.speed) + screen_scroll
    # check if bullet has gone off screen
    if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
      self.kill()
    
    for tile in world.obstacle_list:
      if tile[1].colliderect(self.rect):
        self.kill()
    
    # check collision with enemy
    if pygame.sprite.spritecollide(player, bullet_group, False):
      if player.alive:
        player.health -= 5
        self.kill()

    for enemy in enemy_group:
      if pygame.sprite.spritecollide(enemy, bullet_group, False):
        if enemy.alive:
            enemy.health -= 25
            if enemy.health <= 0:
              enemy.alive = False
              enemy.update_action(3)
              global total_kills
              total_kills += 1
            self.kill()
            

    # fire countdown
    self.timer -= 1
    if self.timer <= 0:
      fire = Flame(self.rect.x, self.rect.y, 0.5)
      flame_group.add(fire)

#################################################################################################
      
# Create Buttons 
start_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 - 70, start_img, 0.7)

exit_button = button.Button(SCREEN_WIDTH // 2 - 108, SCREEN_HEIGHT // 2 + 20, exit_img, 0.7)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 0.7)
audio_btn = button.Button(10, 120, audio_img, 0.02)


# create sprite groups
bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
flame_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#############################################################################################

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


run = True
while run:  

  clock.tick(FPS)
  if start_game == False:
    ### Main Menu ##
    screen.blit(main_menu_background, (0, 0))
    if start_button.draw(screen):
      start_game = True
    if exit_button.draw(screen):
      run = False
    screen.blit(sub_text, (285, 550))
  else:
  ## Game Start ##
    draw_bg()

    world.draw()

    # Music on or off
    if audio_btn.draw(screen):
      if music_paused:
          pygame.mixer.music.pause()
      else:
          pygame.mixer.music.unpause()
      music_paused = not music_paused
    
    if music_paused == False:
      pygame.draw.line(screen, RED, (5 , 150), (45, 120), width=5)
      pygame.draw.line(screen, RED, (5, 120), (45, 150), width=5)
  
    #health bar
    health_bar.draw(player.health)
    #show health
    draw_text(f'Health: {player.health}%', font, WHITE, 10, 70)
    #show ammo
    draw_text(f'AMMO: ', font, WHITE, 10, 35)
    for x in range(player.ammo):
      screen.blit(ammo_box_img, (135 + (x * 15), 50))
    draw_text(f'Deaths: {death_counter}', font, WHITE, 640, 10)
    draw_text(f'Kills: {total_kills}', font, WHITE, 640, 60)
  
    player.update()
    player.draw()

    for enemy in enemy_group:
      enemy.update()
      enemy.draw()
      enemy.ai()

  #group updates
    bullet_group.update()
    item_box_group.update()
    flame_group.update()
    decoration_group.update()
    water_group.update()
    exit_group.update()

    item_box_group.draw(screen)
    bullet_group.draw(screen)
    flame_group.draw(screen)
    decoration_group.draw(screen)
    water_group.draw(screen)
    exit_group.draw(screen)
    

    # update player action
    if player.alive:
      # shoot bullets
      if shoot:
        player.shoot()
      if player.in_air:
        player.update_action(2)
      elif moving_left or moving_right:
        player.update_action(1) # 1 means run
      else:
        player.update_action(0)
      screen_scroll, level_complete = player.move(moving_left, moving_right)
      bg_scroll -= screen_scroll
      if level_complete:
        level += 1
        bg_scroll = 0
        world_data = reset_level()
        if level <= MAX_LEVELS:
          with open(f'level{level}_data.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
              for y, tile in enumerate(row):
                world_data[x][y] = int(tile)
          world = World()
          player, health_bar = world.process_data(world_data)

    else:
      screen_scroll = 0
      if restart_button.draw(screen):
        bg_scroll = 0
        death_counter += 1  
        world_data = reset_level()
        with open(f'level{level}_data.csv', newline='') as csvfile:
          reader = csv.reader(csvfile, delimiter=',')
          for x, row in enumerate(reader):
            for y, tile in enumerate(row):
              world_data[x][y] = int(tile)
          world = World()
          player, health_bar = world.process_data(world_data)

    #### Exit Menu ####
    if level > MAX_LEVELS:
          screen.fill('#211F30')
          screen.blit(game_over_img, (200,0))
          draw_text('STATS', font, WHITE, 335, 450)
          draw_text(f'Deaths: {death_counter}', font, WHITE, 320, 500)
          draw_text(f'Kills: {total_kills}', font, WHITE, 320, 550)
          if exit_button.draw(screen):
            run = False

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

      #player movement
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_RETURN:
        start_game = True
      if event.key == pygame.K_a:
        moving_left = True
        if start_game == True:
          walking_fx.play()
      if event.key == pygame.K_d:
        moving_right = True
        if start_game == True:
          walking_fx.play()
      if event.key == pygame.K_SPACE:
        shoot = True
      if event.key == pygame.K_w and player.alive:
        player.jump = True
        if start_game == True:
          jump_fx.play()
      if event.key == pygame.K_ESCAPE:
        run = False

        #player stop movement
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_a:
        moving_left = False
      if event.key == pygame.K_d:
        moving_right = False
      if event.key == pygame.K_SPACE:
        shoot = False

  pygame.display.update()

pygame.quit()