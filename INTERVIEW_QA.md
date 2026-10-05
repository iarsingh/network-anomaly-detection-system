# network-anomaly-detection-system — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does network-anomaly-detection-system address, and what can you demonstrate?

Score error rate, p95 latency, and unique destinations. At or above 0 is anomalous.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/netanom/main.py`](src/netanom/main.py): Implementation or supporting configuration.
- [`src/netanom/score.py`](src/netanom/score.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/netanom/__init__.py`](src/netanom/__init__.py): Implementation or supporting configuration.
- [`tests/test_score.py`](tests/test_score.py): Executable checks and regression examples.
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml): GitHub Actions job definitions.
- [`README.md`](README.md): Project explanations or operating notes.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `score` and explain the decision it makes?

The main walkthrough here is `score(body)` in [`src/netanom/score.py`](src/netanom/score.py#L11).

```python
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
```

The implementation calls `', '.join`, `InputError`, `WEIGHTS.items`, `isinstance`, `parts.append`, `round`. In an interview, trace those calls in execution order using a fixture input.

## 4. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `HTTPException(status_code=422, detail=str(exc))` in [`src/netanom/main.py`](src/netanom/main.py#L17).
- `InputError('missing ' + ', '.join(missing))` in [`src/netanom/score.py`](src/netanom/score.py#L14).
- `InputError(f'{name} must be a number')` in [`src/netanom/score.py`](src/netanom/score.py#L20).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 5. Which test would you use to demonstrate correctness?

[`tests/test_score.py`](tests/test_score.py#L7) contains `test_high_and_low`:

```python
def test_high_and_low():
    assert client.post("/score", json={'error_rate': 0.4, 'p95_ms': 800, 'unique_dest': 90}).json()["label"]
    high = client.post("/score", json={'error_rate': 0.4, 'p95_ms': 800, 'unique_dest': 90}).json()
    low = client.post("/score", json={'error_rate': 0.01, 'p95_ms': 40, 'unique_dest': 4}).json()
    assert high["label"] != low["label"]
    assert high["score"] > low["score"]
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 6. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/netanom/main.py`](src/netanom/main.py#L8).
- `POST /score` → `post_score` in [`src/netanom/main.py`](src/netanom/main.py#L13).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 7. Where does state live, and what happens with multiple workers?

Module-level containers include `WEIGHTS` in [`src/netanom/score.py`](src/netanom/score.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 8. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 9. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 10. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 11. What is the input-to-output contract of `score`?

In [`src/netanom/score.py`](src/netanom/score.py#L11), `score(body)` receives the inputs. The function computes these intermediate values:

- `missing = [name for name in REQUIRED if name not in body]`
- `total = INTERCEPT`
- `parts = []`
- `label = 'anomaly' if total >= THRESHOLD else 'normal'`

Its result is defined by:

- `{'score': round(total, 4), 'label': label, 'threshold': THRESHOLD, 'parts': parts}`

## 12. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/netanom/score.py`](src/netanom/score.py#L11) branches on:

- `missing`
- `not isinstance(value, (int, float)) or isinstance(value, bool)`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.
