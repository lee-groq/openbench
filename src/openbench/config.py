"""
Minimal configuration for benchmarks.
Only contains human-written metadata that cannot be extracted from code.
Everything else (epochs, temperature, etc.) comes from the actual task definitions.
"""

from dataclasses import dataclass
from functools import lru_cache
import importlib
import importlib.util
import sys
import uuid
from pathlib import Path
from types import ModuleType
from typing import Callable, Iterable, List, Optional


@dataclass
class BenchmarkMetadata:
    """Minimal metadata for a benchmark - only what can't be extracted."""

    name: str  # Human-readable display name
    description: str  # Human-written description
    category: str  # Category for grouping
    tags: List[str]  # Tags for searchability

    # Registry info - still needed
    module_path: str
    function_name: str

    # Alpha/experimental flag
    is_alpha: bool = False  # Whether this benchmark is experimental/alpha


# Benchmark metadata - minimal, no duplication
BENCHMARKS = {
    "mbpp": BenchmarkMetadata(
        name="MBPP",
        description="Mostly Basic Python Problems — code generation tasks with unit test verification",
        category="core",
        tags=["code", "generation", "sandbox", "reasoning"],
        module_path="openbench.evals.mbpp",
        function_name="mbpp",
        is_alpha=False,
    ),
    # Graphwalks benchmarks (alpha)
    "clockbench": BenchmarkMetadata(
        name="ClockBench",
        description="Clock benchmark - time-based reasoning tasks",
        category="community",
        tags=["time", "analog", "clock", "reasoning"],
        module_path="openbench.evals.clockbench",
        function_name="clockbench",
        is_alpha=False,
    ),
    "graphwalks": BenchmarkMetadata(
        name="GraphWalks",
        description="Multi-hop reasoning on graphs - both BFS and parent finding tasks",
        category="core",
        tags=["long-context", "graphs", "reasoning", "alpha"],
        module_path="openbench.evals.graphwalks",
        function_name="graphwalks",
        is_alpha=True,
    ),
    "graphwalks_bfs": BenchmarkMetadata(
        name="GraphWalks BFS",
        description="Multi-hop reasoning on graphs - BFS traversal tasks only",
        category="core",
        tags=["long-context", "graphs", "reasoning", "bfs", "alpha"],
        module_path="openbench.evals.graphwalks",
        function_name="graphwalks_bfs",
        is_alpha=True,
    ),
    "graphwalks_parents": BenchmarkMetadata(
        name="GraphWalks Parents",
        description="Multi-hop reasoning on graphs - parent finding tasks only",
        category="core",
        tags=["long-context", "graphs", "reasoning", "parents", "alpha"],
        module_path="openbench.evals.graphwalks",
        function_name="graphwalks_parents",
        is_alpha=True,
    ),
    # Core benchmarks
    "mmlu": BenchmarkMetadata(
        name="MMLU (cais/mmlu)",
        description="Massive Multitask Language Understanding - 57 academic subjects from the cais/mmlu dataset. Only supports English (EN-US).",
        category="core",
        tags=["multiple-choice", "knowledge", "reasoning", "multitask"],
        module_path="openbench.evals.mmlu",
        function_name="mmlu",
    ),
    "mmlu-pro": BenchmarkMetadata(
        name="MMLU Pro (TIGER-Lab)",
        description="Enhanced version of MMLU with more challenging, reasoning-focused questions.",
        category="core",
        tags=["multiple-choice", "knowledge", "reasoning", "multitask"],
        module_path="openbench.evals.mmlu_pro",
        function_name="mmlu_pro",
    ),
    "mmmlu": BenchmarkMetadata(
        name="MMMLU (openai/MMMLU)",
        description="MMLU translated to 15 languages.",
        category="core",
        tags=["multiple-choice", "knowledge", "reasoning", "multitask"],
        module_path="openbench.evals.mmmlu",
        function_name="mmmlu",
    ),
    "openai_mrcr": BenchmarkMetadata(
        name="OpenAI MRCR (Full)",
        description="Memory-Recall with Contextual Retrieval - long-context evaluation that measures recall of 2, 4, and 8 needles across million-token contexts",
        category="core",
        tags=["long-context", "retrieval", "needle", "sequence-matching"],
        module_path="openbench.evals.mrcr",
        function_name="openai_mrcr",
    ),
    "openai_mrcr_2n": BenchmarkMetadata(
        name="OpenAI MRCR (2 Needles)",
        description="Memory-Recall with Contextual Retrieval - long-context evaluation that measures recall of 2 needles across million-token contexts",
        category="core",
        tags=["long-context", "retrieval", "needle", "sequence-matching"],
        module_path="openbench.evals.mrcr",
        function_name="openai_mrcr_2n",
    ),
    "openai_mrcr_4n": BenchmarkMetadata(
        name="OpenAI MRCR (4 Needles)",
        description="Memory-Recall with Contextual Retrieval - long-context evaluation that measures recall of 4 needles across million-token contexts",
        category="core",
        tags=["long-context", "retrieval", "needle", "sequence-matching"],
        module_path="openbench.evals.mrcr",
        function_name="openai_mrcr_4n",
    ),
    "openai_mrcr_8n": BenchmarkMetadata(
        name="OpenAI MRCR (8 Needles)",
        description="Memory-Recall with Contextual Retrieval - long-context evaluation that measures recall of 8 needles across million-token contexts",
        category="core",
        tags=["long-context", "retrieval", "needle", "sequence-matching"],
        module_path="openbench.evals.mrcr",
        function_name="openai_mrcr_8n",
    ),
    "gpqa_diamond": BenchmarkMetadata(
        name="GPQA Diamond",
        description="Graduate-level Google-Proof Q&A in biology, chemistry, and physics",
        category="core",
        tags=["multiple-choice", "science", "graduate-level"],
        module_path="openbench.evals.gpqa_diamond",
        function_name="gpqa_diamond",
    ),
    "humaneval": BenchmarkMetadata(
        name="HumanEval",
        description="Code generation benchmark with 164 programming problems",
        category="core",
        tags=["coding", "generation", "execution"],
        module_path="openbench.evals.humaneval",
        function_name="humaneval",
    ),
    # Exercism benchmarks
    "exercism": BenchmarkMetadata(
        name="Exercism",
        description="Multi-language coding benchmark with real-world programming exercises across Python, Go, JavaScript, Java, and Rust",
        category="core",
        tags=["coding", "multi-language", "execution", "docker"],
        module_path="openbench.evals.exercism.exercism",
        function_name="exercism",
    ),
    "exercism_python": BenchmarkMetadata(
        name="Exercism (Python)",
        description="Python coding tasks from the Exercism benchmark",
        category="core",
        tags=["coding", "python", "execution", "docker"],
        module_path="openbench.evals.exercism.exercism",
        function_name="exercism_python",
    ),
    "exercism_javascript": BenchmarkMetadata(
        name="Exercism (JavaScript)",
        description="JavaScript coding tasks from the Exercism benchmark",
        category="core",
        tags=["coding", "javascript", "execution", "docker"],
        module_path="openbench.evals.exercism.exercism",
        function_name="exercism_javascript",
    ),
    "exercism_go": BenchmarkMetadata(
        name="Exercism (Go)",
        description="Go coding tasks from the Exercism benchmark",
        category="core",
        tags=["coding", "go", "execution", "docker"],
        module_path="openbench.evals.exercism.exercism",
        function_name="exercism_go",
    ),
    "exercism_java": BenchmarkMetadata(
        name="Exercism (Java)",
        description="Java coding tasks from the Exercism benchmark",
        category="core",
        tags=["coding", "java", "execution", "docker"],
        module_path="openbench.evals.exercism.exercism",
        function_name="exercism_java",
    ),
    "exercism_rust": BenchmarkMetadata(
        name="Exercism (Rust)",
        description="Rust coding tasks from the Exercism benchmark",
        category="core",
        tags=["coding", "rust", "execution", "docker"],
        module_path="openbench.evals.exercism.exercism",
        function_name="exercism_rust",
    ),
    "ifeval": BenchmarkMetadata(
        name="Instruction Following",
        description="Tests ability to follow specific formatting and content constraints with both strict and loose evaluation metrics",
        category="core",
        tags=["instruction-following", "constraints", "formatting"],
        module_path="openbench.evals.ifeval",
        function_name="ifeval",
    ),
    "openbookqa": BenchmarkMetadata(
        name="OpenBookQA",
        description="Elementary-level science questions probing understanding of core facts",
        category="core",
        tags=["multiple-choice", "science", "elementary", "open-book"],
        module_path="openbench.evals.openbookqa",
        function_name="openbookqa",
    ),
    "musr": BenchmarkMetadata(
        name="MuSR",
        description="Testing the Limits of Chain-of-thought with Multistep Soft Reasoning - includes murder mysteries, object placements, and team allocation tasks",
        category="core",
        tags=["multiple-choice", "reasoning", "commonsense", "chain-of-thought"],
        module_path="openbench.evals.musr",
        function_name="musr",
    ),
    "musr_murder_mysteries": BenchmarkMetadata(
        name="MuSR Murder Mysteries",
        description="MuSR murder mystery scenarios - who is the most likely murderer?",
        category="core",
        tags=[
            "multiple-choice",
            "reasoning",
            "commonsense",
            "chain-of-thought",
            "murder-mysteries",
        ],
        module_path="openbench.evals.musr",
        function_name="musr_murder_mysteries",
    ),
    "musr_object_placements": BenchmarkMetadata(
        name="MuSR Object Placements",
        description="MuSR object placement reasoning - where would someone look for an object?",
        category="core",
        tags=[
            "multiple-choice",
            "reasoning",
            "commonsense",
            "chain-of-thought",
            "object-placements",
        ],
        module_path="openbench.evals.musr",
        function_name="musr_object_placements",
    ),
    "musr_team_allocation": BenchmarkMetadata(
        name="MuSR Team Allocation",
        description="MuSR team allocation problems - how to allocate people to tasks efficiently?",
        category="core",
        tags=[
            "multiple-choice",
            "reasoning",
            "commonsense",
            "chain-of-thought",
            "team-allocation",
        ],
        module_path="openbench.evals.musr",
        function_name="musr_team_allocation",
    ),
    "supergpqa": BenchmarkMetadata(
        name="SuperGPQA",
        description="Scaling LLM Evaluation across 285 Graduate Disciplines - 26,529 multiple-choice questions across science, engineering, medicine, economics, and philosophy",
        category="core",
        tags=["multiple-choice", "knowledge", "graduate-level", "multidisciplinary"],
        module_path="openbench.evals.supergpqa",
        function_name="supergpqa",
    ),
    "simpleqa": BenchmarkMetadata(
        name="SimpleQA",
        description="Measuring short-form factuality in large language models with simple Q&A pairs",
        category="core",
        tags=["factuality", "question-answering", "graded"],
        module_path="openbench.evals.simpleqa",
        function_name="simpleqa",
    ),
    "tumlu": BenchmarkMetadata(
        name="TUMLU",
        description="TUMLU is a comprehensive, multilingual, and natively developed language understanding benchmark specifically designed for Turkic languages.",
        category="community",
        tags=["factuality", "question-answering", "multiple-choice", "reasoning"],
        module_path="openbench.evals.tumlu",
        function_name="tumlu",
    ),
    "detailbench": BenchmarkMetadata(
        name="DetailBench",
        description="Tests whether LLMs notify users about wrong facts in a text while they are tasked to translate said text",
        category="community",
        tags=["knowledge", "graded", "instruction-following"],
        module_path="openbench.evals.detailbench",
        function_name="detailbench",
    ),
    "browsecomp": BenchmarkMetadata(
        name="BrowseComp",
        description="A Simple Yet Challenging Benchmark for Browsing Agents - evaluates model performance on browsing-related tasks",
        category="core",
        tags=["browsing", "web", "reasoning", "graded"],
        module_path="openbench.evals.browsecomp",
        function_name="browsecomp",
    ),
    "hle": BenchmarkMetadata(
        name="Humanity's Last Exam",
        description="Multi-modal benchmark at the frontier of human knowledge - 2,500 questions across mathematics, humanities, and natural sciences designed by subject-matter experts globally",
        category="core",
        tags=["knowledge", "reasoning", "multi-modal", "graded", "frontier"],
        module_path="openbench.evals.hle",
        function_name="hle",
    ),
    "hle_text": BenchmarkMetadata(
        name="Humanity's Last Exam (Text-Only)",
        description="Text-only variant of HLE with multi-modal questions filtered out - evaluates models without vision capabilities on text-based questions from the frontier of human knowledge",
        category="core",
        tags=["knowledge", "reasoning", "text-only", "graded", "frontier"],
        module_path="openbench.evals.hle",
        function_name="hle_text",
    ),
    "mmstar": BenchmarkMetadata(
        name="MMStar",
        description="MMStar benchmark for measuring multi-modal gain and leakage via coordinated vision and text ablations",
        category="core",
        tags=["vision", "multi-modal", "leakage", "perception", "reasoning"],
        module_path="openbench.evals.mmstar",
        function_name="mmstar",
    ),
    "healthbench": BenchmarkMetadata(
        name="HealthBench",
        description="Medical dialogue evaluation using physician-created rubrics for assessing healthcare conversations",
        category="core",
        tags=["medical", "dialogue", "graded", "rubric-based"],
        module_path="openbench.evals.healthbench",
        function_name="healthbench",
    ),
    "healthbench_hard": BenchmarkMetadata(
        name="HealthBench Hard",
        description="Most challenging medical dialogue cases from HealthBench requiring nuanced medical knowledge",
        category="core",
        tags=["medical", "dialogue", "graded", "rubric-based", "hard"],
        module_path="openbench.evals.healthbench",
        function_name="healthbench_hard",
    ),
    "healthbench_consensus": BenchmarkMetadata(
        name="HealthBench Consensus",
        description="Medical dialogue cases with strong physician consensus on appropriate responses",
        category="core",
        tags=["medical", "dialogue", "graded", "rubric-based", "consensus"],
        module_path="openbench.evals.healthbench",
        function_name="healthbench_consensus",
    ),
    "mgsm": BenchmarkMetadata(
        name="MGSM",
        description="Multilingual Grade School Math benchmark across 11 languages for testing mathematical reasoning",
        category="core",
        tags=["math", "multilingual", "reasoning", "chain-of-thought"],
        module_path="openbench.evals.mgsm",
        function_name="mgsm",
    ),
    "mgsm_en": BenchmarkMetadata(
        name="MGSM English",
        description="Grade school math problems in English for testing mathematical reasoning",
        category="core",
        tags=["math", "english", "reasoning", "chain-of-thought"],
        module_path="openbench.evals.mgsm",
        function_name="mgsm_en",
    ),
    "mgsm_latin": BenchmarkMetadata(
        name="MGSM Latin Script",
        description="Grade school math problems in Latin script languages (German, English, Spanish, French, Swahili)",
        category="core",
        tags=["math", "multilingual", "latin-script", "reasoning", "chain-of-thought"],
        module_path="openbench.evals.mgsm",
        function_name="mgsm_latin",
    ),
    "mgsm_non_latin": BenchmarkMetadata(
        name="MGSM Non-Latin Script",
        description="Grade school math problems in non-Latin script languages (Bengali, Japanese, Russian, Telugu, Thai, Chinese)",
        category="core",
        tags=[
            "math",
            "multilingual",
            "non-latin-script",
            "reasoning",
            "chain-of-thought",
        ],
        module_path="openbench.evals.mgsm",
        function_name="mgsm_non_latin",
    ),
    "drop": BenchmarkMetadata(
        name="DROP",
        description="Reading comprehension benchmark requiring discrete reasoning over paragraphs (arithmetic, counting, sorting)",
        category="core",
        tags=[
            "reading-comprehension",
            "reasoning",
            "arithmetic",
            "counting",
            "sorting",
        ],
        module_path="openbench.evals.drop",
        function_name="drop",
    ),
    "math": BenchmarkMetadata(
        name="MATH",
        description="Measuring Mathematical Problem Solving - 5000 competition math problems across 7 subjects and 5 difficulty levels",
        category="core",
        tags=["math", "problem-solving", "reasoning", "competition", "graded"],
        module_path="openbench.evals.math",
        function_name="math",
    ),
    "math_500": BenchmarkMetadata(
        name="MATH-500",
        description="500-problem subset of MATH dataset for faster evaluation of mathematical problem solving",
        category="core",
        tags=[
            "math",
            "problem-solving",
            "reasoning",
            "competition",
            "graded",
            "subset",
        ],
        module_path="openbench.evals.math",
        function_name="math_500",
    ),
    # Math competitions
    "aime_2023_I": BenchmarkMetadata(
        name="AIME 2023 I",
        description="American Invitational Mathematics Examination 2023 (First)",
        category="math",
        tags=["math", "competition", "aime", "2023"],
        module_path="openbench.evals.matharena.aime_2023_I.aime_2023_I",
        function_name="aime_2023_I",
    ),
    "aime_2023_II": BenchmarkMetadata(
        name="AIME 2023 II",
        description="American Invitational Mathematics Examination 2023 (Second)",
        category="math",
        tags=["math", "competition", "aime", "2023"],
        module_path="openbench.evals.matharena.aime_2023_II.aime_2023_II",
        function_name="aime_2023_II",
    ),
    "aime_2024": BenchmarkMetadata(
        name="AIME 2024",
        description="American Invitational Mathematics Examination 2024 (Combined I & II)",
        category="math",
        tags=["math", "competition", "aime", "2024", "combined"],
        module_path="openbench.evals.matharena.aime_2024.aime_2024",
        function_name="aime_2024",
    ),
    "aime_2024_I": BenchmarkMetadata(
        name="AIME 2024 I",
        description="American Invitational Mathematics Examination 2024 (First)",
        category="math",
        tags=["math", "competition", "aime", "2024"],
        module_path="openbench.evals.matharena.aime_2024_I.aime_2024_I",
        function_name="aime_2024_I",
    ),
    "aime_2024_II": BenchmarkMetadata(
        name="AIME 2024 II",
        description="American Invitational Mathematics Examination 2024 (Second)",
        category="math",
        tags=["math", "competition", "aime", "2024"],
        module_path="openbench.evals.matharena.aime_2024_II.aime_2024_II",
        function_name="aime_2024_II",
    ),
    "aime_2025": BenchmarkMetadata(
        name="AIME 2025",
        description="American Invitational Mathematics Examination 2025",
        category="math",
        tags=["math", "competition", "aime", "2025"],
        module_path="openbench.evals.matharena.aime_2025.aime_2025",
        function_name="aime_2025",
    ),
    "aime_2025_II": BenchmarkMetadata(
        name="AIME 2025 II",
        description="American Invitational Mathematics Examination 2025 (Second)",
        category="math",
        tags=["math", "competition", "aime", "2025"],
        module_path="openbench.evals.matharena.aime_2025_II.aime_2025_II",
        function_name="aime_2025_II",
    ),
    "brumo_2025": BenchmarkMetadata(
        name="BRUMO 2025",
        description="Bruno Mathematical Olympiad 2025",
        category="math",
        tags=["math", "competition", "olympiad", "2025"],
        module_path="openbench.evals.matharena.brumo_2025.brumo_2025",
        function_name="brumo_2025",
    ),
    "hmmt_feb_2023": BenchmarkMetadata(
        name="HMMT Feb 2023",
        description="Harvard-MIT Mathematics Tournament February 2023",
        category="math",
        tags=["math", "competition", "hmmt", "2023"],
        module_path="openbench.evals.matharena.hmmt_feb_2023.hmmt_feb_2023",
        function_name="hmmt_feb_2023",
    ),
    "hmmt_feb_2024": BenchmarkMetadata(
        name="HMMT Feb 2024",
        description="Harvard-MIT Mathematics Tournament February 2024",
        category="math",
        tags=["math", "competition", "hmmt", "2024"],
        module_path="openbench.evals.matharena.hmmt_feb_2024.hmmt_feb_2024",
        function_name="hmmt_feb_2024",
    ),
    "hmmt_feb_2025": BenchmarkMetadata(
        name="HMMT Feb 2025",
        description="Harvard-MIT Mathematics Tournament February 2025",
        category="math",
        tags=["math", "competition", "hmmt", "2025"],
        module_path="openbench.evals.matharena.hmmt_feb_2025.hmmt_feb_2025",
        function_name="hmmt_feb_2025",
    ),
    # Note: bigbench() and bigbench_lite() removed - use individual tasks instead
    # e.g., bigbench_arithmetic, bigbench_strategyqa, etc.
    "bigbench_anachronisms": BenchmarkMetadata(
        name="BigBench: Anachronisms",
        description="BigBench MCQ task: anachronisms",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_anachronisms",
    ),
    "bigbench_analogical_similarity": BenchmarkMetadata(
        name="BigBench: Analogical Similarity",
        description="BigBench MCQ task: analogical_similarity",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_analogical_similarity",
    ),
    "bigbench_analytic_entailment": BenchmarkMetadata(
        name="BigBench: Analytic Entailment",
        description="BigBench MCQ task: analytic_entailment",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_analytic_entailment",
    ),
    "bigbench_arithmetic": BenchmarkMetadata(
        name="BigBench: Arithmetic",
        description="BigBench MCQ task: arithmetic",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_arithmetic",
    ),
    "bigbench_authorship_verification": BenchmarkMetadata(
        name="BigBench: Authorship Verification",
        description="BigBench MCQ task: authorship_verification",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_authorship_verification",
    ),
    "bigbench_bbq_lite_json": BenchmarkMetadata(
        name="BigBench: Bbq Lite Json",
        description="BigBench MCQ task: bbq_lite_json",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_bbq_lite_json",
    ),
    "bigbench_causal_judgment": BenchmarkMetadata(
        name="BigBench: Causal Judgment",
        description="BigBench MCQ task: causal_judgment",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_causal_judgment",
    ),
    "bigbench_cause_and_effect": BenchmarkMetadata(
        name="BigBench: Cause And Effect",
        description="BigBench MCQ task: cause_and_effect",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_cause_and_effect",
    ),
    "bigbench_checkmate_in_one": BenchmarkMetadata(
        name="BigBench: Checkmate In One",
        description="BigBench MCQ task: checkmate_in_one",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_checkmate_in_one",
    ),
    "bigbench_cifar10_classification": BenchmarkMetadata(
        name="BigBench: Cifar10 Classification",
        description="BigBench MCQ task: cifar10_classification",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_cifar10_classification",
    ),
    "bigbench_code_line_description": BenchmarkMetadata(
        name="BigBench: Code Line Description",
        description="BigBench MCQ task: code_line_description",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_code_line_description",
    ),
    "bigbench_color": BenchmarkMetadata(
        name="BigBench: Color",
        description="BigBench MCQ task: color",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_color",
    ),
    "bigbench_common_morpheme": BenchmarkMetadata(
        name="BigBench: Common Morpheme",
        description="BigBench MCQ task: common_morpheme",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_common_morpheme",
    ),
    "bigbench_conceptual_combinations": BenchmarkMetadata(
        name="BigBench: Conceptual Combinations",
        description="BigBench MCQ task: conceptual_combinations",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_conceptual_combinations",
    ),
    "bigbench_contextual_parametric_knowledge_conflicts": BenchmarkMetadata(
        name="BigBench: Contextual Parametric Knowledge Conflicts",
        description="BigBench MCQ task: contextual_parametric_knowledge_conflicts",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_contextual_parametric_knowledge_conflicts",
    ),
    "bigbench_crash_blossom": BenchmarkMetadata(
        name="BigBench: Crash Blossom",
        description="BigBench MCQ task: crash_blossom",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_crash_blossom",
    ),
    "bigbench_crass_ai": BenchmarkMetadata(
        name="BigBench: Crass Ai",
        description="BigBench MCQ task: crass_ai",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_crass_ai",
    ),
    "bigbench_cryobiology_spanish": BenchmarkMetadata(
        name="BigBench: Cryobiology Spanish",
        description="BigBench MCQ task: cryobiology_spanish",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_cryobiology_spanish",
    ),
    "bigbench_cs_algorithms": BenchmarkMetadata(
        name="BigBench: Cs Algorithms",
        description="BigBench MCQ task: cs_algorithms",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_cs_algorithms",
    ),
    "bigbench_dark_humor_detection": BenchmarkMetadata(
        name="BigBench: Dark Humor Detection",
        description="BigBench MCQ task: dark_humor_detection",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_dark_humor_detection",
    ),
    "bigbench_date_understanding": BenchmarkMetadata(
        name="BigBench: Date Understanding",
        description="BigBench MCQ task: date_understanding",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_date_understanding",
    ),
    "bigbench_disambiguation_qa": BenchmarkMetadata(
        name="BigBench: Disambiguation Qa",
        description="BigBench MCQ task: disambiguation_qa",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_disambiguation_qa",
    ),
    "bigbench_discourse_marker_prediction": BenchmarkMetadata(
        name="BigBench: Discourse Marker Prediction",
        description="BigBench MCQ task: discourse_marker_prediction",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_discourse_marker_prediction",
    ),
    "bigbench_dyck_languages": BenchmarkMetadata(
        name="BigBench: Dyck Languages",
        description="BigBench MCQ task: dyck_languages",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_dyck_languages",
    ),
    "bigbench_elementary_math_qa": BenchmarkMetadata(
        name="BigBench: Elementary Math Qa",
        description="BigBench MCQ task: elementary_math_qa",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_elementary_math_qa",
    ),
    "bigbench_emoji_movie": BenchmarkMetadata(
        name="BigBench: Emoji Movie",
        description="BigBench MCQ task: emoji_movie",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_emoji_movie",
    ),
    "bigbench_emojis_emotion_prediction": BenchmarkMetadata(
        name="BigBench: Emojis Emotion Prediction",
        description="BigBench MCQ task: emojis_emotion_prediction",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_emojis_emotion_prediction",
    ),
    "bigbench_empirical_judgments": BenchmarkMetadata(
        name="BigBench: Empirical Judgments",
        description="BigBench MCQ task: empirical_judgments",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_empirical_judgments",
    ),
    "bigbench_english_proverbs": BenchmarkMetadata(
        name="BigBench: English Proverbs",
        description="BigBench MCQ task: english_proverbs",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_english_proverbs",
    ),
    "bigbench_english_russian_proverbs": BenchmarkMetadata(
        name="BigBench: English Russian Proverbs",
        description="BigBench MCQ task: english_russian_proverbs",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_english_russian_proverbs",
    ),
    "bigbench_entailed_polarity": BenchmarkMetadata(
        name="BigBench: Entailed Polarity",
        description="BigBench MCQ task: entailed_polarity",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_entailed_polarity",
    ),
    "bigbench_entailed_polarity_hindi": BenchmarkMetadata(
        name="BigBench: Entailed Polarity Hindi",
        description="BigBench MCQ task: entailed_polarity_hindi",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_entailed_polarity_hindi",
    ),
    "bigbench_epistemic_reasoning": BenchmarkMetadata(
        name="BigBench: Epistemic Reasoning",
        description="BigBench MCQ task: epistemic_reasoning",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_epistemic_reasoning",
    ),
    "bigbench_evaluating_information_essentiality": BenchmarkMetadata(
        name="BigBench: Evaluating Information Essentiality",
        description="BigBench MCQ task: evaluating_information_essentiality",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_evaluating_information_essentiality",
    ),
    "bigbench_fact_checker": BenchmarkMetadata(
        name="BigBench: Fact Checker",
        description="BigBench MCQ task: fact_checker",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_fact_checker",
    ),
    "bigbench_fantasy_reasoning": BenchmarkMetadata(
        name="BigBench: Fantasy Reasoning",
        description="BigBench MCQ task: fantasy_reasoning",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_fantasy_reasoning",
    ),
    "bigbench_figure_of_speech_detection": BenchmarkMetadata(
        name="BigBench: Figure Of Speech Detection",
        description="BigBench MCQ task: figure_of_speech_detection",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_figure_of_speech_detection",
    ),
    "bigbench_formal_fallacies_syllogisms_negation": BenchmarkMetadata(
        name="BigBench: Formal Fallacies Syllogisms Negation",
        description="BigBench MCQ task: formal_fallacies_syllogisms_negation",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_formal_fallacies_syllogisms_negation",
    ),
    "bigbench_general_knowledge": BenchmarkMetadata(
        name="BigBench: General Knowledge",
        description="BigBench MCQ task: general_knowledge",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_general_knowledge",
    ),
    "bigbench_geometric_shapes": BenchmarkMetadata(
        name="BigBench: Geometric Shapes",
        description="BigBench MCQ task: geometric_shapes",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_geometric_shapes",
    ),
    "bigbench_goal_step_wikihow": BenchmarkMetadata(
        name="BigBench: Goal Step Wikihow",
        description="BigBench MCQ task: goal_step_wikihow",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_goal_step_wikihow",
    ),
    "bigbench_gre_reading_comprehension": BenchmarkMetadata(
        name="BigBench: Gre Reading Comprehension",
        description="BigBench MCQ task: gre_reading_comprehension",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_gre_reading_comprehension",
    ),
    "bigbench_hhh_alignment": BenchmarkMetadata(
        name="BigBench: Hhh Alignment",
        description="BigBench MCQ task: hhh_alignment",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_hhh_alignment",
    ),
    "bigbench_hindu_knowledge": BenchmarkMetadata(
        name="BigBench: Hindu Knowledge",
        description="BigBench MCQ task: hindu_knowledge",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_hindu_knowledge",
    ),
    "bigbench_hinglish_toxicity": BenchmarkMetadata(
        name="BigBench: Hinglish Toxicity",
        description="BigBench MCQ task: hinglish_toxicity",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_hinglish_toxicity",
    ),
    "bigbench_human_organs_senses": BenchmarkMetadata(
        name="BigBench: Human Organs Senses",
        description="BigBench MCQ task: human_organs_senses",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_human_organs_senses",
    ),
    "bigbench_hyperbaton": BenchmarkMetadata(
        name="BigBench: Hyperbaton",
        description="BigBench MCQ task: hyperbaton",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_hyperbaton",
    ),
    "bigbench_identify_math_theorems": BenchmarkMetadata(
        name="BigBench: Identify Math Theorems",
        description="BigBench MCQ task: identify_math_theorems",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_identify_math_theorems",
    ),
    "bigbench_identify_odd_metaphor": BenchmarkMetadata(
        name="BigBench: Identify Odd Metaphor",
        description="BigBench MCQ task: identify_odd_metaphor",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_identify_odd_metaphor",
    ),
    "bigbench_implicatures": BenchmarkMetadata(
        name="BigBench: Implicatures",
        description="BigBench MCQ task: implicatures",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_implicatures",
    ),
    "bigbench_implicit_relations": BenchmarkMetadata(
        name="BigBench: Implicit Relations",
        description="BigBench MCQ task: implicit_relations",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_implicit_relations",
    ),
    "bigbench_indic_cause_and_effect": BenchmarkMetadata(
        name="BigBench: Indic Cause And Effect",
        description="BigBench MCQ task: indic_cause_and_effect",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_indic_cause_and_effect",
    ),
    "bigbench_intent_recognition": BenchmarkMetadata(
        name="BigBench: Intent Recognition",
        description="BigBench MCQ task: intent_recognition",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_intent_recognition",
    ),
    "bigbench_international_phonetic_alphabet_nli": BenchmarkMetadata(
        name="BigBench: International Phonetic Alphabet Nli",
        description="BigBench MCQ task: international_phonetic_alphabet_nli",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_international_phonetic_alphabet_nli",
    ),
    "bigbench_intersect_geometry": BenchmarkMetadata(
        name="BigBench: Intersect Geometry",
        description="BigBench MCQ task: intersect_geometry",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_intersect_geometry",
    ),
    "bigbench_irony_identification": BenchmarkMetadata(
        name="BigBench: Irony Identification",
        description="BigBench MCQ task: irony_identification",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_irony_identification",
    ),
    "bigbench_kanji_ascii": BenchmarkMetadata(
        name="BigBench: Kanji Ascii",
        description="BigBench MCQ task: kanji_ascii",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_kanji_ascii",
    ),
    "bigbench_kannada": BenchmarkMetadata(
        name="BigBench: Kannada",
        description="BigBench MCQ task: kannada",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_kannada",
    ),
    "bigbench_key_value_maps": BenchmarkMetadata(
        name="BigBench: Key Value Maps",
        description="BigBench MCQ task: key_value_maps",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_key_value_maps",
    ),
    "bigbench_known_unknowns": BenchmarkMetadata(
        name="BigBench: Known Unknowns",
        description="BigBench MCQ task: known_unknowns",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_known_unknowns",
    ),
    "bigbench_language_identification": BenchmarkMetadata(
        name="BigBench: Language Identification",
        description="BigBench MCQ task: language_identification",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_language_identification",
    ),
    "bigbench_logic_grid_puzzle": BenchmarkMetadata(
        name="BigBench: Logic Grid Puzzle",
        description="BigBench MCQ task: logic_grid_puzzle",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_logic_grid_puzzle",
    ),
    "bigbench_logical_args": BenchmarkMetadata(
        name="BigBench: Logical Args",
        description="BigBench MCQ task: logical_args",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_logical_args",
    ),
    "bigbench_logical_deduction": BenchmarkMetadata(
        name="BigBench: Logical Deduction",
        description="BigBench MCQ task: logical_deduction",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_logical_deduction",
    ),
    "bigbench_logical_fallacy_detection": BenchmarkMetadata(
        name="BigBench: Logical Fallacy Detection",
        description="BigBench MCQ task: logical_fallacy_detection",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_logical_fallacy_detection",
    ),
    "bigbench_logical_sequence": BenchmarkMetadata(
        name="BigBench: Logical Sequence",
        description="BigBench MCQ task: logical_sequence",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_logical_sequence",
    ),
    "bigbench_mathematical_induction": BenchmarkMetadata(
        name="BigBench: Mathematical Induction",
        description="BigBench MCQ task: mathematical_induction",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_mathematical_induction",
    ),
    "bigbench_medical_questions_russian": BenchmarkMetadata(
        name="BigBench: Medical Questions Russian",
        description="BigBench MCQ task: medical_questions_russian",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_medical_questions_russian",
    ),
    "bigbench_metaphor_boolean": BenchmarkMetadata(
        name="BigBench: Metaphor Boolean",
        description="BigBench MCQ task: metaphor_boolean",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_metaphor_boolean",
    ),
    "bigbench_metaphor_understanding": BenchmarkMetadata(
        name="BigBench: Metaphor Understanding",
        description="BigBench MCQ task: metaphor_understanding",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_metaphor_understanding",
    ),
    "bigbench_minute_mysteries_qa": BenchmarkMetadata(
        name="BigBench: Minute Mysteries Qa",
        description="BigBench MCQ task: minute_mysteries_qa",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_minute_mysteries_qa",
    ),
    "bigbench_misconceptions": BenchmarkMetadata(
        name="BigBench: Misconceptions",
        description="BigBench MCQ task: misconceptions",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_misconceptions",
    ),
    "bigbench_misconceptions_russian": BenchmarkMetadata(
        name="BigBench: Misconceptions Russian",
        description="BigBench MCQ task: misconceptions_russian",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_misconceptions_russian",
    ),
    "bigbench_mnist_ascii": BenchmarkMetadata(
        name="BigBench: Mnist Ascii",
        description="BigBench MCQ task: mnist_ascii",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_mnist_ascii",
    ),
    "bigbench_moral_permissibility": BenchmarkMetadata(
        name="BigBench: Moral Permissibility",
        description="BigBench MCQ task: moral_permissibility",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_moral_permissibility",
    ),
    "bigbench_movie_dialog_same_or_different": BenchmarkMetadata(
        name="BigBench: Movie Dialog Same Or Different",
        description="BigBench MCQ task: movie_dialog_same_or_different",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_movie_dialog_same_or_different",
    ),
    "bigbench_movie_recommendation": BenchmarkMetadata(
        name="BigBench: Movie Recommendation",
        description="BigBench MCQ task: movie_recommendation",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_movie_recommendation",
    ),
    "bigbench_navigate": BenchmarkMetadata(
        name="BigBench: Navigate",
        description="BigBench MCQ task: navigate",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_navigate",
    ),
    "bigbench_nonsense_words_grammar": BenchmarkMetadata(
        name="BigBench: Nonsense Words Grammar",
        description="BigBench MCQ task: nonsense_words_grammar",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_nonsense_words_grammar",
    ),
    "bigbench_novel_concepts": BenchmarkMetadata(
        name="BigBench: Novel Concepts",
        description="BigBench MCQ task: novel_concepts",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_novel_concepts",
    ),
    "bigbench_odd_one_out": BenchmarkMetadata(
        name="BigBench: Odd One Out",
        description="BigBench MCQ task: odd_one_out",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_odd_one_out",
    ),
    "bigbench_parsinlu_qa": BenchmarkMetadata(
        name="BigBench: Parsinlu Qa",
        description="BigBench MCQ task: parsinlu_qa",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_parsinlu_qa",
    ),
    "bigbench_penguins_in_a_table": BenchmarkMetadata(
        name="BigBench: Penguins In A Table",
        description="BigBench MCQ task: penguins_in_a_table",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_penguins_in_a_table",
    ),
    "bigbench_periodic_elements": BenchmarkMetadata(
        name="BigBench: Periodic Elements",
        description="BigBench MCQ task: periodic_elements",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_periodic_elements",
    ),
    "bigbench_persian_idioms": BenchmarkMetadata(
        name="BigBench: Persian Idioms",
        description="BigBench MCQ task: persian_idioms",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_persian_idioms",
    ),
    "bigbench_phrase_relatedness": BenchmarkMetadata(
        name="BigBench: Phrase Relatedness",
        description="BigBench MCQ task: phrase_relatedness",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_phrase_relatedness",
    ),
    "bigbench_physical_intuition": BenchmarkMetadata(
        name="BigBench: Physical Intuition",
        description="BigBench MCQ task: physical_intuition",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_physical_intuition",
    ),
    "bigbench_physics": BenchmarkMetadata(
        name="BigBench: Physics",
        description="BigBench MCQ task: physics",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_physics",
    ),
    "bigbench_play_dialog_same_or_different": BenchmarkMetadata(
        name="BigBench: Play Dialog Same Or Different",
        description="BigBench MCQ task: play_dialog_same_or_different",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_play_dialog_same_or_different",
    ),
    "bigbench_presuppositions_as_nli": BenchmarkMetadata(
        name="BigBench: Presuppositions As Nli",
        description="BigBench MCQ task: presuppositions_as_nli",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_presuppositions_as_nli",
    ),
    "bigbench_question_selection": BenchmarkMetadata(
        name="BigBench: Question Selection",
        description="BigBench MCQ task: question_selection",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_question_selection",
    ),
    "bigbench_real_or_fake_text": BenchmarkMetadata(
        name="BigBench: Real Or Fake Text",
        description="BigBench MCQ task: real_or_fake_text",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_real_or_fake_text",
    ),
    "bigbench_reasoning_about_colored_objects": BenchmarkMetadata(
        name="BigBench: Reasoning About Colored Objects",
        description="BigBench MCQ task: reasoning_about_colored_objects",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_reasoning_about_colored_objects",
    ),
    "bigbench_rhyming": BenchmarkMetadata(
        name="BigBench: Rhyming",
        description="BigBench MCQ task: rhyming",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_rhyming",
    ),
    "bigbench_riddle_sense": BenchmarkMetadata(
        name="BigBench: Riddle Sense",
        description="BigBench MCQ task: riddle_sense",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_riddle_sense",
    ),
    "bigbench_ruin_names": BenchmarkMetadata(
        name="BigBench: Ruin Names",
        description="BigBench MCQ task: ruin_names",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_ruin_names",
    ),
    "bigbench_salient_translation_error_detection": BenchmarkMetadata(
        name="BigBench: Salient Translation Error Detection",
        description="BigBench MCQ task: salient_translation_error_detection",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_salient_translation_error_detection",
    ),
    "bigbench_sentence_ambiguity": BenchmarkMetadata(
        name="BigBench: Sentence Ambiguity",
        description="BigBench MCQ task: sentence_ambiguity",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_sentence_ambiguity",
    ),
    "bigbench_similarities_abstraction": BenchmarkMetadata(
        name="BigBench: Similarities Abstraction",
        description="BigBench MCQ task: similarities_abstraction",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_similarities_abstraction",
    ),
    "bigbench_simple_ethical_questions": BenchmarkMetadata(
        name="BigBench: Simple Ethical Questions",
        description="BigBench MCQ task: simple_ethical_questions",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_simple_ethical_questions",
    ),
    "bigbench_snarks": BenchmarkMetadata(
        name="BigBench: Snarks",
        description="BigBench MCQ task: snarks",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_snarks",
    ),
    "bigbench_social_iqa": BenchmarkMetadata(
        name="BigBench: Social Iqa",
        description="BigBench MCQ task: social_iqa",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_social_iqa",
    ),
    "bigbench_social_support": BenchmarkMetadata(
        name="BigBench: Social Support",
        description="BigBench MCQ task: social_support",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_social_support",
    ),
    "bigbench_sports_understanding": BenchmarkMetadata(
        name="BigBench: Sports Understanding",
        description="BigBench MCQ task: sports_understanding",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_sports_understanding",
    ),
    "bigbench_strange_stories": BenchmarkMetadata(
        name="BigBench: Strange Stories",
        description="BigBench MCQ task: strange_stories",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_strange_stories",
    ),
    "bigbench_strategyqa": BenchmarkMetadata(
        name="BigBench: Strategyqa",
        description="BigBench MCQ task: strategyqa",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_strategyqa",
    ),
    "bigbench_suicide_risk": BenchmarkMetadata(
        name="BigBench: Suicide Risk",
        description="BigBench MCQ task: suicide_risk",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_suicide_risk",
    ),
    "bigbench_swahili_english_proverbs": BenchmarkMetadata(
        name="BigBench: Swahili English Proverbs",
        description="BigBench MCQ task: swahili_english_proverbs",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_swahili_english_proverbs",
    ),
    "bigbench_swedish_to_german_proverbs": BenchmarkMetadata(
        name="BigBench: Swedish To German Proverbs",
        description="BigBench MCQ task: swedish_to_german_proverbs",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_swedish_to_german_proverbs",
    ),
    "bigbench_symbol_interpretation": BenchmarkMetadata(
        name="BigBench: Symbol Interpretation",
        description="BigBench MCQ task: symbol_interpretation",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_symbol_interpretation",
    ),
    "bigbench_temporal_sequences": BenchmarkMetadata(
        name="BigBench: Temporal Sequences",
        description="BigBench MCQ task: temporal_sequences",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_temporal_sequences",
    ),
    "bigbench_timedial": BenchmarkMetadata(
        name="BigBench: Timedial",
        description="BigBench MCQ task: timedial",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_timedial",
    ),
    "bigbench_tracking_shuffled_objects": BenchmarkMetadata(
        name="BigBench: Tracking Shuffled Objects",
        description="BigBench MCQ task: tracking_shuffled_objects",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_tracking_shuffled_objects",
    ),
    "bigbench_understanding_fables": BenchmarkMetadata(
        name="BigBench: Understanding Fables",
        description="BigBench MCQ task: understanding_fables",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_understanding_fables",
    ),
    "bigbench_undo_permutation": BenchmarkMetadata(
        name="BigBench: Undo Permutation",
        description="BigBench MCQ task: undo_permutation",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_undo_permutation",
    ),
    "bigbench_unit_conversion": BenchmarkMetadata(
        name="BigBench: Unit Conversion",
        description="BigBench MCQ task: unit_conversion",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_unit_conversion",
    ),
    "bigbench_unit_interpretation": BenchmarkMetadata(
        name="BigBench: Unit Interpretation",
        description="BigBench MCQ task: unit_interpretation",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_unit_interpretation",
    ),
    "bigbench_vitaminc_fact_verification": BenchmarkMetadata(
        name="BigBench: Vitaminc Fact Verification",
        description="BigBench MCQ task: vitaminc_fact_verification",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_vitaminc_fact_verification",
    ),
    "bigbench_what_is_the_tao": BenchmarkMetadata(
        name="BigBench: What Is The Tao",
        description="BigBench MCQ task: what_is_the_tao",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_what_is_the_tao",
    ),
    "bigbench_which_wiki_edit": BenchmarkMetadata(
        name="BigBench: Which Wiki Edit",
        description="BigBench MCQ task: which_wiki_edit",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_which_wiki_edit",
    ),
    "bigbench_winowhy": BenchmarkMetadata(
        name="BigBench: Winowhy",
        description="BigBench MCQ task: winowhy",
        category="bigbench",
        tags=["multiple-choice", "reasoning", "bigbench"],
        module_path="openbench.evals.bigbench",
        function_name="bigbench_winowhy",
    ),
    "boolq": BenchmarkMetadata(
        name="BoolQ",
        description="BoolQ: A Question Answering Dataset for Boolean Reasoning",
        category="core",
        tags=["boolean-reasoning", "question-answering"],
        module_path="openbench.evals.boolq",
        function_name="boolq",
    ),
    "scicode": BenchmarkMetadata(
        name="SciCode",
        description="Scientific computing and programming challenges",
        category="core",
        tags=["code-generation", "science", "alpha"],
        module_path="openbench.evals.scicode",
        function_name="scicode",
        is_alpha=True,
    ),
    "cti_bench_ate": BenchmarkMetadata(
        name="CTI-Bench ATE",
        description="Extracting MITRE ATT&CK techniques from malware and threat descriptions",
        category="cybersecurity",
        tags=["extraction", "cybersecurity"],
        module_path="openbench.evals.cti_bench",
        function_name="cti_bench_ate",
    ),
    "cti_bench_mcq": BenchmarkMetadata(
        name="CTI-Bench MCQ",
        description="Multiple-choice questions evaluating understanding of CTI standards, threats, detection strategies, and best practices using authoritative sources like NIST and MITRE",
        category="cybersecurity",
        tags=["multiple-choice", "cybersecurity", "knowledge"],
        module_path="openbench.evals.cti_bench",
        function_name="cti_bench_mcq",
    ),
    "cti_bench_rcm": BenchmarkMetadata(
        name="CTI-Bench RCM",
        description="Mapping CVE descriptions to CWE categories to evaluate vulnerability classification ability",
        category="cybersecurity",
        tags=["classification", "cybersecurity"],
        module_path="openbench.evals.cti_bench",
        function_name="cti_bench_rcm",
    ),
    "cti_bench_vsp": BenchmarkMetadata(
        name="CTI-Bench VSP",
        description="Calculating CVSS scores from vulnerability descriptions to assess severity evaluation skills",
        category="cybersecurity",
        tags=["regression", "cybersecurity"],
        module_path="openbench.evals.cti_bench",
        function_name="cti_bench_vsp",
    ),
    "rootly_gmcq": BenchmarkMetadata(
        name="GMCQ",
        description="GitHub Multiple Choice Questions",
        category="core",
        tags=["code-understanding"],
        module_path="openbench.evals.rootly_gmcq",
        function_name="rootly_gmcq",
    ),
    "rootly_terraform": BenchmarkMetadata(
        name="Terraform",
        description="Terraform Multiple Choice Questions",
        category="core",
        tags=["code-understanding"],
        module_path="openbench.evals.rootly_terraform",
        function_name="rootly_terraform",
    ),
    "jsonschemabench": BenchmarkMetadata(
        name="JSONSchemaBench",
        description="JSON Schema generation benchmark with ~10K real-world schemas from GitHub, Kubernetes, and other sources for evaluating constrained decoding",
        category="core",
        tags=["json", "jsonschema", "generation", "constrained-decoding"],
        module_path="openbench.evals.jsonschemabench",
        function_name="jsonschemabench",
        is_alpha=False,
    ),
    "mmmu": BenchmarkMetadata(
        name="MMMU",
        description="Massive Multi-discipline Multimodal Understanding and Reasoning Benchmark with 11.5K questions across 30 subjects from college exams, quizzes, and textbooks",
        category="core",
        tags=["multimodal", "multiple-choice", "reasoning", "college-level", "images"],
        module_path="openbench.evals.mmmu",
        function_name="mmmu",
        is_alpha=False,
    ),
    "mmmu_art": BenchmarkMetadata(
        name="MMMU Art",
        description="MMMU Art subset focusing on art and visual design questions",
        category="core",
        tags=["multimodal", "multiple-choice", "art", "visual-design", "images"],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_art",
        is_alpha=False,
    ),
    "mmmu_biology": BenchmarkMetadata(
        name="MMMU Biology",
        description="MMMU Biology subset focusing on biological sciences",
        category="core",
        tags=["multimodal", "multiple-choice", "biology", "science", "images"],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_biology",
        is_alpha=False,
    ),
    "mmmu_chemistry": BenchmarkMetadata(
        name="MMMU Chemistry",
        description="MMMU Chemistry subset focusing on chemical sciences",
        category="core",
        tags=["multimodal", "multiple-choice", "chemistry", "science", "images"],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_chemistry",
        is_alpha=False,
    ),
    "mmmu_math": BenchmarkMetadata(
        name="MMMU Math",
        description="MMMU Mathematics subset focusing on mathematical reasoning",
        category="math",
        tags=["multimodal", "multiple-choice", "mathematics", "reasoning", "images"],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_math",
        is_alpha=False,
    ),
    "mmmu_physics": BenchmarkMetadata(
        name="MMMU Physics",
        description="MMMU Physics subset focusing on physics and physical sciences",
        category="core",
        tags=["multimodal", "multiple-choice", "physics", "science", "images"],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_physics",
        is_alpha=False,
    ),
    "mmmu_accounting": BenchmarkMetadata(
        name="MMMU Accounting",
        description="MMMU Accounting subset focusing on accounting principles and practices",
        category="core",
        tags=["multimodal", "multiple-choice", "accounting", "business", "images"],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_accounting",
        is_alpha=False,
    ),
    "mmmu_agriculture": BenchmarkMetadata(
        name="MMMU Agriculture",
        description="MMMU Agriculture subset focusing on agricultural sciences and practices",
        category="core",
        tags=["multimodal", "multiple-choice", "agriculture", "science", "images"],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_agriculture",
        is_alpha=False,
    ),
    "mmmu_architecture_and_engineering": BenchmarkMetadata(
        name="MMMU Architecture and Engineering",
        description="MMMU Architecture and Engineering subset focusing on engineering design and architecture",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "architecture",
            "engineering",
            "design",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_architecture_and_engineering",
        is_alpha=False,
    ),
    "mmmu_art_theory": BenchmarkMetadata(
        name="MMMU Art Theory",
        description="MMMU Art Theory subset focusing on art history and theoretical concepts",
        category="core",
        tags=["multimodal", "multiple-choice", "art", "theory", "history", "images"],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_art_theory",
        is_alpha=False,
    ),
    "mmmu_basic_medical_science": BenchmarkMetadata(
        name="MMMU Basic Medical Science",
        description="MMMU Basic Medical Science subset focusing on fundamental medical knowledge",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "medicine",
            "science",
            "health",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_basic_medical_science",
        is_alpha=False,
    ),
    "mmmu_clinical_medicine": BenchmarkMetadata(
        name="MMMU Clinical Medicine",
        description="MMMU Clinical Medicine subset focusing on clinical medical practice",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "medicine",
            "clinical",
            "health",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_clinical_medicine",
        is_alpha=False,
    ),
    "mmmu_design": BenchmarkMetadata(
        name="MMMU Design",
        description="MMMU Design subset focusing on design principles and practices",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "design",
            "visual",
            "creative",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_design",
        is_alpha=False,
    ),
    "mmmu_diagnostics_and_laboratory_medicine": BenchmarkMetadata(
        name="MMMU Diagnostics and Laboratory Medicine",
        description="MMMU Diagnostics and Laboratory Medicine subset focusing on medical diagnostics",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "medicine",
            "diagnostics",
            "laboratory",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_diagnostics_and_laboratory_medicine",
        is_alpha=False,
    ),
    "mmmu_electronics": BenchmarkMetadata(
        name="MMMU Electronics",
        description="MMMU Electronics subset focusing on electronic systems and circuits",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "electronics",
            "engineering",
            "technology",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_electronics",
        is_alpha=False,
    ),
    "mmmu_energy_and_power": BenchmarkMetadata(
        name="MMMU Energy and Power",
        description="MMMU Energy and Power subset focusing on energy systems and power generation",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "energy",
            "power",
            "engineering",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_energy_and_power",
        is_alpha=False,
    ),
    "mmmu_finance": BenchmarkMetadata(
        name="MMMU Finance",
        description="MMMU Finance subset focusing on financial concepts and analysis",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "finance",
            "business",
            "economics",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_finance",
        is_alpha=False,
    ),
    "mmmu_geography": BenchmarkMetadata(
        name="MMMU Geography",
        description="MMMU Geography subset focusing on geographical knowledge and analysis",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "geography",
            "earth-science",
            "spatial",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_geography",
        is_alpha=False,
    ),
    "mmmu_history": BenchmarkMetadata(
        name="MMMU History",
        description="MMMU History subset focusing on historical knowledge and analysis",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "history",
            "humanities",
            "culture",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_history",
        is_alpha=False,
    ),
    "mmmu_literature": BenchmarkMetadata(
        name="MMMU Literature",
        description="MMMU Literature subset focusing on literary analysis and knowledge",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "literature",
            "humanities",
            "language",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_literature",
        is_alpha=False,
    ),
    "mmmu_manage": BenchmarkMetadata(
        name="MMMU Management",
        description="MMMU Management subset focusing on management principles and practices",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "management",
            "business",
            "leadership",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_manage",
        is_alpha=False,
    ),
    "mmmu_marketing": BenchmarkMetadata(
        name="MMMU Marketing",
        description="MMMU Marketing subset focusing on marketing strategies and concepts",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "marketing",
            "business",
            "communication",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_marketing",
        is_alpha=False,
    ),
    "mmmu_materials": BenchmarkMetadata(
        name="MMMU Materials",
        description="MMMU Materials subset focusing on materials science and engineering",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "materials",
            "science",
            "engineering",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_materials",
        is_alpha=False,
    ),
    "mmmu_mechanical_engineering": BenchmarkMetadata(
        name="MMMU Mechanical Engineering",
        description="MMMU Mechanical Engineering subset focusing on mechanical systems and design",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "mechanical",
            "engineering",
            "design",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_mechanical_engineering",
        is_alpha=False,
    ),
    "mmmu_music": BenchmarkMetadata(
        name="MMMU Music",
        description="MMMU Music subset focusing on music theory and analysis",
        category="core",
        tags=["multimodal", "multiple-choice", "music", "arts", "theory", "images"],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_music",
        is_alpha=False,
    ),
    "mmmu_pharmacy": BenchmarkMetadata(
        name="MMMU Pharmacy",
        description="MMMU Pharmacy subset focusing on pharmaceutical sciences and practice",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "pharmacy",
            "medicine",
            "health",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_pharmacy",
        is_alpha=False,
    ),
    "mmmu_public_health": BenchmarkMetadata(
        name="MMMU Public Health",
        description="MMMU Public Health subset focusing on public health concepts and practices",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "public-health",
            "health",
            "population",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_public_health",
        is_alpha=False,
    ),
    "mmmu_sociology": BenchmarkMetadata(
        name="MMMU Sociology",
        description="MMMU Sociology subset focusing on sociological concepts and analysis",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "sociology",
            "social-science",
            "society",
            "images",
        ],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_sociology",
        is_alpha=False,
    ),
    "mmmu_mcq": BenchmarkMetadata(
        name="MMMU MCQ",
        description="MMMU MCQ subset focusing on multiple choice questions",
        category="core",
        tags=["multimodal", "multiple-choice", "images"],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_mcq",
        is_alpha=False,
    ),
    "mmmu_open": BenchmarkMetadata(
        name="MMMU Open",
        description="MMMU Open subset focusing on open-ended questions",
        category="core",
        tags=["multimodal", "open-ended", "images"],
        module_path="openbench.evals.mmmu",
        function_name="mmmu_open",
        is_alpha=False,
    ),
    "mmmu_pro": BenchmarkMetadata(
        name="MMMU-Pro",
        description="Enhanced multimodal MMMU-Pro benchmark with multiple-choice across many options and images",
        category="core",
        tags=[
            "multimodal",
            "multiple-choice",
            "reasoning",
            "images",
            "mmmu-pro",
        ],
        module_path="openbench.evals.mmmu_pro",
        function_name="mmmu_pro",
        is_alpha=False,
    ),
    "mmmu_pro_vision": BenchmarkMetadata(
        name="MMMU-Pro (Vision)",
        description="MMMU-Pro vision subset with images and multiple-choice questions",
        category="core",
        tags=["multimodal", "vision", "multiple-choice", "images", "mmmu-pro"],
        module_path="openbench.evals.mmmu_pro",
        function_name="mmmu_pro_vision",
        is_alpha=False,
    ),
    "arc_agi": BenchmarkMetadata(
        name="ARC-AGI",
        description="Abstraction and Reasoning Corpus for Artificial General Intelligence; specify version with -T version=1 or version=2",
        category="core",
        tags=[
            "reasoning",
            "pattern-recognition",
            "abstract-reasoning",
            "visual",
            "logic",
            "agi",
        ],
        module_path="openbench.evals.arc_agi",
        function_name="arc_agi",
    ),
    "arc_agi_1": BenchmarkMetadata(
        name="ARC-AGI-1",
        description="ARC-AGI dataset version 1",
        category="core",
        tags=[
            "reasoning",
            "pattern-recognition",
            "abstract-reasoning",
            "visual",
            "logic",
            "agi",
        ],
        module_path="openbench.evals.arc_agi",
        function_name="arc_agi_1",
    ),
    "arc_agi_2": BenchmarkMetadata(
        name="ARC-AGI-2",
        description="ARC-AGI dataset version 2",
        category="core",
        tags=[
            "reasoning",
            "pattern-recognition",
            "abstract-reasoning",
            "visual",
            "logic",
            "agi",
        ],
        module_path="openbench.evals.arc_agi",
        function_name="arc_agi_2",
    ),
    "livemcpbench": BenchmarkMetadata(
        name="LiveMCPBench",
        description="Benchmark for evaluating LLM agents on real-world tasks using the Model Context Protocol (MCP) - 95 tasks across different categories",
        category="core",
        tags=["mcp", "agents", "real-world", "tools", "graded"],
        module_path="openbench.evals.livemcpbench",
        function_name="livemcpbench",
        is_alpha=False,
    ),
}


