import re
from typing import Optional

from pysqlsync.formation.object_types import Column, ObjectFactory, Table
from pysqlsync.model.data_types import SqlTimestampType, SqlIntegerType
from pysqlsync.model.id_types import LocalId

_sql_quoted_str_table = str.maketrans(
    {
        "\\": "\\\\",
        "'": "\\'",
        '"': '\\"',
        "\0": "\\0",
        "\b": "\\b",
        "\f": "\\f",
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
    }
)


def sql_quoted_string(text: str) -> str:
    if re.search(r"[\\\0\b\f\n\r\t]", text):
        text = text.translate(_sql_quoted_str_table)
    elif "'" in text:
        text = text.replace("'", "''")
    return f"'{text}'"


class SnowflakeTable(Table):
    def create_stmt(self) -> str:
        defs: list[str] = []
        defs.extend(str(c) for c in self.columns.values())
        defs.append(self.create_keys())
        definitions = ",\n".join(defs)
        comment = (
            f"\nCOMMENT = {sql_quoted_string(self.description)}"
            if self.description
            else ""
        )
        return f"CREATE TABLE {self.name} (\n{definitions}\n){comment};"

    @property
    def primary_key_constraint_id(self) -> LocalId:
        return LocalId(f"pk_{self.name.local_id.replace('.', '_')}")


class SnowflakeColumn(Column):
    @property
    def default_expr(self) -> str:
    if self.identity is True:
        return ""

    if self.default is None:
        if isinstance(self.data_type, SqlIntegerType):
            return " DEFAULT 0"
        else:
            return ""

    if isinstance(self.data_type, SqlTimestampType):
        m = re.match(
            r"^'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}) (?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})'$",
            self.default,
        )
        if m:
            return f" DEFAULT TIMESTAMP {self.default}"

    return f" DEFAULT {self.default}"

    @property
    def data_spec(self) -> str:
        nullable = " NOT NULL" if not self.nullable and not self.identity else ""
        default = self.default_expr
        identity = " IDENTITY" if self.identity else ""
        description = f" COMMENT {self.comment}" if self.description is not None else ""
        return f"{self.data_type}{nullable}{default}{identity}{description}"

    @property
    def comment(self) -> Optional[str]:
        if self.description is not None:
            return sql_quoted_string(self.description)
        else:
            return None


class SnowflakeObjectFactory(ObjectFactory):
    @property
    def column_class(self) -> type[Column]:
        return SnowflakeColumn

    @property
    def table_class(self) -> type[Table]:
        return SnowflakeTable
