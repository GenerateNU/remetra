# Architecture Overview

Quick note before anything else:

We’re throwing a *lot* of information at you at once — new concepts, new tech, new patterns.  
It is **not expected** that this all makes sense right away. If even ~10% clicks at first, that’s totally fine.

The goal of this doc is just to give you a **high-level mental model** of how things are structured.  
You’ll build real understanding by working on tickets and asking questions ‼️‼️‼️ (please do).

---
# Backend Architecture

## High-Level Idea

Remetra’s backend follows a **layered (N-tier) architecture**.

Most requests flow like this:

Client → Router → Service → Repository → Database


You don’t need to memorize this — you’ll see the pattern everywhere.

---

## What Each Layer Does

### Routers (API layer)
- Define API endpoints (`GET /health`, `POST /symptoms`, etc.)
- Handle HTTP stuff (requests, responses, status codes)
- Call the service layer

They should **not**:
- Contain business logic  
- Talk directly to the database  

---

### Services (business logic)
- Where most of the “thinking” happens
- Apply rules, validation, and transformations
- Coordinate multiple operations
- Call repositories when data is needed

If you’re unsure where code should live, it usually belongs here.

---

### Repositories (data access)
- Handle database reads and writes
- Hide database details from the rest of the app

Think of these as a clean interface between Python code and the DB.

---

### Database
- Stores persistent data
- Other layers don’t need to know how it’s implemented

---

## Folder Mapping

How this shows up in `backend/`:

```
backend/
├── routers/ # API endpoints
├── services/ # Business logic
├── repositories/ # Database access
├── models/ # Pydantic / DB models
├── examples/ # Reference code (start here)
└── tests/ # Tests

```

If you’re ever confused, check `examples/` or ask us!

---

## Dependency Rule (Important)

Dependencies should only flow **downward**:

router → service → repository → database

Avoid:
- Repositories importing services  
- Services importing routers  
- Routers talking directly to the database  

If you’re unsure whether something breaks this rule, just ask.

---

## Example Request Flow

Rough idea of what happens when a request comes in:

1. Router receives the request  
2. Router calls a service function  
3. Service applies logic and calls a repository  
4. Repository talks to the database  
5. Result flows back up and returns a response  

You’ll see this pattern everywhere.

---

# Frontend Architecture

## High-Level Idea

The frontend follows an **MVVM-lite** pattern adapted for React Native.

Most user interactions flow like this:

```
User → Screen (View) → Hook (ViewModel) → API Layer (Model)
```

---

## What Each Layer Does

### Screens (View)
- Render UI based on data from hooks
- Handle user gestures (press, scroll, etc.)
- Should be "dumb" — minimal logic, mostly JSX

They should **not**:
- Contain business logic
- Make API calls directly
- Manage complex state internally

---

### Hooks (ViewModel)
- Where most of the "thinking" happens
- Manage local state (loading, error, data)
- Call the API layer
- Return everything the screen needs to render

Named like `useUsers`, `useAuth`, `useSymptoms`, etc.

If you're unsure where code should live, it usually belongs here.

---

### API Layer (Model)
- Axios client configuration
- Endpoint functions that talk to the backend
- Type definitions for request/response data

Think of this as a clean interface between the app and the server.

---

### Store (Global State)
- Zustand stores for state that multiple screens need
- Auth tokens, user info, app-wide settings
- Not every piece of state belongs here — prefer hooks for screen-specific data

---

## Folder Mapping

How this shows up in `frontend/`:

```
frontend/src/
├── api/           # Axios client + endpoint functions
├── assets/        # pngs, images, etc
├── components/    # Reusable UI pieces
├── hooks/         # Custom hooks ("ViewModels")
├── navigation/    # React Navigation setup
├── screens/       # Screen components ("Views")
├── store/         # Zustand stores (global state)
└── types/         # TypeScript types
```

---

## Dependency Rule (Important)

Dependencies should only flow **downward**:

```
screen → hook → api
           ↘ store (when needed)
```

Avoid:
- API layer importing hooks
- Hooks importing screens
- Screens making fetch calls directly

---

## Example Interaction Flow

Rough idea of what happens when a user taps a button:

1. Screen receives the tap event
2. Screen calls a function from its hook (`fetchUsers()`)
3. Hook sets loading state, calls the API layer
4. API layer makes the request to the backend
5. Hook receives data, updates state
6. Screen re-renders with new data

You'll see this pattern everywhere.

---

## Quick Comparison

| Backend | Frontend | Role |
|---------|----------|------|
| Router | Screen | Entry point, handles I/O |
| Service | Hook | Business logic, coordination |
| Repository | API Layer | Data access |
| Database | Backend API | Persistent storage |

The mental model is the same — just different tech.

---

## Final Notes

If this feels overwhelming, that’s normal. You’re not expected to understand all of this immediately.

Understanding comes from:
- Reading example code  
- Working on small pieces  
- Asking questions ‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️

This doc is just here to give you a map — not to test you.