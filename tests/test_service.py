"""Testes das regras de negócio (RF-01, RF-03, RF-04, RNF-08). Só dados fictícios."""
from datetime import datetime, timezone

import pytest

from mini_tars.models import EmptyText, InvalidDate, InvalidProject, TextTooLong, UnknownId
from mini_tars.service import Service
from mini_tars.store import Store


def make(tmp_path, now="2026-09-23T15:00:00+00:00"):
    clock_value = {"now": datetime.fromisoformat(now)}
    svc = Service(Store(tmp_path / "m.db"), clock=lambda: clock_value["now"])
    return svc, clock_value


def test_texto_vazio_e_recusado(tmp_path):
    svc, _ = make(tmp_path)
    for vazio in ("", "   ", None):
        with pytest.raises(EmptyText):
            svc.remember(vazio)


def test_texto_acima_do_limite_e_recusado_e_no_limite_passa(tmp_path):
    svc, _ = make(tmp_path)
    svc.remember("x" * 2000)
    with pytest.raises(TextTooLong):
        svc.remember("x" * 2001)


def test_data_padrao_e_a_data_local_perto_da_meia_noite(tmp_path):
    # 02:30 UTC de 24/09 = 23:30 de 23/09 em São Paulo (UTC-3)
    svc, _ = make(tmp_path, now="2026-09-24T02:30:00+00:00")
    fid = svc.remember("fato perto da meia-noite")
    fact = svc.get(fid)
    assert fact.fact_date == "2026-09-23"
    assert fact.created_at == "2026-09-24T02:30:00Z"  # carimbo interno em UTC


def test_data_padrao_depois_da_meia_noite_local(tmp_path):
    svc, _ = make(tmp_path, now="2026-09-24T03:30:00+00:00")  # 00:30 local do dia 24
    assert svc.get(svc.remember("x")).fact_date == "2026-09-24"


@pytest.mark.parametrize("ruim", ["2026-13-01", "2026-02-30", "20260301", "01/03/2026", "2026-3-1", "ontem"])
def test_data_invalida_e_recusada(tmp_path, ruim):
    svc, _ = make(tmp_path)
    with pytest.raises(InvalidDate):
        svc.remember("x", date=ruim)


def test_data_informada_e_respeitada(tmp_path):
    svc, _ = make(tmp_path)
    assert svc.get(svc.remember("x", date="2026-03-02")).fact_date == "2026-03-02"


def test_projeto_vazio_vira_nenhum_e_longo_e_recusado(tmp_path):
    svc, _ = make(tmp_path)
    assert svc.get(svc.remember("x", project="   ")).project is None
    assert svc.get(svc.remember("y", project=" clinica ")).project == "clinica"
    with pytest.raises(InvalidProject):
        svc.remember("z", project="p" * 101)


def test_substituir_pelo_servico(tmp_path):
    svc, _ = make(tmp_path)
    a = svc.remember("Plano básico: R$ 79.")
    b = svc.remember("Plano básico: R$ 89.", supersedes=a)
    assert svc.get(a).superseded_by == b
    assert [f.id for f in svc.list_recent()] == [b]


def test_forget_e_erro_de_id(tmp_path):
    svc, _ = make(tmp_path)
    fid = svc.remember("apagar")
    svc.forget(fid)
    with pytest.raises(UnknownId):
        svc.get(fid)
    with pytest.raises(UnknownId):
        svc.forget(fid)


def test_list_recent_limita_entre_1_e_100(tmp_path):
    svc, _ = make(tmp_path)
    for i in range(5):
        svc.remember(f"fato {i}", date=f"2026-01-0{i+1}")
    assert len(svc.list_recent(limit=0)) == 1
    assert len(svc.list_recent(limit=3)) == 3
    assert svc.list_recent(limit=1000)[0].text == "fato 4"


def test_erros_tem_codigo_estavel_e_mensagem():
    from mini_tars import models
    assert models.EmptyText("m").code == "empty_text"
    assert models.TextTooLong("m").code == "text_too_long"
    assert models.UnknownId("m").code == "unknown_id"
    assert models.InvalidDate("m").code == "invalid_date"


