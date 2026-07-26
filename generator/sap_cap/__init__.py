"""
SAP CAP task generation module for Endless Terminals.

This module provides task generation for SAP Cloud Application Programming (CAP) model,
including data modeling, service definitions, database operations, and handler implementations.
"""

from .task_templates import CAP_TASK_CATEGORIES, generate_cap_task
from .container_setup import get_cap_container_def
from .test_generators import generate_cap_initial_test, generate_cap_final_test

__all__ = [
    "CAP_TASK_CATEGORIES",
    "generate_cap_task",
    "get_cap_container_def",
    "generate_cap_initial_test",
    "generate_cap_final_test",
]
