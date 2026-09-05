from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
    CLOUDFLARE_PROVIDER_ID,
    CLOUDFLARE_ROUTE_ID,
)
from .google_interactions_provider_client import (
    GOOGLE_37_MODEL_ID,
    GOOGLE_38_MODEL_ID,
    GOOGLE_HOSTED_PROVIDER_ID,
    GOOGLE_INTERACTIONS_ROUTE_ID,
)
from .groq_provider_client import GROQ_MODEL_ID, GROQ_PROVIDER_ID, GROQ_ROUTE_ID
from .provider_clients import OPENAI_MODEL_ID, OPENAI_PROVIDER_ID, OPENAI_ROUTE_ID


Maturity = Literal["ga", "beta", "preview"]


@dataclass(frozen=True)
class HostedCandidateSpec:
    provider_id: str
    model_id: str
    route_id: str
    api_key_environment: str
    model_maturity: Maturity
    api_maturity: Maturity
    account_id_environment: str | None = None

    @property
    def candidate_id(self) -> str:
        return f"{self.provider_id}:{self.model_id}"


HOSTED_CANDIDATE_SPECS = (
    HostedCandidateSpec(
        provider_id=OPENAI_PROVIDER_ID,
        model_id=OPENAI_MODEL_ID,
        route_id=OPENAI_ROUTE_ID,
        api_key_environment="OPENAI_API_KEY",
        model_maturity="ga",
        api_maturity="ga",
    ),
    HostedCandidateSpec(
        provider_id=GOOGLE_HOSTED_PROVIDER_ID,
        model_id=GOOGLE_37_MODEL_ID,
        route_id=GOOGLE_INTERACTIONS_ROUTE_ID,
        api_key_environment="GOOGLE_API_KEY",
        model_maturity="ga",
        api_maturity="ga",
    ),
    HostedCandidateSpec(
        provider_id=GOOGLE_HOSTED_PROVIDER_ID,
        model_id=GOOGLE_38_MODEL_ID,
        route_id=GOOGLE_INTERACTIONS_ROUTE_ID,
        api_key_environment="GOOGLE_API_KEY",
        model_maturity="ga",
        api_maturity="ga",
    ),
    HostedCandidateSpec(
        provider_id=GROQ_PROVIDER_ID,
        model_id=GROQ_MODEL_ID,
        route_id=GROQ_ROUTE_ID,
        api_key_environment="GROQ_API_KEY",
        model_maturity="ga",
        api_maturity="ga",
    ),
    HostedCandidateSpec(
        provider_id=CLOUDFLARE_PROVIDER_ID,
        model_id=CLOUDFLARE_GLM_MODEL_ID,
        route_id=CLOUDFLARE_ROUTE_ID,
        api_key_environment="CLOUDFLARE_API_TOKEN",
        account_id_environment="CLOUDFLARE_ACCOUNT_ID",
        model_maturity="ga",
        api_maturity="ga",
    ),
    HostedCandidateSpec(
        provider_id=CLOUDFLARE_PROVIDER_ID,
        model_id=CLOUDFLARE_NEMOTRON_MODEL_ID,
        route_id=CLOUDFLARE_ROUTE_ID,
        api_key_environment="CLOUDFLARE_API_TOKEN",
        account_id_environment="CLOUDFLARE_ACCOUNT_ID",
        model_maturity="ga",
        api_maturity="ga",
    ),
)

HOSTED_CANDIDATES_BY_PAIR = {
    (spec.provider_id, spec.model_id): spec for spec in HOSTED_CANDIDATE_SPECS
}
HOSTED_CANDIDATES_BY_ID = {spec.candidate_id: spec for spec in HOSTED_CANDIDATE_SPECS}
SUPPORTED_HOSTED_PROVIDERS = frozenset(spec.provider_id for spec in HOSTED_CANDIDATE_SPECS)

if len(HOSTED_CANDIDATES_BY_PAIR) != len(HOSTED_CANDIDATE_SPECS):
    raise RuntimeError("duplicate_hosted_candidate_pair")
if len(HOSTED_CANDIDATES_BY_ID) != len(HOSTED_CANDIDATE_SPECS):
    raise RuntimeError("duplicate_hosted_candidate_id")


def resolve_hosted_candidate(provider: str, model: str) -> HostedCandidateSpec:
    key = (provider.strip().lower(), model.strip())
    try:
        return HOSTED_CANDIDATES_BY_PAIR[key]
    except KeyError:
        raise ValueError("unsupported_hosted_candidate") from None
