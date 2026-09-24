#!/usr/bin/env python3
"""Baseline de recuperação por palavra-chave (H1). Só biblioteca padrão.

Uso: python3 evals/run_baseline.py evals/cases.json [consultas.json]
O segundo argumento (opcional) é um JSON {"q01": "consulta reescrita", ...} que substitui o texto usado na busca; os relatórios continuam mostrando a pergunta original.
Mede hit@1 e hit@3 nas perguntas com resposta e reporta à parte as sem resposta.
"""
import json
import math
import re
import sys
import unicodedata
from collections import Counter

STOPWORDS = set("""
a o as os um uma uns umas de do da dos das em no na nos nas por para com sem sobre
e ou que qual quais quem quando onde como foi ser era eram sao e foi ficou
se ao aos ha ja mais muito pela pelo pelas pelos isso essa esse este esta
""".split())


def normalize(text: str) -> list[str]:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    tokens = re.findall(r"[a-z0-9]+", text)
    return [stem(t) for t in tokens if t not in STOPWORDS and len(t) > 1]


def stem(token: str) -> str:
    """Corte de sufixo mínimo, só para juntar plurais simples."""
    for suffix in ("coes", "oes", "s"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 3:
            return token[: -len(suffix)]
    return token


def build_index(facts):
    docs = {f["id"]: Counter(normalize(f["text"])) for f in facts}
    df = Counter()
    for counts in docs.values():
        df.update(counts.keys())
    return docs, df, len(docs)


def search(query, docs, df, n, k=3):
    q_tokens = normalize(query)
    scored = []
    for fid, counts in docs.items():
        score = 0.0
        for t in q_tokens:
            if t in counts:
                idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                score += idf
        scored.append((score, fid))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [(fid, s) for s, fid in scored[:k]]


def main(path, overrides_path=None):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    facts, questions = data["facts"], data["questions"]
    docs, df, n = build_index(facts)
    overrides = {}
    if overrides_path:
        with open(overrides_path, encoding="utf-8") as f:
            overrides = json.load(f)
        print(f"Modo: consultas reescritas de {overrides_path} ({len(overrides)} consultas)\n")

    def text_for(q):
        return overrides.get(q["id"], q["q"])

    answerable = [q for q in questions if q["gold"]]
    unanswerable = [q for q in questions if not q["gold"]]
    hit1 = hit3 = 0
    misses = []
    by_type = {}  # tipo -> [acertos@3, total]
    for q in answerable:
        results = search(text_for(q), docs, df, n, k=3)
        ids = [fid for fid, s in results if s > 0]
        ok3 = any(i in q["gold"] for i in ids)
        if ids[:1] and ids[0] in q["gold"]:
            hit1 += 1
        if ok3:
            hit3 += 1
        else:
            misses.append((q, [(fid, s) for fid, s in results if s > 0]))
        tipo = q.get("tipo", "sem-tipo")
        stats = by_type.setdefault(tipo, [0, 0])
        stats[0] += int(ok3)
        stats[1] += 1

    total = len(answerable)
    drafts = [q for q in questions if q.get("status") == "rascunho"]
    if drafts:
        print(f"ATENÇÃO: {len(drafts)} de {len(questions)} perguntas ainda estão como 'rascunho'.")
        print("A nota abaixo é PROVISÓRIA: reescreva as perguntas com suas palavras e mude o status para 'final'.\n")
    print(f"Fatos: {len(facts)} | perguntas com resposta: {total} | sem resposta: {len(unanswerable)}")
    if total:
        print(f"hit@1: {hit1}/{total} = {100*hit1/total:.0f}%")
        print(f"hit@3: {hit3}/{total} = {100*hit3/total:.0f}%   (K1: precisa de pelo menos 70%)")
    if len(by_type) > 1 or "sem-tipo" not in by_type:
        print("\nhit@3 por tipo de pergunta:")
        for tipo, (ok, tot) in sorted(by_type.items()):
            print(f"- {tipo}: {ok}/{tot} = {100*ok/tot:.0f}%")
    if misses:
        print("\nErros (leia estes, eles dizem mais que a nota):")
        for q, results in misses:
            print(f"- {q['id']}: {q['q']}  | esperado: {q['gold']} | veio: {[r[0] for r in results] or 'nada (nenhuma palavra em comum)'}")
    if unanswerable:
        print("\nPerguntas sem resposta (o sistema devolve algo com pontuação > 0?):")
        for q in unanswerable:
            results = search(text_for(q), docs, df, n, k=1)
            top = results[0] if results else None
            noisy = bool(top and top[1] > 0)
            print(f"- {q['id']}: {q['q']} | ruído: {'sim (' + top[0] + ')' if noisy else 'não'}")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("Uso: python3 evals/run_baseline.py evals/cases.json [consultas.json]")
    main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None)
