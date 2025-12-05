# Physics Simulator: Projectile Motion (Tkinter)

## Introduction

This project is a 2D physics simulator built with Python and Tkinter, designed to model projectile motion under various environmental conditions. It features an interactive graphical interface where users can launch projectiles and observe their trajectories, affected by factors like gravity, air resistance, and wind. The simulator demonstrates core object-oriented programming (OOP) principles through its class design for `Projectile`, `Particle`, and `Simulator` components.

## Features

* **Interactive GUI:** Built with Tkinter for a user-friendly experience.
* **Projectile Firing:** Launch projectiles by clicking the mouse or pressing the spacebar. Hold spacebar for rapid auto-fire.
* **Adjustable Aiming:** Control projectile launch angle using the mouse position or arrow keys.
* **Physics Simulation:**
    *   **Gravity:** Configurable gravitational force affecting projectiles.
    *   **Air Resistance (Drag):** Adjustable air drag coefficient.
    *   **Wind:** Dynamic wind forces that can be adjusted during simulation.
* **Particle Effects:** Visual explosions and ricochet sparks upon projectile impact or expiry.
* **Targeting System:** An interactive target that reacts to direct hits.
* **Debug Overlay:** Toggleable debug information showing current FPS, projectile count, and particle count.
* **Customizable Simulation Parameters:** Easily adjust parameters like projectile speed, maximum active projectiles/particles, auto-fire rate, and canvas dimensions.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

* **Python 3.7+**: The simulator is developed using modern Python syntax and features.
* **Tkinter**: Usually comes pre-installed with standard Python distributions. No additional installation is typically required.

## Usage

Once the application window appears:

- **Aim:** Move your mouse to aim the cannon. You can also use the **Left** and **Right** arrow keys for fine-tuning the aim.

- **Fire:** Click the left mouse button or press the **Spacebar** to launch a projectile. Hold down the **Spacebar** for rapid fire.

- **Adjust Wind:** Use the **[** (left bracket) and **]** (right bracket) keys to decrease and increase the wind force, respectively.

- **Toggle Debug Info:** Press the **D** key to show/hide the debug overlay (displaying projectile/particle counts).

- **Adjust Gravity, Air Drag, Projectile Speed, etc.:** These parameters can be modified by editing the `application.py` file directly, where the `Simulator` instance is configured.

## Object-Oriented Principles Applied

This project heavily utilizes OOP concepts to achieve a modular and maintainable design:

- **Encapsulation:** Attributes like `Projectile`'s `GRAVITY`, `AIR_DRAG`, and `WIND` are encapsulated using Python properties (`@property` and `@setter`). This allows controlled access and modification, as demonstrated by the resolution of previous `AttributeError`s and `RecursionError`s.

- **Inheritance:** The `Simulator` class inherits from `Projectile`. This design choice allows the `Simulator` instance itself to hold and manage physics parameters like `GRAVITY` and `WIND` directly, which are then passed to the individual `Projectile` objects it creates.

- **Composition:** The `Simulator` class manages a list of `Projectile` and `Particle` objects, demonstrating composition as it "has a" collection of these other objects.

- **`__slots__`:** The `Projectile` and `Particle` classes use `__slots__` to explicitly define their attributes, reducing memory consumption and improving attribute access speed.

- **Modular Design:** The separation of concerns into distinct classes (`Simulator`, `Projectile`, `Particle`) makes the codebase easier to understand, test, and extend.

## Folder Structure

```

Physics_Simulator_Projectile_TKinter/
│
├── Non_OO_Version_of_simulator/
│          │
│          └── aim_nd_fire_cpu.py             # Main file that contains the (spaghetti) version of the code
│         
├── OO_Version_of_Projectile_fire_simulator/  # OO version of the simulator engine
│               │
│               ├── main.py
│               └── Engine/        
│                       │
│                       ├── application.py      # application
│                       ├── Simulator_class.py  # simulator class that holds the projectile and particle 
│                       ├── Projectile_class.py # projectile contains the particles
│                       └── Particle_class.py   # particles forming after the collision of the projectile
│
├── README.md
└── LICENSE

```