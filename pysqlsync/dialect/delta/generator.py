import datetime
import ipaddress
import uuid

from strong_typing.auxiliary import float32, float64
from strong_typing.core import JsonType

from pysqlsync.base import BaseGenerator, GeneratorOptions
from pysqlsync.formation.mutation import Mutator
from pysqlsync.formation.object_types import FormationError
from pysqlsync.formation.py_to_sql import (
    ArrayMode,
    DataclassConverter,
    DataclassConverterOptions,
    EnumMode,
    NamespaceMapping,
    StructMode,
)
from pysqlsync.model.data_types import SqlVariableCharacterType
from pysqlsync.util.typing import override

from .data_types import (
    DeltaDoubleType,
    DeltaFixedBinaryType,
    DeltaRealType,
    DeltaTimestampType,
    DeltaVariableCharacterType,
)
from .object_types import DeltaObjectFactory


class DeltaGenerator(BaseGenerator):
    "Generator for Delta Lake on Databricks."

    converter: DataclassConverter

    def __init__(self, options: GeneratorOptions) -> None:
        super().__init__(
            options,
            DeltaObjectFactory(),
            Mutator(options.synchronization),
        )

        if (
            options.enum_mode is EnumMode.INLINE
            or options.enum_mode is EnumMode.RELATION
            or options.enum_mode is EnumMode.TYPE
        ):
            raise FormationError(
                f"unsupported enum conversion mode for {self.__class__.__name__}: {options.enum_mode}"
            )
        if options.struct_mode is StructMode.TYPE:
            raise FormationError(
                f"unsupported struct conversion mode for {self.__class__.__name__}: {options.struct_mode}"
            )

        self.converter = DataclassConverter(
            options=DataclassConverterOptions(
                enum_mode=options.enum_mode or EnumMode.CHECK,
                struct_mode=options.struct_mode or StructMode.INLINE,
                array_mode=options.array_mode or ArrayMode.ARRAY,
                namespaces=NamespaceMapping(options.namespaces),
                check_constraints=False,
                foreign_constraints=False,
                initialize_tables=options.initialize_tables,
                substitutions={
                    datetime.datetime: DeltaTimestampType(),
                    float: DeltaDoubleType(),
                    float32: DeltaRealType(),
                    float64: DeltaDoubleType(),
                    str: DeltaVariableCharacterType(),
                    uuid.UUID: DeltaFixedBinaryType(16),
                    JsonType: SqlVariableCharacterType(),
                    ipaddress.IPv4Address: DeltaFixedBinaryType(4),
                    ipaddress.IPv6Address: DeltaFixedBinaryType(16),
                },
                skip_annotations=options.skip_annotations,
                factory=self.factory,
            )
        )

    @override
    def placeholder(self, index: int) -> str:
        return f":{index}"
