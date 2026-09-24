"""Avaliações como regressão (RNF-05) e sinal de resultado fraco (RF-05), no conjunto de ajuste.

O conjunto reservado NUNCA é lido aqui (evals/experimento-03.md).
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
import run_pkg  # noqa: E402

CORPUS = ROOT / "evals" / "cases.grande.json"


def test_regressao_hit3_no_ajuste_nao_cai_abaixo_de_19_de_29():
    r = run_pkg.evaluate(CORPUS)
    assert r["total"] == 29
    assert r["hit3"] >= 19, f"hit@3 caiu para {r['hit3']}/29; a busca piorou ou o corpus mudou"


def test_reproduz_o_resultado_medido_no_experimento_3():
    r = run_pkg.evaluate(CORPUS, use_supersedes=False)
    assert (r["hit3"], r["hit1"], r["noise"]) == (19, 13, 3)


def test_sinal_de_resultado_fraco_nao_marca_primeiro_resultado_correto():
    r = run_pkg.evaluate(CORPUS)
    assert r["weak_correct"] == 0


def test_perguntas_sem_resposta_voltam_vazias_ou_sinalizadas():
    r = run_pkg.evaluate(CORPUS)
    assert (r["unans"] - r["noise"]) + r["weak_unans"] >= 5


def test_script_recusa_o_conjunto_reservado_sem_final():
    p = subprocess.run([sys.executable, str(ROOT / "evals" / "run_pkg.py"), "--perguntas",
                        str(ROOT / "evals" / "teste-reservado.json")], capture_output=True, text=True)
    assert p.returncode != 0 and "RECUSADO" in (p.stdout + p.stderr)
