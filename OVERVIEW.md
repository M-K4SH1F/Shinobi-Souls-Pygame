# Pygame — Package / Library Overview

---

## 1. Which package/library did I select?

I selected **Pygame**, a Python library used for making 2D games and multimedia applications. It is one of the most well-known libraries in the Python ecosystem for game development [1].

---

## 2. What is Pygame?

### Purpose

Pygame is a set of Python modules built on top of the **SDL (Simple DirectMedia Layer)** library [2]. SDL is a cross-platform C library that gives low-level access to things like audio, keyboard, mouse and display hardware. Pygame essentially wraps all of that into Python so you can use it without dealing with C code.

The main purpose of Pygame is to let developers build **2D games and interactive multimedia apps** in Python. It handles a lot of the hard stuff for you such as opening a window, drawing shapes and images, playing sounds, reading keyboard/mouse input and controlling the game loop.

### How do you use it?

You install it with pip:

```bash
pip install pygame
```

Then you import it and call `pygame.init()` to start everything up:

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Game")
```

Every Pygame program follows the same basic structure:

1. **Initialize** — `pygame.init()` sets up all modules
2. **Create a window** — `pygame.display.set_mode((width, height))`
3. **Game loop** — a `while True` loop that runs every frame
4. **Handle events** — check for keyboard, mouse, quit events
5. **Update game state** — move objects, check collisions, etc.
6. **Draw everything** — clear the screen, draw sprites, flip the display
7. **Control FPS** — use `pygame.time.Clock().tick(60)` to cap frame rate

Here is a minimal working example:

```python
import pygame, sys

pygame.init()
screen = pygame.display.set_mode((600, 400))
clock  = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((20, 20, 40))          # clear screen (dark background)
    pygame.draw.circle(screen, (255, 200, 50), (300, 200), 40)  # draw a gold circle
    pygame.display.flip()              # show the frame
    clock.tick(60)                     # cap at 60 FPS
```

**Output:** A window opens with a dark background and a gold circle in the centre, running at 60 frames per second.

---

### How does Pygame actually work? (Detail Section)

This section goes deeper into the key systems inside Pygame.

#### Display & Drawing

Pygame uses a **Surface** object to represent any drawable area i.e. the screen, a sprite image, a background, etc. You draw onto surfaces using built-in functions.

```python
# Drawing shapes
pygame.draw.rect(screen, (255, 0, 0), (100, 100, 80, 60))          # red rectangle
pygame.draw.circle(screen, (0, 200, 255), (300, 200), 30)          # blue circle
pygame.draw.line(screen, (255, 255, 255), (0, 0), (400, 300), 2)   # white line
pygame.draw.polygon(screen, (255, 200, 0), [(50,50),(80,10),(110,50)])  # gold triangle
```

`pygame.display.flip()` — or `pygame.display.update()` — pushes the finished frame to the screen.

#### Sprites

Pygame has a `Sprite` class and `Group` class to help organize game objects. Each sprite has an `image` (a Surface) and a `rect` (its position/size). Groups handle drawing and updating all sprites at once.

```python
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 60), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (70, 130, 220), (10, 20, 20, 30))
        self.rect  = self.image.get_rect(center=(400, 300))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  self.rect.x -= 5
        if keys[pygame.K_RIGHT]: self.rect.x += 5

player     = Player()
all_sprites = pygame.sprite.Group(player)
```

To draw all sprites in a group: `all_sprites.draw(screen)`
To update them all: `all_sprites.update()`

#### Collision Detection

Pygame makes collision detection very straightforward using rect-based checks:

```python
# Check if two sprites overlap
if pygame.sprite.collide_rect(player, enemy):
    player.take_damage(10)

# Check one sprite against a group
hit = pygame.sprite.spritecollideany(projectile, enemy_group)
if hit:
    hit.hp -= 20
```

There are also pixel-perfect collision methods for better accuracy (`collide_mask`), but rect-based is fast and works great for most 2D games.

#### Input Handling

Pygame gives you two ways to check input:

```python
# Event-based (triggers once per press)
for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            player.jump()

# State-based (holds true while key is held)
keys = pygame.key.get_pressed()
if keys[pygame.K_RIGHT]:
    player.rect.x += 5
```

#### Audio

Pygame has a mixer module for playing sounds and music:

```python
pygame.mixer.init()
pygame.mixer.music.load("background.mp3")
pygame.mixer.music.play(-1)          # -1 = loop forever

hit_sound = pygame.mixer.Sound("hit.wav")
hit_sound.play()
```

#### Text & Fonts

```python
font = pygame.font.SysFont("consolas", 28, bold=True)
text_surface = font.render("Score: 500", True, (255, 255, 255))
screen.blit(text_surface, (20, 20))
```

#### Timers & FPS

```python
clock = pygame.time.Clock()

