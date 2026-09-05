"""Time a callable against a latency budget without ever raising on it.

Content-agnostic timing utility: it knows nothing about what `fn` does.
It just measures wall-clock elapsed time with time.perf_counter and
reports whether that elapsed time fit inside a budget. It never raises
because the budget was exceeded -- if `fn` itself raises, that
exception still propagates normally.
"""

from __future__ import annotations

import time
from typing import Any, Callable


def timed_call(fn: Callable[..., Any], *args: Any, budget_ms: float = 400, **kwargs: Any) -> dict:
    """Call fn(*args, **kwargs), timing it, and report against a budget.

    Args:
        fn: The callable to invoke.
        *args: Positional arguments passed through to fn.
        budget_ms: Latency budget in milliseconds. Only used to compute
            within_budget -- never enforced (no timeout, no exception).
        **kwargs: Keyword arguments passed through to fn.

    Returns:
        A dict with exactly the keys:
            result: whatever fn(*args, **kwargs) returned.
            elapsed_ms: float, wall-clock time the call took, in
                milliseconds.
            within_budget: bool, True iff elapsed_ms <= budget_ms.
    """
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    return {
        "result": result,
        "elapsed_ms": elapsed_ms,
        "within_budget": elapsed_ms <= budget_ms,
    }
