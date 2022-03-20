# File for the main flocking simulation for the boids
# Different sims can then use this to show real-time, debug, triangles etc.

import numpy as np

def flock(pos, vel, speed=0.04, influence_prox=0.5, map_size = 20,
          alignment_factor = 0.1, cohesion_factor = 0.01,
          separation_factor = 0.05, debug=False, dt=1):
    """
    Main algo for update boid positions and velocitie
    pos being the 2 x Number of boids array of x and y boid centers
    vel being the 2 x Number of boids array of x and y veolcites

    NOTE
    Now not in use, forces used over this
    """

    # Update positions:
    pos += vel * speed * dt 

    # Bounce off walls...
    # The old method (below) doesn't work sinc ethe velocities can change
    # when it goes out of bounds leading to the next itteration still being
    # out of bounds, despite the change in sign of the velocity, the boid
    # then gets stuck out of bounds until further interactions wiht other
    # boids.
    # Old with bug:
    # vel[pos > map_size] = -vel[pos > map_size]
    # vel[pos + vel * speed < 0] = -vel[pos + vel * speed < 0]
    # Better approach:
    # An ugly method for the fix is just to set the postions of those out of
    # bounds back in bounds and flip the axis velocity as before. This still
    # has potential to force the boids back out of bouns, but now only if
    # other boids are around pushing them out.
    # This methods causes some division by 0 errors that I should probably
    # find the cause of...
    vel[pos > map_size] = -vel[pos > map_size]
    pos[pos > map_size] = map_size
    vel[pos < 0] = -vel[pos < 0]
    pos[pos < 0] = 0  # Setting to 0 here makes some division errors...

    # Wrapping works nicely: 
    # pos = pos % map_size

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

    # Getting some errors when distance is 0... it seems highly unlikely
    # that the distance between boids as a float should ever be 0, but to
    # mitigate against it use small value here
    test1 = relative_x_local / (distance**2 + 1e-12)
    test2 = relative_y_local / (distance**2 + 1e-12)
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



def flock_forces(pos, vel, influence_prox=0.5, map_size = 20,
          alignment_factor = 0.1, cohesion_factor = 0.01,
          separation_factor = 0.05):
    """
    Main algo for update boid positions and velocitie
    pos being the 2 x Number of boids array of x and y boid centers
    vel being the 2 x Number of boids array of x and y veolcites

    NOTE
    Rather than returning the posision and velocity of the boids, this
    func returns the forces acting on the boids. 
    This func does not update the positions or velocities
    """

    # Bounce off walls...
    vel[pos > map_size] = -vel[pos > map_size]
    pos[pos > map_size] = map_size
    vel[pos < 0] = -vel[pos < 0]
    pos[pos < 0] = 0  # Setting to 0 here makes some division errors...

    # Wrapping works nicely: 
    # pos = pos % map_size

    # Get local boids:
    distance = np.linalg.norm(pos - pos[:,None], axis=-1)
    local = distance < influence_prox


    # # Cohesion:
    ##############
    # Add a veolcity vector towards the COM:
    local_coms = (np.dot(local, pos).T / (local.sum(axis=1) + 1e-8)).T
    local_com_diff = local_coms - pos
    cohesion_force = (local_com_diff * cohesion_factor)

    # # Align:
    #############
    local_vel_avg = (np.dot(local, vel).T / (local.sum(axis=1) + 1e-8)).T
    local_vel_diff = local_vel_avg - vel
    align_force = (local_vel_diff * alignment_factor)

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

    # Getting some errors when distance is 0... it seems highly unlikely
    # that the distance between boids as a float should ever be 0, but to
    # mitigate against it use small value here
    test1 = relative_x_local / (distance**2 + 1e-12)
    test2 = relative_y_local / (distance**2 + 1e-12)
    # dividing by the distance converts to unit vectors, dividing again
    # adds a inverse component, stronger at close distances

    sep = -np.array([test1.sum(axis=1), test2.sum(axis=1)]).T
    sep_force = (sep * separation_factor)

    return cohesion_force, align_force, sep_force