def _normalize_benchmark_key(name: str) -> str:
    """Normalize benchmark keys so '-' and '_' are treated the same."""

    return name.replace("-", "_")


def _build_normalized_lookup(names: Iterable[str]) -> dict[str, str]:
    """Build a lookup mapping normalized benchmark keys to canonical names."""

    lookup: dict[str, str] = {}
    for key in names:
        normalized = _normalize_benchmark_key(key)
        existing = lookup.get(normalized)
        if existing and existing != key:
            raise ValueError(
                "Benchmark names cannot differ only by '-' vs '_' ("
                f"conflict between '{existing}' and '{key}')"
            )
        lookup[normalized] = key
    return lookup


_NORMALIZED_BENCHMARK_NAMES = _build_normalized_lookup(BENCHMARKS.keys())


def get_benchmark_metadata(name: str) -> Optional[BenchmarkMetadata]:
    """Get benchmark metadata by name."""
    metadata = BENCHMARKS.get(name)
    if metadata:
        return metadata

    canonical_name = _NORMALIZED_BENCHMARK_NAMES.get(_normalize_benchmark_key(name))
    if canonical_name:
        return BENCHMARKS[canonical_name]

    return None


def get_all_benchmarks(include_alpha: bool = False) -> dict[str, BenchmarkMetadata]:
    """Get all benchmark metadata.

    Args:
        include_alpha: Whether to include alpha/experimental benchmarks
    """
    if include_alpha:
        return BENCHMARKS
    return {name: meta for name, meta in BENCHMARKS.items() if not meta.is_alpha}


