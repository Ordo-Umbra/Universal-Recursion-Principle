"""
particles.py

Minimal particle describer primitives built on top of S Compass.

Provides lightweight data structures for particle/element descriptions,
heuristic property extraction, deterministic description generation, and an
in-memory periodic-table view that can be surfaced through the gateway/API.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import networkx as nx

from .graph import graph_to_dict
from .schemas import RetrievedChunk


@dataclass
class ParticleProperty:
    """A structured property attached to a particle or element."""

    key: str
    value: Any
    unit: Optional[str] = None
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "unit": self.unit,
            "confidence": self.confidence,
        }


@dataclass
class ParticleDescription:
    """One scored particle description stored in the periodic table view."""

    element_name: str
    atomic_number: int
    description_text: str
    properties: List[ParticleProperty] = field(default_factory=list)
    scores: Dict[str, float] = field(default_factory=dict)
    regime: str = "unknown"
    confidence: float = 0.65
    mode: str = "black-box"
    session_id: Optional[str] = None
    trace_id: Optional[str] = None

    def property_map(self) -> Dict[str, Any]:
        return {prop.key: prop.value for prop in self.properties}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_name": self.element_name,
            "atomic_number": self.atomic_number,
            "description_text": self.description_text,
            "properties": [prop.to_dict() for prop in self.properties],
            "scores": dict(self.scores),
            "regime": self.regime,
            "confidence": self.confidence,
            "mode": self.mode,
            "session_id": self.session_id,
            "trace_id": self.trace_id,
        }


class PeriodicTable:
    """In-memory collection of particle descriptions plus simple structure graph."""

    def __init__(self) -> None:
        self._descriptions: Dict[int, ParticleDescription] = {}

    def add_description(self, description: ParticleDescription) -> None:
        self._descriptions[description.atomic_number] = description

    def get_particle(self, atomic_number: int) -> Optional[ParticleDescription]:
        return self._descriptions.get(atomic_number)

    def list_particles(self) -> List[ParticleDescription]:
        return [self._descriptions[z] for z in sorted(self._descriptions)]

    def build_graph(self) -> nx.DiGraph:
        """Build a simple relational graph over stored elements."""
        g = nx.DiGraph()
        particles = self.list_particles()

        for desc in particles:
            node_id = f"el_{desc.atomic_number}"
            prop_map = desc.property_map()
            g.add_node(
                node_id,
                kind="element",
                element_name=desc.element_name,
                atomic_number=desc.atomic_number,
                group=prop_map.get("group"),
                period=prop_map.get("period"),
                regime=desc.regime,
                score=desc.scores.get("s"),
            )

        for left, right in zip(particles, particles[1:]):
            self._add_relation_edge(
                g,
                f"el_{left.atomic_number}",
                f"el_{right.atomic_number}",
                "adjacent_atomic_number",
            )

        for relation_key in ("group", "period"):
            buckets: Dict[str, List[ParticleDescription]] = {}
            for desc in particles:
                value = desc.property_map().get(relation_key)
                if value is None:
                    continue
                buckets[str(value)] = buckets.get(str(value), []) + [desc]
            for related in buckets.values():
                if len(related) < 2:
                    continue
                for left, right in zip(related, related[1:]):
                    self._add_relation_edge(
                        g,
                        f"el_{left.atomic_number}",
                        f"el_{right.atomic_number}",
                        f"same_{relation_key}",
                    )

        return g

    @staticmethod
    def _add_relation_edge(
        graph: nx.DiGraph,
        source_id: str,
        target_id: str,
        relation: str,
    ) -> None:
        """Add or extend a relation edge without overwriting existing labels."""
        if graph.has_edge(source_id, target_id):
            data = graph[source_id][target_id]
            relations = list(data.get("relations", []))
            if relation not in relations:
                relations.append(relation)
            data["relations"] = relations
            return
        graph.add_edge(
            source_id,
            target_id,
            relations=[relation],
        )

    def to_dict(self) -> Dict[str, Any]:
        graph = self.build_graph()
        return {
            "elements": [desc.to_dict() for desc in self.list_particles()],
            "graph": graph_to_dict(graph),
        }


_PROPERTY_PATTERNS = {
    "atomic_mass": re.compile(
        r"(?:atomic mass|mass)\s*(?:is|=|:)?\s*([0-9]+(?:\.[0-9]+)?)\s*(u|amu)?",
        re.IGNORECASE,
    ),
    "group": re.compile(r"group\s*(?:is|=|:)?\s*([0-9]+)", re.IGNORECASE),
    "period": re.compile(r"period\s*(?:is|=|:)?\s*([0-9]+)", re.IGNORECASE),
    "valence_electrons": re.compile(
        r"valence electrons?\s*(?:is|=|:)?\s*([0-9]+)",
        re.IGNORECASE,
    ),
    "electron_configuration": re.compile(
        r"electron configuration\s*(?:is|=|:)?\s*([^.;\n]+)",
        re.IGNORECASE,
    ),
    "classification": re.compile(
        r"(?:classification|category)\s*(?:is|=|:)?\s*([^.;\n]+)",
        re.IGNORECASE,
    ),
}

_ORBITAL_FILL_ORDER: List[Tuple[str, int]] = [
    ("1s", 2),
    ("2s", 2),
    ("2p", 6),
    ("3s", 2),
    ("3p", 6),
    ("4s", 2),
    ("3d", 10),
    ("4p", 6),
    ("5s", 2),
    ("4d", 10),
    ("5p", 6),
    ("6s", 2),
    ("4f", 14),
    ("5d", 10),
    ("6p", 6),
    ("7s", 2),
    ("5f", 14),
    ("6d", 10),
    ("7p", 6),
]

_ATOMIC_MASS_LOOKUP = {
    1: 1.008,
    2: 4.0026,
    3: 6.94,
    4: 9.0122,
    5: 10.81,
    6: 12.011,
    7: 14.007,
    8: 15.999,
    9: 18.998,
    10: 20.180,
    11: 22.990,
    12: 24.305,
    13: 26.982,
    14: 28.085,
    15: 30.974,
    16: 32.06,
    17: 35.45,
    18: 39.948,
}

_NONMETALS = {1, 6, 7, 8, 15, 16}
_METALLOIDS = {5, 14}
_HELIUM_Z_EFF = 1.8366
_HELIUM_IONIZATION_EV = 24.590


def infer_particle_properties(atomic_number: int) -> List[ParticleProperty]:
    """Infer a basic element profile from atomic number and shell-filling dynamics."""
    if atomic_number < 1:
        return []

    properties: Dict[str, ParticleProperty] = {}
    _merge_property(properties, "atomic_number", atomic_number)

    remaining = atomic_number
    shell_occupancy: Dict[int, int] = {}
    configuration_parts: List[str] = []
    last_orbital = ""
    last_fill = 0
    last_capacity = 0

    for orbital, capacity in _ORBITAL_FILL_ORDER:
        if remaining <= 0:
            break
        filled = min(capacity, remaining)
        configuration_parts.append(f"{orbital}{filled}")
        shell_index = int(orbital[0])
        shell_occupancy[shell_index] = shell_occupancy.get(shell_index, 0) + filled
        remaining -= filled
        last_orbital = orbital
        last_fill = filled
        last_capacity = capacity

    if not shell_occupancy:
        return list(properties.values())

    period = max(shell_occupancy)
    valence_electrons = shell_occupancy[period]
    block = last_orbital[-1] if last_orbital else None
    group = _infer_group(atomic_number, block, last_fill, shell_occupancy)
    classification = _infer_classification(atomic_number, group, block)
    stability = _infer_stability_regime(atomic_number, valence_electrons, last_fill, last_capacity)

    _merge_property(properties, "electron_configuration", " ".join(configuration_parts))
    _merge_property(
        properties,
        "shell_occupancy",
        "-".join(str(shell_occupancy[idx]) for idx in sorted(shell_occupancy)),
    )
    _merge_property(properties, "period", period)
    _merge_property(properties, "valence_electrons", valence_electrons)
    _merge_property(properties, "block", block)
    _merge_property(properties, "group", group)
    _merge_property(properties, "classification", classification)
    _merge_property(properties, "stability_regime", stability)
    if atomic_number in _ATOMIC_MASS_LOOKUP:
        _merge_property(properties, "atomic_mass", _ATOMIC_MASS_LOOKUP[atomic_number], unit="u")
    if atomic_number == 2:
        for prop in _infer_helium_urp_properties():
            properties[prop.key] = prop

    return list(properties.values())


def _infer_helium_urp_properties() -> List[ParticleProperty]:
    """Return helium-specific observables grounded in the repo's URP model."""
    return [
        ParticleProperty(key="effective_nuclear_charge", value=_HELIUM_Z_EFF),
        ParticleProperty(
            key="ionization_potential",
            value=_HELIUM_IONIZATION_EV,
            unit="eV",
        ),
        ParticleProperty(key="urp_beta", value=0.09),
        ParticleProperty(key="accuracy_ppm", value=112),
    ]


