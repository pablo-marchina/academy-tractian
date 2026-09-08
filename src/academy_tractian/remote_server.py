from __future__ import annotations

from fastapi import FastAPI


def app_factory() -> FastAPI:
    from scripts.research.run_provider_tournament_v3_immediate import main as run_immediate_tournament

    exit_code = run_immediate_tournament()
    app = FastAPI(title="DP-004 Immediate Provider Tournament")
    app.state.tournament_exit_code = exit_code

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok" if exit_code == 0 else "blocked",
            "tournament_exit_code": exit_code,
            "purpose": "DP-004-provider-tournament-v3-immediate-single-day-v2",
        }

    return app


def main() -> None:
    import os
    import uvicorn

    uvicorn.run(
        app_factory,
        factory=True,
        host=os.environ.get("ACADEMY_BIND_HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", os.environ.get("ACADEMY_PORT", "8000"))),
        log_level=os.environ.get("ACADEMY_LOG_LEVEL", "info"),
        proxy_headers=True,
        forwarded_allow_ips=os.environ.get("ACADEMY_FORWARDED_ALLOW_IPS", "127.0.0.1"),
    )


if __name__ == "__main__":
    main()