def get_benchmarks_by_category(
    category: str, include_alpha: bool = False
) -> dict[str, BenchmarkMetadata]:
    """Get all benchmarks in a category.

    Args:
        category: Category to filter by
        include_alpha: Whether to include alpha/experimental benchmarks
    """
    results = {
        name: meta for name, meta in BENCHMARKS.items() if meta.category == category
    }
    if not include_alpha:
        results = {name: meta for name, meta in results.items() if not meta.is_alpha}
    return results


def get_categories() -> List[str]:
    """Get all available categories."""
    return sorted(list(set(meta.category for meta in BENCHMARKS.values())))


def search_benchmarks(
    query: str, include_alpha: bool = False
) -> dict[str, BenchmarkMetadata]:
    """Search benchmarks by name, description, or tags.

    Args:
        query: Search query
        include_alpha: Whether to include alpha/experimental benchmarks
    """
    query = query.lower()
    results = {}

    for name, meta in BENCHMARKS.items():
        if not include_alpha and meta.is_alpha:
            continue
        if (
            query in meta.name.lower()
            or query in meta.description.lower()
            or any(query in tag.lower() for tag in meta.tags)
        ):
            results[name] = meta

    return results


# ============================================================================
# Task Loading for CLI
# ============================================================================


def _generate_task_registry(include_alpha: bool = True):
    """Generate task registry from config.

    Args:
        include_alpha: Whether to include alpha/experimental benchmarks
    """
    registry = {}
    for name, metadata in get_all_benchmarks(include_alpha=include_alpha).items():
        registry[name] = f"{metadata.module_path}.{metadata.function_name}"
    return registry


