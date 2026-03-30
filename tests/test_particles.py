"""
test_particles.py

Tests for the particle describer layer built on top of S Compass.
"""

from s_compass.gateway import SCompassGateway


def _prop_map(properties):
    return {prop["key"]: prop["value"] for prop in properties}


def test_submit_particle_description_generates_and_stores_particle():
    gw = SCompassGateway()

    result = gw.submit_particle_description(
        element_name="Helium",
        atomic_number=2,
        properties=[
            {"key": "classification", "value": "noble gas"},
            {"key": "group", "value": 18},
            {"key": "period", "value": 1},
            {"key": "atomic_mass", "value": 4.0026, "unit": "u"},
            {"key": "valence_electrons", "value": 2},
        ],
    )

    assert result["ok"] is True
    assert result["particle"]["element_name"] == "Helium"
    assert result["particle"]["atomic_number"] == 2
    assert "URP framing" in result["particle"]["description_text"]

    prop_map = _prop_map(result["particle"]["properties"])
    assert prop_map["atomic_number"] == 2
    assert prop_map["group"] == 18
    assert prop_map["classification"] == "noble gas"

    stored = gw.get_particle_description(2)
    assert stored is not None
    assert stored["element_name"] == "Helium"
    assert stored["scores"]["s"] == result["scores"]["s"]
    assert 0.0 <= stored["scores"]["s"] <= 2.0


def test_periodic_table_graph_captures_relationships():
    gw = SCompassGateway()

    gw.submit_particle_description(
        element_name="Hydrogen",
        atomic_number=1,
        properties=[
            {"key": "group", "value": 1},
            {"key": "period", "value": 1},
        ],
    )
    gw.submit_particle_description(
        element_name="Helium",
        atomic_number=2,
        properties=[
            {"key": "group", "value": 18},
            {"key": "period", "value": 1},
        ],
    )

    table = gw.get_periodic_table()
    assert [element["atomic_number"] for element in table["elements"]] == [1, 2]

    edge = table["graph"]["edges"][0]
    assert edge["source"] == "el_1"
    assert edge["target"] == "el_2"
    assert "adjacent_atomic_number" in edge["relations"]
    assert "same_period" in edge["relations"]


def test_submit_particle_description_infers_helium_dynamics_from_repo_model():
    gw = SCompassGateway()

    result = gw.submit_particle_description(
        element_name="Helium",
        atomic_number=2,
    )

    prop_map = _prop_map(result["particle"]["properties"])
    assert prop_map["classification"] == "noble gas"
    assert prop_map["group"] == 18
    assert prop_map["electron_configuration"] == "1s2"
    assert prop_map["effective_nuclear_charge"] == 1.8366
    assert prop_map["ionization_potential"] == 24.59
    assert prop_map["accuracy_ppm"] == 112
    assert "Z_eff ≈ 1.8366" in result["particle"]["description_text"]
    assert "24.59 eV" in result["particle"]["description_text"]
