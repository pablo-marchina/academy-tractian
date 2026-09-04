import pytest

from academy_tractian.decision_source import ProviderDecisionSource
from academy_tractian.hosted_provider import create_hosted_decision_source


@pytest.mark.parametrize(
    ("provider", "expected_model"),
    [("openai", "gpt-5.6-sol"), ("google", "gemini-3.7-flash")],
)
def test_hosted_provider_factory_builds_audited_live_decision_source(
    provider: str,
    expected_model: str,
) -> None:
    source = create_hosted_decision_source(provider=provider, api_key="test-key")

    assert isinstance(source, ProviderDecisionSource)
    assert source.call_identity is not None
    assert source.call_identity.provider_id == provider
    assert source.call_identity.model_id == expected_model
    assert source.call_identity.live_call is True
    assert len(source.registry) == 18
    assert "test-key" not in repr(source.client)


def test_hosted_provider_factory_rejects_unselected_or_local_provider() -> None:
    with pytest.raises(ValueError, match="unsupported_hosted_provider"):
        create_hosted_decision_source(provider="local-ollama", api_key="test-key")
