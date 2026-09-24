"""Testes da busca (RF-02, RF-05) e equivalência com o script das avaliações (ADR-0002)."""
import importlib.util
import json
from pathlib import Path

import pytest
from types import SimpleNamespace as F

from mini_tars.search import SearchIndex, normalize

ROOT = Path(__file__).resolve().parents[1]


def facts(*items):
    return [F(id=i, text=t, fact_date=d) for i, t, d in items]


def test_normalizacao_tira_acento_caixa_stopwords_e_plural():
    assert normalize("As CLÍNICAS pagam?") == ["clinica", "pagam"]  # 'pagam' não termina em s
    assert normalize("Qual é o banco?") == ["banco"]


def test_palavra_rara_pontua_mais_que_comum():
    idx = SearchIndex(facts((1, "banco de dados Postgres", "2026-01-01"),
                            (2, "banco de horas do time", "2026-01-02"),
                            (3, "reunião com o time", "2026-01-03")))
    ids = [h.id for h in idx.search("Postgres time")]
    assert ids[0] == 1  # 'postgres' é raro; 'time' aparece em dois fatos


def test_desempate_mais_palavras_depois_data_mais_recente_depois_id():
    # mesma pontuação por construção (mesmas palavras, mesma raridade)
    idx = SearchIndex(facts((10, "alfa beta", "2026-01-01"), (11, "alfa beta", "2026-03-01"),
                            (12, "alfa beta", "2026-03-01"), (13, "gama delta", "2026-05-01")))
    assert [h.id for h in idx.search("alfa beta")] == [11, 12, 10]  # mais recente primeiro; empate de data por id


def test_sem_palavra_em_comum_devolve_vazio_e_sem_indice_tambem():
    assert SearchIndex(facts((1, "banco", "2026-01-01"))).search("cachorro") == []
    assert SearchIndex().search("qualquer") == []
    assert SearchIndex(facts((1, "banco", "2026-01-01"))).search("de o a") == []


def test_limite_de_resultados():
    idx = SearchIndex(facts(*[(i, "tema comum", f"2026-01-{i:02d}") for i in range(1, 8)]))
    assert len(idx.search("tema", limit=3)) == 3
    assert len(idx.search("tema", limit=5)) == 5


def test_weak_match_sinaliza_consulta_mal_atendida_sem_filtrar():
    idx = SearchIndex(facts((1, "O backup do banco é diário", "2026-01-01"),
                            (2, "Reunião com a clínica", "2026-01-02"),
                            (3, "Deploy fora do horário", "2026-01-03")))
    forte = idx.search("backup diário")[0]
    fraco = idx.search("A empresa tem CNPJ registrado banco")  # só 'banco' bate
    assert not forte.weak_match
    assert fraco and fraco[0].weak_match  # devolve, mas marca como fraco


def test_add_e_remove_mantem_o_indice_consistente():
    idx = SearchIndex(facts((1, "alfa", "2026-01-01")))
    idx.add(F(id=2, text="alfa beta", fact_date="2026-01-02"))
    assert len(idx) == 2
    idx.remove(2)
    assert [h.id for h in idx.search("beta")] == []
    idx.add(F(id=1, text="beta", fact_date="2026-01-01"))  # re-adicionar substitui
    assert [h.id for h in idx.search("alfa")] == [] and [h.id for h in idx.search("beta")] == [1]
    assert len(idx) == 1


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "evals" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.path.insert(0, str(ROOT / "evals"))
    spec.loader.exec_module(mod)
    return mod


def test_mesmo_resultado_que_o_script_do_experimento_3():
    """O pacote precisa devolver exatamente o que foi medido (ADR-0002), no corpus e perguntas de ajuste."""
    exp = _load("run_exp03")
    data = json.load(open(ROOT / "evals" / "cases.grande.json", encoding="utf-8"))
    idx = SearchIndex(F(id=f["id"], text=f["text"], fact_date=f["date"]) for f in data["facts"])
    docs, df, n = exp.build_index(data["facts"])
    dates = {f["id"]: f["date"] for f in data["facts"]}
    for q in data["questions"]:
        esperado = [fid for fid, _s in exp.search(q["q"], docs, df, n, dates, tiebreak="rule", k=3)]
        obtido = idx.search(q["q"], 3)
        assert [h.id for h in obtido] == esperado, q["id"]
        esperado_scores = [s for _fid, s in exp.search(q["q"], docs, df, n, dates, tiebreak="rule", k=3)]
        assert [h.score for h in obtido] == pytest.approx(esperado_scores), q["id"]


def test_idf_segue_a_formula_medida():
    import math
    idx = SearchIndex(facts((1, "alfa", "2026-01-01"), (2, "beta", "2026-01-02"), (3, "gama", "2026-01-03")))
    # n = 3, df('alfa') = 1  ->  log(1 + (3 - 1 + 0.5) / (1 + 0.5))
    assert math.isclose(idx._idf("alfa"), math.log(1 + 2.5 / 1.5))
    assert math.isclose(idx.search("alfa")[0].score, math.log(1 + 2.5 / 1.5))


def test_pontuacao_igual_desempata_por_mais_palavras_casadas():
    class IdfFixo(SearchIndex):
        def _idf(self, token):  # 'raro' vale 2; as demais valem 1
            return 2.0 if token == "raro" else 1.0

    idx = IdfFixo(facts((1, "raro sozinho", "2026-05-01"), (2, "comum1 comum2 outro", "2026-01-01")))
    hits = idx.search("raro comum1 comum2")
    assert [h.id for h in hits] == [2, 1]  # 2 casa 2 palavras; 1 casa 1; mesma pontuação (2,0), fato 1 é mais recente
    assert hits[0].score == hits[1].score == 2.0