# Full registry including alpha benchmarks for backward compatibility
TASK_REGISTRY = _generate_task_registry(include_alpha=True)

_NORMALIZED_TASK_REGISTRY = _build_normalized_lookup(TASK_REGISTRY.keys())


def _import_module_from_path(path: Path) -> ModuleType:
    """
    Import a .py file or package directory as an anonymous module.
    """
    file_path = path
    if path.is_dir():
        file_path = path / "__init__.py"
        if not file_path.exists():
            raise ValueError(f"{path} is a directory but has no __init__.py")

    mod_name = f"_openbench_dyn_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(mod_name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create import spec for {file_path}")

    module = importlib.util.module_from_spec(spec)

    # For packages, set up proper package structure for relative imports
    if path.is_dir():
        module.__package__ = mod_name
        sys.modules[mod_name] = module

        # Pre-load submodules to support relative imports
        for submodule_file in path.glob("*.py"):
            if submodule_file.name != "__init__.py":
                submodule_name = submodule_file.stem
                submodule_full_name = f"{mod_name}.{submodule_name}"
                submodule_spec = importlib.util.spec_from_file_location(
                    submodule_full_name, str(submodule_file)
                )
                if submodule_spec and submodule_spec.loader:
                    submodule = importlib.util.module_from_spec(submodule_spec)
                    submodule.__package__ = mod_name
                    sys.modules[submodule_full_name] = submodule
                    submodule_spec.loader.exec_module(submodule)
    else:
        sys.modules[mod_name] = module

    spec.loader.exec_module(module)
    return module


