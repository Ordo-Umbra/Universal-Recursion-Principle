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
from Sims.biology_urp import (
    simulate_cell_demon,
    simulate_enzyme_demon,
    sagawa_ito_check,
)
from Sims.layerwise_transformer import compute_layer_metrics, simulate_layerwise
from Sims.real_transformer_layerwise import (
    entropy as real_entropy,
    softmax as real_softmax,
    compute_layer_c,
    compute_layer_i,
    compute_layer_kappa,
    compute_layer_s,
    per_head_metrics,
)

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


# ===========================================================================
# Biology URP simulation
# ===========================================================================

def test_cell_demon_returns_correct_shapes():
    n = 30
    dC, dI, kap, S = simulate_cell_demon(n_steps=n, rng_seed=1)
    for arr in (dC, dI, kap, S):
        assert arr.shape == (n,)


def test_cell_demon_s_values_non_negative():
    dC, dI, kap, S = simulate_cell_demon(n_steps=40, rng_seed=2)
    assert np.all(S >= 0)


def test_cell_demon_kappa_in_valid_range():
    _, _, kap, _ = simulate_cell_demon(n_steps=40, rng_seed=3)
    assert np.all(kap > 0)
    assert np.all(kap <= 1.0)


def test_cell_demon_custom_kappa_schedule():
    schedule = [0.9, 0.8, 0.7]
    dC, dI, kap, S = simulate_cell_demon(n_steps=5, kappa_schedule=schedule, rng_seed=4)
    assert kap[0] == pytest.approx(0.9)
    assert kap[1] == pytest.approx(0.8)
    assert kap[2] == pytest.approx(0.7)
    # Last value repeated for remaining steps
    assert kap[3] == pytest.approx(0.7)
    assert kap[4] == pytest.approx(0.7)


def test_enzyme_demon_returns_correct_shapes():
    n = 50
    C, I, kap, S, dev = simulate_enzyme_demon(n_steps=n, rng_seed=5)
    for arr in (C, I, kap, S, dev):
        assert arr.shape == (n,)


def test_enzyme_demon_deviation_non_negative():
    _, _, _, _, dev = simulate_enzyme_demon(n_steps=40, rng_seed=6)
    assert np.all(dev >= 0)


def test_enzyme_demon_s_formula():
    """S = C + kappa * I at every step."""
    C, I, kap, S, _ = simulate_enzyme_demon(n_steps=20, rng_seed=7)
    expected_S = C + kap * I
    assert np.allclose(S, expected_S)


def test_sagawa_ito_check_no_violations():
    """Well-behaved cell demon should satisfy the budget bound."""
    dC, dI, kap, _ = simulate_cell_demon(n_steps=60, rng_seed=8)
    violations, ok = sagawa_ito_check(dC, dI, kap)
    assert ok is True


def test_sagawa_ito_check_detects_violations():
    """Manually constructed violation should be caught."""
    dC = np.array([0.1, 0.1, 0.1])
    dI = np.array([0.5, 0.5, 0.5])  # dI > kap * dC → violation
    kap = np.array([1.0, 1.0, 1.0])
    violations, ok = sagawa_ito_check(dC, dI, kap)
    assert ok is False
    assert violations.any()


# ===========================================================================
# Layerwise transformer simulation
# ===========================================================================

def test_layerwise_returns_correct_shapes():
    n = 6
    C, I, kap, S, dS = simulate_layerwise(n_layers=n, seq_len=8, vocab_size=32, rng_seed=0)
    for arr in (C, I, kap, S, dS):
        assert arr.shape == (n,)


def test_layerwise_delta_s_starts_at_zero():
    _, _, _, _, dS = simulate_layerwise(n_layers=4, rng_seed=1)
    assert dS[0] == pytest.approx(0.0)


def test_layerwise_delta_s_matches_diff():
    _, _, _, S, dS = simulate_layerwise(n_layers=6, rng_seed=2)
    for l in range(1, len(S)):
        assert dS[l] == pytest.approx(S[l] - S[l - 1])


def test_layerwise_s_mostly_increases():
    """At least half of layer transitions should show S increasing (§6 hypothesis)."""
    _, _, _, S, dS = simulate_layerwise(n_layers=8, seq_len=16, vocab_size=64, rng_seed=0)
    n_nondecreasing = int((dS[1:] >= 0).sum())
    # The hypothesis is probabilistic; require at least half
    assert n_nondecreasing >= len(S) // 2


def test_layerwise_final_layer_c_drops():
    """Output collapse at the final layer should drive C below the early-layer peak."""
    C, _, _, _, _ = simulate_layerwise(n_layers=8, seq_len=16, vocab_size=64, rng_seed=0)
    peak_C = C[:-1].max()
    assert C[-1] < peak_C


def test_compute_layer_metrics_known_values():
    """Uniform distributions should give maximum entropy C and zero I."""
    n_tokens = 4
    vocab_size = 8
    # Uniform predictive → max entropy
    uniform_preds = np.full((n_tokens, vocab_size), 1.0 / vocab_size)
    # Uniform attention → zero integration
    uniform_attn = np.full((n_tokens, n_tokens), 1.0 / n_tokens)
    C, I, kappa, S = compute_layer_metrics(uniform_preds, uniform_attn, beta=1.0)
    expected_C = np.log(vocab_size)
    expected_I = 0.0
    assert C == pytest.approx(expected_C, rel=1e-4)
    assert I == pytest.approx(expected_I, abs=1e-6)
    assert kappa > 0
    assert S == pytest.approx(C + kappa * I, rel=1e-6)


