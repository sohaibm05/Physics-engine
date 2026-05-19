"""physengine — a minimal 2D rigid-body physics engine.

Public API:

    from physengine import World, Body, Vec2, Box, Circle

    world = World(gravity=Vec2(0, 500))
    world.add(Body(pos=Vec2(100, 100), shape=Circle(20), mass=1.0))
    for _ in range(60):
        world.step(dt=1/60)
"""
from .vec2 import Vec2
from .shapes import Box, Circle
from .body import Body
from .world import World

__all__ = ["Vec2", "Box", "Circle", "Body", "World"]
__version__ = "0.1.0"
