import re
from typing import Optional

from pysqlsync.formation.object_types import Column, Namespace, ObjectFactory, Table
from pysqlsync.model.id_types import LocalId

_sql_quoted_str_table = str.maketrans(
    {
        "\\": "\\\\",
        "'": "\\'",
        '"': '\\"',
        "\0": "\\0",
        "\b": "\\b",
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
        "\u001A": "\\Z",
    }
)


def sql_quoted_string(text: str) -> str:
    if re.search(r"[\\'\"\0\b\n\r\t\u001A]", text):
        text = text.translate(_sql_quoted_str_table)
    return f"'{text}'"


class DeltaTable(Table):
    def create_stmt(self) -> str:
        defs: list[str] = []
        defs.extend(str(c) for c in self.columns.values())
        defs.append(self.create_keys())
        definition = ",\n".join(defs)
        comment = (
            f"\nCOMMENT {sql_quoted_string(self.description)}"
            if self.description
            else ""
        )
        return f"CREATE TABLE {self.name} (\n{definition}\n){comment};"

    @property
    def primary_key_constraint_id(self) -> LocalId:
        return LocalId(f"pk_{self.name.local_id.replace('.', '_')}")


class DeltaColumn(Column):
    @property
    def data_spec(self) -> str:
        nullable = " NOT NULL" if not self.nullable and not self.identity else ""
        identity = " GENERATED BY DEFAULT AS IDENTITY" if self.identity else ""
        description = f" COMMENT {self.comment}" if self.description is not None else ""

        # DEFAULT requires TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'enabled')
        # default = f" DEFAULT {self.default}" if self.default is not None else ""

        return f"{self.data_type}{nullable}{identity}{description}"

    @property
    def comment(self) -> Optional[str]:
        if self.description is not None:
            return sql_quoted_string(self.description)
        else:
            return None


class DeltaNamespace(Namespace):
    def create_schema_stmt(self) -> Optional[str]:
        if self.name.local_id:
            return f"CREATE SCHEMA IF NOT EXISTS {self.name};"
        else:
            return None

    def drop_schema_stmt(self) -> Optional[str]:
        if self.name.local_id:
            return f"DROP SCHEMA IF EXISTS {self.name} CASCADE;"
        else:
            return None


class DeltaObjectFactory(ObjectFactory):
    @property
    def column_class(self) -> type[Column]:
        return DeltaColumn

    @property
    def table_class(self) -> type[Table]:
        return DeltaTable

    @property
    def namespace_class(self) -> type[Namespace]:
        return DeltaNamespace
