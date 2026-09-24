"""Exportar e importar em JSON, com versão de esquema (RF-08).

O arquivo guarda todos os fatos (ativos e substituídos), com id, texto, data, projeto,
carimbo de criação e a cadeia de substituições. Importar exige um banco vazio: os ids
originais são preservados, o que exclui reaproveitar um banco já em uso.
"""
import json
from pathlib import Path

from .models import EmptyText, Fact, InvalidExportFile, TextTooLong, UnknownExportVersion
from .service import MAX_TEXT, Service

EXPORT_VERSION = 1


def export_to_file(service: Service, path: Path) -> int:
    """Escreve o arquivo de exportação. Devolve a quantidade de fatos exportados."""
    facts = service.export_all()
    data = {
        "schema_version": EXPORT_VERSION,
        "facts": [
            {"id": f.id, "text": f.text, "date": f.fact_date, "project": f.project,
             "created_at": f.created_at, "superseded_by": f.superseded_by}
            for f in facts
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(facts)


def _parse_fact(item: dict) -> Fact:
    try:
        return Fact(id=item["id"], text=item["text"], fact_date=item["date"], project=item.get("project"),
                    created_at=item["created_at"], superseded_by=item.get("superseded_by"))
    except (KeyError, TypeError) as exc:
        raise InvalidExportFile(f"Fato malformado no arquivo de exportação: {exc}") from None


def _check_facts(facts: list[Fact]) -> None:
    """Valida antes de tocar no banco: erro claro em vez de o SQLite recusar no meio da importação.

    A validação normal do `Service.remember` (texto, data, projeto) é reaplicada aqui, porque
    `import_all` grava direto no armazenamento. Além disso, confere que os ids não se repetem
    dentro do arquivo e que `superseded_by` só aponta para um id que também está sendo importado
    (uma referência solta viraria erro de integridade do SQLite, sem mensagem clara).
    """
    ids: set[int] = set()
    for f in facts:
        if not isinstance(f.text, str) or not f.text.strip():
            raise EmptyText(f"Fato id {f.id}: texto vazio no arquivo de exportação.")
        if len(f.text) > MAX_TEXT:
            raise TextTooLong(f"Fato id {f.id}: texto com {len(f.text)} caracteres; o máximo é {MAX_TEXT}.")
        Service._validate_date(f.fact_date)
        Service._validate_project(f.project)
        if f.id in ids:
            raise InvalidExportFile(f"Id {f.id} aparece repetido no arquivo de exportação.")
        ids.add(f.id)
    for f in facts:
        if f.superseded_by is not None and f.superseded_by not in ids:
            raise InvalidExportFile(
                f"Fato id {f.id}: `superseded_by` aponta para o id {f.superseded_by}, "
                "que não existe no arquivo de exportação.")


def import_from_file(service: Service, path: Path) -> int:
    """Lê o arquivo de exportação e recria os fatos. Devolve a quantidade importada.

    Levanta `UnknownExportVersion` para uma versão de esquema desconhecida ou arquivo
    que não é JSON, e `InvalidExportFile` para um formato reconhecível mas malformado.
    """
    try:
        texto = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise UnknownExportVersion(f"Arquivo não é texto UTF-8 válido: {exc}") from None
    try:
        data = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise UnknownExportVersion(f"Arquivo não é um JSON válido: {exc}") from None

    versao = data.get("schema_version") if isinstance(data, dict) else None
    if versao != EXPORT_VERSION:
        raise UnknownExportVersion(
            f"Versão do arquivo de exportação não reconhecida ({versao!r}); "
            f"este mini-tars só importa a versão {EXPORT_VERSION}.")

    itens = data.get("facts")
    if not isinstance(itens, list):
        raise InvalidExportFile("Campo `facts` ausente ou não é uma lista.")
    facts = [_parse_fact(item) for item in itens]
    _check_facts(facts)
    service.import_all(facts)
    return len(facts)
