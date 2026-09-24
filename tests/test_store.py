"""Testes do armazenamento (RF-01, RF-03, RF-04, RNF-04). Só dados fictícios."""
import sqlite3
from pathlib import Path

import pytest

from mini_tars.models import AlreadySuperseded, UnknownId
from mini_tars.store import MIGRATIONS, Store


def new_store(tmp_path) -> Store:
    return Store(tmp_path / "memoria.db")


def test_novo_banco_recebe_versao_do_esquema(tmp_path):
    s = new_store(tmp_path)
    s.close()
    v = sqlite3.connect(tmp_path / "memoria.db").execute("PRAGMA user_version").fetchone()[0]
    assert v == max(MIGRATIONS)


def test_fato_sobrevive_a_reiniciar(tmp_path):
    s = new_store(tmp_path)
    fid = s.add("Usamos Postgres.", "2026-03-02", "clinica", "2026-03-02T12:00:00Z")
    s.close()
    s2 = new_store(tmp_path)
    fact = s2.get(fid)
    assert fact is not None and fact.text == "Usamos Postgres." and fact.project == "clinica"


def test_substituir_esconde_o_antigo_e_historico_mostra(tmp_path):
    s = new_store(tmp_path)
    a = s.add("Plano básico: R$ 79.", "2026-06-03", None, "2026-06-03T12:00:00Z")
    b = s.add("Plano básico: R$ 89.", "2026-06-10", None, "2026-06-10T12:00:00Z", supersedes=a)
    assert [f.id for f in s.all()] == [b]
    assert [f.id for f in s.all(include_superseded=True)] == [a, b]
    assert s.get(a).superseded_by == b


def test_cadeia_a_b_c_devolve_so_o_ultimo(tmp_path):
    s = new_store(tmp_path)
    a = s.add("v1", "2026-01-01", None, "t")
    b = s.add("v2", "2026-01-02", None, "t", supersedes=a)
    c = s.add("v3", "2026-01-03", None, "t", supersedes=b)
    assert [f.id for f in s.all()] == [c]


def test_nao_substitui_fato_ja_substituido(tmp_path):
    s = new_store(tmp_path)
    a = s.add("v1", "2026-01-01", None, "t")
    s.add("v2", "2026-01-02", None, "t", supersedes=a)
    with pytest.raises(AlreadySuperseded):
        s.add("v3", "2026-01-03", None, "t", supersedes=a)
    assert len(s.all(include_superseded=True)) == 2  # nada foi gravado na tentativa falha


def test_substituir_id_inexistente_falha_sem_gravar(tmp_path):
    s = new_store(tmp_path)
    with pytest.raises(UnknownId):
        s.add("x", "2026-01-01", None, "t", supersedes=999)
    assert s.all(include_superseded=True) == []


def test_apagar_e_definitivo_no_arquivo(tmp_path):
    s = new_store(tmp_path)
    fid = s.add("Segredo fictício ZEBRA-AZUL-7731 do projeto.", "2026-01-01", None, "t")
    s.delete(fid)
    s.close()
    assert s.path.read_bytes().find(b"ZEBRA-AZUL-7731") == -1
    s2 = new_store(tmp_path)
    assert s2.get(fid) is None


def test_apagar_id_inexistente_da_erro(tmp_path):
    with pytest.raises(UnknownId):
        new_store(tmp_path).delete(42)


def test_apagar_o_substituto_reativa_o_antigo(tmp_path):
    s = new_store(tmp_path)
    a = s.add("v1", "2026-01-01", None, "t")
    b = s.add("v2", "2026-01-02", None, "t", supersedes=a)
    s.delete(b)
    assert [f.id for f in s.all()] == [a]


def test_filtro_por_projeto_e_recentes(tmp_path):
    s = new_store(tmp_path)
    s.add("a", "2026-01-01", "p1", "t1")
    s.add("b", "2026-01-03", "p2", "t2")
    s.add("c", "2026-01-02", "p1", "t3")
    assert [f.text for f in s.recent(10)] == ["b", "c", "a"]
    assert [f.text for f in s.recent(10, "p1")] == ["c", "a"]
    assert [f.text for f in s.all(project="p2")] == ["b"]


def test_limite_de_texto_do_banco(tmp_path):
    s = new_store(tmp_path)
    with pytest.raises(sqlite3.IntegrityError):
        s.add("x" * 2001, "2026-01-01", None, "t")


# --- migrações (RNF-04) -------------------------------------------------
V2 = {**MIGRATIONS, 2: ["ALTER TABLE facts ADD COLUMN extra TEXT"]}


def test_migracao_faz_backup_e_preserva_dados(tmp_path):
    s = new_store(tmp_path)
    fid = s.add("dado antigo", "2026-01-01", None, "t")
    s.close()
    s2 = Store(tmp_path / "memoria.db", migrations=V2)
    assert s2.get(fid).text == "dado antigo"
    assert (tmp_path / "memoria.db.bak-v1").exists()
    v = sqlite3.connect(tmp_path / "memoria.db").execute("PRAGMA user_version").fetchone()[0]
    assert v == 2


def test_migracao_com_falha_restaura_o_original(tmp_path):
    s = new_store(tmp_path)
    fid = s.add("dado antigo", "2026-01-01", None, "t")
    s.close()
    ruim = {**MIGRATIONS, 2: ["ALTER TABLE facts ADD COLUMN ok TEXT", "ISSO NAO E SQL"]}
    with pytest.raises(sqlite3.Error):
        Store(tmp_path / "memoria.db", migrations=ruim)
    s3 = new_store(tmp_path)  # abre normalmente na versão 1
    assert s3.get(fid).text == "dado antigo"
    v = sqlite3.connect(tmp_path / "memoria.db").execute("PRAGMA user_version").fetchone()[0]
    assert v == 1
    cols = [r[1] for r in sqlite3.connect(tmp_path / "memoria.db").execute("PRAGMA table_info(facts)")]
    assert "ok" not in cols


def test_migracao_com_falha_preserva_o_backup(tmp_path):
    s = new_store(tmp_path)
    s.add("dado antigo", "2026-01-01", None, "t")
    s.close()
    ruim = {**MIGRATIONS, 2: ["ISSO NAO E SQL"]}
    with pytest.raises(sqlite3.Error):
        Store(tmp_path / "memoria.db", migrations=ruim)
    assert (tmp_path / "memoria.db.bak-v1").exists()


def test_banco_de_esquema_mais_novo_e_recusado_sem_alterar(tmp_path):
    from mini_tars.models import SchemaTooNew
    s = new_store(tmp_path)
    s.close()
    con = sqlite3.connect(tmp_path / "memoria.db")
    con.execute("PRAGMA user_version = 99")
    con.commit(); con.close()
    antes = (tmp_path / "memoria.db").read_bytes()
    with pytest.raises(SchemaTooNew):
        new_store(tmp_path)
    assert (tmp_path / "memoria.db").read_bytes() == antes


def test_apagar_nao_remove_backups_de_migracao(tmp_path):
    """Limite documentado (RF-04): o backup criado antes de migrar mantém o conteúdo antigo."""
    s = new_store(tmp_path)
    fid = s.add("texto no backup ZEBRA-9911", "2026-01-01", None, "t")
    s.close()
    s2 = Store(tmp_path / "memoria.db", migrations=V2)
    s2.delete(fid)
    s2.close()
    assert b"ZEBRA-9911" in (tmp_path / "memoria.db.bak-v1").read_bytes()
    assert b"ZEBRA-9911" not in (tmp_path / "memoria.db").read_bytes()
