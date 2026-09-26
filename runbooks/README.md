# Runbooks

Same steps as the TypeScript harness workshop. Claude is the model. Python is the language.

| Step | Branch | Topic |
|---|---|---|
| 00 | `start` | Setup |
| 01 | `step-01-model` | One request |
| 02 | `step-02-messages` | Messages |
| 03 | `step-03-function` | `run_agent` |
| 04 | `step-04-tools` | Tool schemas |
| 05 | `step-05-call` | Send tools |
| 06 | `step-06-execute` | Run tools |
| 07 | `step-07-history` | History |
| 08 | `step-08-loop` | Loop |
| 09 | `step-09-retry` | Retry |
| 10 | `step-10-context` | Project context |
| 11 | `step-11-skills` | Skills |
| 12 | `step-12-guard` | Write guard |

`main` matches step 12. `STEP` in the repo root is the checkpoint number. `pytest` skips tests from later steps.

Start at [00. Setup](00-start.md).
