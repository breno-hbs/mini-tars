"""Armazenamento em SQLite (ADR-0001): esquema versionado, backup antes de migrar."""
import shutil
import sqlite3
import threading
from pathlib import Path

from .models import AlreadySuperseded, Fact, SchemaTooNew, UnknownId

MIGRATIONS: dict[int, list[str]] = {
    1: [
        """CREATE TABLE facts (
             id            INTEGER PRIMARY KEY,
             text          TEXT    NOT NULL CHECK (length(text) BETWEEN 1 AND 2000),
             fact_date     TEXT    NOT NULL,
             project       TEXT,
             created_at    TEXT    NOT NULL,
             superseded_by INTEGER REFERENCES facts(id) ON DELETE SET NULL
           )""",
        "CREATE INDEX idx_facts_project ON facts(project)",
    ],
}

_COLS = "id, text, fact_date, project, created_at, superseded_by"


def _to_fact(row) -> Fact:
    return Fact(*row)


class Store:
    def __init__(self, path: Path | str, migrations: dict[int, list[str]] | None = None):
        self.path = Path(path)
        self._migrations = MIGRATIONS if migrations is None else migrations
        self._lock = threading.RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._migrate()
        self._conn = self._connect()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA secure_delete = ON")  # apagar de verdade (RF-04)
        return conn

    # --- migrações -------------------------------------------------------
    def _migrate(self) -> None:
        target = max(self._migrations)
        existed = self.path.exists() and self.path.stat().st_size > 0
        conn = sqlite3.connect(self.path)
        try:
            current = conn.execute("PRAGMA user_version").fetchone()[0]
            if current > target:
                raise SchemaTooNew(
                    f"Este banco tem esquema v{current}, mais novo que o suportado (v{target}). "
                    "Atualize o mini-tars; nada foi alterado.")
            if current == target:
                return
            backup = None
            if existed and current > 0:
                conn.close()
                backup = self.path.with_name(f"{self.path.name}.bak-v{current}")
                shutil.copy2(self.path, backup)
                conn = sqlite3.connect(self.path)
            try:
                conn.isolation_level = None  # controle manual da transação
                conn.execute("BEGIN")
                for version in range(current + 1, target + 1):
                    for stmt in self._migrations[version]:
                        conn.execute(stmt)
                    conn.execute(f"PRAGMA user_version = {version}")
                conn.execute("COMMIT")
            except Exception:
                try:
                    conn.execute("ROLLBACK")
                except sqlite3.Error:
                    pass
                # O ROLLBACK acima desfaz tudo (no SQLite até o DDL e o user_version são
                # transacionais); o arquivo de backup permanece ao lado do banco.
                raise
        finally:
            try:
                conn.close()
            except sqlite3.Error:
                pass

    # --- operações -------------------------------------------------------
    def add(self, text: str, fact_date: str, project: str | None, created_at: str,
            supersedes: int | None = None) -> int:
        with self._lock, self._conn:
            if supersedes is not None:
                old = self._conn.execute(
                    "SELECT superseded_by FROM facts WHERE id = ?", (supersedes,)).fetchone()
                if old is None:
                    raise UnknownId(f"Não existe fato com id {supersedes} para substituir.")
                if old[0] is not None:
                    raise AlreadySuperseded(
                        f"O fato {supersedes} já foi substituído pelo fato {old[0]}; substitua o mais recente.")
            cur = self._conn.execute(
                "INSERT INTO facts (text, fact_date, project, created_at) VALUES (?, ?, ?, ?)",
                (text, fact_date, project, created_at))
            new_id = cur.lastrowid
            if supersedes is not None:
                self._conn.execute("UPDATE facts SET superseded_by = ? WHERE id = ?", (new_id, supersedes))
            return new_id

    def get(self, fact_id: int) -> Fact | None:
        with self._lock:
            row = self._conn.execute(f"SELECT {_COLS} FROM facts WHERE id = ?", (fact_id,)).fetchone()
        return _to_fact(row) if row else None

    def all(self, include_superseded: bool = False, project: str | None = None) -> list[Fact]:
        sql = f"SELECT {_COLS} FROM facts"
        where, args = [], []
        if not include_superseded:
            where.append("superseded_by IS NULL")
        if project is not None:
            where.append("project = ?")
            args.append(project)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY id"
        with self._lock:
            return [_to_fact(r) for r in self._conn.execute(sql, args).fetchall()]

    def recent(self, limit: int, project: str | None = None) -> list[Fact]:
        sql = f"SELECT {_COLS} FROM facts WHERE superseded_by IS NULL"
        args: list = []
        if project is not None:
            sql += " AND project = ?"
            args.append(project)
        sql += " ORDER BY fact_date DESC, created_at DESC, id DESC LIMIT ?"
        args.append(limit)
        with self._lock:
            return [_to_fact(r) for r in self._conn.execute(sql, args).fetchall()]

    def count(self) -> int:
        with self._lock:
            return self._conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]

    def import_all(self, facts: list[Fact]) -> None:
        """Recria fatos com os ids e substituições originais (RF-08). O chamador garante banco vazio.

        Em duas passagens: primeiro insere todos com `superseded_by` nulo, depois preenche as
        substituições. Evita violar a referência (um fato pode citar um id maior, inserido depois).
        """
        with self._lock, self._conn:
            for f in facts:
                self._conn.execute(
                    "INSERT INTO facts (id, text, fact_date, project, created_at, superseded_by) "
                    "VALUES (?, ?, ?, ?, ?, NULL)",
                    (f.id, f.text, f.fact_date, f.project, f.created_at))
            for f in facts:
                if f.superseded_by is not None:
                    self._conn.execute("UPDATE facts SET superseded_by = ? WHERE id = ?", (f.superseded_by, f.id))

    def delete(self, fact_id: int) -> None:
        """Remoção definitiva. Se o fato substituía outro, o antigo volta a ficar ativo."""
        with self._lock, self._conn:
            cur = self._conn.execute("DELETE FROM facts WHERE id = ?", (fact_id,))
            if cur.rowcount == 0:
                raise UnknownId(f"Não existe fato com id {fact_id}.")

    def close(self) -> None:
        with self._lock:
            self._conn.close()