def _infer_group(
    atomic_number: int,
    block: Optional[str],
    last_fill: int,
    shell_occupancy: Dict[int, int],
) -> Optional[int]:
    """Infer a periodic-table group where a simple shell model is reliable."""
    if atomic_number == 1:
        return 1
    if atomic_number == 2:
        return 18
    if block == "s":
        return last_fill
    if block == "p":
        return 12 + last_fill
    if block == "d":
        outer_s = shell_occupancy.get(max(shell_occupancy), 0)
        return min(12, max(3, outer_s + last_fill))
    return None


def _infer_classification(
    atomic_number: int,
    group: Optional[int],
    block: Optional[str],
) -> Optional[str]:
    """Map inferred structural signals to a lightweight chemistry category."""
    if atomic_number == 1:
        return "nonmetal"
    if group == 18:
        return "noble gas"
    if group == 17:
        return "halogen"
    if group == 1:
        return "alkali metal"
    if group == 2:
        return "alkaline earth metal"
    if atomic_number in _METALLOIDS:
        return "metalloid"
    if atomic_number in _NONMETALS:
        return "nonmetal"
    if block == "d":
        return "transition metal"
    return None


def _infer_stability_regime(
    atomic_number: int,
    valence_electrons: int,
    last_fill: int,
    last_capacity: int,
) -> str:
    """Describe how close the outer shell/orbital is to closure."""
    if atomic_number == 2 or (last_capacity and last_fill == last_capacity):
        return "closed-shell"
    if valence_electrons == 1:
        return "open-shell reactive"
    if valence_electrons == max(0, last_capacity - 1):
        return "near-closure"
    return "open-shell"


