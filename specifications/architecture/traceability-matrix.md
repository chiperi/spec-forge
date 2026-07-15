# Traceability Matrix — spec-forge

Requirement → design/decision → task → test. Nothing gets "lost".

| Requirement | Design / ADR | Task | Test | Status |
|-------------|--------------|------|------|--------|
| FR-001 (scaffold) | plan §4 scaffolder | T-005, T-006 | test_scaffold_creates_bundle | ✅ |
| FR-002 (interview) | plan §4 cli | T-006 | test_init_yes_creates_bundle | ✅ |
| FR-003 (BA spec) | plan §4 personas | T-009, T-010 | test_spec_writes_draft | ✅ |
| FR-007 (stack profiles) | ADR-0001 seams | T-004 | test_init_rejects_unknown_stack | ✅ |
| FR-010 (AI backend) | ADR-0001 | T-008, T-010 | test_get_backend_default_is_mock | ✅ |
| FR-012 (re-spec) | plan §4 respec | T-016 | — | ⬜ |
| US-1 (init) | plan §4 | T-006 | test_init_* | ✅ |
| US-2 (spec) | plan §4 | T-009, T-010 | test_spec_* | ✅ |
| NFR-002/003 (determinism) | plan §7 | T-005 | test_scaffold_is_reproducible / _order | ✅ |
| NFR-004 (guard/idempotent) | plan §7 | T-006 | test_*_guards_existing | ✅ |
| FR-004 (SA plan) | plan §4 personas | T-P1 | test_plan_writes_plan | ✅ |
| FR-005 (tasks) | plan §4 personas | T-P2 | test_tasks_writes_tasks | ✅ |
| FR-006 (quality gates) | plan §7 validators | T-012, T-013 | test_validate_* | ✅ |
| FR-008 (deploy) | plan §4 | T-014 | test_deploy_creates_agents_symlink | ✅ |
| US-3/4/5/6 | plan §4 | T-P1/P2/012-014 | test_cli_phases | ✅ |
| FR-009 (lifecycle gates) | plan §5 state | T-017 | test_state, test_status_reflects_phases | ✅ |
| FR-012 / US-8 (re-spec) | plan §4 respec | T-016 | test_respec_diff_confirm | ✅ |
| FR-013 / US-9 (PDF export) | ADR-0003 | T-019 | test_export_*, test_export_cli_writes_pdf | ✅ |
| FR-014 / US-10 (slash command) | ADR-0004 | T-020 | test_integrations, test_command_install_uninstall_cli | ✅ |
| FR-015 / US-11 (analyze brownfield) | ADR-0005 | T-021 | test_codescan, test_cli_analyze | ✅ |
| FR-016 / US-12 (subcommand dispatcher, native on subscription) | ADR-0006 | T-022, T-026 | test_wrapper_is_subcommand_dispatcher | ✅ |
| FR-017 (install/remove 6 subagents + self-upgrade) | ADR-0006 | T-023, T-026 | test_install_writes_command_and_agents, test_command_self_upgrades_on_old_version, test_bundled_agents_enumeration | ✅ |
| FR-018 / US-13 (`fill` wizard: step-by-step filling + todo checklist) | ADR-0006 | T-029 | test_wrapper_has_fill_wizard | ✅ |

Legend: ✅ covered · 🟡 partial (mock/stub) · ⬜ not yet.
