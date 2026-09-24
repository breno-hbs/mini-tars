"""Tipos do domínio: fato e erros com código estável (ver arquitetura.md)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Fact:
    id: int
    text: str
    fact_date: str          # AAAA-MM-DD, data local (America/Sao_Paulo)
    project: str | None
    created_at: str         # UTC, ISO 8601
    superseded_by: int | None = None


class DomainError(Exception):
    """Erro esperado, com código estável para o cliente e mensagem clara em português."""

    code = "error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class EmptyText(DomainError):
    code = "empty_text"


class TextTooLong(DomainError):
    code = "text_too_long"


class UnknownId(DomainError):
    code = "unknown_id"


class InvalidDate(DomainError):
    code = "invalid_date"


class InvalidProject(DomainError):
    code = "invalid_project"


class AlreadySuperseded(DomainError):
    code = "already_superseded"


class InvalidArgument(DomainError):
    """Argumento com tipo errado (por exemplo, texto que não é texto)."""

    code = "invalid_argument"


class SchemaTooNew(DomainError):
    """O banco foi criado por uma versão mais nova do mini-tars."""

    code = "schema_too_new"


class UnknownExportVersion(DomainError):
    """O arquivo de exportação tem uma versão de esquema que este mini-tars não conhece (RF-08)."""

    code = "unknown_export_version"


class DatabaseNotEmpty(DomainError):
    """Importar exige um banco vazio, para preservar os ids originais sem colisão (RF-08)."""

    code = "database_not_empty"


class InvalidExportFile(DomainError):
    """O arquivo de exportação não é um JSON válido, ou não tem o formato esperado (RF-08)."""

    code = "invalid_export_file"
