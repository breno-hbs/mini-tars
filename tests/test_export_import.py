"""Testes de exportar e importar (RF-08). Só dados fictícios."""
import json

import pytest

from mini_tars.export_import import EXPORT_VERSION, export_to_file, import_from_file
from mini_tars.models import DatabaseNotEmpty, InvalidExportFile, UnknownExportVersion
from mini_tars.service import Service
from mini_tars.store import Store


def make(tmp_path, nome="m.db"):
    return Service(Store(tmp_path / nome))


def test_exportar_e_importar_em_banco_vazio_reproduz_o_mesmo_conteudo(tmp_path):
    origem = make(tmp_path, "origem.db")
    a = origem.remember("preço do plano: R$ 79", date="2026-01-01", project="vendas")
    b = origem.remember("preço do plano: R$ 89", date="2026-03-01", supersedes=a)
    origem.remember("fato sem projeto nem substituição")

    arquivo = tmp_path / "saida.json"
    n = export_to_file(origem, arquivo)
    assert n == 3

    destino = make(tmp_path, "destino.db")
    m = import_from_file(destino, arquivo)
    assert m == 3

    originais = {f.id: f for f in origem.export_all()}
    importados = {f.id: f for f in destino.export_all()}
    assert originais == importados
    # A substituição foi preservada: a busca padrão só devolve o fato novo (b)
    resultado = destino.search("preço do plano")
    assert [f.id for f, _ in resultado] == [b]


def test_arquivo_bem_formado(tmp_path):
    svc = make(tmp_path)
    svc.remember("um fato qualquer")
    arquivo = tmp_path / "saida.json"
    export_to_file(svc, arquivo)
    data = json.loads(arquivo.read_text(encoding="utf-8"))
    assert data["schema_version"] == EXPORT_VERSION
    assert data["facts"][0]["text"] == "um fato qualquer"


def test_importar_em_banco_nao_vazio_e_recusado(tmp_path):
    origem = make(tmp_path, "origem.db")
    origem.remember("fato")
    arquivo = tmp_path / "saida.json"
    export_to_file(origem, arquivo)

    destino = make(tmp_path, "destino.db")
    destino.remember("já tinha algo aqui")
    with pytest.raises(DatabaseNotEmpty):
        import_from_file(destino, arquivo)


def test_versao_desconhecida_falha_com_aviso(tmp_path):
    destino = make(tmp_path)
    arquivo = tmp_path / "velho.json"
    arquivo.write_text(json.dumps({"schema_version": 999, "facts": []}), encoding="utf-8")
    with pytest.raises(UnknownExportVersion):
        import_from_file(destino, arquivo)
    assert destino.list_recent() == []  # nada foi alterado


def test_arquivo_sem_versao_ou_nao_json_falha_com_aviso(tmp_path):
    destino = make(tmp_path)
    sem_versao = tmp_path / "sem_versao.json"
    sem_versao.write_text(json.dumps({"facts": []}), encoding="utf-8")
    with pytest.raises(UnknownExportVersion):
        import_from_file(destino, sem_versao)

    nao_json = tmp_path / "nao_json.json"
    nao_json.write_text("isto não é json{{{", encoding="utf-8")
    with pytest.raises(UnknownExportVersion):
        import_from_file(destino, nao_json)


def test_fato_malformado_falha_com_invalid_export_file(tmp_path):
    destino = make(tmp_path)
    arquivo = tmp_path / "malformado.json"
    arquivo.write_text(json.dumps({"schema_version": EXPORT_VERSION, "facts": [{"id": 1}]}), encoding="utf-8")
    with pytest.raises(InvalidExportFile):
        import_from_file(destino, arquivo)

    sem_lista = tmp_path / "sem_lista.json"
    sem_lista.write_text(json.dumps({"schema_version": EXPORT_VERSION, "facts": "não é lista"}), encoding="utf-8")
    with pytest.raises(InvalidExportFile):
        import_from_file(destino, sem_lista)


def _arquivo(tmp_path, facts, nome="entrada.json"):
    arquivo = tmp_path / nome
    arquivo.write_text(json.dumps({"schema_version": EXPORT_VERSION, "facts": facts}), encoding="utf-8")
    return arquivo


def _fato(id, text="fato fictício", date="2026-01-01", project=None, created_at="2026-01-01T00:00:00Z",
          superseded_by=None):
    return {"id": id, "text": text, "date": date, "project": project, "created_at": created_at,
            "superseded_by": superseded_by}


def test_id_repetido_e_recusado_e_nao_grava_nada(tmp_path):
    destino = make(tmp_path)
    arquivo = _arquivo(tmp_path, [_fato(1, text="a"), _fato(1, text="b")])
    with pytest.raises(InvalidExportFile):
        import_from_file(destino, arquivo)
    assert destino.list_recent() == []


def test_superseded_by_solto_e_recusado_e_nao_grava_nada(tmp_path):
    destino = make(tmp_path)
    arquivo = _arquivo(tmp_path, [_fato(1, superseded_by=999)])
    with pytest.raises(InvalidExportFile):
        import_from_file(destino, arquivo)
    assert destino.list_recent() == []


def test_texto_vazio_ou_grande_demais_no_import_e_recusado(tmp_path):
    from mini_tars.models import EmptyText, TextTooLong
    destino = make(tmp_path)
    with pytest.raises(EmptyText):
        import_from_file(destino, _arquivo(tmp_path, [_fato(1, text="   ")], "vazio.json"))
    assert destino.list_recent() == []
    with pytest.raises(TextTooLong):
        import_from_file(destino, _arquivo(tmp_path, [_fato(1, text="x" * 2001)], "grande.json"))
    assert destino.list_recent() == []


def test_data_ou_projeto_invalidos_no_import_sao_recusados(tmp_path):
    from mini_tars.models import InvalidDate, InvalidProject
    destino = make(tmp_path)
    with pytest.raises(InvalidDate):
        import_from_file(destino, _arquivo(tmp_path, [_fato(1, date="31/12/2026")], "data.json"))
    assert destino.list_recent() == []
    with pytest.raises(InvalidProject):
        import_from_file(destino, _arquivo(tmp_path, [_fato(1, project="x" * 101)], "projeto.json"))
    assert destino.list_recent() == []
