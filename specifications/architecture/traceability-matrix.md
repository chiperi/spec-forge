# Traceability Matrix — spec-forge

Вимога → дизайн/рішення → задача → тест. Ніщо не «загубилось».

| Requirement | Design / ADR | Task | Test | Status |
|-------------|--------------|------|------|--------|
| FR-001 (scaffold) | plan §4 scaffolder | T-005, T-006 | test_scaffold_creates_bundle | ✅ |
| FR-002 (interview) | plan §4 cli | T-006 | test_init_yes_creates_bundle | ✅ |
| FR-003 (BA spec) | plan §4 personas | T-009, T-010 | test_spec_mock_writes_draft | ✅ (claude+mock) |
| FR-007 (stack profiles) | ADR-0001 seams | T-004 | test_init_rejects_unknown_stack | ✅ |
| FR-010 (AI backend) | ADR-0001, ADR-0002 | T-008, T-010 | test_get_backend_claude_default_model | ✅ |
| FR-012 (re-spec) | plan §4 respec | T-016 | — | ⬜ |
| US-1 (init) | plan §4 | T-006 | test_init_* | ✅ |
| US-2 (spec) | plan §4 | T-009, T-010 | test_spec_* | ✅ (claude+mock) |
| NFR-002/003 (детермінізм) | plan §7 | T-005 | test_scaffold_is_reproducible / _order | ✅ |
| NFR-004 (guard/idempotent) | plan §7 | T-006 | test_*_guards_existing | ✅ |
| FR-004 (SA plan) | plan §4 personas | T-P1 | test_plan_writes_plan | ✅ (mock+claude) |
| FR-005 (tasks) | plan §4 personas | T-P2 | test_tasks_writes_tasks | ✅ (mock+claude) |
| FR-006 (quality gates) | plan §7 validators | T-012, T-013 | test_validate_* | ✅ |
| FR-008 (deploy) | plan §4 | T-014 | test_deploy_creates_agents_symlink | ✅ |
| US-3/4/5/6 | plan §4 | T-P1/P2/012-014 | test_cli_phases | ✅ |
| FR-009 (lifecycle gates) | plan §5 state | T-017 | test_state, test_status_reflects_phases | ✅ |
| FR-012 / US-8 (re-spec) | plan §4 respec | T-016 | test_respec_diff_confirm | ✅ |
| FR-013 / US-9 (PDF export) | ADR-0003 | T-019 | test_export_*, test_export_cli_writes_pdf | ✅ |
| FR-014 / US-10 (slash-команда) | ADR-0004 | T-020 | test_integrations, test_command_install_uninstall_cli | ✅ |
| FR-015 / US-11 (analyze brownfield) | ADR-0005 | T-021 | test_codescan, test_cli_analyze | ✅ |

Легенда: ✅ покрито · 🟡 частково (mock/stub) · ⬜ ще ні.
