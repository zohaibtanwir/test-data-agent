"""Intelligence router for selecting optimal data generation path."""

from dataclasses import dataclass
from enum import Enum

from test_data_agent.proto import test_data_pb2
from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


class GenerationPath(Enum):
    """Available generation paths."""

    TRADITIONAL = "traditional"  # Faker-based, fast and cheap
    LLM = "llm"  # Claude/vLLM for intelligent, coherent data
    RAG = "rag"  # Retrieve patterns from vector DB
    HYBRID = "hybrid"  # RAG + LLM combined


@dataclass
class RoutingDecision:
    """Result of routing decision."""

    path: GenerationPath
    reason: str
    confidence: float  # 0.0 to 1.0


class IntelligenceRouter:
    """Routes generation requests to the optimal generation path."""

    def route(self, request: test_data_pb2.GenerateRequest) -> RoutingDecision:
        """Determine the best generation path for a request.

        Args:
            request: Generation request

        Returns:
            RoutingDecision with path, reason, and confidence
        """
        # Priority 0: Respect explicit generation_method if set (non-zero means explicitly chosen)
        # Proto enum: TRADITIONAL=0, LLM=1, RAG=2, HYBRID=3
        if request.generation_method > 0:
            method_map = {
                test_data_pb2.LLM: GenerationPath.LLM,
                test_data_pb2.RAG: GenerationPath.RAG,
                test_data_pb2.HYBRID: GenerationPath.HYBRID,
            }
            path = method_map.get(request.generation_method, GenerationPath.TRADITIONAL)
            return RoutingDecision(
                path=path,
                reason=f"User explicitly selected {path.value} generation method",
                confidence=1.0,
            )

        hints = [h.lower() for h in request.hints]

        # Priority 1: HYBRID (RAG + LLM) - Most sophisticated
        if self._should_use_hybrid(request, hints):
            return RoutingDecision(
                path=GenerationPath.HYBRID,
                reason="Complex request with historical patterns and intelligence needed",
                confidence=0.9,
            )

        # Priority 2: RAG - Pattern-based from history
        if self._should_use_rag(request, hints):
            return RoutingDecision(
                path=GenerationPath.RAG,
                reason=self._get_rag_reason(request, hints),
                confidence=0.85,
            )

        # Priority 3: LLM - Intelligent, coherent generation
        if self._should_use_llm(request, hints):
            return RoutingDecision(
                path=GenerationPath.LLM,
                reason=self._get_llm_reason(request, hints),
                confidence=0.8,
            )

        # Default: TRADITIONAL - Fast, cheap, simple
        return RoutingDecision(
            path=GenerationPath.TRADITIONAL,
            reason=self._get_traditional_reason(request, hints),
            confidence=0.95,
        )

    def _should_use_hybrid(self, request: test_data_pb2.GenerateRequest, hints: list[str]) -> bool:
        """Check if HYBRID path should be used.

        Args:
            request: Generation request
            hints: Lowercased hints

        Returns:
            True if hybrid generation is best
        """
        # Use HYBRID when both RAG and LLM conditions are met
        needs_rag = self._should_use_rag(request, hints)
        needs_llm = self._should_use_llm(request, hints)

        if needs_rag and needs_llm:
            return True

        # Also use HYBRID for complex scenarios with historical patterns
        if request.scenarios and len(request.scenarios) > 2:
            if request.learn_from_history or request.production_like:
                return True

        return False

    def _should_use_rag(self, request: test_data_pb2.GenerateRequest, hints: list[str]) -> bool:
        """Check if RAG path should be used.

        Args:
            request: Generation request
            hints: Lowercased hints

        Returns:
            True if RAG generation is best
        """
        # Use RAG if explicitly requested
        if request.learn_from_history:
            return True

        if request.defect_triggering:
            return True

        if request.production_like:
            return True

        # Use RAG if hints suggest pattern matching
        rag_hints = {"similar", "pattern", "historical", "production"}
        if any(hint in hints for hint in rag_hints):
            return True

        return False

    def _should_use_llm(self, request: test_data_pb2.GenerateRequest, hints: list[str]) -> bool:
        """Check if LLM path should be used.

        Args:
            request: Generation request
            hints: Lowercased hints

        Returns:
            True if LLM generation is best
        """
        # Use LLM if context is provided
        if request.context and len(request.context) > 10:
            return True

        # Use LLM for coherence-requiring entities
        if request.entity in ["cart", "order"] and any(
            hint in hints for hint in ["coherent", "realistic"]
        ):
            return True

        # Use LLM for text-heavy entities
        if request.entity in ["review", "comment", "feedback", "description"]:
            return True

        # Use LLM if hints suggest intelligent generation
        llm_hints = {"realistic", "coherent", "intelligent", "natural"}
        if any(hint in hints for hint in llm_hints):
            return True

        # Use LLM if scenarios have detailed descriptions
        if request.scenarios:
            if any(s.description and len(s.description) > 20 for s in request.scenarios):
                return True

        return False

    def _get_rag_reason(self, request: test_data_pb2.GenerateRequest, hints: list[str]) -> str:
        """Get explanation for RAG routing.

        Args:
            request: Generation request
            hints: Lowercased hints

        Returns:
            Reason string
        """
        reasons = []

        if request.learn_from_history:
            reasons.append("learn_from_history flag set")

        if request.defect_triggering:
            reasons.append("defect_triggering mode requested")

        if request.production_like:
            reasons.append("production-like distributions needed")

        if any(hint in hints for hint in {"similar", "pattern", "historical"}):
            reasons.append(f"hints suggest pattern matching: {hints}")

        return "RAG: " + ", ".join(reasons) if reasons else "RAG: pattern-based generation"

    def _get_llm_reason(self, request: test_data_pb2.GenerateRequest, hints: list[str]) -> str:
        """Get explanation for LLM routing.

        Args:
            request: Generation request
            hints: Lowercased hints

        Returns:
            Reason string
        """
        reasons = []

        if request.context:
            reasons.append("context provided")

        if request.entity in ["cart", "order"]:
            reasons.append(f"coherence needed for {request.entity}")

        if request.entity in ["review", "comment", "feedback"]:
            reasons.append(f"text content generation for {request.entity}")

        if any(hint in hints for hint in {"realistic", "coherent", "intelligent"}):
            reasons.append(f"intelligent generation requested via hints: {hints}")

        if request.scenarios and any(s.description for s in request.scenarios):
            reasons.append("detailed scenario descriptions provided")

        return "LLM: " + ", ".join(reasons) if reasons else "LLM: intelligent generation"

    def _get_traditional_reason(
        self, request: test_data_pb2.GenerateRequest, hints: list[str]
    ) -> str:
        """Get explanation for TRADITIONAL routing.

        Args:
            request: Generation request
            hints: Lowercased hints

        Returns:
            Reason string
        """
        reasons = []

        if not request.context:
            reasons.append("no context provided")

        if request.count > 500:
            reasons.append(f"high volume ({request.count} records)")

        if "fast" in hints:
            reasons.append("fast generation requested")

        if request.entity in ["user", "payment"] and not any(
            hint in hints for hint in {"realistic", "coherent"}
        ):
            reasons.append(f"simple entity ({request.entity})")

        return (
            "Traditional: " + ", ".join(reasons)
            if reasons
            else "Traditional: default fast generation"
        )
