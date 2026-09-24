#!/usr/bin/env python3
"""Busca por palavra-chave com opções do experimento 3. Só biblioteca padrão.

Uso: python3 evals/run_exp03.py CORPUS.json [PERGUNTAS.json] [--tiebreak id|rule] [--threshold F] [--synonyms ARQ.json] [--queries ARQ.json] [--final] [-v]
- CORPUS.json tem "facts". PERGUNTAS.json (opcional) tem "questions"; sem ele usa as do corpus.
- O arquivo teste-reservado.json só roda com --final (ver evals/experimento-03.md).
"""
import argparse, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_baseline import normalize, build_index  # noqa: E402


def load_synonyms(path):
    if not path:
        return {}
    groups = json.load(open(path, encoding="utf-8"))["grupos"]
    syn = {}
    for g in groups:
        toks = {normalize(w)[0] for w in g if normalize(w)}
        for t in toks:
            syn.setdefault(t, set()).update(toks - {t})
    return syn


def search(query, docs, df, n, dates, tiebreak="id", threshold=0.0, syn=None, k=3):
    syn = syn or {}
    q_tokens = list(dict.fromkeys(normalize(query)))

    def idf(t):
        return math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))

    # pontuação máxima possível = soma do idf de TODAS as palavras da consulta (como no protocolo);
    # palavra que não existe em nenhum fato (df=0) conta com o idf máximo e faz a consulta parecer mal atendida
    max_possible = sum(max(idf(x) for x in ({t} | syn.get(t, set()))) for t in q_tokens)
    scored = []
    for fid, counts in docs.items():
        score, matched = 0.0, 0
        for t in q_tokens:
            present = [x for x in ({t} | syn.get(t, set())) if x in counts]
            if present:
                score += max(idf(x) for x in present)
                matched += 1
        scored.append((score, matched, fid))
    if tiebreak == "rule":
        scored.sort(key=lambda x: (-x[0], -x[1], [-int(c) for c in dates[x[2]].replace("-", "")[:8]], x[2]))
    else:
        scored.sort(key=lambda x: (-x[0], x[2]))
    out = [(fid, s) for s, m, fid in scored[:k] if s > 0 and s >= threshold * max_possible]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus"); ap.add_argument("perguntas", nargs="?")
    ap.add_argument("--tiebreak", default="id", choices=["id", "rule"])
    ap.add_argument("--threshold", type=float, default=0.0)
    ap.add_argument("--synonyms"); ap.add_argument("--queries")
    ap.add_argument("--final", action="store_true"); ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    if a.perguntas and "teste-reservado" in a.perguntas and not a.final:
        sys.exit("RECUSADO: o conjunto reservado só roda no passo final, com --final (evals/experimento-03.md).")
    corpus = json.load(open(a.corpus, encoding="utf-8"))
    questions = json.load(open(a.perguntas, encoding="utf-8"))["questions"] if a.perguntas else corpus["questions"]
    over = json.load(open(a.queries, encoding="utf-8")) if a.queries else {}
    docs, df, n = build_index(corpus["facts"])
    dates = {f["id"]: f["date"] for f in corpus["facts"]}
    syn = load_synonyms(a.synonyms)
    h1 = h3 = tot = noise = nu = 0
    miss = []; noisy = []
    for q in questions:
        res = search(over.get(q["id"], q["q"]), docs, df, n, dates, a.tiebreak, a.threshold, syn)
        ids = [r[0] for r in res]
        if q["gold"]:
            tot += 1
            h1 += bool(ids and ids[0] in q["gold"])
            ok = any(i in q["gold"] for i in ids)
            h3 += ok
            if not ok: miss.append((q["id"], ids))
        else:
            nu += 1
            if ids: noise += 1; noisy.append(q["id"])
    print(f"hit@3 {h3}/{tot} = {100*h3/tot:.0f}% | hit@1 {h1}/{tot} = {100*h1/tot:.0f}% | ruído {noise}/{nu}"
          f"  [tiebreak={a.tiebreak} limiar={a.threshold} sinônimos={'sim' if syn else 'não'}]")
    if a.v:
        print("erros:", miss); print("ruído em:", noisy)


if __name__ == "__main__":
    main()
