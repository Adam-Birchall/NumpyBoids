#!/usr/bin/python
"""
Rather than using matplot lib for the display, using pygame for display, 
should be much quicker.
"""

# %%
import sys
from turtle import position  # Only used for the dpi scaling of pygame on windows
import numpy as np
import pygame as pg
from pygame.locals import *
from Flocking import flock_forces


# %%
# Boids init

map_size = 20
params = {
    'speed': 0.005,
    'influence_prox': 1,
    'alignment_factor': 0.005,
    'cohesion_factor': 0.005,
    'separation_factor': 0.005
}

number_of_boids = 200

# pygame dimentions
width = 800
height = 800

# Scaling on windows
# If this is on a high or low res screen the window might be smaller or
# larger respectively. Comment out the following for standard sizing.
# if sys.platform == 'win32':
#     print("Running on windows, if scale is weird check ~ lines 34")
#     import ctypes
#     try:
#        ctypes.windll.user32.SetProcessDPIAware()
#     except AttributeError:
#         pass # Windows XP doesn't support monitor scaling, so just do nothing.


# %%
def draw(screen, particles):
    for p in particles:
        pg.draw.circle(screen, (0, 0, 0), p, 5)
    pg.display.flip()


def update(dt, positions, velocities, params):
    f1, f2, f3 = flock_forces(
        positions, velocities,
        map_size = map_size,
        **params
    )
    # Need to limit the speeds here somehow since the forces returned
    # don't limit speed
    velocities = velocities + (f1 + f2 + f3) * dt
    # There has to be a better way of doing this bit, but this is speed
    # setting, ensuring all boids have unit speed (otherwise things tend to
    # stop)
    for v in range(len(velocities)):
        velocities[v, :] = (velocities[v, :] / 
            np.linalg.norm(velocities[v, :]))

    positions = positions + velocities * dt * params['speed']
    return positions, velocities


def render_text(screen, what, color, where):
    font = pg.font.SysFont('monospace', 20)
    text = font.render(str(what), 1, pg.Color(color))
    screen.blit(text, where)


# %%
def runPyGame():
    pg.init()
    pg.display.set_caption('Boids')

    fps = 60.0

    # Set up the window.
    screen = pg.display.set_mode((width, height))
    fpsClock = pg.time.Clock()
    screen.fill((255, 255, 255))

    # Set up boids
    positions = np.random.rand(number_of_boids, 2) * map_size
    velocities = (np.random.rand(number_of_boids, 2) * 2) - 1

    text_toggles = True
    dt = 1/fps
    while True:
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit() 
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    text_toggles = not text_toggles
            if event.type == pg.KEYUP:
                # Speed
                if event.key == pg.K_w:
                    params['speed'] += 0.0005
                if event.key == pg.K_q:
                    params['speed'] -= 0.0005

                # Influence Proximity
                if event.key == pg.K_s:
                    params['influence_prox'] += 0.0005
                if event.key == pg.K_a:
                    params['influence_prox'] -= 0.0005

                # Alignment factor
                if event.key == pg.K_r:
                    params['alignment_factor'] += 0.0005
                if event.key == pg.K_e:
                    params['alignment_factor'] -= 0.0005
                
                # Cohesion
                if event.key == pg.K_f:
                    params['cohesion_factor'] += 0.0005
                if event.key == pg.K_d:
                    params['cohesion_factor'] -= 0.0005
                
                # Separation
                if event.key == pg.K_y:
                    params['separation_factor'] += 0.0005
                if event.key == pg.K_t:
                    params['separation_factor'] -= 0.0005


        # Clear screen
        screen.fill((255, 255, 255))

        # Show prompts
        render_text(screen, '[Space]: Show / hide variables',
            (100, 100, 100), (10, height - 30))
        if text_toggles:
            render_text(
                screen,
                f'Speed:               {params["speed"]*10000:3.0f}'
                '     [W / Q] Increment / decrement',
                (100, 100, 100),
                (10, height - 50)
            )
            render_text(
                screen,
                f'Influence Proximity: {params["influence_prox"]*100:3.0f}'
                '     [S / A] Increment / decrement ',
                (100, 100, 100),
                (10, height - 70)
            )
            render_text(
                screen,
                f'Alignment factor:    {params["alignment_factor"]*10000:3.0f}'
                '     [R / E] Increment / decrement ',
                (100, 100, 100),
                (10, height - 90)
            )
            render_text(
                screen,
                f'Cohesion factor:     {params["cohesion_factor"]*10000:3.0f}'
                '     [F / D] Increment / decrement',
                (100, 100, 100),
                (10, height - 110)
            )
            render_text(
                screen,
                f'Separation factor:   {params["separation_factor"]*10000:3.0f}'
                '     [Y / T] Increment / decrement',
                (100, 100, 100),
                (10, height - 130)
            )

        # Actual stuff
        positions, velocities = update(dt, positions, velocities, params)
        draw(screen, positions*width/map_size)

        dt = fpsClock.tick(fps)

runPyGame()
