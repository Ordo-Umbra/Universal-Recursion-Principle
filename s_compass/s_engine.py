"""
S-Engine: Structural Shape Rotator for Universal Recursion Principle
Implements S = ΔC + κ ΔI with semantic geometry and stress detection.
"""

import networkx as nx
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from .graph import SemanticGraph  # Assuming existing graph module
from .schemas import StepInput, StepResult  # Adjust as per existing


@dataclass
class SEngineMetrics:
    delta_C: float
    delta_I: float
    S: float
    stress_level: float
    regime: str  # 'stable', 'stressed', 'critical'
    recommendation: str


class SEngine:
    def __init__(self, kappa: float = 1.0, stress_threshold: float = 0.7):
        self.kappa = kappa
        self.stress_threshold = stress_threshold
        self.graph = SemanticGraph()  # Extend existing
        self.previous_state: Optional[Dict] = None
        self.history = []

    def compute_deltas(self, current_state: Dict[str, Any], previous_state: Optional[Dict] = None) -> Tuple[float, float]:
        """Compute ΔC (complexity/distinctions) and ΔI (integration/coherence)"""
        if previous_state is None:
            previous_state = self.previous_state or {}

        # ΔC: New distinctions (nodes, edges, entropy)
        delta_C = self._measure_complexity_growth(current_state, previous_state)

        # ΔI: Coherence / integration (clustering, connectivity)
        delta_I = self._measure_integration(current_state)

        return delta_C, delta_I

    def _measure_complexity_growth(self, current: Dict, previous: Dict) -> float:
        # Simple implementation: node/edge growth + embedding variance
        current_nodes = len(current.get('claims', []))
        prev_nodes = len(previous.get('claims', []))
        growth = max(0, current_nodes - prev_nodes)
        # Could use graph entropy or embedding distance
        return float(growth + 0.1 * np.random.randn())  # Placeholder for richer metrics

    def _measure_integration(self, state: Dict) -> float:
        """Coherence score from graph"""
        if not hasattr(self.graph, 'G') or self.graph.G.number_of_nodes() == 0:
            return 0.5
        clustering = nx.average_clustering(self.graph.G)
        return clustering

    def assess_step(self, step: StepInput, output_text: str) -> SEngineMetrics:
        """Main entry point: Process a step and compute S"""
        current_state = self._extract_state(step, output_text)

        delta_C, delta_I = self.compute_deltas(current_state)
        S = delta_C + self.kappa * delta_I

        stress = max(0.0, (delta_C - self.kappa * delta_I) / (delta_C + 1e-6))

        if stress > self.stress_threshold * 1.5:
            regime = 'critical'
            rec = 'REJECT: High structural stress - incoherence detected'
        elif stress > self.stress_threshold:
            regime = 'stressed'
            rec = 'CAUTION: Moderate stress - monitor recursion'
        else:
            regime = 'stable'
            rec = 'COHERENT: Structural integrity maintained'

        metrics = SEngineMetrics(
            delta_C=delta_C,
            delta_I=delta_I,
            S=S,
            stress_level=stress,
            regime=regime,
            recommendation=rec
        )

        # Update state
        self.previous_state = current_state
        self.history.append(metrics)
        self.graph.update_from_step(current_state)  # Extend graph

        return metrics

    def _extract_state(self, step: StepInput, output_text: str) -> Dict:
        """Extract claims/entities for graph"""
        # Placeholder - in practice use LLM or simple parsing
        return {
            'prompt': step.prompt,
            'output': output_text,
            'claims': self._simple_claim_extract(output_text)
        }

    def _simple_claim_extract(self, text: str) -> list:
        # Very basic for initial version
        return [sentence.strip() for sentence in text.split('.') if sentence.strip()]

    def get_visualization_data(self) -> Dict:
        """For 3D graph viz"""
        return self.graph.get_viz_data() if hasattr(self.graph, 'get_viz_data') else {}


def create_s_engine_wrapper(gateway):
    """Factory to wrap existing SCompassGateway"""
    engine = SEngine()

    original_submit = gateway.submit_step

    def wrapped_submit(step: StepInput):
        result = original_submit(step)
        # Enhance with S-Engine
        s_metrics = engine.assess_step(step, result.get('output_text', ''))
        result['s_engine'] = s_metrics.__dict__
        return result

    gateway.submit_step = wrapped_submit
    return engine


# For testing
if __name__ == "__main__":
    print("S-Engine initialized - ready for integration with S-Compass Gateway")