@lru_cache()
def load_task(benchmark_name: str, allow_alpha: bool = False) -> Callable:
    """
    Loads a task by benchmark name using the registry or from a local path.

    Args:
        benchmark_name (str): The name of the benchmark or path to a local eval.
        allow_alpha (bool): Whether to allow loading alpha/experimental benchmarks.

    Returns:
        Callable: The imported function object.

    Raises:
        ValueError: If the benchmark is not in the registry and not a valid path.
        ImportError: If the module cannot be imported.
        AttributeError: If the function does not exist in the module.
    """
    # Check if this is an alpha benchmark
    benchmark_meta = get_benchmark_metadata(benchmark_name)
    if benchmark_meta and benchmark_meta.is_alpha and not allow_alpha:
        raise ValueError(
            f"'{benchmark_name}' is an experimental/alpha benchmark. "
            f"Use --alpha flag to run it."
        )

    # Try registry first (registry names take precedence)
    import_path = TASK_REGISTRY.get(benchmark_name)
    if import_path is None:
        canonical_name = _NORMALIZED_TASK_REGISTRY.get(
            _normalize_benchmark_key(benchmark_name)
        )
        if canonical_name:
            import_path = TASK_REGISTRY[canonical_name]
            benchmark_name = canonical_name
    if import_path:
        module_path, func_name = import_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, func_name)

    # Fallback to path-based loading
    path = Path(benchmark_name).expanduser()
    if path.exists():
        return _load_task_from_local_path(path)

    # Neither registry nor valid path
    raise ValueError(
        f"Unknown benchmark: '{benchmark_name}'. "
        f"Available benchmarks: {', '.join(TASK_REGISTRY.keys())}"
    )


