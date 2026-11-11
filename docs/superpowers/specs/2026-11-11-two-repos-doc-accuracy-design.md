# Two-Repository Documentation Accuracy

## Goal

Make two small documentation improvements without changing runtime behavior,
public APIs, tests, or the original learning project.

## Scope

- In LLMKit's README, state that automatic retries apply to `complete()` and
  not to `stream()`, matching `LLMClient`.
- In SafeDesk's README, explain that environment variables are read when the
  service process starts and show how to clear the variables and return to
  mock mode in PowerShell and Bash.
- Preserve the existing Function Calling roadmap item as unimplemented.

## Verification

- Run the complete pytest suite in each repository.
- Check each diff for whitespace errors and ensure only intended documentation
  files (plus this design record in LLMKit) are changed.
- Commit with the required `phy` identity, push both `main` branches, and verify
  the six-job CI matrix for each pushed commit.

## Constraints

- Do not edit library implementation, public signatures, or test assertions.
- Do not modify or remove the original learning project.
- Do not claim Function Calling is implemented.
