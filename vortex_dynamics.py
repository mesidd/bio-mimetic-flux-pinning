import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
num_vortices = 80        
num_pins = 80            
box_size = 20.0          
force_steps = 60         
max_current = 2.5        

# --- 1. DEFINE GEOMETRIES ---

def generate_random_pins(n, box):
    """Standard Industry: Chaos."""
    return np.random.rand(n, 2) * box

def generate_hex_pins(n, box):
    """Crystal: Perfect Order, but Brittle (Straight Lines)."""
    side = int(np.sqrt(n)) 
    x = np.linspace(0, box, side)
    y = np.linspace(0, box, side)
    xv, yv = np.meshgrid(x, y)
    xv[::2] += (box / side) / 2
    pins = np.column_stack((xv.flatten(), yv.flatten()))
    return pins[:n]

def generate_spiral_pins(n, box):
    """THE HYBRID: Golden Angle Spiral (Schauberger/Phyllotaxis).
    High packing density, but NO straight lines for vortices to slide on."""
    pins = []
    golden_angle = np.pi * (3 - np.sqrt(5)) # ~137.5 degrees
    
    # Place pins from center outwards
    for i in range(n):
        theta = i * golden_angle
        r = np.sqrt(i) / np.sqrt(n) * (box/2 * 0.95) # Scale to fit box
        
        # Convert polar to cartesian and center in box
        x = r * np.cos(theta) + box/2
        y = r * np.sin(theta) + box/2
        pins.append([x, y])
        
    return np.array(pins)

# --- 2. THE PHYSICS ENGINE (Vortex Dynamics) ---

def run_wind_tunnel(pins, label):
    # Initialize Vortices (Start them at random positions)
    vortices = np.random.rand(num_vortices, 2) * box_size
    currents = np.linspace(0, max_current, force_steps)
    voltages = [] 
    
    print(f"Testing {label} Design...")
    
    for drive_force in currents:
        avg_velocity = 0
        
        # Simulation Loop (Relaxation)
        for t in range(40): 
            forces = np.zeros_like(vortices)
            
            # A. Vortex Repulsion
            for i in range(num_vortices):
                diff = vortices - vortices[i]
                diff = diff - np.round(diff / box_size) * box_size # Toroidal BC
                dist = np.linalg.norm(diff, axis=1)
                
                with np.errstate(divide='ignore'):
                    force_mag = 1.0 / (dist + 0.1)
                force_mag[i] = 0
                
                norm_diff = np.zeros_like(diff)
                mask = dist > 0
                norm_diff[mask] = diff[mask] / dist[mask, None]
                forces[i] += np.sum(norm_diff * force_mag[:, None], axis=0)

            # B. Pin Attraction
            for i in range(num_vortices):
                diff_p = pins - vortices[i]
                diff_p = diff_p - np.round(diff_p / box_size) * box_size
                dist_p = np.linalg.norm(diff_p, axis=1)
                
                # Stronger, shorter-range pins for this test
                mask_p = dist_p < 0.8
                if np.any(mask_p):
                    pull = diff_p[mask_p] * 8.0 
                    forces[i] += np.sum(pull, axis=0)

            # C. The Wind (Current)
            forces[:, 0] += drive_force 
            
            # D. Move
            vortices += forces * 0.05
            vortices = np.mod(vortices, box_size)
            
            avg_velocity += np.mean(forces[:, 0]) # Measure speed in wind direction
            
        voltages.append(avg_velocity / 40)
        
    return currents, voltages

# --- 3. RUN THE BATTLE ---

# Generate Boards
pins_rand = generate_random_pins(num_pins, box_size)
pins_hex = generate_hex_pins(num_pins, box_size)
pins_spiral = generate_spiral_pins(num_pins, box_size)

# Run Simulations
j_rand, v_rand = run_wind_tunnel(pins_rand, "Standard (Random)")
j_hex, v_hex = run_wind_tunnel(pins_hex, "Crystal (Hexagonal)")
j_spiral, v_spiral = run_wind_tunnel(pins_spiral, "Hybrid (Golden Spiral)")

# --- 4. VISUALIZE ---
plt.figure(figsize=(10, 6))

plt.plot(j_rand, v_rand, 'b-o', label='Random (Standard)', markersize=3, alpha=0.4)
plt.plot(j_hex, v_hex, 'r--', label='Hexagonal (Brittle)', linewidth=1.5, alpha=0.6)
plt.plot(j_spiral, v_spiral, 'g-s', label='Golden Spiral (Schauberger)', linewidth=2.5)

plt.title("The Ultimate Pinning Test: Random vs. Crystal vs. Spiral")
plt.xlabel("Applied Current (Wind Force)")
plt.ylabel("Voltage (Resistance)")
plt.legend()
plt.grid(True, alpha=0.3)

plt.show()

# Show the Pin layouts for visual confirmation
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
ax1.scatter(pins_rand[:,0], pins_rand[:,1], c='blue'); ax1.set_title("Random")
ax2.scatter(pins_hex[:,0], pins_hex[:,1], c='red'); ax2.set_title("Hexagonal")
ax3.scatter(pins_spiral[:,0], pins_spiral[:,1], c='green'); ax3.set_title("Golden Spiral")
plt.show()
