"""Busca por palavra-chave (ADR-0002): o mesmo algoritmo medido em evals/ (experimento 3, desempate por regra).

Pontuação: soma do idf das palavras distintas da consulta presentes no fato.
Desempate: mais palavras da consulta presentes, depois data do fato mais recente, depois menor id.
Sem limiar e sem sinônimos (não venceram nos experimentos). `weak_match` só sinaliza, nunca filtra.
"""
import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Protocol

STOPWORDS = set("""
a o as os um uma uns umas de do da dos das em no na nos nas por para com sem sobre
e ou que qual quais quem quando onde como foi ser era eram sao e foi ficou
se ao aos ha ja mais muito pela pelo pelas pelos isso essa esse este esta
""".split())

# Um resultado é "fraco" se a pontuação for menor que esta fração da pontuação máxima possível da consulta.
# Valor vindo do experimento 3 (com 0,3 o ruído no ajuste caía a zero); é um sinal, não um filtro.
WEAK_FRACTION = 0.3


class Indexable(Protocol):
    id: int | str
    text: str
    fact_date: str


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


@dataclass(frozen=True)
class Hit:
    id: int | str
    score: float
    weak_match: bool


class SearchIndex:
    def __init__(self, facts: Iterable[Indexable] = ()):
        self._docs: dict = {}
        self._dates: dict = {}
        self._df: Counter = Counter()
        for f in facts:
            self.add(f)

    def __len__(self) -> int:
        return len(self._docs)

    def add(self, fact: Indexable) -> None:
        if fact.id in self._docs:
            self.remove(fact.id)
        counts = Counter(normalize(fact.text))
        self._docs[fact.id] = counts
        self._dates[fact.id] = fact.fact_date
        self._df.update(counts.keys())

    def remove(self, fact_id) -> None:
        counts = self._docs.pop(fact_id, None)
        self._dates.pop(fact_id, None)
        if counts is not None:
            for t in counts:
                self._df[t] -= 1
                if self._df[t] <= 0:
                    del self._df[t]

    def _idf(self, token: str) -> float:
        n, df = len(self._docs), self._df[token]
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def search(self, query: str, limit: int = 3) -> list[Hit]:
        q_tokens = list(dict.fromkeys(normalize(query)))
        if not q_tokens or not self._docs:
            return []
        idf = {t: self._idf(t) for t in q_tokens}
        max_possible = sum(idf.values())
        scored = []
        for fid, counts in self._docs.items():
            score, matched = 0.0, 0
            for t in q_tokens:
                if t in counts:
                    score += idf[t]
                    matched += 1
            if score > 0:
                digits = int(re.sub(r"\D", "", self._dates[fid])[:8] or 0)
                scored.append((score, matched, digits, fid))
        scored.sort(key=lambda x: (-x[0], -x[1], -x[2], str(x[3]) if isinstance(x[3], str) else x[3]))
        return [Hit(fid, s, s < WEAK_FRACTION * max_possible) for s, _m, _d, fid in scored[:limit]]
