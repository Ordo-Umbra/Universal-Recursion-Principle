# sims/s_landscape_explorer.py
# ========================================================
# URP S-Landscape Explorer
# Particles climb the S-functional in 2D "physical space"
# Makes the attractor intuitive and playable
#
# Run with: python sims/s_landscape_explorer.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def s_potential(x, y):
    """Simple 2D S-landscape with multiple attractors."""
    return - (x**2 + y**2) + 0.5 * (x**4 + y**4) + 2 * np.sin(3*x) * np.cos(3*y)

def gradient_ascent_step(pos, lr=0.02):
    x, y = pos
    dx = -2*x + 2*x**3 + 6*np.cos(3*x)*np.sin(3*y)
    dy = -2*y + 2*y**3 - 6*np.sin(3*x)*np.cos(3*y)
    return [x + lr*dx, y + lr*dy]

if __name__ == "__main__":
    print("🚀 Running URP S-Landscape Explorer...\n")
    
    # Create landscape
    x = np.linspace(-2, 2, 100)
    y = np.linspace(-2, 2, 100)
    X, Y = np.meshgrid(x, y)
    Z = s_potential(X, Y)
    
    # Particles (agents/ideas) starting random
    n_particles = 30
    positions = np.random.uniform(-1.5, 1.5, (n_particles, 2))
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.contourf(X, Y, Z, levels=30, cmap='viridis')
    ax.set_title('URP S-Landscape Explorer\n'
                 'Particles climb ΔC + κΔI toward stable attractors')
    ax.set_xlabel('Distinction axis')
    ax.set_ylabel('Integration axis')
    scatter = ax.scatter(positions[:,0], positions[:,1], c='red', s=40, alpha=0.8)
    
    def update(frame):
        for i in range(n_particles):
            positions[i] = gradient_ascent_step(positions[i])
        scatter.set_offsets(positions)
        return scatter,
    
    ani = FuncAnimation(fig, update, frames=80, interval=50, blit=True)
    plt.savefig('s_landscape_explorer.png', dpi=300, bbox_inches='tight')
    print("✅ Plot saved as 's_landscape_explorer.png'")
    print("🎯 Watch ideas/agents physically climb the S-surface in real time.")
    print("   This is the intuitive 'physical space' version of the attractor.")
