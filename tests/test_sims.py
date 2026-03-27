import os
import sys

import numpy as np
import matplotlib
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Use a non-interactive backend for headless test environments
matplotlib.use("Agg")

from Sims.Helium_variational import helium_energy, ionization_potential
from Sims.beta_g_emergence import urp_evolve
from Sims.qcd_attractor_emergence import urp_step
from Sims.multi_agent_cooperation import graph_s_metrics
from Sims.s_landscape_explorer import s_potential, gradient_ascent_step


def test_helium_energy_known_point():
    energy = helium_energy(2.0, beta=0.09, prefactor=0.1337)
    assert energy == pytest.approx(-2.557472, rel=1e-6)


def test_ionization_potential_positive_and_consistent():
    z_eff = 1.8
    energy = helium_energy(z_eff, beta=0.09)
    ip = ionization_potential(z_eff)
    assert ip > 0
    assert ip == pytest.approx(-energy * 27.211386, rel=1e-6)


def test_urp_step_preserves_constant_field():
    phi = np.ones((4, 4)) * 0.5
    updated = urp_step(phi.copy(), alpha=0.5, beta=0.09, G=0.22, dt=0.1)
    assert np.allclose(updated, phi)


def test_urp_evolve_stable_on_uniform_field():
    phi = np.ones(10) * 0.3
    evolved = urp_evolve(phi.copy(), beta=0.1, G=0.2, steps=5)
    assert np.allclose(evolved, phi)


def test_graph_s_metrics_two_node_graph():
    import networkx as nx

    g = nx.Graph()
    g.add_edge("a", "b")
    entropy, efficiency, kappa = graph_s_metrics(g)

    expected_entropy = np.log(2.0)  # degrees are [1, 1]
    expected_efficiency = 1.0
    expected_kappa = 1 / 6

    assert entropy == pytest.approx(expected_entropy, rel=1e-6)
    assert efficiency == pytest.approx(expected_efficiency, rel=1e-6)
    assert kappa == pytest.approx(expected_kappa, rel=1e-6)


def test_gradient_ascent_increases_s_potential():
    start = np.array([0.4, -0.6])
    start_value = s_potential(*start)
    next_pos = gradient_ascent_step(start, lr=0.02)
    next_value = s_potential(*next_pos)
    assert next_value > start_value