def _load_task_from_local_path(path: Path) -> Callable:
    """
    Load a task from a local path containing __metadata__.

    Args:
        path: Path to a directory or .py file containing an eval

    Returns:
        Callable: The imported function object

    Raises:
        ValueError: If no valid __metadata__ is found
        AttributeError: If the function does not exist in the module
        ImportError: If the module cannot be imported
    """
    root_module = _import_module_from_path(path)
    metadata = getattr(root_module, "__metadata__", None)

    if not isinstance(metadata, BenchmarkMetadata):
        raise ValueError(f"{path} has no valid __metadata__")

    # Resolve module path relative to root module
    # For local evals, module_path is typically relative like "simpleqa.simpleqa"
    # We need to extract just the last part and combine with the root module name
    if metadata.module_path.startswith(root_module.__name__):
        full_module_name = metadata.module_path
    else:
        # For paths like "simpleqa.simpleqa", we want the last component "simpleqa"
        module_components = metadata.module_path.split(".")
        module_name = module_components[-1]  # Take the last component
        full_module_name = f"{root_module.__name__}.{module_name}"

    try:
        module = importlib.import_module(full_module_name)
    except ImportError as e:
        raise ImportError(f"Cannot import module '{full_module_name}': {e}")

    try:
        return getattr(module, metadata.function_name)
    except AttributeError:
        raise AttributeError(
            f"Function '{metadata.function_name}' not found in module '{full_module_name}'"
        )


def get_eval_metadata(path_like: str) -> BenchmarkMetadata | None:
    """
    Best-effort extraction of __metadata__ for path-based evals.
    Returns None for registry-based benchmarks or when no metadata is present.
    """
    p = Path(path_like).expanduser()
    if not p.exists():
        return None

    try:
        module = _import_module_from_path(p)
        meta = getattr(module, "__metadata__", None)
        return meta if isinstance(meta, BenchmarkMetadata) else None
    except Exception:
        return None
