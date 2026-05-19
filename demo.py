"""Visual demo with pygame. Run:

    pip install -r requirements.txt
    python demo.py

Click anywhere to drop a ball/box. Press R to reset, ESC to quit.
"""
from __future__ import annotations
import random
import sys

import pygame

from physengine import World, Body, Vec2, Circle, Box


SCREEN_W = 800
SCREEN_H = 600
FPS = 60


def make_world():
    world = World(gravity=Vec2(0, 800))
    walls = [
        Body(pos=Vec2(SCREEN_W / 2, SCREEN_H - 10), shape=Box(SCREEN_W / 2, 10)),
        Body(pos=Vec2(10, SCREEN_H / 2), shape=Box(10, SCREEN_H / 2)),
        Body(pos=Vec2(SCREEN_W - 10, SCREEN_H / 2), shape=Box(10, SCREEN_H / 2)),
    ]
    for w in walls:
        w.make_static()
        world.add(w)

    for i in range(5):
        world.add(Body(pos=Vec2(SCREEN_W / 2, SCREEN_H - 60 - i * 42),
                       shape=Box(20, 20), mass=1.0, restitution=0.2))
    return world


def draw_body(screen, body):
    color = (180, 180, 180) if body.is_static else (60, 180, 250)
    if body.shape.kind == "circle":
        pygame.draw.circle(screen, color,
                           (int(body.pos.x), int(body.pos.y)),
                           int(body.shape.radius), 2)
    else:
        rect = pygame.Rect(
            int(body.pos.x - body.shape.half_width),
            int(body.pos.y - body.shape.half_height),
            int(2 * body.shape.half_width),
            int(2 * body.shape.half_height),
        )
        pygame.draw.rect(screen, color, rect, 2)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("physengine demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)

    world = make_world()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    world = make_world()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if random.random() < 0.5:
                    shape = Circle(random.randint(10, 25))
                else:
                    s = random.randint(15, 30)
                    shape = Box(s, s)
                world.add(Body(pos=Vec2(x, y), shape=shape,
                               mass=1.0, restitution=0.5))

        world.step(1 / FPS, iterations=10)
        screen.fill((25, 25, 35))
        for body in world.bodies:
            draw_body(screen, body)

        hud = font.render(
            f"bodies: {len(world.bodies)}  contacts: {world.last_step_contacts}  "
            "[click to drop · R reset · ESC quit]",
            True, (200, 200, 200))
        screen.blit(hud, (10, 10))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
