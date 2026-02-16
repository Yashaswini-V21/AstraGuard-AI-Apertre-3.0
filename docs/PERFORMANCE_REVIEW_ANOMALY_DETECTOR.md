# Performance Review: anomaly_detector.py

**Issue:** #26 — Optimization: Performance Review for anomaly_detector.py  
**Date:** 2025  
**Scope:** `src/anomaly/anomaly_detector.py`

---

## Summary of Findings

### 1. Resource check blocking the hot path (~100ms per call)

**Location:** `detect_anomaly()` → `resource_monitor.check_resource_health()`

**Problem:** On every `detect_anomaly()` call, `check_resource_health()` is invoked. This internally calls `get_current_metrics()`, which uses `psutil.cpu_percent(interval=0.1)`. That call blocks for 100ms to measure CPU usage. When resources are critical, the code only logs a warning and proceeds—no behavior change.

**Impact:** Adds ~100ms latency per detection, dominating typical model prediction time for small models.

---

### 2. Sequential model predict + score_samples

**Location:** `detect_anomaly()` model-based path (lines ~554–565)

**Problem:** `_MODEL.predict([features])` and `_MODEL.score_samples([features])` run sequentially via two `asyncio.to_thread` calls. Both operate on the same feature vector and are independent. Sklearn models (e.g. IsolationForest) generally release the GIL and are safe to call from separate threads for different invocations.

**Impact:** Doubles the effective CPU-bound wait time for model inference when both predict and score_samples are used.

---

### 3. Bug: undefined variable in resource warning

**Location:** Lines 369–376 (before fix)

**Problem:** `if resource_status['overall'] == 'critical':` triggers a `logger.warning()` that references `e`, which is not defined in that scope, causing `NameError` when resources are critical.

---

### 4. Bug: missing `List` import

**Location:** Line 411 (before fix)

**Problem:** `features: List[float] = [...]` uses `List` without importing it from `typing`, causing `NameError` at runtime.

---

### 5. Feature type consistency

**Location:** Feature preparation for model input

**Problem:** Raw `data.get(...)` values may not be floats; `abs(data.get("gyro", 0.0))` can raise `TypeError` for non-numeric values. Heuristic path already uses `float()` conversion.

---

## Async/Await Assessment

- **Model load:** Already uses `asyncio.to_thread` for `pickle.load`.
- **Model predict/score_samples:** Uses `asyncio.to_thread` but was sequential; now parallelized with `asyncio.gather`.
- **Resource check:** Was sync and blocking. Now offloaded to thread pool and cached.
- **I/O:** No disk/network I/O in the detection hot path except during model load (once).
- **Conclusion:** Async/await is used appropriately; the main gains come from avoiding blocking calls and parallelizing independent work, not from adding more async.

---

## Optimizations Applied

### 1. Cached, non-blocking resource status

- Introduced `_get_resource_status_cached()`:
  - Runs `check_resource_health()` via `asyncio.to_thread` so it doesn’t block the event loop.
  - Caches result for 3 seconds (`_RESOURCE_CACHE_TTL`).
- **Effect:** First call in a 3s window pays the ~100ms cost in a thread; subsequent calls use the cache and skip the check. Event loop stays responsive.

### 2. Parallel predict + score_samples

- When `score_samples` exists, both calls run concurrently via `asyncio.gather()`.
- **Effect:** Prediction latency drops to roughly the maximum of predict and score_samples instead of their sum.

### 3. Bug fixes

- Corrected undefined `e` in resource-critical warning.
- Added `List` to typing imports.
- Used `float()` for feature values to avoid `TypeError`.

---

## Benchmarking

### How to run benchmarks

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"  # or equivalent on Windows
python -m tests.benchmarks.benchmark_anomaly_detector
```

**Requirements:** Project dependencies installed (e.g. redis, numpy, scikit-learn, psutil).

### Expected impact (by call type)

| Scenario | Before (approx) | After (approx) |
|----------|-----------------|----------------|
| Model path, first call in 3s window | ~100ms resource + ~Xms predict + ~Yms score | ~max(100ms in thread, X, Y) |
| Model path, cached resource | ~100ms + X + Y | ~max(X, Y) |
| Heuristic path | ~100ms resource | ~0ms (cached) |

The benchmark script (`tests/benchmarks/benchmark_anomaly_detector.py`) was updated to print avg, min, max, P95 latency and total time.

---

## Recommendations for Future Work

1. **Resource monitor:** Add a “quick” mode using `psutil.cpu_percent(interval=0)` for lower latency when full accuracy is not required.
2. **Profiling:** Use `cProfile` or `py-spy` on a representative workload to confirm hotspots.
3. **Batch detection:** If multiple samples need to be scored, consider batch `predict` / `score_samples` instead of per-sample calls.
