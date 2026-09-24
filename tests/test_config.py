from pathlib import Path

from mini_tars.config import Config


def test_padrao_e_local_e_sem_token():
    cfg = Config.from_env({})
    assert cfg.host == "127.0.0.1" and cfg.is_local_host and cfg.token is None
    assert cfg.db_path.name == "memory.db"


def test_variaveis_de_ambiente():
    cfg = Config.from_env({"MINI_TARS_DB": "/tmp/x.db", "MINI_TARS_HOST": "0.0.0.0",
                           "MINI_TARS_PORT": "9000", "MINI_TARS_TOKEN": "abc"})
    assert cfg.db_path == Path("/tmp/x.db") and not cfg.is_local_host
    assert cfg.port == 9000 and cfg.token == "abc"


def test_token_vazio_conta_como_ausente():
    assert Config.from_env({"MINI_TARS_TOKEN": ""}).token is None
