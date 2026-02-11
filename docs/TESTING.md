# Testing Guide

## Why We Test

Tests help us:
- Catch bugs before they hit `main`
- Refactor without fear
- Make PRs easier to review
- Verify edge cases we won't manually test every time

---

## Core Pattern: Arrange → Act → Assert

Every test follows this structure:

```
Arrange  →  Set up input data and dependencies
Act      →  Call the function/render the component
Assert   →  Check the output matches expectations
```

Keep this pattern visible in your tests. It makes them scannable.

---

# Backend Testing

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

---

# Frontend Testing

### What to Test

| Layer | What to Test |
|-------|--------------|
| Hooks | State transitions, API call handling, error states |
| Components | Rendering, user interactions, conditional display |
| Utils | Pure function input/output |

### Test File Location

Place tests in `__tests__/` directory adjacent to source:

```
src/
├── hooks/
│   ├── useAuth.ts
│   └── __tests__/
│       └── useAuth.test.ts
```

### Dependencies

- `jest` - Testing framework
- `jest-expo` - Expo-specific Jest preset
- `@testing-library/react-native` - Testing utilities for React Native
- `@types/jest` - TypeScript types for Jest
- `react-test-renderer`

## Running Tests

```bash
npm test  # all tests

npm run test:watch  # watch mode

npm run test:coverage  # coverage report

npm test -- test.test.tsx  # specific test file
```

## Writing Tests

### Simple Component Tests

For simple components, just mock what you need. Ex:

```typescript
import { render } from "@testing-library/react-native";
import { MyComponent } from "../my-component";

// Mock external deps
jest.mock("@/hooks/use-theme-color", () => ({
  useThemeColor: () => "#000000",
}));

describe("MyComponent", () => {
  it("renders correctly", () => {
    const { getByText } = render(<MyComponent>Hello</MyComponent>);
    expect(getByText("Hello")).toBeTruthy();
  });
});
```

### Hook Tests

```typescript
import { renderHook } from "@testing-library/react-native";
import { useMyHook } from "../use-my-hook";

describe("useMyHook", () => {
  it("returns expected value", () => {
    const { result } = renderHook(() => useMyHook());
    expect(result.current).toBe("expected");
  });
});
```

### Screen Tests

For screens with a lot of dependencies, mock the complex components:

```typescript
jest.mock("expo-router", () => {
  const { View } = require("react-native");
  return {
    Link: ({ children }: any) => <View>{children}</View>,
  };
});

jest.mock("@/components/complex-component", () => ({
  ComplexComponent: ({ children }: any) => {
    const { View } = require("react-native");
    return <View>{children}</View>;
  },
}));
```

## Best Practices

1. **Keep tests simple** - Test component behavior, not implementation
2. **Mock external dependencies** - Expo modules, navigation, images
3. **Use lazy requires in mocks** - `require('react-native')` inside mock factories
4. **Focus on user-visible behavior** - What users see and interact with
5. **Avoid over-mocking** - Only mock what's necessary for the test to run

## Common Issues

### Module Not Found in Mocks

Use `require()` inside mock factories instead of imports to avoid hoisting issues:

```typescript
// do this
jest.mock("my-module", () => ({
  Component: () => {
    const { View } = require("react-native");
    return <View />;
  },
}));

// don't do this
import { View } from "react-native";
jest.mock("my-module", () => ({
  Component: () => <View />,
}));
```

## Checklist

Before opening a PR:
- [ ] `npm test` passes
- [ ] New hooks have success + error tests
- [ ] Interactive components have user event tests
- [ ] Mocks are minimal and documented

## Test Types

**Integration Tests** (`tests/integration/`)
- Test the full stack: router → service → repository → database
- Use real PostgreSQL test database (no mocks)
- Catch SQL errors, constraint violations, real-world bugs
- Each test gets fresh transaction (auto-rolled back after test)

**Unit Tests** (`tests/`)
- Test pure utility functions (password hashing, JWT generation)
- No database needed, very fast
- Keep these minimal - only for standalone utilities

**Write integration tests.** They give you the most confidence!

## Test Database Setup

We use a real PostgreSQL database (not mocks) for integration tests.

**Starting the test database:**
```bash
docker compose up -d test-db
```

**Connection:**
- Inside Docker: `postgresql://test_user:test_password@test-db:5432/test_remetra`
- From local: `postgresql://test_user:test_password@localhost:5433/test_remetra`

**How it works:**
1. `conftest.py` creates all tables at start of test session
2. Each test gets a fresh database transaction
3. Transaction is rolled back after each test (clean slate)
4. Tables are dropped after all tests complete

**You don't need to manually reset data - it's automatic.**

## Creating Test Fixtures

Fixtures are defined in `conftest.py` and available to all tests automatically.

**Example - Sample data fixture:**
```python
@pytest.fixture
def sample_user_data():
    """Reusable test user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "disease": ["lupus"],
        "weight": 150.0
    }
```

**Example - Database session fixture:**
```python
@pytest.fixture(scope="function")
def db_session(db_engine):
    """Fresh database session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()  # Automatic cleanup
    connection.close()
```

**Using fixtures in tests:**
```python
def test_create_user(db_session, sample_user_data):
    # db_session and sample_user_data are injected automatically
    repo = UserRepository()
    user = repo.create(db_session, **sample_user_data)
    assert user.username == sample_user_data["username"]
```

**Fixture scopes:**
- `scope="function"` (default): New fixture for each test
- `scope="session"`: One fixture for entire test run

## Running Tests

**All tests:**
```bash
just test
```

**Integration tests only:**
```bash
docker compose run --rm backend pytest tests/integration/
```

**Unit tests only:**
```bash
docker compose run --rm backend pytest tests/test_*.py
```

**Single test file:**
```bash
docker compose run --rm backend pytest tests/integration/test_auth_integration.py
```

**Single test by name:**
```bash
docker compose run --rm backend pytest -k test_register_user_success
```

**With coverage:**
```bash
docker compose run --rm backend pytest --cov=services --cov-report=term-missing
```