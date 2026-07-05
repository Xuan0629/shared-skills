---
verdict: REQUEST_CHANGES
summary: "Requested check passes, but committed pipeline YAML files are unparsable."
findings:
  - severity: blocker
    category: correctness
    summary: ".unison/pipelines/p0.yaml, p1.yaml, and p3.yaml have unescaped nested double quotes in project.test_command, so PyYAML cannot parse those pipeline definitions."
    evidence:
      - ".unison/pipelines/p0.yaml:8"
      - ".unison/pipelines/p1.yaml:8"
      - ".unison/pipelines/p3.yaml:8"
metrics:
  test_command: "python3 sync-skills.py --check 2>&1 | head -5"
  test_exit_code: 0
  test_output:
    - "planning-with-files:"
    - "  hermes: UP-TO-DATE"
    - "  claude: UP-TO-DATE"
    - "  codex: UP-TO-DATE"
    - "  openclaw: UP-TO-DATE"
  additional_checks:
    pipeline_yaml_parse: "3 failed, 1 passed"
---
