import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- CONFIGURATION (The "Physics" Dial) ---
N = 100           # Grid size (resolution of the field)
L = 20.0          # Physical size of the superconductor
kappa = 5.0       # Ginzburg-Landau parameter (Type-II superconductor)
B_ext = 0.8       # External Magnetic Field strength
dt = 0.01         # Time step
steps = 500       # Number of simulation frames

# --- INITIALIZATION ---
# Create the "Orgone Field" (Order Parameter psi)
# We start with a random complex field (chaos)
x = np.linspace(-L/2, L/2, N)
y = np.linspace(-L/2, L/2, N)
X, Y = np.meshgrid(x, y)
psi = np.ones((N, N), dtype=complex) + 0.1 * (np.random.rand(N, N) + 1j * np.random.rand(N, N))

# Vector Potential A (Simulating the magnetic stress)
# Using Landau gauge A = (0, Bx, 0)
A_x = np.zeros((N, N))
A_y = B_ext * X

# Laplacian operator for the kinetic energy term
def laplacian(f, dx):
    return (np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0) +
            np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1) - 4*f) / (dx**2)

# --- THE SIMULATION LOOP (Evolving the Field) ---
dx = L / N
fig, ax = plt.subplots(figsize=(6, 5))
cax = ax.imshow(np.abs(psi)**2, extent=[-L/2, L/2, -L/2, L/2], origin='lower', cmap='inferno')
ax.set_title("Vortex Lattice Formation (Superconducting Density)")
fig.colorbar(cax, label="Superconducting Density |psi|^2")

def update(frame):
    global psi
    
    # 1. Calculate the Supercurrent / Kinetic Term
    # (Simplified discretized covariant derivative for visualization purposes)
    D2_psi = laplacian(psi, dx) - (2j * dx * B_ext * X * np.gradient(psi, axis=0)[0]) # Approx magnetic coupling
    
    # 2. The Ginzburg-Landau "Potentials"
    # alpha * psi + beta * |psi|^2 * psi
    # This term forces the field to be either 0 (normal) or 1 (superconducting)
    potential_term = (1 - np.abs(psi)**4) * psi
    
    # 3. Evolve the system (Relaxation)
    psi += dt * (D2_psi + potential_term)
    
    # Boundary conditions (Periodic to simulate infinite field)
    psi[0, :] = psi[-2, :]
    psi[-1, :] = psi[1, :]
    psi[:, 0] = psi[:, -2]
    psi[:, -1] = psi[:, 1]

    cax.set_data(np.abs(psi)**2)
    return cax,

ani = animation.FuncAnimation(fig, update, frames=steps, interval=20, blit=False)
plt.show()
