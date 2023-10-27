import ipaddress
import typing
import unittest
from datetime import date, datetime, time, timezone

from strong_typing.inspection import DataclassInstance

import tests.tables as tables
from pysqlsync.base import BaseGenerator, GeneratorOptions
from pysqlsync.factory import get_dialect


def get_generator(dialect: str) -> BaseGenerator:
    return get_dialect(dialect).create_generator(
        GeneratorOptions(namespaces={tables: None})
    )


def get_create_stmt(table: type[DataclassInstance], dialect: str) -> str:
    statement = get_generator(dialect=dialect).create(tables=[table])
    return statement or ""


class TestGenerator(unittest.TestCase):
    def test_create_boolean_table(self) -> None:
        self.maxDiff = None
        self.assertMultiLineEqual(
            get_create_stmt(tables.BooleanTable, dialect="postgresql"),
            'CREATE TABLE "BooleanTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"boolean" boolean NOT NULL,\n'
            '"nullable_boolean" boolean,\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )
        self.assertMultiLineEqual(
            get_create_stmt(tables.BooleanTable, dialect="mssql"),
            'CREATE TABLE "BooleanTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"boolean" bit NOT NULL,\n'
            '"nullable_boolean" bit,\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )
        self.assertMultiLineEqual(
            get_create_stmt(tables.BooleanTable, dialect="mysql"),
            'CREATE TABLE "BooleanTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"boolean" tinyint NOT NULL,\n'
            '"nullable_boolean" tinyint,\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )

    def test_create_numeric_table(self) -> None:
        self.maxDiff = None
        for dialect in ["postgresql", "mssql", "mysql"]:
            with self.subTest(dialect=dialect):
                self.assertMultiLineEqual(
                    get_create_stmt(tables.NumericTable, dialect=dialect),
                    'CREATE TABLE "NumericTable" (\n'
                    '"id" bigint NOT NULL,\n'
                    '"signed_integer_8" smallint NOT NULL,\n'
                    '"signed_integer_16" smallint NOT NULL,\n'
                    '"signed_integer_32" integer NOT NULL,\n'
                    '"signed_integer_64" bigint NOT NULL,\n'
                    '"unsigned_integer_8" smallint NOT NULL,\n'
                    '"unsigned_integer_16" smallint NOT NULL,\n'
                    '"unsigned_integer_32" integer NOT NULL,\n'
                    '"unsigned_integer_64" bigint NOT NULL,\n'
                    '"integer" bigint NOT NULL,\n'
                    '"nullable_integer" bigint,\n'
                    'PRIMARY KEY ("id")\n'
                    ");",
                )

    def test_create_fixed_precision_float_table(self) -> None:
        self.maxDiff = None
        for dialect in ["postgresql", "mssql", "mysql"]:
            with self.subTest(dialect=dialect):
                self.assertMultiLineEqual(
                    get_create_stmt(tables.FixedPrecisionFloatTable, dialect=dialect),
                    'CREATE TABLE "FixedPrecisionFloatTable" (\n'
                    '"id" bigint NOT NULL,\n'
                    '"float_32" real NOT NULL,\n'
                    '"float_64" double precision NOT NULL,\n'
                    '"optional_float_32" real,\n'
                    '"optional_float_64" double precision,\n'
                    'PRIMARY KEY ("id")\n'
                    ");",
                )

    def test_create_decimal_table(self) -> None:
        self.maxDiff = None
        for dialect in ["postgresql", "mssql", "mysql"]:
            with self.subTest(dialect=dialect):
                self.assertMultiLineEqual(
                    get_create_stmt(tables.DecimalTable, dialect=dialect),
                    'CREATE TABLE "DecimalTable" (\n'
                    '"id" bigint NOT NULL,\n'
                    '"decimal_value" decimal NOT NULL,\n'
                    '"optional_decimal" decimal,\n'
                    '"decimal_precision" decimal(5, 2) NOT NULL,\n'
                    'PRIMARY KEY ("id")\n'
                    ");",
                )

    def test_create_string_table(self) -> None:
        self.maxDiff = None
        self.assertMultiLineEqual(
            get_create_stmt(tables.StringTable, dialect="postgresql"),
            'CREATE TABLE "StringTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"arbitrary_length_string" text NOT NULL,\n'
            '"nullable_arbitrary_length_string" text,\n'
            '"maximum_length_string" varchar(128) NOT NULL,\n'
            '"nullable_maximum_length_string" varchar(128),\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )
        self.assertMultiLineEqual(
            get_create_stmt(tables.StringTable, dialect="mssql"),
            'CREATE TABLE "StringTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"arbitrary_length_string" varchar(max) NOT NULL,\n'
            '"nullable_arbitrary_length_string" varchar(max),\n'
            '"maximum_length_string" varchar(128) NOT NULL,\n'
            '"nullable_maximum_length_string" varchar(128),\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )
        self.assertMultiLineEqual(
            get_create_stmt(tables.StringTable, dialect="mysql"),
            'CREATE TABLE "StringTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"arbitrary_length_string" mediumtext NOT NULL,\n'
            '"nullable_arbitrary_length_string" mediumtext,\n'
            '"maximum_length_string" varchar(128) NOT NULL,\n'
            '"nullable_maximum_length_string" varchar(128),\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )

    def test_create_date_time_table(self) -> None:
        self.maxDiff = None
        self.assertMultiLineEqual(
            get_create_stmt(tables.DateTimeTable, dialect="postgresql"),
            'CREATE TABLE "DateTimeTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"iso_date_time" timestamp NOT NULL,\n'
            '"iso_date" date NOT NULL,\n'
            '"iso_time" time NOT NULL,\n'
            '"optional_date_time" timestamp,\n'
            '"timestamp_precision" timestamp(6) NOT NULL,\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )
        self.assertMultiLineEqual(
            get_create_stmt(tables.DateTimeTable, dialect="mssql"),
            'CREATE TABLE "DateTimeTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"iso_date_time" datetime2 NOT NULL,\n'
            '"iso_date" date NOT NULL,\n'
            '"iso_time" time NOT NULL,\n'
            '"optional_date_time" datetime2,\n'
            '"timestamp_precision" datetime2 NOT NULL,\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )
        self.assertMultiLineEqual(
            get_create_stmt(tables.DateTimeTable, dialect="mysql"),
            'CREATE TABLE "DateTimeTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"iso_date_time" datetime NOT NULL,\n'
            '"iso_date" date NOT NULL,\n'
            '"iso_time" time NOT NULL,\n'
            '"optional_date_time" datetime,\n'
            '"timestamp_precision" datetime(6) NOT NULL,\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )

    def test_create_enum_table(self) -> None:
        self.maxDiff = None
        self.assertMultiLineEqual(
            get_create_stmt(tables.EnumTable, dialect="postgresql"),
            """CREATE TYPE "WorkflowState" AS ENUM ('active', 'inactive', 'deleted');\n"""
            'CREATE TABLE "EnumTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"state" "WorkflowState" NOT NULL,\n'
            '"optional_state" "WorkflowState",\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )
        self.assertMultiLineEqual(
            get_create_stmt(tables.EnumTable, dialect="mysql"),
            'CREATE TABLE "EnumTable" (\n'
            '"id" bigint NOT NULL,\n'
            """"state" ENUM ('active', 'inactive', 'deleted') CHARACTER SET ascii COLLATE ascii_bin NOT NULL,\n"""
            """"optional_state" ENUM ('active', 'inactive', 'deleted') CHARACTER SET ascii COLLATE ascii_bin,\n"""
            'PRIMARY KEY ("id")\n'
            ");",
        )
        self.assertMultiLineEqual(
            get_create_stmt(tables.EnumTable, dialect="mssql"),
            'CREATE TABLE "EnumTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"state" integer NOT NULL,\n'
            '"optional_state" integer,\n'
            'PRIMARY KEY ("id")\n'
            ");\n"
            'CREATE TABLE "WorkflowState" (\n'
            '"id" integer NOT NULL IDENTITY,\n'
            '"value" varchar(64) NOT NULL,\n'
            'PRIMARY KEY ("id")\n'
            ");\n"
            'ALTER TABLE "EnumTable" ADD\n'
            'CONSTRAINT "fk_EnumTable_state" FOREIGN KEY ("state") REFERENCES "WorkflowState" ("id"),\n'
            'CONSTRAINT "fk_EnumTable_optional_state" FOREIGN KEY ("optional_state") REFERENCES "WorkflowState" ("id")\n'
            ";\n"
            'ALTER TABLE "WorkflowState" ADD\n'
            'CONSTRAINT "uq_WorkflowState" UNIQUE ("value")\n'
            ";",
        )

    def test_create_ipaddress_table(self) -> None:
        self.maxDiff = None
        self.assertMultiLineEqual(
            get_create_stmt(tables.IPAddressTable, dialect="postgresql"),
            'CREATE TABLE "IPAddressTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"ipv4" inet NOT NULL,\n'
            '"ipv6" inet NOT NULL,\n'
            '"optional_ipv4" inet,\n'
            '"optional_ipv6" inet,\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )
        for dialect in ["mssql", "mysql"]:
            with self.subTest(dialect=dialect):
                self.assertMultiLineEqual(
                    get_create_stmt(tables.IPAddressTable, dialect=dialect),
                    'CREATE TABLE "IPAddressTable" (\n'
                    '"id" bigint NOT NULL,\n'
                    '"ipv4" binary(4) NOT NULL,\n'
                    '"ipv6" binary(16) NOT NULL,\n'
                    '"optional_ipv4" binary(4),\n'
                    '"optional_ipv6" binary(16),\n'
                    'PRIMARY KEY ("id")\n'
                    ");",
                )

    def test_create_primary_key_table(self) -> None:
        self.maxDiff = None
        self.assertMultiLineEqual(
            get_create_stmt(tables.DataTable, dialect="postgresql"),
            'CREATE TABLE "DataTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"data" text NOT NULL,\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )
        self.assertMultiLineEqual(
            get_create_stmt(tables.DataTable, dialect="mssql"),
            'CREATE TABLE "DataTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"data" varchar(max) NOT NULL,\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )
        self.assertMultiLineEqual(
            get_create_stmt(tables.DataTable, dialect="mysql"),
            'CREATE TABLE "DataTable" (\n'
            '"id" bigint NOT NULL,\n'
            '"data" mediumtext NOT NULL,\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )

    def test_create_table_with_description(self) -> None:
        self.maxDiff = None
        self.assertMultiLineEqual(
            get_create_stmt(tables.Person, dialect="postgresql"),
            'CREATE TABLE "Address" (\n'
            '"id" bigint NOT NULL,\n'
            '"city" text NOT NULL,\n'
            '"state" text,\n'
            'PRIMARY KEY ("id")\n'
            ");\n"
            'CREATE TABLE "Person" (\n'
            '"id" bigint NOT NULL,\n'
            '"address" bigint NOT NULL,\n'
            'PRIMARY KEY ("id")\n'
            ");\n"
            """COMMENT ON TABLE "Person" IS 'A person.';\n"""
            """COMMENT ON COLUMN "Person"."address" IS 'The address of the person''s permanent residence.';\n"""
            'ALTER TABLE "Person"\n'
            'ADD CONSTRAINT "fk_Person_address" FOREIGN KEY ("address") REFERENCES "Address" ("id")\n'
            ";",
        )
        self.assertMultiLineEqual(
            get_create_stmt(tables.Person, dialect="mysql"),
            'CREATE TABLE "Address" (\n'
            '"id" bigint NOT NULL,\n'
            '"city" mediumtext NOT NULL,\n'
            '"state" mediumtext,\n'
            'PRIMARY KEY ("id")\n'
            ");\n"
            'CREATE TABLE "Person" (\n'
            '"id" bigint NOT NULL,\n'
            """"address" bigint NOT NULL COMMENT 'The address of the person''s permanent residence.',\n"""
            'PRIMARY KEY ("id")\n'
            ")\n"
            "COMMENT = 'A person.';\n"
            'ALTER TABLE "Person"\n'
            'ADD CONSTRAINT "fk_Person_address" FOREIGN KEY ("address") REFERENCES "Address" ("id")\n'
            ";",
        )

    def test_create_type_with_description(self) -> None:
        self.maxDiff = None
        self.assertMultiLineEqual(
            get_create_stmt(tables.Location, dialect="postgresql"),
            'CREATE TYPE "Coordinates" AS (\n'
            '"lat" double precision,\n'
            '"long" double precision\n'
            ");\n"
            """COMMENT ON TYPE "Coordinates" IS 'Coordinates in the geographic coordinate system.';\n"""
            """COMMENT ON COLUMN "Coordinates"."lat" IS 'Latitude in degrees.';\n"""
            """COMMENT ON COLUMN "Coordinates"."long" IS 'Longitude in degrees.';\n"""
            'CREATE TABLE "Location" (\n'
            '"id" bigint NOT NULL,\n'
            '"coords" "Coordinates" NOT NULL,\n'
            'PRIMARY KEY ("id")\n'
            ");",
        )

    def test_insert_single(self) -> None:
        self.maxDiff = None
        generator = get_generator(dialect="postgresql")
        generator.create(tables=[tables.DataTable])
        self.assertMultiLineEqual(
            generator.get_dataclass_upsert_stmt(tables.DataTable),
            'INSERT INTO "DataTable"\n'
            '("id", "data") VALUES ($1, $2)\n'
            'ON CONFLICT ("id") DO UPDATE SET\n'
            '"data" = EXCLUDED."data"\n'
            ";",
        )

        generator = get_generator(dialect="mysql")
        generator.create(tables=[tables.DataTable])
        self.assertMultiLineEqual(
            generator.get_dataclass_upsert_stmt(tables.DataTable),
            'INSERT INTO "DataTable"\n'
            '("id", "data") VALUES (%s, %s)\n'
            "ON DUPLICATE KEY UPDATE\n"
            '"data" = VALUES("data")\n'
            ";",
        )

    def test_insert_multiple(self) -> None:
        self.maxDiff = None
        generator = get_generator(dialect="postgresql")
        generator.create(tables=[tables.BooleanTable])
        self.assertMultiLineEqual(
            generator.get_dataclass_upsert_stmt(tables.BooleanTable),
            'INSERT INTO "BooleanTable"\n'
            '("id", "boolean", "nullable_boolean") VALUES ($1, $2, $3)\n'
            'ON CONFLICT ("id") DO UPDATE SET\n'
            '"boolean" = EXCLUDED."boolean",\n'
            '"nullable_boolean" = EXCLUDED."nullable_boolean"\n'
            ";",
        )

        generator = get_generator(dialect="mysql")
        generator.create(tables=[tables.BooleanTable])
        self.assertMultiLineEqual(
            generator.get_dataclass_upsert_stmt(tables.BooleanTable),
            'INSERT INTO "BooleanTable"\n'
            '("id", "boolean", "nullable_boolean") VALUES (%s, %s, %s)\n'
            "ON DUPLICATE KEY UPDATE\n"
            '"boolean" = VALUES("boolean"),\n'
            '"nullable_boolean" = VALUES("nullable_boolean")\n'
            ";",
        )

    def test_table_data(self) -> None:
        generator = get_generator(dialect="postgresql")
        generator.create(
            tables=[
                tables.DataTable,
                tables.DateTimeTable,
                tables.EnumTable,
                tables.IPAddressTable,
                tables.StringTable,
            ]
        )

        self.assertEqual(
            generator.get_dataclass_as_record(tables.DataTable(123, "abc")),
            (123, "abc"),
        )
        self.assertEqual(
            generator.get_dataclass_as_record(
                tables.StringTable(1, "abc", None, "def", None)
            ),
            (1, "abc", None, "def", None),
        )
        self.assertEqual(
            generator.get_dataclass_as_record(
                tables.StringTable(2, "abc", "def", "ghi", "jkl")
            ),
            (2, "abc", "def", "ghi", "jkl"),
        )
        self.assertEqual(
            generator.get_dataclass_as_record(
                tables.DateTimeTable(
                    1,
                    datetime(1982, 10, 23, 23, 59, 59, tzinfo=timezone.utc),
                    date(2023, 1, 1),
                    time(23, 59, 59, tzinfo=timezone.utc),
                    None,
                    datetime(1984, 1, 1, 23, 59, 59, tzinfo=timezone.utc),
                )
            ),
            (
                1,
                datetime(1982, 10, 23, 23, 59, 59, tzinfo=timezone.utc),
                date(2023, 1, 1),
                time(23, 59, 59, tzinfo=timezone.utc),
                None,
                datetime(1984, 1, 1, 23, 59, 59, tzinfo=timezone.utc),
            ),
        )
        self.assertEqual(
            generator.get_dataclass_as_record(
                tables.EnumTable(1, tables.WorkflowState.active, None)
            ),
            (1, "active", None),
        )
        self.assertEqual(
            generator.get_dataclass_as_record(
                tables.IPAddressTable(
                    1,
                    ipaddress.IPv4Address("192.168.0.1"),
                    ipaddress.IPv6Address("2001:db8::"),
                    None,
                    None,
                )
            ),
            (
                1,
                ipaddress.IPv4Address("192.168.0.1"),
                ipaddress.IPv6Address("2001:db8::"),
                None,
                None,
            ),
        )


if __name__ == "__main__":
    unittest.main()
