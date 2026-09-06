from types import SimpleNamespace

import pytest

from academy_tractian.remote_server import _configure_runtime_evaluator


class FakeApp:
    def __init__(
        self,
        *,
        with_supervisor: bool = True,
        remote_production: bool = True,
    ) -> None:
        self.state = SimpleNamespace(remote_production=remote_production)
        if with_supervisor:
            self.state.runtime_handoff_supervisor = SimpleNamespace(evaluator=None)


def test_release0_remote_runtime_uses_traced_provider_evaluation() -> None:
    app = FakeApp()
    _configure_runtime_evaluator(app, provider_calls_enabled=True)

    evaluator = app.state.runtime_handoff_supervisor.evaluator
    assert app.state.production_evaluation_mode == "traced_provider"
    assert evaluator.policy.provider_free is False
    assert evaluator.policy.require_model_call_provenance is True
    assert evaluator.policy.read_only is True


def test_provider_free_remote_runtime_keeps_provider_free_evaluation() -> None:
    app = FakeApp()
    _configure_runtime_evaluator(app, provider_calls_enabled=False)

    evaluator = app.state.runtime_handoff_supervisor.evaluator
    assert app.state.production_evaluation_mode == "provider_free"
    assert evaluator.policy.provider_free is True
    assert evaluator.policy.require_model_call_provenance is False


def test_remote_runtime_fails_closed_without_horizontal_supervisor() -> None:
    app = FakeApp(with_supervisor=False)
    with pytest.raises(RuntimeError, match="remote_runtime_handoff_supervisor_required"):
        _configure_runtime_evaluator(app, provider_calls_enabled=True)


def test_non_remote_composition_double_without_supervisor_is_side_effect_free() -> None:
    app = FakeApp(with_supervisor=False, remote_production=False)

    _configure_runtime_evaluator(app, provider_calls_enabled=True)

    assert not hasattr(app.state, "production_evaluation_mode")
