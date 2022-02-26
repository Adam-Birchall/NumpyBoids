#!/usr/bin/python3
# 2022-02-19

# Debug code for the main flocking algo

# %%
import numpy as np
from Flocking import flock
from matplotlib import pyplot as plt
from matplotlib import animation

# %%
# Initialisation:

influence_prox = 1
speed = 0.04

map_size = 10

alignment_factor = 0.05
cohesion_factor = 0.005
separation_factor = 0.005

number = 20
positions = np.random.rand(number, 2) * map_size
velocities = (np.random.rand(number, 2) * 2) - 1

# # Super debug mode:
# positions = np.array([[1, map_size/2], [4, map_size/2], ])
# velocities = np.array([[1.0, 0], [-1, 0], ])

# %%
def onkey(event):
    global positions
    global velocities
    plt.clf()
    positions, velocities, local, local_coms, local_vel_avg, local_com_diff, sep = \
        flock(positions, velocities, 
              debug=True,
              influence_prox = influence_prox,
              speed = speed,
              map_size = map_size,
              alignment_factor = alignment_factor,
              cohesion_factor = cohesion_factor,
              separation_factor = separation_factor)

    ##########
    # Visuals:
    ##########
    arrow_widths = 0.04
    # Other boids:
    plt.scatter(*positions[~local[0], :].T, alpha=0.2)
    plt.quiver(
        *positions[~local[0], :].T,
        *velocities[~local[0], :].T,
        color='blue', alpha=0.2, width=arrow_widths,
        units='xy'
    )

    # Separation
    plt.quiver(
        *positions.T,
        *sep.T,
        color='red', alpha=0.2, width=arrow_widths,
        units='xy', scale = 1
    )

    # Local boids:
    plt.scatter(*positions[local[0], :].T)
    plt.quiver(
        *positions[local[0], :].T,
        *velocities[local[0], :].T,
        color='blue', width=arrow_widths,
        units='xy'
    )
    local_rad = plt.Circle(positions[0, :], influence_prox, color='r',
        alpha=0.2)
    plt.gca().add_patch(local_rad)

    # Centre of mass for boid of interest:
    plt.scatter(*local_coms[0].T, color='green')

    # Boid of interest:
    plt.scatter(*positions[0, :])
    plt.text(*positions[0, :],
        f'{np.sqrt(velocities[0, 0]**2 + velocities[0, 1]**2):.2f}')

    # Alignment:
    plt.quiver(
        *positions[0, :],
        *local_vel_avg[0, :],
        color='yellow', width=arrow_widths,
        units='xy', scale = 1
    )

    # Cohesion:
    plt.quiver(
        *positions[0, :],
        *local_com_diff[0, :],
        color='green', width=arrow_widths,
        units='xy', scale = 1
    )

    # Separation:
    plt.quiver(
        *positions[0, :],
        *sep[0, :],
        color='red', width=arrow_widths,
        units='xy', scale = 1
    )

    plt.xlim([0, map_size])
    plt.ylim([0, map_size])
    plt.gca().set_aspect('equal')

    # plt.subplot(212)
    # plt.hist(dirs , bins='auto', range=(-np.pi, np.pi))
    plt.draw()


# fig, ax = plt.subplots(2, 1)

print("Displaying in debug mode. Press any key when focused on plot to "
      "continue to the next time step")
fig, ax = plt.subplots(figsize=(7, 7))
plt.subplots_adjust(bottom=0.25)

fig.canvas.mpl_connect('key_press_event', onkey)
onkey(None)
plt.show()
