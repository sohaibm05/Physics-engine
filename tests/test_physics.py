"""Sanity tests for the physics core. Pure numerical — no display required."""
import pytest

from physengine import Vec2, Box, Circle, Body, World


def test_vec2_basic_ops():
    a = Vec2(3, 4)
    b = Vec2(1, 2)
    assert (a + b) == Vec2(4, 6)
    assert (a - b) == Vec2(2, 2)
    assert (a * 2) == Vec2(6, 8)
    assert a.dot(b) == 11
    assert a.length() == pytest.approx(5.0)
    assert a.normalized().length() == pytest.approx(1.0)


def test_free_fall():
    world = World(gravity=Vec2(0, 10))
    ball = world.add(Body(pos=Vec2(0, 0), shape=Circle(1), mass=1.0))
    for _ in range(100):
        world.step(dt=0.01)
    # After 1s under g=10: distance = 0.5 * g * t^2 = 5
    assert ball.pos.y == pytest.approx(5.0, rel=0.05)


def test_ball_hits_static_floor_and_doesnt_fall_through():
    world = World(gravity=Vec2(0, 100))
    ball = world.add(Body(pos=Vec2(0, -50), shape=Circle(5),
                          mass=1.0, restitution=0.9))
    floor = world.add(Body(pos=Vec2(0, 0), shape=Box(100, 5)))
    floor.make_static()

    for _ in range(120):
        world.step(dt=1 / 60)

    assert ball.pos.y < 0           # above the floor (y grows downward)
    assert ball.pos.y > -200        # didn't fly off into space


def test_two_circles_collide_and_separate():
    world = World(gravity=Vec2(0, 0))
    a = world.add(Body(pos=Vec2(-10, 0), vel=Vec2(50, 0),
                       shape=Circle(5), mass=1.0, restitution=1.0))
    b = world.add(Body(pos=Vec2(10, 0), vel=Vec2(-50, 0),
                       shape=Circle(5), mass=1.0, restitution=1.0))
    for _ in range(30):
        world.step(dt=1 / 60)
    # Equal mass, perfectly elastic, head-on → velocities swap signs
    assert a.vel.x < 0
    assert b.vel.x > 0


def test_static_box_immovable():
    world = World(gravity=Vec2(0, 100))
    wall = world.add(Body(pos=Vec2(0, 0), shape=Box(50, 50)))
    wall.make_static()
    for _ in range(60):
        world.step(dt=1 / 60)
    assert wall.pos == Vec2(0, 0)
    assert wall.vel == Vec2(0, 0)
