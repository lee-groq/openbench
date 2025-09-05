from inspect_ai import task, Task
from inspect_ai.solver import generate
from inspect_ai.model import GenerateConfig
from openbench.datasets.arc_agi import get_arc_agi_dataset
from openbench.scorers.arc_agi import arc_agi_scorer


@task
def arc_agi(version: int = 1) -> Task:
    """
    ARC-AGI (Abstraction and Reasoning Corpus) evaluation task.

    Tests abstract reasoning and pattern recognition capabilities by presenting
    training input-output pairs and requiring the model to identify the pattern
    and apply it to a test input.

    Args:
        version: Version of ARC-AGI dataset (1 or 2). Use -T version=2 for ARC-AGI-2.

    Returns:
        Task: Configured ARC-AGI task for evaluation
    """
    return Task(
        dataset=get_arc_agi_dataset(version=version),
        solver=[generate()],
        scorer=arc_agi_scorer(),
        name=f"arc_agi_v{version}",
        config=GenerateConfig(
            max_tokens=131072,  # Max token limit allowed by model for reasoning and explanation
            temperature=0.0,
        ),
    )
