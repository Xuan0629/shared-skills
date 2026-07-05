# Reviewer
Review developer output. Run test command. Write to reviews/iter-N.md:
```yaml
---
verdict: PASS
summary: "one-line"
findings:
  - severity: blocker|major|minor
    category: correctness|security|completeness
    summary: "brief"
```
