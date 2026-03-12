---
name: task-verification
description: Task verification skill that ensures agents actively verify task completion by actually running tests, executing scripts, and validating builds. Use when completing any task that produces code, scripts, or artifacts that need real-world validation. Includes environment assessment and isolation using Python venv, Docker, or Podman to avoid affecting the current environment.
---

# Task Verification

## Overview

This skill ensures that tasks are verified through actual execution, not just code review. It provides:

1. **Script verification** - Execute scripts and verify output
2. **Build verification** - Compile projects and validate success
3. **Environment isolation** - Use venv, Docker, or Podman for safe verification
4. **Environment assessment** - Determine if verification requires isolation

## When to Use This Skill

Use this skill BEFORE claiming any task is complete:

- After generating scripts → Verify they execute correctly
- After code changes → Verify compilation and tests pass
- After configuration changes → Verify configuration is valid
- After building projects → Verify the build succeeds
- Any task with deliverables → Verify deliverables work as expected

## Verification Workflow

### Step 1: Determine Verification Requirements

Based on the task type, identify what needs verification:

| Task Type | Verification Action |
|-----------|---------------------|
| Script generation | Execute script, check output |
| Code changes | Compile, run tests |
| Configuration | Validate syntax, test loading |
| Documentation | Check links, verify formatting |
| Build task | Compile, check artifacts |

### Step 2: Assess Environment Impact

**Critical Question:** Will this verification affect the current environment?

Consider:
- Will it modify files?
- Will it change system state?
- Will it install dependencies?
- Will it consume significant resources?

**If yes → Use isolation (venv/Docker)**
**If no → Can verify directly**

### Step 3: Choose Verification Method

**Method A: Direct Verification**
- For read-only checks (syntax, links, format)
- No isolation needed

**Method B: Python venv**
- For Python scripts and packages
- Isolates Python dependencies

```python
# Create venv
python scripts/manage_venv.py create --type venv --name test-env

# Run verification
python scripts/manage_venv.py run --venv test-env -- python script.py
```

**Method C: Docker/Podman**
- For complex/multi-language projects
- Full environment isolation

```python
# Create container
python scripts/manage_venv.py create --type docker --image python:3.11-slim

# Run verification
python scripts/manage_venv.py run --container <id> -- python script.py
```

## Core Verification Scripts

### 1. Script Verification

Verify scripts are executable and produce expected output:

```python
python scripts/verify_script.py <script_path> \
    --expected-output "expected text" \
    --expected-returncode 0 \
    --json
```

Checks:
- File exists and is executable
- Has valid shebang (if applicable)
- Returns expected exit code
- Produces expected output

### 2. Build Verification

Verify projects compile/build successfully:

```python
python scripts/verify_build.py <project_path> --json
```

Auto-detects project type:
- Node.js (package.json)
- Python (setup.py, pyproject.toml)
- Rust (Cargo.toml)
- Go (go.mod or .go files)
- Make (Makefile)
- CMake (CMakeLists.txt)

### 3. Environment Management

Create and manage isolated environments:

```python
# Detect available tools
python scripts/manage_venv.py detect

# Create environment
python scripts/manage_venv.py create --type venv --name my-env
python scripts/manage_venv.py create --type docker --image ubuntu:22.04

# Run commands
python scripts/manage_venv.py run --venv my-env -- python script.py
python scripts/manage_venv.py run --container <id> -- command

# Cleanup
python scripts/manage_venv.py cleanup --path <venv_path>
```

## Verification Decision Tree

```
Task Complete?
    ↓
What needs verification?
    ├── Script → verify_script.py
    ├── Build → verify_build.py
    └── Other → Custom verification
    ↓
Is environment impact acceptable?
    ├── Yes → Run directly
    └── No → Use isolation
        ├── Python → venv
        ├── Complex → Docker
        └── Rootless → Podman
    ↓
Run verification → Pass? → Claim complete
            ↓ No
        Fix → Re-verify
```

## Environment Assessment Guide

Before verifying, assess the risk level:

**Low Risk (Direct):**
- Static analysis
- Syntax checking
- Read-only operations

**Medium Risk (venv):**
- Python script execution
- Package installation
- File generation in temp directories

**High Risk (Container):**
- System-level changes
- Network services
- Database operations
- Unknown/untrusted code

See [references/environment-assessment.md](references/environment-assessment.md) for detailed guidance.

## Verification Checklist

Before claiming task completion:

- [ ] Identified what needs verification
- [ ] Assessed environment impact
- [ ] Chosen appropriate isolation method (if needed)
- [ ] Executed verification
- [ ] Reviewed verification results
- [ ] Fixed any issues found
- [ ] Re-verified after fixes

## Best Practices

1. **Always verify before claiming completion** - "Should work" is not evidence
2. **Prefer isolation** - Better safe than sorry
3. **Use JSON output** for programmatic result checking
4. **Set timeouts** to prevent hanging
5. **Clean up** environments after verification
6. **Document verification results** in task completion summary

## Common Patterns

### Pattern 1: Simple Script Verification

```python
import subprocess

# Verify script execution
result = subprocess.run(
    ['python', 'scripts/verify_script.py', 'my_script.sh', '--json'],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✓ Script verification passed")
else:
    print("✗ Script verification failed")
    print(result.stdout)
```

### Pattern 2: Build Verification with Isolation

```python
import subprocess
import tempfile
import os

with tempfile.TemporaryDirectory() as tmpdir:
    # Create venv in temp directory
    subprocess.run(['python', '-m', 'venv', f'{tmpdir}/env'])

    # Verify build
    result = subprocess.run(
        ['python', 'scripts/verify_build.py', './my-project', '--json'],
        capture_output=True,
        text=True
    )

# Automatically cleaned up
```

### Pattern 3: Full Container Verification

```python
# Create isolated container
create_result = subprocess.run(
    ['python', 'scripts/manage_venv.py', 'create', '--type', 'docker', '--json'],
    capture_output=True,
    text=True
)

# Parse container ID and run verification
# ... (parse JSON and extract container_id)

# Run verification in container
run_result = subprocess.run(
    ['python', 'scripts/manage_venv.py', 'run', '--container', container_id, '--', 'python', 'verify.py'],
    capture_output=True,
    text=True
)
```

## References

- [Verification Workflows](references/verification-workflows.md) - Detailed workflow guide
- [Environment Assessment](references/environment-assessment.md) - Environment risk assessment guide

## Anti-Patterns

❌ **Don't:**
- Trust code looks correct without running it
- Skip verification "just this once"
- Use production environment for verification
- Ignore warnings from verification tools
- Assume previous success means current success

✅ **Do:**
- Run actual verification commands
- Use isolated environments
- Document verification results
- Re-verify after any changes
- Treat verification as mandatory, not optional
