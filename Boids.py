#!/usr/bin/python3
# 2022-02-19

# Boids 1.0
# A roughly working version.
# still some bugs with edges, and motion becomes a predictable
# swirl with i think is unavoidable...

# %%
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

# %%
# Initialisation:

# Commnad line args for mode:
import sys
try:
    modes = {
        '0': 'FILE_SAVE',
        '1': 'REAL_TIME',
        '2': 'DEBUG'
    }
    MODE = modes[sys.argv[1]]
except IndexError:
    # MODE = 'FILE_SAVE'
    MODE = 'REAL_TIME'
    # MODE = 'DEBUG'
except KeyError:
    # Running in vs code
    MODE = 'VSCODE_DEBUG'
    np.set_printoptions(precision=2)

influence_prox = .5
speed = 0.04

map_size = 20
number = 200

alignment_factor = 0.1
cohesion_factor = 0.01
separation_factor = 0.05

positions = np.random.rand(number, 2) * map_size
velocities = (np.random.rand(number, 2) * 2) - 1

# # Super debug mode:
# positions = np.array([[1, map_size/2], [4, map_size/2], ])
# velocities = np.array([[1.0, 0], [-1, 0], ])

# %%
def algo(pos, vel, debug=False):
    """ Main algo for update boid positions and velocities"""

    # Update positions:
    pos += vel * speed

    # Bounce off walls...
    # This has a slight bug of showing 1 ish frames with the boid off the
    # screen when going to large x and y
    vel[pos > map_size] = -vel[pos > map_size]
    vel[pos + vel * speed < 0] = -vel[pos + vel * speed < 0]

    # Get local boids:
    distance = np.linalg.norm(pos - pos[:,None], axis=-1)
    local = distance < influence_prox


    # # Cohesion:
    ##############
    # Add a veolcity vector towards the COM:
    local_coms = (np.dot(local, pos).T / (local.sum(axis=1) + 1e-8)).T
    local_com_diff = local_coms - pos
    cohesion_v = (local_com_diff * cohesion_factor)

    # # Align:
    #############
    local_vel_avg = (np.dot(local, vel).T / (local.sum(axis=1) + 1e-8)).T
    local_vel_diff = local_vel_avg - vel
    align_v = (local_vel_diff * alignment_factor)

    # Drop Boids from their own local regions:
    np.fill_diagonal(local, False)
    # But ensure that they won't error out on a divide:
    np.fill_diagonal(distance, 1)

    # # Separation:
    ##############
    # There might be a better way to do this, but at the moment
    # I can't think of one...
    relative_x = pos[:, 0] - pos[:, 0, None]
    relative_y = pos[:, 1] - pos[:, 1, None]
    relative_x_local = relative_x * local
    relative_y_local = relative_y * local

    test1 = relative_x_local / distance**2
    test2 = relative_y_local / distance**2
    # dividing by the distance converts to unit vectors, dividing again
    # adds a inverse component, stronger at close distances

    sep = -np.array([test1.sum(axis=1), test2.sum(axis=1)]).T
    sep_v = (sep * separation_factor)

    vel += cohesion_v + align_v + sep_v

    # There has to be a better way of doing this bit, but this is speed
    # setting, ensuring all boids have unit speed (otherwise things tend to
    # stop)
    for v in range(len(vel)):
        vel[v, :] = vel[v, :] / np.linalg.norm(vel[v, :])

    if debug:
        return pos, vel, local, local_coms, local_vel_avg, local_com_diff, sep

    return pos, vel

# %%
if MODE == 'DEBUG':
    def onspace(event):
        global positions
        global velocities
        plt.clf()
        positions, velocities, local, local_coms, local_vel_avg, local_com_diff, sep = \
            algo(positions, velocities, debug=True)

        ##########
        # Visuals:
        ##########

        # Other boids:
        plt.scatter(*positions[~local[0], :].T, alpha=0.2)
        plt.quiver(
            *positions[~local[0], :].T,
            *velocities[~local[0], :].T,
            color='blue', alpha=0.2, width=0.01,
            units='xy'
        )

        # Separation
        plt.quiver(
            *positions.T,
            *sep.T,
            color='red', alpha=0.2, width=0.01,
            units='xy', scale = 1
        )

        # Local boids:
        plt.scatter(*positions[local[0], :].T)
        plt.quiver(
            *positions[local[0], :].T,
            *velocities[local[0], :].T,
            color='blue', width=0.01,
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
            color='yellow', width=0.01,
            units='xy', scale = 1
        )

        # Cohesion:
        plt.quiver(
            *positions[0, :],
            *local_com_diff[0, :],
            color='green', width=0.01,
            units='xy', scale = 1
        )

        # Separation:
        plt.quiver(
            *positions[0, :],
            *sep[0, :],
            color='red', width=0.01,
            units='xy', scale = 1
        )

        plt.xlim([0, map_size])
        plt.ylim([0, map_size])
        plt.gca().set_aspect('equal')

        # plt.subplot(212)
        # plt.hist(dirs , bins='auto', range=(-np.pi, np.pi))
        plt.draw()


    # fig, ax = plt.subplots(2, 1)
    fig, ax = plt.subplots(figsize=(7, 7))
    fig.canvas.mpl_connect('key_press_event', onspace)
    onspace(None)
    plt.show()

