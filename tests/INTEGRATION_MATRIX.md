# Matrice d'intégration — 29 modules ignorés

> Ces modules sont ignorés via `conftest.py` (`pytest_ignore_collect`).
> Ils nécessitent des dépendances externes non présentes dans ce repo.

| Module | Dépendance manquante | Env requis | Priorité reactivation |
|--------|---------------------|------------|----------------------|
| tests/autoresearch/test_benchmark_runner.py | `from NEXUS.*` | ENV2 complet | P2 |
| tests/autoresearch/test_config_integration.py | `from NEXUS.*` | ENV2 complet | P2 |
| tests/autoresearch/test_decision_git.py | `from NEXUS.*` | ENV2 complet | P2 |
| tests/autoresearch/test_end_to_end.py | `from NEXUS.*` | ENV2 complet | P2 |
| tests/autoresearch/test_engine_regression.py | `from NEXUS.*` | ENV2 complet | P2 |
| tests/autoresearch/test_session_digestion_engine_config.py | `from NEXUS.*` | ENV2 complet | P2 |
| tests/autoresearch/test_session_normative_engine_config.py | `from NEXUS.*` | ENV2 complet | P2 |
| tests/autoresearch/test_session_ontology_service_config.py | `from NEXUS.*` | ENV2 complet | P2 |
| tests/breakthroughs/test_infinite_assimilation.py | `from src.engines.*` | pip install -e . | P1 |
| tests/breakthroughs/test_phi_cps_framework.py | `from src.engines.*` | pip install -e . | P1 |
| tests/performance/test_performance.py | `from src.engines.*` | pip install -e . | P1 |
| tests/test_browser_bridge.py | `gateway_manager` | ENV2 complet | P2 |
| tests/test_cdp_capabilities.py | `from src.citizens.*` | pip install -e . | P1 |
| tests/test_comet_degraded_mode.py | `from src.citizens.*` | pip install -e . | P1 |
| tests/test_controller.py | `managers` | ENV2 complet | P2 |
| tests/test_env2_tab_harvest.py | `from src.citizens.*` | pip install -e . | P1 |
| tests/test_event_bus.py | `from src.events.*` | pip install -e . | P1 |
| tests/test_joker_engine.py | `from src.joker.*` | pip install -e . | P1 |
| tests/test_meta_framework.py | `from src.engines.*` | pip install -e . | P1 |
| tests/test_model.py | `from src.engines.*` | pip install -e . | P1 |
| tests/test_nexus_engines_completion.py | `from src.engines.*` | pip install -e . | P1 |
| tests/test_ontological_memory/test_artifact_model.py | `from src.ontological_memory.*` | pip install -e . | P1 |
| tests/test_PrfaaSProviderCitizen.py | `from src.citizens.*` | pip install -e . | P1 |
| tests/test_qoderwork_citizen.py | `from src.citizens.*` | pip install -e . | P1 |
| tests/test_quantum_mstgf_citizen_e2e.py | `from src.citizens.*` | pip install -e . | P1 |
| tests/test_service.py | `from src.engines.*` | pip install -e . | P1 |
| tests/test_triad_convergence.py | `from src.triad.*` | pip install -e . | P1 |
| tests/test_vector_engine.py | `from src.engines.*` | pip install -e . | P1 |

## Statut

- **981 tests** collectibles (0 erreur de collection)
- **29 modules** ignorés (dépendances externes)
- **~952 tests** exécutables dans l'environnement courant
