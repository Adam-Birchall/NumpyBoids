#!/usr/bin/python3
# 2022-02-19

# Boids
# Motion becomes a predictable swirl under some input params which I think is
# unavoidable
# The alighnment, cohesion andseparation are all handeled the in flock 
# function, in the Flocking file.

# %%
import numpy as np
from Flocking import flock
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.widgets import Slider, CheckButtons

# %%
# Initialisation:

initial_speed = 0.04
inital_influence_prox = .5

map_size = 10

inital_alignment_factor = 0.1
inital_cohesion_factor = 0.5
inital_separation_factor = 0.01

number = 200
positions = np.random.rand(number, 2) * map_size
velocities = (np.random.rand(number, 2) * 2) - 1

slider_visible = False

# %%
fig = plt.figure(figsize=(7, 7))
ax = fig.add_axes([0, 0, 1, 1])
ax.axis('off')
ax.set_xlim(0, map_size)
ax.set_ylim(0, map_size)

def animate(frame, boids, positions, velocities):
    positions, velocities = flock(positions, velocities,
                                  influence_prox = influence_slider.val,
                                  speed = speed_slider.val,
                                  map_size = map_size,
                                  alignment_factor = alignment_slider.val,
                                  cohesion_factor = cohesion_slider.val,
                                  separation_factor = separation_slider.val)
    boids.set_data(*positions.T)

boids,  = plt.plot(*positions.T, '.')

# Sliders for parmeters:
ax_speed = plt.axes([0.3, 0.05, 0.4, 0.03])
speed_slider = Slider(ax_speed, 'Speed', 0.01, 0.1, valinit=initial_speed)
ax_speed.set_visible(False)

ax_influence = plt.axes([0.3, 0.1, 0.4, 0.03])
influence_slider = Slider(ax_influence, 'Influence Proximity', 0, 3,
    valinit=inital_influence_prox)

ax_alignment = plt.axes([0.3, 0.15, 0.4, 0.03])
alignment_slider = Slider(ax_alignment, 'Alignment factor', 0, 0.5,
    valinit=inital_alignment_factor)

ax_cohesion = plt.axes([0.3, 0.2, 0.4, 0.03])
cohesion_slider = Slider(ax_cohesion, 'Cohesion factor', 0, 1,
    valinit=inital_cohesion_factor)

ax_separation = plt.axes([0.3, 0.25, 0.4, 0.03])
separation_slider = Slider(ax_separation, 'Separation factor', 0, 0.2,
    valinit=inital_separation_factor)

ax_speed.set_visible(slider_visible)
ax_influence.set_visible(slider_visible)
ax_alignment.set_visible(slider_visible)
ax_cohesion.set_visible(slider_visible)
ax_separation.set_visible(slider_visible)

def toggle_sliders(_):
    global slider_visible
    if slider_visible:
        ax_speed.set_visible(False)
        ax_influence.set_visible(False)
        ax_alignment.set_visible(False)
        ax_cohesion.set_visible(False)
        ax_separation.set_visible(False)
        slider_visible = False
    else:
        ax_speed.set_visible(True)
        ax_influence.set_visible(True)
        ax_alignment.set_visible(True)
        ax_cohesion.set_visible(True)
        ax_separation.set_visible(True)
        slider_visible = True


ax_toggle = plt.axes([0.01, 0.01, 0.1, 0.1])
ax_toggle.axis('off')
check = CheckButtons(ax_toggle, ['Show sliders'], [slider_visible])
check.on_clicked(toggle_sliders)

anim = animation.FuncAnimation(
    fig, animate, fargs=(boids, positions, velocities), interval=10,
    blit=False
)
plt.show()
