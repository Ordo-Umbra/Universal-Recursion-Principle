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
from typing import Any, Dict, List, Optional, Sequence

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
            data["relation"] = relations[0] if len(relations) == 1 else ",".join(relations)
            return
        graph.add_edge(
            source_id,
            target_id,
            relation=relation,
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
    _merge_property(properties, "atomic_number", atomic_number)

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

    valence_electrons = prop_map.get("valence_electrons")
    if valence_electrons is not None:
        sentences.append(f"It has {valence_electrons} valence electrons.")

    sentences.append(
        "Within the URP framing, these recurring constraints and relational placements "
        "help explain the element's stable characteristics as a coherent pattern."
    )
    return " ".join(sentences)