# In the game loop:
clock.tick(60)   # Limits loop to 60 FPS and returns ms since last frame
```

#### Images

```python
image = pygame.image.load("sprite.png").convert_alpha()
screen.blit(image, (100, 200))
```

`convert_alpha()` is important as it speeds up rendering by pre-converting the image format to match the display.

---

## 3. What are the functionalities of Pygame?

Here is a summary of Pygame's main modules and what they do:

| Module | What it does |
|--------|--------------|
| `pygame.display` | Creates and manages the game window |
| `pygame.draw` | Draws shapes (circles, rects, lines, polygons) |
| `pygame.sprite` | Sprite and group management, collision detection |
| `pygame.event` | Handles keyboard, mouse, quit, and custom events |
| `pygame.key` | Reads keyboard input states |
| `pygame.mouse` | Reads mouse position and button states |
| `pygame.image` | Loads and saves image files |
| `pygame.font` | Renders text to surfaces |
| `pygame.mixer` | Plays audio files and background music |
| `pygame.time` | Controls FPS and frame timing |
| `pygame.Surface` | The core drawable object — everything is a surface |
| `pygame.Rect` | Axis-aligned bounding box, used for positions and collisions |
| `pygame.transform` | Scales, rotates, and flips surfaces |

### Code snippet — Particle effect example

```python
import pygame, random

class Particle:
    def __init__(self, x, y):
        self.x    = x
        self.y    = y
        self.vx   = random.uniform(-3, 3)
        self.vy   = random.uniform(-4, -1)
        self.life = random.randint(20, 45)
        self.r    = random.randint(2, 5)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.15          # gravity
        self.life -= 1

    def draw(self, surf):
        alpha = int(255 * self.life / 45)
        s = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 200, 50, alpha), (self.r, self.r), self.r)
        surf.blit(s, (int(self.x) - self.r, int(self.y) - self.r))
```

**Output:** Small gold circles that fly outward, fall with gravity and fade out as their life decreases that is used to create explosion and impact effects in Shinobi Souls.

---

## 4. When was Pygame created?

Pygame was originally created by **Pete Shinners** in **2000** [3]. It was designed as a replacement for the older PySDL library. Over the years it has been maintained by the community and the modern version **Pygame-CE (Community Edition)** is actively maintained as of 2024 [4].

---

## 5. Why did I select Pygame?

I picked Pygame because I am genuinely into gaming — I have 100% completed The Witcher 3, spent hundreds of hours in Elden Ring and the rest of the Soulsborne games and I am always curious about how games actually work under the hood. I wanted to pick a library that would let me explore something I actually care about instead of just doing something generic.

Beyond personal interest, Pygame specifically made sense because it is Python-based, which is a language I am already studying, so I could focus on learning the library instead of fighting the language at the same time. I also wanted to understand the fundamentals of a game loop — things like frame rate control, sprite management and collision detection — which are concepts that apply to basically every game engine including more advanced ones like Unity or Unreal [5].

Building a small anime-inspired game seemed like a good way to genuinely engage with those concepts while making something that is actually fun to look at and play.

---

## 6. How did learning Pygame influence my learning of Python?

Learning Pygame made me much more comfortable with object-oriented programming in Python. Before this, I had used classes in assignments but not in a way where the design actually mattered. With Pygame, each game object (player, enemy, projectile) naturally becomes its own class because they all share structure (image, rect, update method) but have different behaviour. That really made the concept of inheritance and `super().__init__()` click for me in a practical way.

I also got a lot more familiar with Python's `random` module, `math` module, list comprehensions and working with tuples for colour values. Managing the particle system, which is just a regular Python list of objects that get added and removed each frame was a good exercise in thinking about performance and how many objects you can reasonably update 60 times per second.

---

## 7. Overall Experience

### When would I recommend Pygame?

I would ofcourse recommend Pygame to anyone who is learning Python and wants to build something visual and interactive. It is a great fit for students who are bored of command-line projects and want something they can actually show people. It is also a good starting point before jumping into larger engines like Godot, Unity or Unreal Engine because you actually have to implement things like the game loop, physics and collision manually. So, you understand what those engines are doing for you.

I would not recommend it for someone trying to build a 3D game or something that needs a physics engine, networking or advanced audio. Pygame is best for 2D, relatively simple games [6].

### Would I continue using Pygame?

Probably not as my main tool long-term but, I would likely move to **Unreal Engine** or **Unity** for bigger projects because they have visual editors, built-in physics and much larger ecosystems. But I would absolutely use Pygame again for quick prototyping or game jam projects. It is lightweight, requires zero setup beyond a pip install and there is no GUI to learn, you just write code and run it.

Overall it was a really fun library to explore and thank you so much for letting me for on this Pygame project genuinely the best project I have ever worked so far in my degree. I am glad that I picked this.

---

## References

[1] https://www.pygame.org/wiki/about

[2] https://www.libsdl.org/

[3] https://www.pygame.org/wiki/HistoryOfPygame

[4] https://pyga.me/ (Pygame-CE Community Edition)

[5] https://docs.unrealengine.com/5.0/en-US/game-loop-in-unreal-engine/

[6] https://realpython.com/pygame-a-primer/

[7] https://www.youtube.com/playlist?list=PLzMcBGfZo4-lp3jAExUCewBfMx3UZFkh5