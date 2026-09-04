from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .oidc_runtime_identity import OIDCClaimMapping


@dataclass(frozen=True)
class OIDCCandidateProfile:
    """Non-secret claim contract for a hosted identity pilot candidate.

    A profile does not select a vendor. It only freezes the claim mapping and algorithm surface that
    must be proven by a live token before the candidate can be promoted.
    """

    candidate_id: str
    algorithms: tuple[str, ...]
    organization_claim: str
    role_claim: str
    permissions_claim: str
    identity_claim: str
    max_token_ttl_seconds: int
    required_custom_claims: tuple[str, ...] = ()

    def claim_mapping(self) -> OIDCClaimMapping:
        return OIDCClaimMapping(
            organization_claim=self.organization_claim,
            role_claim=self.role_claim,
            permissions_claim=self.permissions_claim,
            identity_claim=self.identity_claim,
            required_claims=self.required_custom_claims,
        )

    def environment_overrides(self) -> Mapping[str, str]:
        """Return only public claim/algorithm configuration; never issuer secrets or credentials."""

        return {
            "ACADEMY_OIDC_ALGORITHMS": ",".join(self.algorithms),
            "ACADEMY_OIDC_ORGANIZATION_CLAIM": self.organization_claim,
            "ACADEMY_OIDC_ROLE_CLAIM": self.role_claim,
            "ACADEMY_OIDC_PERMISSIONS_CLAIM": self.permissions_claim,
            "ACADEMY_OIDC_IDENTITY_CLAIM": self.identity_claim,
            "ACADEMY_OIDC_REQUIRED_CLAIMS": ",".join(self.required_custom_claims),
        }


AUTH0_PILOT_PROFILE = OIDCCandidateProfile(
    candidate_id="auth0-free",
    algorithms=("RS256",),
    organization_claim="org_id",
    role_claim="https://academy.tractian/role",
    permissions_claim="permissions",
    identity_claim="sub",
    max_token_ttl_seconds=3600,
    required_custom_claims=("https://academy.tractian/role",),
)


OIDC_PILOT_PROFILES = {AUTH0_PILOT_PROFILE.candidate_id: AUTH0_PILOT_PROFILE}


def resolve_oidc_pilot_profile(candidate_id: str) -> OIDCCandidateProfile:
    try:
        return OIDC_PILOT_PROFILES[candidate_id.strip().lower()]
    except KeyError:
        raise ValueError("unsupported_oidc_pilot_candidate") from None
