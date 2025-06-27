import struct
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO, Literal, Optional, Self

from pydantic import BaseModel, NonNegativeInt

QVMMajorVersion = Literal[8]

QVMMinorVersion = Literal[5, 7]


class QVMInstruction(BaseModel, ABC):
    address: NonNegativeInt
    address_next: NonNegativeInt

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        return cls(address=address, address_next=stream.tell())

    @property
    def operator(self) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} does not have an operator")

    @property
    def priority(self) -> int:
        raise NotImplementedError(f"{self.__class__.__name__} does not have a priority")


class UnsupportedQVMInstruction(QVMInstruction, ABC):
    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        raise NotImplementedError(f"{cls.__name__} is not implemented")


# Unsupported instructions


# noinspection DuplicatedCode
class InstructionNOP(UnsupportedQVMInstruction):
    pass


class InstructionRET(UnsupportedQVMInstruction):
    pass


class InstructionBT(UnsupportedQVMInstruction):
    pass


class InstructionJSR(UnsupportedQVMInstruction):
    pass


class InstructionPUSHA(UnsupportedQVMInstruction):
    pass


class InstructionPUSHS(UnsupportedQVMInstruction):
    pass


class InstructionPUSHI(UnsupportedQVMInstruction):
    pass


class InstructionBLK(UnsupportedQVMInstruction):
    pass


class InstructionILLEGAL(UnsupportedQVMInstruction):
    pass


# Instructions with arguments


def read_argument(stream: BinaryIO, argument_format: str) -> tuple[Any, ...]:
    argument_bytes = stream.read(struct.calcsize(argument_format))
    argument = struct.unpack(argument_format, argument_bytes)
    return argument


# noinspection DuplicatedCode
class InstructionPUSH(QVMInstruction):
    argument: int

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        argument = read_argument(stream, "<I")[0]
        return cls(address=address, address_next=stream.tell(), argument=argument)


class InstructionPUSHB(QVMInstruction):
    argument: int

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        argument = read_argument(stream, "<B")[0]
        return cls(address=address, address_next=stream.tell(), argument=argument)


class InstructionPUSHW(QVMInstruction):
    argument: int

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        argument = read_argument(stream, "<H")[0]
        return cls(address=address, address_next=stream.tell(), argument=argument)


class InstructionPUSHF(QVMInstruction):
    argument: float

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        argument = read_argument(stream, "<f")[0]
        return cls(address=address, address_next=stream.tell(), argument=argument)


# noinspection DuplicatedCode
class InstructionPUSHSI(QVMInstruction):
    argument: int

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        argument = read_argument(stream, "<I")[0]
        return cls(address=address, address_next=stream.tell(), argument=argument)


class InstructionPUSHSIB(QVMInstruction):
    argument: int

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        argument = read_argument(stream, "<B")[0]
        return cls(address=address, address_next=stream.tell(), argument=argument)


class InstructionPUSHSIW(QVMInstruction):
    argument: int

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        argument = read_argument(stream, "<H")[0]
        return cls(address=address, address_next=stream.tell(), argument=argument)


# noinspection DuplicatedCode
class InstructionPUSHII(QVMInstruction):
    argument: int

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        argument = read_argument(stream, "<I")[0]
        return cls(address=address, address_next=stream.tell(), argument=argument)


class InstructionPUSHIIB(QVMInstruction):
    argument: int

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        argument = read_argument(stream, "<B")[0]
        return cls(address=address, address_next=stream.tell(), argument=argument)


class InstructionPUSHIIW(QVMInstruction):
    argument: int

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        argument = read_argument(stream, "<H")[0]
        return cls(address=address, address_next=stream.tell(), argument=argument)


class InstructionBRA(QVMInstruction):
    argument: int

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        argument = read_argument(stream, "<i")[0]
        return cls(address=address, address_next=stream.tell(), argument=argument)


