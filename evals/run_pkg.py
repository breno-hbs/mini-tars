#!/usr/bin/env python3
"""Mede a busca do PACOTE (mini_tars.service) nas avaliações, com substituições e modos (RF-02, RF-03, RF-05).

Uso: python3 evals/run_pkg.py [corpus.json] [--sem-substituicoes] [--perguntas ARQ.json --final] [-v]
O conjunto reservado (teste-reservado.json) só roda com --final (evals/experimento-03.md, e ele já foi usado).
"""
import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from mini_tars.service import Service  # noqa: E402
from mini_tars.store import Store  # noqa: E402


def evaluate(corpus_path, questions=None, use_supersedes=True, modos_path=None, supersedes_path=None):
    corpus = json.load(open(corpus_path, encoding="utf-8"))
    questions = questions if questions is not None else corpus["questions"]
    sup = json.load(open(supersedes_path or HERE / "supersedes.json", encoding="utf-8")) if use_supersedes else {}
    sup = {k: v for k, v in sup.items() if not k.startswith("_")}
    modos = json.load(open(modos_path or HERE / "modos.json", encoding="utf-8")) if use_supersedes else {}
    modos = {k: v for k, v in modos.items() if not k.startswith("_")}
    with tempfile.TemporaryDirectory() as tmp:
        store = Store(Path(tmp) / "eval.db")
        try:
            return _run(corpus, questions, sup, modos, store)
        finally:
            store.close()  # no Windows, arquivo aberto não pode ser apagado ao limpar a pasta temporária


def _run(corpus, questions, sup, modos, store):
    svc = Service(store, clock=lambda: datetime(2026, 9, 23, tzinfo=timezone.utc))
    ids = {}
    by_id = {f["id"]: f for f in corpus["facts"]}

    def insert(fid):  # o fato antigo precisa existir antes do que o substitui
        if fid in ids:
            return
        old_key = sup.get(fid)
        if old_key is not None:
            if old_key not in by_id:
                raise SystemExit(f"supersedes.json cita {old_key}, que não existe no corpus")
            insert(old_key)
        f = by_id[fid]
        ids[fid] = svc.remember(f["text"], date=f["date"], supersedes=ids[old_key] if old_key else None)

    for fid in sorted(by_id):  # ordem por id: mesmo desempate dos experimentos
        insert(fid)
    back = {v: k for k, v in ids.items()}
    res = {"hit1": 0, "hit3": 0, "total": 0, "noise": 0, "unans": 0,
           "weak_unans": 0, "weak_correct": 0, "weak_wrong": 0, "misses": [], "noisy": []}
    for q in questions:
        hist = modos.get(q["id"]) == "historico"
        hits = svc.search(q["q"], limit=3, include_superseded=hist)
        got = [back[fact.id] for fact, _h in hits]
        if q["gold"]:
            res["total"] += 1
            res["hit1"] += bool(got and got[0] in q["gold"])
            ok = any(g in q["gold"] for g in got)
            res["hit3"] += ok
            if not ok:
                res["misses"].append((q["id"], got))
            if hits and hits[0][1].weak_match:
                if got[0] in q["gold"]:
                    res["weak_correct"] += 1   # falso alarme: o 1º resultado estava certo
                else:
                    res["weak_wrong"] += 1     # alarme útil: o 1º resultado estava errado
        else:
            res["unans"] += 1
            if got:
                res["noise"] += 1
                res["noisy"].append(q["id"])
                if hits[0][1].weak_match:
                    res["weak_unans"] += 1
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", nargs="?", default=str(HERE / "cases.grande.json"))
    ap.add_argument("--sem-substituicoes", action="store_true")
    ap.add_argument("--perguntas")
    ap.add_argument("--final", action="store_true")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    qs = None
    if a.perguntas:
        if "teste-reservado" in a.perguntas and not a.final:
            sys.exit("RECUSADO: o conjunto reservado só roda com --final.")
        qs = json.load(open(a.perguntas, encoding="utf-8"))["questions"]
    r = evaluate(a.corpus, qs, use_supersedes=not a.sem_substituicoes)
    t = r["total"]
    print(f"hit@3 {r['hit3']}/{t} = {100*r['hit3']/t:.0f}% | hit@1 {r['hit1']}/{t} = {100*r['hit1']/t:.0f}% | "
          f"ruído {r['noise']}/{r['unans']}")
    vazio_ou_fraco = (r["unans"] - r["noise"]) + r["weak_unans"]
    print(f"weak_match: sem resposta que voltam vazias ou sinalizadas {vazio_ou_fraco}/{r['unans']}; "
          f"1º resultado sinalizado e CERTO (falso alarme) {r['weak_correct']}; sinalizado e ERRADO {r['weak_wrong']}")
    if a.v:
        print("erros:", r["misses"]); print("ruído em:", r["noisy"])


if __name__ == "__main__":
    main()
