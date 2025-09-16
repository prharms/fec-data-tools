from __future__ import annotations

import os
from pathlib import Path


def pytest_sessionfinish(session, exitstatus):  # type: ignore[no-untyped-def]
    """Enforce per-file coverage ≥ 80% for fec_formatter/*.

    Relies on pytest-cov; if missing, does nothing.
    """
    plug = session.config.pluginmanager.getplugin("_cov")
    if not plug or not hasattr(plug, "cov_controller"):
        return
    cov = plug.cov_controller.cov
    if not cov:
        return

    # Ensure data saved
    try:
        cov.stop()
    except Exception:
        pass
    try:
        cov.save()
    except Exception:
        pass

    data = cov.get_data()
    threshold = float(os.getenv("PER_FILE_COVERAGE", "80"))

    failures = []
    for filename in data.measured_files():
        if ("fec_formatter" not in filename) or filename.endswith("__init__.py"):
            continue
        try:
            analysis = cov._analyze(filename)  # private API but commonly used
            total = analysis.numbers.n_statements
            missing = analysis.numbers.n_missing
        except Exception:
            continue
        if total == 0:
            continue
        pct = 100.0 * (total - missing) / total
        if pct + 1e-9 < threshold:
            failures.append((filename, pct))

    if failures:
        print("[ERROR] Per-file coverage below threshold:")
        for f, pct in failures:
            print(f" - {f}: {pct:.1f}% (< {threshold:.0f}%)")
        session.exitstatus = 1