class InstructionBF(QVMInstruction):
    argument: int

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        argument = read_argument(stream, "<i")[0]
        return cls(address=address, address_next=stream.tell(), argument=argument)


class InstructionCALL(QVMInstruction):
    argument: list[int]

    @classmethod
    def model_validate_stream(cls, stream: BinaryIO, address: NonNegativeInt) -> Self:
        argument_count: int = read_argument(stream, "<I")[0]
        argument_bytes = stream.read(4 * argument_count)
        argument = struct.unpack("<" + "i" * argument_count, argument_bytes)
        return cls(address=address, address_next=stream.tell(), argument=argument)


# Instructions without arguments


# noinspection DuplicatedCode
class InstructionPUSH0(QVMInstruction):
    pass


class InstructionPUSH1(QVMInstruction):
    pass


class InstructionPUSHM(QVMInstruction):
    pass


class InstructionPOP(QVMInstruction):
    pass


class InstructionADD(QVMInstruction):
    @property
    def operator(self) -> str:
        return "+"

    @property
    def priority(self) -> int:
        return 4


class InstructionSUB(QVMInstruction):
    @property
    def operator(self) -> str:
        return "-"

    @property
    def priority(self) -> int:
        return 4


class InstructionMUL(QVMInstruction):
    @property
    def operator(self) -> str:
        return "*"

    @property
    def priority(self) -> int:
        return 3


class InstructionDIV(QVMInstruction):
    @property
    def operator(self) -> str:
        return "/"

    @property
    def priority(self) -> int:
        return 3


class InstructionSHL(QVMInstruction):
    @property
    def operator(self) -> str:
        return "<<"

    @property
    def priority(self) -> int:
        return 5


class InstructionSHR(QVMInstruction):
    @property
    def operator(self) -> str:
        return ">>"

    @property
    def priority(self) -> int:
        return 5


class InstructionAND(QVMInstruction):
    @property
    def operator(self) -> str:
        return "&"

    @property
    def priority(self) -> int:
        return 8


class InstructionOR(QVMInstruction):
    @property
    def operator(self) -> str:
        return "|"

    @property
    def priority(self) -> int:
        return 10


class InstructionXOR(QVMInstruction):
    @property
    def operator(self) -> str:
        return "^"

    @property
    def priority(self) -> int:
        return 9


class InstructionLAND(QVMInstruction):
    @property
    def operator(self) -> str:
        return "&&"

    @property
    def priority(self) -> int:
        return 11


class InstructionLOR(QVMInstruction):
    @property
    def operator(self) -> str:
        return "||"

    @property
    def priority(self) -> int:
        return 12


class InstructionEQ(QVMInstruction):
    @property
    def operator(self) -> str:
        return "=="

    @property
    def priority(self) -> int:
        return 7


class InstructionNE(QVMInstruction):
    @property
    def operator(self) -> str:
        return "!="

    @property
    def priority(self) -> int:
        return 7


class InstructionLT(QVMInstruction):
    @property
    def operator(self) -> str:
        return "<"

    @property
    def priority(self) -> int:
        return 6


class InstructionLE(QVMInstruction):
    @property
    def operator(self) -> str:
        return "<="

    @property
    def priority(self) -> int:
        return 6


class InstructionGT(QVMInstruction):
    @property
    def operator(self) -> str:
        return ">"

    @property
    def priority(self) -> int:
        return 6


class InstructionGE(QVMInstruction):
    @property
    def operator(self) -> str:
        return ">="

    @property
    def priority(self) -> int:
        return 6


class InstructionASSIGN(QVMInstruction):
    @property
    def operator(self) -> str:
        return "="

    @property
    def priority(self) -> int:
        return 14


class InstructionPLUS(QVMInstruction):
    @property
    def operator(self) -> str:
        return "+"

    @property
    def priority(self) -> int:
        return 2


class InstructionMINUS(QVMInstruction):
    @property
    def operator(self) -> str:
        return "-"

    @property
    def priority(self) -> int:
        return 2


