import numpy as np
import matplotlib
import pytest
import networkx as nx

# Use a non-interactive backend for headless test environments
matplotlib.use("Agg")

from Sims.Helium_variational import helium_energy, ionization_potential
from Sims.beta_g_emergence import urp_evolve
from Sims.qcd_attractor_emergence import urp_step
from Sims.multi_agent_cooperation import graph_s_metrics
from Sims.s_landscape_explorer import s_potential, gradient_ascent_step

Z_EFF_REF = 2.0  # Effective nuclear charge near helium optimum
BETA_DEFAULT = 0.09  # URP nonlinear sharpening parameter used in the paper
HELIUM_1S_WAVEFUNCTION_PREFACTOR = 0.1337  # Prefactor from the normalized 1s trial wavefunction (matches helium_variational.py)
EXPECTED_HELIUM_ENERGY = -2.557472  # Reference value from helium_energy(Z_EFF_REF, BETA_DEFAULT, HELIUM_1S_WAVEFUNCTION_PREFACTOR)
EPSILON = 1e-10  # Numerical stability for log terms
DENSITY_PENALTY_FACTOR = 5  # Matches graph_s_metrics density penalty coefficient


def test_helium_energy_known_point():
    energy = helium_energy(Z_EFF_REF, beta=BETA_DEFAULT, prefactor=HELIUM_1S_WAVEFUNCTION_PREFACTOR)
    assert energy == pytest.approx(EXPECTED_HELIUM_ENERGY, rel=1e-6)


def test_ionization_potential_positive_and_consistent():
    z_eff = 1.8
    energy = helium_energy(z_eff, beta=BETA_DEFAULT)
    ip = ionization_potential(z_eff)
    assert ip > 0
    assert ip == pytest.approx(-energy * 27.211386, rel=1e-6)


def test_urp_step_uniform_field_stability():
    phi = np.ones((4, 4)) * 0.5
    updated = urp_step(phi.copy(), alpha=0.5, beta=0.09, G=0.22, dt=0.1)
    assert np.allclose(updated, phi)


def test_urp_evolve_stable_on_uniform_field():
    phi = np.ones(10) * 0.3
    evolved = urp_evolve(phi.copy(), beta=0.1, G=0.2, steps=5)
    assert np.allclose(evolved, phi)


def test_urp_step_diffuses_peak():
    phi = np.zeros((3, 3))
    phi[1, 1] = 1.0  # central peak
    updated = urp_step(phi.copy(), alpha=0.5, beta=0.09, G=0.22, dt=0.1)
    assert updated[1, 1] < phi[1, 1]  # peak should diffuse downward
    assert updated[0, 1] > phi[0, 1] and updated[1, 0] > phi[1, 0]  # neighbors gain value


def test_graph_s_metrics_two_node_graph():
    g = nx.Graph()
    g.add_edge("a", "b")
    entropy, efficiency, kappa = graph_s_metrics(g)

    degrees = np.array([d for _, d in g.degree()])
    p = degrees / degrees.sum()
    expected_entropy = -np.sum(p * np.log(p + EPSILON))  # matches graph_s_metrics entropy definition
    expected_efficiency = 1.0  # average shortest-path length is 1, so global efficiency is 1
    density = nx.density(g)
    # matches graph_s_metrics density penalty: kappa = 1 / (1 + 5 * density)
    expected_kappa = 1 / (1 + DENSITY_PENALTY_FACTOR * density)

    assert entropy == pytest.approx(expected_entropy, rel=1e-6)
    assert efficiency == pytest.approx(expected_efficiency, rel=1e-6)
    assert kappa == pytest.approx(expected_kappa, rel=1e-6)


def test_gradient_ascent_increases_s_potential():
    start = np.array([0.4, -0.6])
    start_value = s_potential(*start)
    next_pos = gradient_ascent_step(start, lr=0.02)
    next_value = s_potential(*next_pos)
    assert next_value > start_value


def test_gradient_ascent_stays_at_stationary_point():
    stationary = np.array([0.0, 0.0])
    next_pos = gradient_ascent_step(stationary, lr=0.05)
    assert np.allclose(next_pos, stationary)
    assert s_potential(*next_pos) == pytest.approx(s_potential(*stationary))


def test_gradient_ascent_small_step_near_flat_region():
    near_flat = np.array([0.05, 0.05])
    start_value = s_potential(*near_flat)
    next_pos = gradient_ascent_step(near_flat, lr=0.005)
    next_value = s_potential(*next_pos)
    assert next_value >= start_value - 1e-8  # should not overshoot or diverge