# ===========================================================================
# Real transformer layerwise metric functions
# ===========================================================================

def test_real_transformer_entropy_uniform():
    """Uniform distribution → H = log(n)."""
    n = 8
    p = np.ones(n) / n
    assert real_entropy(p) == pytest.approx(np.log(n), rel=1e-6)


def test_real_transformer_entropy_peaked():
    """One-hot distribution → H ≈ 0."""
    p = np.zeros(10)
    p[3] = 1.0
    assert real_entropy(p) == pytest.approx(0.0, abs=1e-9)


def test_real_transformer_softmax_uniform():
    """Equal logits → uniform probabilities."""
    x = np.zeros((4, 8))
    probs = real_softmax(x)
    assert np.allclose(probs, 1.0 / 8, atol=1e-10)


def test_real_transformer_softmax_preserves_rows():
    """Softmax rows sum to 1."""
    rng = np.random.default_rng(42)
    x = rng.standard_normal((6, 20))
    probs = real_softmax(x)
    assert np.allclose(probs.sum(axis=-1), 1.0, atol=1e-10)
    assert np.all(probs >= 0)


def test_real_transformer_c_uniform_logits():
    """Uniform logits → C = log(vocab_size) (maximum entropy)."""
    seq_len, vocab = 4, 16
    logits = np.zeros((seq_len, vocab))
    c = compute_layer_c(logits)
    assert c == pytest.approx(np.log(vocab), rel=1e-4)


def test_real_transformer_c_peaked_logits():
    """Peaked logits → C near 0."""
    seq_len, vocab = 4, 16
    logits = np.full((seq_len, vocab), -100.0)
    for i in range(seq_len):
        logits[i, i % vocab] = 100.0
    c = compute_layer_c(logits)
    assert c < 0.01


def test_real_transformer_i_uniform_attention():
    """Uniform attention → I = 0 (no selective routing)."""
    n_heads, seq_len = 2, 8
    attn = np.ones((n_heads, seq_len, seq_len)) / seq_len
    i = compute_layer_i(attn)
    assert i == pytest.approx(0.0, abs=1e-6)


def test_real_transformer_i_focused_attention():
    """One-hot attention → I = log(n) (maximum integration)."""
    n_heads, seq_len = 2, 8
    attn = np.zeros((n_heads, seq_len, seq_len))
    for h in range(n_heads):
        for pos in range(seq_len):
            attn[h, pos, 0] = 1.0  # all attend to position 0
    i = compute_layer_i(attn)
    assert i == pytest.approx(np.log(seq_len), rel=1e-4)


def test_real_transformer_kappa_uniform():
    """Uniform attention → low variance → κ ≈ 1."""
    n_heads, seq_len = 2, 8
    attn = np.ones((n_heads, seq_len, seq_len)) / seq_len
    kappa = compute_layer_kappa(attn)
    assert kappa == pytest.approx(1.0, abs=0.01)


def test_real_transformer_kappa_formula():
    """κ = 1/(1 + β·σ²) matches direct computation."""
    n_heads, seq_len = 2, 4
    rng = np.random.default_rng(99)
    raw = rng.random((n_heads, seq_len, seq_len))
    attn = raw / raw.sum(axis=-1, keepdims=True)
    beta = 2.5

    # Direct computation
    variances = []
    for h in range(n_heads):
        for i in range(seq_len):
            variances.append(float(np.var(attn[h, i])))
    expected_sigma_sq = float(np.mean(variances))
    expected_kappa = 1.0 / (1.0 + beta * expected_sigma_sq)

    kappa = compute_layer_kappa(attn, beta=beta)
    assert kappa == pytest.approx(expected_kappa, rel=1e-9)


def test_real_transformer_s_formula():
    """S = C + κ·I for known inputs."""
    seq_len, vocab = 4, 16
    n_heads = 2
    logits = np.zeros((seq_len, vocab))  # uniform → C = log(16)
    attn = np.ones((n_heads, seq_len, seq_len)) / seq_len  # uniform → I = 0
    c, i, kappa, s = compute_layer_s(logits, attn)
    expected_s = c + kappa * i
    assert s == pytest.approx(expected_s, rel=1e-9)
    assert s == pytest.approx(c, rel=1e-6)  # since I ≈ 0


def test_real_transformer_s_increases_with_focus():
    """More focused attention should increase I and thus S."""
    seq_len, vocab = 4, 16
    n_heads = 2
    logits = np.zeros((seq_len, vocab))

    # Diffuse attention
    attn_diffuse = np.ones((n_heads, seq_len, seq_len)) / seq_len
    _, _, _, s_diffuse = compute_layer_s(logits, attn_diffuse)

    # Focused attention (one-hot)
    attn_focused = np.zeros((n_heads, seq_len, seq_len))
    for h in range(n_heads):
        for pos in range(seq_len):
            attn_focused[h, pos, 0] = 1.0
    _, _, _, s_focused = compute_layer_s(logits, attn_focused)

    assert s_focused > s_diffuse


def test_real_transformer_per_head_structure():
    """per_head_metrics returns one dict per head with expected keys."""
    n_heads, seq_len = 3, 6
    rng = np.random.default_rng(42)
    raw = rng.random((n_heads, seq_len, seq_len))
    attn = raw / raw.sum(axis=-1, keepdims=True)

    heads = per_head_metrics(attn)
    assert len(heads) == n_heads
    for h_info in heads:
        assert "head" in h_info
        assert "I_mean" in h_info
        assert "variance_mean" in h_info
        assert "max_attn_mean" in h_info
        assert h_info["variance_mean"] >= 0
        assert h_info["max_attn_mean"] > 0