class InstructionINV(QVMInstruction):
    @property
    def operator(self) -> str:
        return "~"

    @property
    def priority(self) -> int:
        return 2


class InstructionNOT(QVMInstruction):
    @property
    def operator(self) -> str:
        return "!"

    @property
    def priority(self) -> int:
        return 2


class InstructionBRK(QVMInstruction):
    pass


# AST


class ASTNode(BaseModel, ABC):
    @abstractmethod
    def get_token(self, indent: int = 0) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} does not have a token")


class NumberLiteral(ASTNode):
    value: int | float

    def get_token(self, indent: int = 0) -> str:
        return f"{self.value}"


class StringLiteral(ASTNode):
    value: str

    def get_token(self, indent: int = 0) -> str:
        return f'"{self.value}"'


class IdentifierLiteral(ASTNode):
    value: str

    def get_token(self, indent: int = 0) -> str:
        return f"{self.value}"


class UnaryOperator(ASTNode):
    operator: str
    operand: ASTNode
    priority: int

    def get_token(self, indent: int = 0) -> str:
        operand_token = self.operand.get_token(indent=indent + 1)
        return f"{self.operator}{operand_token}"


class BinaryOperator(ASTNode):
    operator: str
    left_operand: ASTNode
    right_operand: ASTNode
    priority: int

    def get_token(self, indent: int = 0) -> str:
        left_operand_token = self.left_operand.get_token(indent=indent + 1)
        right_operand_token = self.right_operand.get_token(indent=indent + 1)
        return f"{left_operand_token} {self.operator} {right_operand_token}"


class Parentheses(ASTNode):
    expression: ASTNode

    def get_token(self, indent: int = 0) -> str:
        expression_token = self.expression.get_token(indent=indent + 1)
        return f"({expression_token})"


class CallStatement(ASTNode):
    function: ASTNode
    arguments: list[ASTNode]

    def get_token(self, indent: int = 0) -> str:
        function_token = self.function.get_token(indent=indent + 1)
        token_length = len(function_token)
        token_list = []

        for argument in self.arguments:
            argument_token = argument.get_token(indent=indent + 1)

            if isinstance(argument, CallStatement):
                argument_token_indent = "\t" * (indent + 1)
                argument_token = f"\n{argument_token_indent}{argument_token}"
                token_length = len(argument_token) + 2
            elif len(argument_token) + token_length > 300:
                argument_token = f"\n{argument_token}"
                token_length = len(argument_token) + 2
            else:
                token_length += len(argument_token) + 2

            token_list.append(argument_token)

        arguments_token = ", ".join(token_list)
        token = f"{function_token}({arguments_token})"

        return token


class WhileStatement(ASTNode):
    condition: ASTNode
    body: "StatementList"

    def get_token(self, indent: int = 0) -> str:
        token = ""
        token += f"{indent * '\t'}while({self.condition.get_token(indent + 1)})\n"
        token += f"{indent * '\t'}{{\n"

        for statement in self.body.statements:
            if isinstance(statement, (IfStatement, WhileStatement)):
                token += f"{statement.get_token(indent + 1)}\n"
            else:
                token += f"{(indent + 1) * '\t'}{statement.get_token(indent + 1)};\n"

        token += f"{indent * '\t'}}}\n"

        return token