def test_busca_padrao_ignora_substituido_e_historico_traz_de_volta(tmp_path):
    svc, _ = make(tmp_path)
    a = svc.remember("O preço do plano básico é 79 reais por mês.", date="2026-06-03")
    b = svc.remember("Correção: o preço do plano básico passou a 89 reais por mês.",
                     date="2026-06-10", supersedes=a)
    padrao = [f.id for f, _h in svc.search("preço do plano básico")]
    assert padrao == [b]
    historico = {f.id for f, _h in svc.search("preço do plano básico", include_superseded=True)}
    assert historico == {a, b}


def test_busca_reflete_escrita_e_apagar_sem_reiniciar(tmp_path):
    svc, _ = make(tmp_path)
    assert svc.search("zebra") == []
    fid = svc.remember("A zebra apareceu no relatório.")
    assert [f.id for f, _h in svc.search("zebra")] == [fid]
    svc.forget(fid)
    assert svc.search("zebra") == []


def test_busca_por_projeto_e_limites(tmp_path):
    svc, _ = make(tmp_path)
    a = svc.remember("tema comum do projeto um", project="p1")
    svc.remember("tema comum do projeto dois", project="p2")
    assert [f.id for f, _h in svc.search("tema comum", project="p1")] == [a]
    assert len(svc.search("tema", limit=0)) == 1  # limite mínimo 1
    for i in range(12):
        svc.remember(f"tema comum extra {i}")
    assert len(svc.search("tema", limit=50)) == 10  # limite máximo 10


def test_resultado_carrega_score_e_sinal(tmp_path):
    svc, _ = make(tmp_path)
    svc.remember("O backup do banco é diário às 3h.")
    (fact, hit), = svc.search("backup diário")
    assert hit.score > 0 and hit.weak_match is False and fact.text.startswith("O backup")


def test_tipos_errados_viram_erro_de_dominio(tmp_path):
    from mini_tars.models import InvalidArgument
    svc, _ = make(tmp_path)
    with pytest.raises(InvalidArgument):
        svc.remember(5)
    with pytest.raises(InvalidArgument):
        svc.remember("x", date=20260101)
    with pytest.raises(InvalidArgument):
        svc.remember("x", supersedes="1")
    with pytest.raises(InvalidArgument):
        svc.remember("x", supersedes=True)
    with pytest.raises(InvalidArgument):
        svc.search("x", limit="abc")
    with pytest.raises(InvalidArgument):
        svc.search(None)
    with pytest.raises(InvalidArgument):
        svc.list_recent(limit=2.5)
    with pytest.raises(InvalidArgument):
        svc.forget("1")
    with pytest.raises(InvalidArgument):
        svc.get("1")


def test_data_vazia_e_erro_e_ausente_e_hoje(tmp_path):
    svc, _ = make(tmp_path)
    with pytest.raises(InvalidDate):
        svc.remember("x", date="")  # perguntar em vez de adivinhar (CLAUDE.md)
    assert svc.get(svc.remember("x", date=None)).fact_date == "2026-09-23"


def test_escrita_durante_montagem_do_indice_nao_deixa_indice_velho(tmp_path):
    """Sem trava, a busca reinstalava um índice montado antes de uma escrita concorrente."""
    import threading
    svc, _ = make(tmp_path)
    svc.remember("alfa um")
    writer = threading.Thread(target=lambda: svc.remember("alfa dois"))
    original = svc.store.all

    def all_and_write(*a, **kw):
        facts = original(*a, **kw)
        writer.start()      # escrita concorrente enquanto o índice é montado
        writer.join(0.3)    # com a trava, ela espera; sem trava, termina aqui
        return facts

    svc.store.all = all_and_write
    svc.search("alfa")
    svc.store.all = original
    writer.join(5)
    assert len(svc.search("alfa", limit=10)) == 2
