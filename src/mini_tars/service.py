"""Regras de negócio: validação, datas em America/Sao_Paulo, substituição (RF-01, RF-03, RF-04)."""
import re
import sqlite3
import threading
from datetime import date, datetime, timezone
from typing import Callable
from zoneinfo import ZoneInfo

from .models import (DatabaseNotEmpty, EmptyText, Fact, InvalidArgument, InvalidDate, InvalidExportFile,
                     InvalidProject, TextTooLong, UnknownId)
from .search import Hit, SearchIndex
from .store import Store

TZ = ZoneInfo("America/Sao_Paulo")
MAX_TEXT = 2000
MAX_PROJECT = 100
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Service:
    def __init__(self, store: Store, clock: Callable[[], datetime] = _utc_now):
        self.store = store
        self._clock = clock
        self._indexes: dict[tuple[bool, str | None], SearchIndex] = {}
        self._lock = threading.RLock()  # escrita e montagem de índice não podem se intercalar

    def _today_local(self) -> str:
        return self._clock().astimezone(TZ).date().isoformat()

    def remember(self, text: str, date: str | None = None, project: str | None = None,
                 supersedes: int | None = None) -> int:
        if text is not None and not isinstance(text, str):
            raise InvalidArgument("O texto do fato deve ser uma string.")
        if date is not None and not isinstance(date, str):
            raise InvalidArgument("A data deve ser uma string AAAA-MM-DD.")
        if supersedes is not None and (isinstance(supersedes, bool) or not isinstance(supersedes, int)):
            raise InvalidArgument("`supersedes` deve ser o id (número inteiro) de um fato.")
        text = (text or "").strip()
        if not text:
            raise EmptyText("O texto do fato está vazio.")
        if len(text) > MAX_TEXT:
            raise TextTooLong(f"O texto tem {len(text)} caracteres; o máximo é {MAX_TEXT}.")
        fact_date = self._today_local() if date is None else self._validate_date(date)
        project = self._validate_project(project)
        created = self._clock().astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with self._lock:
            new_id = self.store.add(text, fact_date, project, created, supersedes)
            self._indexes.clear()  # índices são reconstruídos sob demanda
        return new_id

    def forget(self, fact_id: int) -> None:
        self._check_id(fact_id)
        with self._lock:
            self.store.delete(fact_id)
            self._indexes.clear()

    @staticmethod
    def _check_id(fact_id) -> None:
        if isinstance(fact_id, bool) or not isinstance(fact_id, int):
            raise InvalidArgument("O id do fato deve ser um número inteiro.")

    @staticmethod
    def _check_limit(limit, maximum: int) -> int:
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise InvalidArgument("`limit` deve ser um número inteiro.")
        return max(1, min(limit, maximum))

    def search(self, query: str, limit: int = 3, project: str | None = None,
               include_superseded: bool = False) -> list[tuple[Fact, Hit]]:
        """Busca padrão só nos fatos ativos; `include_superseded` inclui o histórico (RF-03)."""
        if not isinstance(query, str):
            raise InvalidArgument("A consulta deve ser uma string.")
        limit = self._check_limit(limit, 10)
        project = self._validate_project(project)
        key = (include_superseded, project)
        with self._lock:
            index = self._indexes.get(key)
            if index is None:
                index = SearchIndex(self.store.all(include_superseded=include_superseded, project=project))
                self._indexes[key] = index
            hits = index.search(query, limit)
            out = []
            for hit in hits:
                fact = self.store.get(hit.id)
                if fact is not None:
                    out.append((fact, hit))
        return out

    def get(self, fact_id: int) -> Fact:
        self._check_id(fact_id)
        fact = self.store.get(fact_id)
        if fact is None:
            raise UnknownId(f"Não existe fato com id {fact_id}.")
        return fact

    def list_recent(self, limit: int = 10, project: str | None = None) -> list[Fact]:
        limit = self._check_limit(limit, 100)
        return self.store.recent(limit, self._validate_project(project))

    def export_all(self) -> list[Fact]:
        """Todos os fatos, ativos e substituídos, para exportação (RF-08)."""
        with self._lock:
            return self.store.all(include_superseded=True)

    def import_all(self, facts: list[Fact]) -> None:
        """Recria os fatos com os ids e substituições originais. Exige banco vazio (RF-08).

        `export_import.py` já valida cada fato antes de chamar isto; a checagem de
        integridade aqui é uma rede de segurança para quem chamar `Service.import_all`
        diretamente (ids repetidos, `superseded_by` sem correspondência).
        """
        with self._lock:
            if self.store.count() > 0:
                raise DatabaseNotEmpty(
                    "Importar exige um banco vazio, para preservar os ids sem colisão. "
                    "Use um banco novo (--db) ou exporte e apague o atual antes.")
            try:
                self.store.import_all(facts)
            except sqlite3.IntegrityError as exc:
                # Nada foi persistido: `Store.import_all` roda em uma única transação.
                raise InvalidExportFile(f"Fatos malformados ou inconsistentes entre si: {exc}") from None
            self._indexes.clear()

    @staticmethod
    def _validate_date(value: str) -> str:
        if not _DATE_RE.match(value):
            raise InvalidDate("A data deve ter o formato AAAA-MM-DD.")
        try:
            date.fromisoformat(value)
        except ValueError:
            raise InvalidDate("Essa data não existe no calendário.") from None
        return value

    @staticmethod
    def _validate_project(project: str | None) -> str | None:
        if project is None:
            return None
        project = project.strip()
        if not project:
            return None
        if len(project) > MAX_PROJECT:
            raise InvalidProject(f"O nome do projeto tem mais de {MAX_PROJECT} caracteres.")
        return project