class IfStatement(ASTNode):
    condition: ASTNode
    body: "StatementList"
    else_body: Optional["StatementList"] = None

    def get_token(self, indent: int = 0) -> str:
        condition_token = self.condition.get_token(indent=indent + 1)
        condition_token_indent = "\t" * indent

        token_indent_string = "\t" * indent

        token = f"{condition_token_indent}if({condition_token})\n"
        token += self.get_statements_token(self.body.statements, indent=indent)

        if self.else_body:
            token += f"{token_indent_string}else\n"
            token += self.get_statements_token(self.else_body.statements, indent=indent)

        return token

    @classmethod
    def get_statements_token(cls, statements: list[ASTNode], indent: int = 0) -> str:
        statements_token_indent = "\t" * indent
        statements_token = ""
        statements_token += f"{statements_token_indent}{{\n"

        for statement in statements:
            statement_token_indent = "\t" * (indent + 1)
            statement_token = statement.get_token(indent=indent + 1)

            if not isinstance(statement, (IfStatement, WhileStatement)):
                statement_token = f"{statement_token_indent}{statement_token};\n"

            statements_token += statement_token

        statements_token += f"{statements_token_indent}}}\n"

        return statements_token


class StatementList(ASTNode):
    statements: list[ASTNode]

    @classmethod
    def from_instructions(
        cls,
        identifiers: list[str],
        strings: list[str],
        instructions: dict[NonNegativeInt, QVMInstruction],
        start_address: NonNegativeInt = 0,
        stop_address: NonNegativeInt | None = None,
    ) -> Self:
        statements: list[ASTNode] = []

        current_address = start_address

        while current_address != stop_address:
            current_instruction = instructions[current_address]

            match current_instruction.__class__.__qualname__:
                case "InstructionBRK" | "InstructionBRA":
                    break

                case "InstructionPOP":
                    current_address = current_instruction.address_next

                case "InstructionPUSH" | "InstructionPUSHB" | "InstructionPUSHW" | "InstructionPUSHF":
                    statement = NumberLiteral(value=current_instruction.argument)
                    statements.append(statement)
                    current_address = current_instruction.address_next

                case "InstructionPUSH0":
                    statement = NumberLiteral(value=0)
                    statements.append(statement)
                    current_address = current_instruction.address_next

                case "InstructionPUSH1":
                    statement = NumberLiteral(value=1)
                    statements.append(statement)
                    current_address = current_instruction.address_next

                case "InstructionPUSHM":
                    statement = NumberLiteral(value=0xFFFFFFFF)
                    statements.append(statement)
                    current_address = current_instruction.address_next

                case "InstructionPUSHSI" | "InstructionPUSHSIB" | "InstructionPUSHSIW":
                    statement = StringLiteral(value=strings[current_instruction.argument])
                    statements.append(statement)
                    current_address = current_instruction.address_next

                case "InstructionPUSHII" | "InstructionPUSHIIB" | "InstructionPUSHIIW":
                    statement = IdentifierLiteral(value=identifiers[current_instruction.argument])
                    statements.append(statement)
                    current_address = current_instruction.address_next

                case "InstructionPLUS" | "InstructionMINUS" | "InstructionINV" | "InstructionNOT":
                    operand = statements.pop()

                    if isinstance(operand, (UnaryOperator, BinaryOperator)):
                        operand = Parentheses(expression=operand)

                    statement = UnaryOperator(
                        operator=current_instruction.operator,
                        operand=operand,
                        priority=current_instruction.priority,
                    )
                    statements.append(statement)
                    current_address = current_instruction.address_next

                case (
                    "InstructionADD"
                    | "InstructionSUB"
                    | "InstructionMUL"
                    | "InstructionDIV"
                    | "InstructionSHL"
                    | "InstructionSHR"
                    | "InstructionAND"
                    | "InstructionOR"
                    | "InstructionXOR"
                    | "InstructionLAND"
                    | "InstructionLOR"
                    | "InstructionEQ"
                    | "InstructionNE"
                    | "InstructionLT"
                    | "InstructionLE"
                    | "InstructionGT"
                    | "InstructionGE"
                    | "InstructionASSIGN"
                ):
                    right_operand = statements.pop()
                    left_operand = statements.pop()

                    if (
                        isinstance(right_operand, (UnaryOperator, BinaryOperator))
                        and current_instruction.priority < right_operand.priority
                    ):
                        right_operand = Parentheses(expression=right_operand)

                    if (
                        isinstance(left_operand, (UnaryOperator, BinaryOperator))
                        and current_instruction.priority < left_operand.priority
                    ):
                        left_operand = Parentheses(expression=left_operand)

                    statement = BinaryOperator(
                        operator=current_instruction.operator,
                        left_operand=left_operand,
                        right_operand=right_operand,
                        priority=current_instruction.priority,
                    )
                    statements.append(statement)
                    current_address = current_instruction.address_next

                case "InstructionCALL":
                    function = statements.pop()
                    arguments = []

                    for address in current_instruction.argument:
                        argument = cls.from_instructions(
                            identifiers=identifiers,
                            strings=strings,
                            instructions=instructions,
                            start_address=address,
                            stop_address=None,
                        )

                        if len(argument.statements) > 1:
                            raise ValueError(f"Unexpected statement count: {len(argument.statements)}")

                        argument = argument.statements[0]
                        arguments.append(argument)

                    statement = CallStatement(function=function, arguments=arguments)
                    statements.append(statement)

                    next_address = current_instruction.address_next
                    next_instruction = instructions[next_address]

                    current_address = next_instruction.address_next + next_instruction.argument

                case "InstructionBF":
                    condition = statements.pop()
                    body = cls.from_instructions(
                        identifiers=identifiers,
                        strings=strings,
                        instructions=instructions,
                        start_address=current_instruction.address_next,
                        stop_address=None,
                    )

                    next_address = current_instruction.address_next + current_instruction.argument - 5
                    next_instruction = instructions[next_address]

                    match next_instruction.argument:
                        case _ if next_instruction.argument < 0:
                            statement = WhileStatement(condition=condition, body=body)
                            current_address = current_instruction.address_next + current_instruction.argument

                        case 0:
                            statement = IfStatement(condition=condition, body=body)
                            current_address = current_instruction.address_next + current_instruction.argument

                        case _ if next_instruction.argument > 0:
                            else_body = cls.from_instructions(
                                identifiers=identifiers,
                                strings=strings,
                                instructions=instructions,
                                start_address=current_instruction.address_next + current_instruction.argument,
                                stop_address=next_instruction.address_next + next_instruction.argument,
                            )
                            statement = IfStatement(condition=condition, body=body, else_body=else_body)
                            current_address = next_instruction.address_next + next_instruction.argument
                        case _:
                            raise ValueError(f"Unsupported argument: {next_instruction.argument}")

                    statements.append(statement)
                case _:
                    raise ValueError(f"Unsupported instruction: {current_instruction.__class__.__qualname__}")

        return cls(statements=statements)

    def get_token(self, indent: int = 0) -> str:
        token = ""

        for statement in self.statements:
            statement_token = statement.get_token(indent=indent)

            if not isinstance(statement, (IfStatement, WhileStatement)):
                statement_token = f"{statement_token};\n"

            token += statement_token

        return token


