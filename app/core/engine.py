from app.core.analyzer import InputAnalyzer
from app.core.decision import DecisionEngine
from app.llm.base import LLMProvider
from app.models.schemas import OptimizedContext, PreLyrResult,ProcessingOperation
from app.processors.structure import StructureProcessor
from app.processors.deduplicator import Deduplicator
from app.processors.redundancy import RedundancyProcessor
from app.processors.relevant_context import RelevantContextProcessor
from app.core.token_counter import TokenCounter
from app.processors.clean_normalize import CleanNormalizeProcessor

class PreLyrEngine:

    def __init__(self, llm_provider: LLMProvider | None = None):
        self.analyzer = InputAnalyzer()
        self.decision_engine = DecisionEngine()
        self.structure_processor = StructureProcessor()
        self.llm_provider = llm_provider
        self.deduplicator = Deduplicator()
        self.redundancy_processor = RedundancyProcessor()
        self.relevant_context_processor = RelevantContextProcessor()
        self.token_counter = TokenCounter()
        self.clean_normalize_processor = CleanNormalizeProcessor()

    def process(self, text: str) -> PreLyrResult:
        analysis = self.analyzer.analyze(text)

        decision = self.decision_engine.decide(analysis)

        optimized_text = analysis.input_text

        if (
            ProcessingOperation.CLEAN in decision.operations
            or ProcessingOperation.NORMALIZE in decision.operations
        ):
            optimized_text = self.clean_normalize_processor.process(
            optimized_text
        )

        if ProcessingOperation.DEDUPLICATE in decision.operations:
            optimized_text = self.deduplicator.process(
                optimized_text
            )
        
        if ProcessingOperation.SELECT_RELEVANT_CONTEXT in decision.operations:
            optimized_text = self.relevant_context_processor.process(
                optimized_text,
                analysis.task_type,
            )

        if ProcessingOperation.STRUCTURE in decision.operations:
            optimized_text = self.structure_processor.process(
            optimized_text
        )

        if ProcessingOperation.DEDUPLICATE in decision.operations:
            optimized_text = self.redundancy_processor.process(optimized_text)

        original_tokens = self.token_counter.count(
            analysis.input_text
        )

        optimized_tokens = self.token_counter.count(
            optimized_text
        )

        token_reduction_percentage = (
            self.token_counter.reduction_percentage(
                analysis.input_text,
                optimized_text,
            )
        )

        
        context = OptimizedContext(
            original_text=analysis.input_text,
            optimized_text=optimized_text,
            original_length=len(analysis.input_text),
            optimized_length=len(optimized_text),
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            token_reduction_percentage=token_reduction_percentage,
            operations_applied=decision.operations,
        )

        return PreLyrResult(
            analysis=analysis,
            decision=decision,
            context=context,
    )

    def generate(self, text: str) -> str:
        if self.llm_provider is None:
            raise ValueError("No LLM provider configured.")

        result = self.process(text)

        prompt = f"""
        You are receiving context prepared by PreLyr.

        Use the following context to answer the user's request.

        --- Optimized Context ---
        {result.context.optimized_text}
        --- End Context ---

        Answer the user's request accurately.
        """

        return self.llm_provider.generate(prompt)

