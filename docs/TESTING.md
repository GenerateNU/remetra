# Testing

If you're new to unit-testing or haven't tested code in a bit this should help you 🙏

---

## Why we test

Tests help us:
- catch bugs before they hit `main` 😬😬😬
- refactor without fear 
- make PRs easier to review 
- verify edge cases that we may not manually test every time

---

## What we test (priority order)

**1) Service layer (most important)**
- services contain the “thinking” (rules, validation, calculations)
- easiest place to test without HTTP noise

**2) Repository layer (when needed)**
- DB queries, inserts, edge cases
- not every repo method needs a test immediately, but anything tricky should

**3) Routers (least important)**
- router tests are usually for “does this endpoint wire up correctly?”
- we don’t want a huge amount of router-only tests unless there’s a reason 
  - maybe for routers with different error responses and handling

---

## Where tests live

All tests go in:
```
backend/tests/
```

Conventions:
- files: `test_*.py`
- functions: `def test_*():`
- pytest auto-discovers them

We also keep:
- `tests/examples/` for reference patterns (copy these)

---

## Running tests

From repo root:

```
just test
```

Or manually:

```
docker compose run --rm backend pytest
```

Run a single file:

```
docker compose run --rm backend pytest tests/examples/test_example.py
```

Run a single test (by name):

```
docker compose run --rm backend pytest -k create_order_success
```

## The pattern we want (what our example file shows)

### Arrange → Act → Assert

Basic flow:
- **Arrange:** set up input data
- **Act:** call the function you’re testing
- **Assert:** check the output is what you expect

---

## Fixtures (aka reusable setup)

Fixtures are how we avoid copy/pasting setup code everywhere.

In your example:
- `chocolate_service()` gives a fresh `ChocolateService` each test
- `reset_data(autouse=True)` resets in-memory state before every test so tests don’t mess with each other

---

## Testing error cases

We want tests for:
- success case ✅
- expected failure case ✅ (bad input, duplicates, insufficient stock, etc.)

Use:

```py
with pytest.raises(ValueError):
    ...
```
and (ideally) assert part of the message so we know it failed for the right reason.

## Async tests

If the function is async, mark the test:

```py
@pytest.mark.asyncio
async def test_something():
    ...
```

## What to assert (keep it simple)

Assert the stuff that matters:
- key fields exist
- values are correct
- side effects happened (ex: stock decreased, record created)
- error thrown when it should

Don’t assert every field just because it exists.

---

## Common mistakes (pls avoid)

- **Not resetting shared state**  
  if you mutate global/in-memory stuff, reset it (fixture)

- **Testing routers instead of services**  
  services are where the value is

- **Giant test setups**  
  if it’s getting huge, turn it into a fixture/helper

---

## Checklist

Before you open a PR:
- [ ] `just test` passes
- [ ] New logic has at least 1–2 service tests
- [ ] You tested at least one error case (when relevant)
- [ ] Tests don’t rely on test order

---

## Reference

Look at `tests/examples/` for the style we want. It shows:
- fixtures
- Arrange/Act/Assert
- testing success + failure
- async tests

If you’re unsure what to test or how much to test, ask a TL‼️‼️‼️‼️