# QVM


class QVMHeader(BaseModel):
    signature: Literal[b"LOOP"]
    major_version: QVMMajorVersion
    minor_version: QVMMinorVersion
    identifiers_points_offset: NonNegativeInt
    identifiers_data_offset: NonNegativeInt
    identifiers_points_size: NonNegativeInt
    identifiers_data_size: NonNegativeInt
    strings_points_offset: NonNegativeInt
    strings_data_offset: NonNegativeInt
    strings_points_size: NonNegativeInt
    strings_data_size: NonNegativeInt
    instructions_data_offset: NonNegativeInt
    instructions_data_size: NonNegativeInt
    unknown_1: Literal[0]
    unknown_2: Literal[0]
    footer_data_offset: NonNegativeInt | None = None

    @classmethod
    def model_validate_bytes(cls, data: bytes) -> "QVMHeader":
        obj_values = struct.unpack("4s14I", data[:60])
        obj_mapping = dict(zip(cls.__pydantic_fields__.keys(), obj_values, strict=False))
        obj = cls(**obj_mapping)

        if obj.minor_version == 5 and len(data[60:]) > 4:
            footer_offset = struct.unpack("I", data[60:64])[0]
            obj.footer_data_offset = footer_offset

        return obj

    @property
    def identifiers_data_slice(self) -> slice:
        return slice(self.identifiers_data_offset, self.identifiers_data_offset + self.identifiers_data_size)

    @property
    def strings_data_slice(self) -> slice:
        return slice(self.strings_data_offset, self.strings_data_offset + self.strings_data_size)

    @property
    def instructions_data_slice(self) -> slice:
        return slice(self.instructions_data_offset, self.instructions_data_offset + self.instructions_data_size)