def _coerce_value(value: Any) -> Any:
    """Coerce numeric-looking strings to ints/floats while preserving text."""
    if isinstance(value, (int, float)):
        return value
    text = str(value).strip()
    if not text:
        return text
    if re.fullmatch(r"-?[0-9]+", text):
        return int(text)
    if re.fullmatch(r"-?[0-9]+\.[0-9]+", text):
        return float(text)
    return text


def _merge_property(
    properties: Dict[str, ParticleProperty],
    key: str,
    value: Any,
    *,
    unit: Optional[str] = None,
    confidence: float = 1.0,
) -> None:
    if key == "" or value in (None, ""):
        return
    properties[key] = ParticleProperty(
        key=key,
        value=_coerce_value(value),
        unit=unit,
        confidence=confidence,
    )


def parse_particle_properties(
    *,
    atomic_number: int,
    description_text: str = "",
    retrieved_context: Optional[Sequence[RetrievedChunk]] = None,
    raw_properties: Optional[Sequence[Dict[str, Any]]] = None,
) -> List[ParticleProperty]:
    """Build a normalized property list from explicit and heuristic sources."""
    properties: Dict[str, ParticleProperty] = {}
    for prop in infer_particle_properties(atomic_number):
        properties[prop.key] = prop

    for prop in raw_properties or ():
        _merge_property(
            properties,
            str(prop.get("key", "")).strip(),
            prop.get("value"),
            unit=prop.get("unit"),
            confidence=float(prop.get("confidence", 1.0)),
        )

    corpus = "\n".join(
        [description_text] + [chunk.text for chunk in (retrieved_context or []) if chunk.text]
    )
    for key, pattern in _PROPERTY_PATTERNS.items():
        if key in properties:
            continue
        match = pattern.search(corpus)
        if not match:
            continue
        if key == "atomic_mass":
            _merge_property(properties, key, match.group(1), unit=match.group(2) or "u")
        else:
            _merge_property(properties, key, match.group(1))

    return list(properties.values())


