# Troubleshooting

I came up with a rough list of what issues I think people may commonly run into please feel free to add to it! Hopefully this helps

---

## First checks (do this before anything)

- Is **Docker Desktop running**?
- Are you in the **repo root** (same folder as `docker-compose.yml` and `Justfile`)?
- Did you try:
  - `just down`
  - `just rebuild`
  - then `just dev`

---

## Docker issues

### “Cannot connect to the Docker daemon” / “Docker daemon is not running”
**What it means:** Docker Desktop isn’t running.

**Fix:**
- Open Docker Desktop
- Wait until it says it’s running
- Retry `just dev`

---

### “Port 8000 is already in use”
**What it means:** Something else is using port 8000.

**Fix (recommended):**
```bash
just down
```

---

### “Port 5432 is already in use” (database port)

**What it means:**  
You already have Postgres running locally, or another container is using it.

**Fix:**
```bash
just down
```

If you still get it, ask a TL we can change the local port mapping

---

### Containers start then instantly stop / “Exited (1)”

**What it means:**  
The app crashed on startup.

**Fix:**
```bash
just logs
```

---

### “No space left on device” / Docker taking up too much storage
**Fix:**
- Docker Desktop → Settings → Resources (increase disk if needed)
- Or run Docker cleanup (ask a TL before doing anything crazy tho)

---

### Dependency / Python issues (uv)
#### “uv: command not found”

**Fix:**

- Restart your terminal
- If still broken, reinstall uv (see README-DEV.md)
- Ask a TL if that doesn't work

---

### “Import errors” / red squiggles in VS Code or PyCharm
**Fix:**
* Make sure your interpreter is set to backend/.venv
* Restart your IDE
* If Docker works but the IDE is yelling, it’s annoying but not critical tbh
---

### “CI failed because of linting”

**What it means:**
CI runs ruff and tests on your PR. If ruff fails, the PR can’t merge.

**Fix locally:**

```
just format
just lint #should show you any formatting issues that weren't resolved by just format
just test
```
---

## Git issues

### “Permission denied (publickey)” when cloning or pushing

**What it means:**  
SSH key isn’t set up for GitHub.

**Fix:**
- Use HTTPS clone instead, or set up SSH keys
- Ask a TL if you want help — this is super common

---

### Merge conflicts

**Fix:**
- Don’t panic
- Ask a TL to walk through it the first time
- Conflicts are normal in team repos

---

## If you’re stuck

Ask for help ‼️‼️‼️