class QVMStringList(BaseModel):
    value: list[str]

    @classmethod
    def model_validate_bytes(cls, data: bytes) -> Self:
        value_bytes = data.split(b"\x00")[:-1]
        value_strings = [value.decode("utf-8") for value in value_bytes]
        value = [value.replace("\n", "\\n").replace('"', '\\"') for value in value_strings]
        return cls(value=value)


class QVMInstructionDict(BaseModel):
    value: dict[NonNegativeInt, QVMInstruction]

    @classmethod
    def model_validate_bytes(cls, data: bytes, version: QVMMinorVersion) -> Self:
        stream = BytesIO(data)
        value = {}
        codes = cls.get_code_instruction_dict(version)

        while stream.tell() < len(data):
            address = stream.tell()
            instruction_class = codes.get(stream.read(1), UnsupportedQVMInstruction)
            instruction = instruction_class.model_validate_stream(stream, address)
            value[instruction.address] = instruction

        return cls(value=value)

    @classmethod
    def get_code_instruction_dict(cls, version: QVMMinorVersion) -> dict[bytes, type[QVMInstruction]]:
        match version:
            case 5:
                return cls.get_code_instruction_dict_v5()
            case 7:
                return cls.get_code_instruction_dict_v7()
            case _:
                raise ValueError(f"Unsupported QVM version: {version}")

    # noinspection DuplicatedCode
    @classmethod
    def get_code_instruction_dict_v5(cls) -> dict[bytes, type[QVMInstruction]]:
        return {
            b"\x00": InstructionBRK,
            b"\x01": InstructionNOP,
            b"\x02": InstructionPUSH,
            b"\x03": InstructionPUSHB,
            b"\x04": InstructionPUSHW,
            b"\x05": InstructionPUSHF,
            b"\x06": InstructionPUSHA,
            b"\x07": InstructionPUSHS,
            b"\x08": InstructionPUSHSI,
            b"\x09": InstructionPUSHSIB,
            b"\x0a": InstructionPUSHSIW,
            b"\x0b": InstructionPUSHI,
            b"\x0c": InstructionPUSHII,
            b"\x0d": InstructionPUSHIIB,
            b"\x0e": InstructionPUSHIIW,
            b"\x0f": InstructionPUSH0,
            b"\x10": InstructionPUSH1,
            b"\x11": InstructionPUSHM,
            b"\x12": InstructionPOP,
            b"\x13": InstructionRET,
            b"\x14": InstructionBRA,
            b"\x15": InstructionBF,
            b"\x16": InstructionBT,
            b"\x17": InstructionJSR,
            b"\x18": InstructionCALL,
            b"\x19": InstructionADD,
            b"\x1a": InstructionSUB,
            b"\x1b": InstructionMUL,
            b"\x1c": InstructionDIV,
            b"\x1d": InstructionSHL,
            b"\x1e": InstructionSHR,
            b"\x1f": InstructionAND,
            b"\x20": InstructionOR,
            b"\x21": InstructionXOR,
            b"\x22": InstructionLAND,
            b"\x23": InstructionLOR,
            b"\x24": InstructionEQ,
            b"\x25": InstructionNE,
            b"\x26": InstructionLT,
            b"\x27": InstructionLE,
            b"\x28": InstructionGT,
            b"\x29": InstructionGE,
            b"\x2a": InstructionASSIGN,
            b"\x2b": InstructionPLUS,
            b"\x2c": InstructionMINUS,
            b"\x2d": InstructionINV,
            b"\x2e": InstructionNOT,
            b"\x2f": InstructionBLK,
            b"\x30": InstructionILLEGAL,
        }

    # noinspection DuplicatedCode
    @classmethod
    def get_code_instruction_dict_v7(cls) -> dict[bytes, type[QVMInstruction]]:
        return {
            b"\x00": InstructionBRK,
            b"\x01": InstructionNOP,
            b"\x02": InstructionRET,
            b"\x03": InstructionBRA,
            b"\x04": InstructionBF,
            b"\x05": InstructionBT,
            b"\x06": InstructionJSR,
            b"\x07": InstructionCALL,
            b"\x08": InstructionPUSH,
            b"\x09": InstructionPUSHB,
            b"\x0a": InstructionPUSHW,
            b"\x0b": InstructionPUSHF,
            b"\x0c": InstructionPUSHA,
            b"\x0d": InstructionPUSHS,
            b"\x0e": InstructionPUSHSI,
            b"\x0f": InstructionPUSHSIB,
            b"\x10": InstructionPUSHSIW,
            b"\x11": InstructionPUSHI,
            b"\x12": InstructionPUSHII,
            b"\x13": InstructionPUSHIIB,
            b"\x14": InstructionPUSHIIW,
            b"\x15": InstructionPUSH0,
            b"\x16": InstructionPUSH1,
            b"\x17": InstructionPUSHM,
            b"\x18": InstructionPOP,
            b"\x19": InstructionADD,
            b"\x1a": InstructionSUB,
            b"\x1b": InstructionMUL,
            b"\x1c": InstructionDIV,
            b"\x1d": InstructionSHL,
            b"\x1e": InstructionSHR,
            b"\x1f": InstructionAND,
            b"\x20": InstructionOR,
            b"\x21": InstructionXOR,
            b"\x22": InstructionLAND,
            b"\x23": InstructionLOR,
            b"\x24": InstructionEQ,
            b"\x25": InstructionNE,
            b"\x26": InstructionLT,
            b"\x27": InstructionLE,
            b"\x28": InstructionGT,
            b"\x29": InstructionGE,
            b"\x2a": InstructionASSIGN,
            b"\x2b": InstructionPLUS,
            b"\x2c": InstructionMINUS,
            b"\x2d": InstructionINV,
            b"\x2e": InstructionNOT,
            b"\x2f": InstructionBLK,
            b"\x30": InstructionILLEGAL,
        }


class QVM(BaseModel):
    header: QVMHeader
    identifiers: QVMStringList
    strings: QVMStringList
    instructions: QVMInstructionDict

    @classmethod
    def model_validate_bytes(cls, data: bytes) -> Self:
        header = QVMHeader.model_validate_bytes(data=data)

        identifiers_data = data[header.identifiers_data_slice]
        identifiers = QVMStringList.model_validate_bytes(data=identifiers_data)

        strings_data = data[header.strings_data_slice]
        strings = QVMStringList.model_validate_bytes(data=strings_data)

        instructions_data = data[header.instructions_data_slice]
        instructions = QVMInstructionDict.model_validate_bytes(data=instructions_data, version=header.minor_version)

        obj = cls(header=header, identifiers=identifiers, strings=strings, instructions=instructions)
        return obj

    @classmethod
    def model_validate_file(cls, file: str | Path) -> Self:
        data = Path(file).read_bytes()
        return cls.model_validate_bytes(data)

    def get_statement_list(self) -> "StatementList":
        return StatementList.from_instructions(
            identifiers=self.identifiers.value,
            strings=self.strings.value,
            instructions=self.instructions.value,
        )