def properties_to_retrieved_context(
    element_name: str,
    properties: Sequence[ParticleProperty],
) -> List[RetrievedChunk]:
    """Turn structured properties into grounding chunks when none are supplied."""
    chunks: List[RetrievedChunk] = []
    for prop in properties:
        value = f"{prop.value} {prop.unit}".strip() if prop.unit else str(prop.value)
        chunks.append(
            RetrievedChunk(
                doc_id=f"{element_name.lower()}_{prop.key}",
                text=f"{element_name} has {prop.key.replace('_', ' ')} {value}.",
                score=prop.confidence,
            )
        )
    return chunks


def compose_particle_description(
    element_name: str,
    atomic_number: int,
    properties: Sequence[ParticleProperty],
) -> str:
    """Generate a deterministic URP-flavoured description for an element."""
    prop_map = {prop.key: prop.value for prop in properties}
    sentences = [f"{element_name} is element {atomic_number} in the periodic table."]

    classification = prop_map.get("classification")
    if classification:
        sentences.append(f"It is classified as {classification}.")

    group = prop_map.get("group")
    period = prop_map.get("period")
    if group is not None or period is not None:
        location_bits = []
        if group is not None:
            location_bits.append(f"group {group}")
        if period is not None:
            location_bits.append(f"period {period}")
        sentences.append(f"It occupies {' and '.join(location_bits)}.")

    atomic_mass = prop_map.get("atomic_mass")
    if atomic_mass is not None:
        sentences.append(f"Its atomic mass is approximately {atomic_mass} u.")

    electron_configuration = prop_map.get("electron_configuration")
    if electron_configuration:
        sentences.append(f"Its electron configuration is {electron_configuration}.")

    shell_occupancy = prop_map.get("shell_occupancy")
    if shell_occupancy:
        sentences.append(f"Its shell-filling dynamics distribute electrons as {shell_occupancy}.")

    valence_electrons = prop_map.get("valence_electrons")
    if valence_electrons is not None:
        sentences.append(f"It has {valence_electrons} valence electrons.")

    effective_nuclear_charge = prop_map.get("effective_nuclear_charge")
    ionization_potential_ev = prop_map.get("ionization_potential")
    accuracy_ppm = prop_map.get("accuracy_ppm")
    if atomic_number == 2 and effective_nuclear_charge is not None and ionization_potential_ev is not None:
        sentences.append(
            f"In the repo's helium URP variational result, minimizing the constrained energy functional gives Z_eff ≈ {effective_nuclear_charge} "
            f"and a first ionization potential of {ionization_potential_ev} eV."
        )
        if accuracy_ppm is not None:
            sentences.append(
                f"That sits within about {accuracy_ppm} ppm of the NIST value, so helium is the clearest current example of these dynamics generating a realistic atomic description."
            )

    stability_regime = prop_map.get("stability_regime")
    if stability_regime == "closed-shell":
        sentences.append(
            "That closes its accessible outer structure, so the element naturally settles into a comparatively stable and inert pattern."
        )
    elif stability_regime == "near-closure":
        sentences.append(
            "Its outer shell is close to closure, so the system tends to seek completion through strong interactions with nearby partners."
        )
    elif stability_regime == "open-shell reactive":
        sentences.append(
            "A single loosely held outer electron leaves the structure easy to perturb, which naturally supports higher reactivity."
        )
    elif stability_regime:
        sentences.append(
            "Its outer structure remains open, so stability emerges through selective bonding rather than full shell closure."
        )

    sentences.append(
        "Within the URP framing, these shell capacities and orbital-filling constraints act like a local dynamics of distinction and integration, "
        "helping explain the element's recurring characteristics as a coherent pattern rather than an arbitrary label."
    )
    return " ".join(sentences)