if MODE == 'REAL_TIME':
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.set_xlim(0, map_size)
    ax.set_ylim(0, map_size)

    def animate(frame, boids, positions, velocities):
        positions, velocities = algo(positions, velocities)
        boids.set_data(*positions.T)

    boids,  = plt.plot(*positions.T, '.')
    anim = animation.FuncAnimation(
        fig, animate, fargs=(boids, positions, velocities), interval=10,
        blit=False
    )
    plt.show()

if MODE == 'VSCODE_DEBUG':
    positions += velocities * speed
    # Bounce off walls...
    # This has a slight bug of showing 1 ish frames with the boid off the
    # screen when going to large x and y
    velocities[positions > map_size] = -velocities[positions > map_size]
    velocities[positions + velocities * speed < 0] = -velocities[positions + velocities * speed < 0]

    # Get local boids:
    distance = np.linalg.norm(positions - positions[:,None], axis=-1)
    local = distance < influence_prox


    # # Cohesion:
    ##############
    # Add a veolcity vector towards the COM:
    local_coms = (np.dot(local, positions).T / (local.sum(axis=1) + 1e-8)).T
    local_com_diff = local_coms - positions
    cohesion_v = (local_com_diff * cohesion_factor)

    # # Align:
    #############
    local_vel_avg = (np.dot(local, velocities).T / (local.sum(axis=1) + 1e-8)).T
    local_vel_diff = local_vel_avg - velocities
    align_v = (local_vel_diff * alignment_factor)

    # Drop Boids from their own local regions:
    np.fill_diagonal(local, False)

    # But ensure that they won't error out on a divide:
    np.fill_diagonal(distance, 1)

    # # Separation:
    ##############
    relative_x = pos[:, 0] - pos[:, 0, None]
    relative_y = pos[:, 1] - pos[:, 1, None]
    relative_x_local = relative_x * local
    relative_y_local = relative_y * local

    test1 = relative_x_local / distance**2
    test2 = relative_y_local / distance**2

    sep = -np.array([test1.sum(axis=1), test2.sum(axis=1)]).T
    sep_v = (sep * separation_factor)

    velocities += cohesion_v + align_v + sep_v

    #######
    # DEBUG
    #######

    print(relative_x_local)
    print(relative_y_local)



    ##########
    # Visuals:
    ##########

    # Other boids:
    plt.scatter(*positions[~local[0], :].T, alpha=0.2)
    plt.quiver(
        *positions[~local[0], :].T,
        *velocities[~local[0], :].T,
        color='blue', alpha=0.2, width=0.01,
        units='xy'
    )

    # Separation
    plt.quiver(
        *positions.T,
        *sep.T,
        color='red', alpha=0.2, width=0.01,
        units='xy', scale = 1
    )

    # Local boids:
    plt.scatter(*positions[local[0], :].T)
    plt.quiver(
        *positions[local[0], :].T,
        *velocities[local[0], :].T,
        color='blue', width=0.01,
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
        color='yellow', width=0.01,
        units='xy', scale = 1
    )

    # Cohesion:
    plt.quiver(
        *positions[0, :],
        *local_com_diff[0, :],
        color='green', width=0.01,
        units='xy', scale = 1
    )

    # Separation:
    plt.quiver(
        *positions[0, :],
        *sep[0, :],
        color='red', width=0.01,
        units='xy', scale = 1
    )

    plt.xlim([0, map_size])
    plt.ylim([0, map_size]) 
    plt.gca().set_aspect('equal')

    # plt.subplot(212)
    # plt.hist(dirs , bins='auto', range=(-np.pi, np.pi))
    plt.draw()
# %%
