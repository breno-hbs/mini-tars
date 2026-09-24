"""Configuração por variáveis de ambiente. Nenhum segredo em arquivo do repositório (RF-10)."""
import os
import sys
from dataclasses import dataclass
from pathlib import Path

LOCAL_HOSTS = ("127.0.0.1", "localhost", "::1")


def default_data_dir() -> Path:
    """Diretório de dados do usuário, por sistema operacional."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "mini-tars"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "mini-tars"
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / "mini-tars"


@dataclass(frozen=True)
class Config:
    db_path: Path
    host: str = "127.0.0.1"
    port: int = 8765
    token: str | None = None

    @property
    def is_local_host(self) -> bool:
        return self.host in LOCAL_HOSTS

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Config":
        env = os.environ if env is None else env
        db = env.get("MINI_TARS_DB")
        return cls(
            db_path=Path(db) if db else default_data_dir() / "memory.db",
            host=env.get("MINI_TARS_HOST", "127.0.0.1"),
            port=int(env.get("MINI_TARS_PORT", "8765")),
            token=env.get("MINI_TARS_TOKEN") or None,
        )
