REQUIRED = ("error_rate", "p95_ms", "unique_dest",)
WEIGHTS = {"error_rate": 8.0, "p95_ms": 0.02, "unique_dest": 0.1}
INTERCEPT = -4.0
THRESHOLD = 0.0


class InputError(ValueError):
    pass


def score(body):
    missing = [name for name in REQUIRED if name not in body]
    if missing:
        raise InputError("missing " + ", ".join(missing))
    total = INTERCEPT
    parts = []
    for name, weight in WEIGHTS.items():
        value = body[name]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise InputError(f"{name} must be a number")
        contrib = weight * value
        total += contrib
        parts.append({"feature": name, "contribution": round(contrib, 4)})
    label = "anomaly" if total >= THRESHOLD else "normal"
    return {"score": round(total, 4), "label": label, "threshold": THRESHOLD, "parts": parts}
