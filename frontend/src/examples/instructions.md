# Running Example Code

## Backend

Add the example router to `main.py`:
```python
from examples.example_router import router as chocolate_router

app.include_router(chocolate_router)
```

## Frontend

1. Create a `.env` file in the frontend root:
```
EXPO_PUBLIC_API_URL=http://0.0.0.0:8000
```

2. Update the import in `App.tsx`:
```typescript
import { RootNavigator } from "./src/examples/RootNavigator";