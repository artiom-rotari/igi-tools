from collections import defaultdict
from functools import cached_property
from io import BytesIO
from struct import Struct
from typing import ClassVar, Literal, Self

from pydantic import BaseModel, Field, NonNegativeInt, model_validator

from igipy.formats import ilff
from igipy.formats.base import StructModel


class HSEMChunk(ilff.Chunk):
    unknown_01: NonNegativeInt
    created_at_year: NonNegativeInt
    created_at_month: NonNegativeInt
    created_at_day: NonNegativeInt
    created_at_hour: NonNegativeInt
    created_at_minute: NonNegativeInt
    created_at_second: NonNegativeInt
    created_at_millisecond: NonNegativeInt
    model_type: NonNegativeInt
    unknown_02: NonNegativeInt
    unknown_03: NonNegativeInt
    unknown_04: NonNegativeInt
    unknown_05: float
    unknown_06: float
    unknown_07: float
    unknown_08: float
    unknown_09: float
    unknown_10: float
    unknown_11: float
    unknown_12: float
    unknown_13: float
    unknown_14: float
    unknown_15: float
    unknown_16: float
    render_face_count: NonNegativeInt
    xtrv_length: NonNegativeInt
    unknown_17: NonNegativeInt
    ecfc_total_length: NonNegativeInt
    xtvc_total_length: NonNegativeInt
    unknown_18: NonNegativeInt
    unknown_19: float
    xtvm_length: NonNegativeInt
    atta_length: NonNegativeInt
    xvtp_length: NonNegativeInt
    cftp_length: NonNegativeInt
    trop_length: NonNegativeInt
    unknown_20: Literal[0]
    unknown_21: Literal[0]
    unknown_22: Literal[0]
    unknown_23: Literal[0]
    unknown_24: Literal[0]
    unknown_25: Literal[0]

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"HSEM")

    @classmethod
    def model_validate_content(cls, content: bytes) -> dict:
        # noinspection PyTypeChecker
        fields = [field for field in cls.model_fields if field not in {"meta_start", "meta_end", "header"}]
        values = Struct("12I12f6If6H5I").unpack(content)
        return dict(zip(fields, values, strict=True))


class ATTAChunk(ilff.Chunk):
    class ATTAItem(StructModel):
        struct: ClassVar = Struct("<16s12fi")

        unknown_01: bytes = Field(min_length=16, max_length=16)
        unknown_02: float
        unknown_03: float
        unknown_04: float
        unknown_05: float
        unknown_06: float
        unknown_07: float
        unknown_08: float
        unknown_09: float
        unknown_10: float
        unknown_11: float
        unknown_12: float
        unknown_13: float
        unknown_14: int

    content: list[ATTAItem]

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"ATTA")

    @classmethod
    def model_validate_content(cls, content: bytes) -> dict:
        return {"content": cls.ATTAItem.unpack_many(content)}


class XTVMChunk(ilff.Chunk):
    class XTVMItem(StructModel):
        struct: ClassVar = Struct("<3fi")

        unknown_01: float
        unknown_02: float
        unknown_03: float
        unknown_04: int

    content: list[XTVMItem]

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"XTVM")

    @classmethod
    def model_validate_content(cls, content: bytes) -> dict:
        return {"content": cls.XTVMItem.unpack_many(content)}


class TROPChunk(ilff.Chunk):
    class TROPItem(StructModel):
        struct: ClassVar = Struct("<5I")

        unknown_01: NonNegativeInt
        unknown_02: NonNegativeInt
        unknown_03: NonNegativeInt
        unknown_04: NonNegativeInt
        unknown_05: NonNegativeInt

    content: list[TROPItem]

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"TROP")

    @classmethod
    def model_validate_content(cls, content: bytes) -> dict:
        return {"content": cls.TROPItem.unpack_many(content)}


class XVTPChunk(ilff.Chunk):
    class XVTPItem(StructModel):
        struct: ClassVar = Struct("<3f")

        unknown_01: float
        unknown_02: float
        unknown_03: float

    content: list[XVTPItem]

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"XVTP")

    @classmethod
    def model_validate_content(cls, content: bytes) -> dict:
        return {"content": cls.XVTPItem.unpack_many(content)}


class CFTPChunk(ilff.Chunk):
    class CFTPItem(StructModel):
        struct: ClassVar = Struct("<3I")

        unknown_01: NonNegativeInt
        unknown_02: NonNegativeInt
        unknown_03: NonNegativeInt

    content: list[CFTPItem]

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"CFTP")

    @classmethod
    def model_validate_content(cls, content: bytes) -> dict:
        return {"content": cls.CFTPItem.unpack_many(content)}


class D3DRChunk(ilff.RawChunk):
    class D3DRItem0(StructModel):
        struct: ClassVar = Struct("<12I")

        unknown_01: NonNegativeInt
        unknown_02: NonNegativeInt
        unknown_03: NonNegativeInt
        unknown_04: NonNegativeInt
        unknown_05: NonNegativeInt
        unknown_06: NonNegativeInt
        unknown_07: NonNegativeInt
        unknown_08: NonNegativeInt
        unknown_09: NonNegativeInt
        unknown_10: NonNegativeInt
        unknown_11: NonNegativeInt
        unknown_12: NonNegativeInt

    class D3DRItem1(StructModel):
        struct: ClassVar = Struct("<14I")

        unknown_01: NonNegativeInt
        unknown_02: NonNegativeInt
        unknown_03: NonNegativeInt
        unknown_04: NonNegativeInt
        unknown_05: NonNegativeInt
        unknown_06: NonNegativeInt
        unknown_07: NonNegativeInt
        unknown_08: NonNegativeInt
        unknown_09: NonNegativeInt
        unknown_10: NonNegativeInt
        unknown_11: NonNegativeInt
        unknown_12: NonNegativeInt
        unknown_13: NonNegativeInt
        unknown_14: NonNegativeInt

    class D3DRItem3(StructModel):
        struct: ClassVar = Struct("<14I")

        unknown_01: NonNegativeInt
        unknown_02: NonNegativeInt
        unknown_03: NonNegativeInt
        unknown_04: NonNegativeInt
        unknown_05: NonNegativeInt
        unknown_06: NonNegativeInt
        unknown_07: NonNegativeInt
        unknown_08: NonNegativeInt
        unknown_09: NonNegativeInt
        unknown_10: NonNegativeInt
        unknown_11: NonNegativeInt
        unknown_12: NonNegativeInt
        unknown_13: NonNegativeInt
        unknown_14: NonNegativeInt

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"D3DR")

    @classmethod
    def parse_content(
        cls, content: bytes, item_class: type[D3DRItem0 | D3DRItem1 | D3DRItem3]
    ) -> D3DRItem0 | D3DRItem1 | D3DRItem3:
        content = item_class.unpack_many(content)

        if len(content) != 1:
            raise ValueError("Expected exactly one item in content.")

        return content[0]

    @cached_property
    def content_0(self) -> D3DRItem0:
        return self.parse_content(self.content, self.D3DRItem0)

    @cached_property
    def content_1(self) -> D3DRItem1:
        return self.parse_content(self.content, self.D3DRItem1)

    @cached_property
    def content_3(self) -> D3DRItem3:
        return self.parse_content(self.content, self.D3DRItem3)


class DNERChunk(ilff.RawChunk):
    class DNERItem0(BaseModel):
        unknown_01: float
        unknown_02: float
        unknown_03: float
        unknown_04: NonNegativeInt
        unknown_05: NonNegativeInt
        unknown_06: NonNegativeInt
        unknown_07: NonNegativeInt
        unknown_08: NonNegativeInt
        unknown_09: NonNegativeInt
        unknown_10: NonNegativeInt
        unknown_11: NonNegativeInt
        unknown_12: list[int]

        @classmethod
        def model_validate_stream(cls, stream: BytesIO) -> Self:
            struct = Struct("<3f8H")
            fields: list[str] = [
                "unknown_01",
                "unknown_02",
                "unknown_03",
                "unknown_04",
                "unknown_05",
                "unknown_06",
                "unknown_07",
                "unknown_08",
                "unknown_09",
                "unknown_10",
                "unknown_11",
            ]

            content = dict(zip(fields, struct.unpack(stream.read(cls.struct.size)), strict=True))

            unknown_12_struct = Struct(f"{content['unknown_04']}H")
            content["unknown_12"] = list(unknown_12_struct.unpack(stream.read(unknown_12_struct.size)))

            return cls(**content)

    class DNERItem1(DNERItem0):
        pass

    class DNERItem3(BaseModel):
        unknown_01: float
        unknown_02: float
        unknown_03: float
        unknown_04: int
        unknown_05: int
        unknown_06: int
        unknown_07: int
        unknown_08: int
        unknown_09: int
        unknown_10: int
        unknown_11: int
        unknown_12: int
        unknown_13: int
        unknown_14: list[int]

        @classmethod
        def model_validate_stream(cls, stream: BytesIO) -> Self:
            struct = Struct("<3f10h")
            fields: list[str] = [
                "unknown_01",
                "unknown_02",
                "unknown_03",
                "unknown_04",
                "unknown_05",
                "unknown_06",
                "unknown_07",
                "unknown_08",
                "unknown_09",
                "unknown_10",
                "unknown_11",
                "unknown_12",
                "unknown_13",
            ]

            content = dict(zip(fields, struct.unpack(stream.read(struct.size)), strict=True))

            unknown_14_struct = Struct(f"{content['unknown_04']}H")
            content["unknown_14"] = list(unknown_14_struct.unpack(stream.read(unknown_14_struct.size)))

            return cls(**content)

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"DNER")

    @classmethod
    def parse_content(
        cls, content: bytes, item_class: type[DNERItem0 | DNERItem1 | DNERItem3]
    ) -> list[DNERItem0] | list[DNERItem1] | list[DNERItem3]:
        stream = BytesIO(content)
        result = []

        while stream.tell() < len(content):
            result.append(item_class.model_validate_stream(stream))

        return result

    def content_0(self) -> list[DNERItem0]:
        return self.parse_content(self.content, self.DNERItem0)

    def content_1(self) -> list[DNERItem1]:
        return self.parse_content(self.content, self.DNERItem1)

    def content_3(self) -> list[DNERItem3]:
        return self.parse_content(self.content, self.DNERItem3)


class XTRVChunk(ilff.RawChunk):
    class XTRVItem0(StructModel):
        struct: ClassVar = Struct("<8f")

        unknown_01: float
        unknown_02: float
        unknown_03: float
        unknown_04: float
        unknown_05: float
        unknown_06: float
        unknown_07: float
        unknown_08: float

    class XTRVItem1(StructModel):
        struct: ClassVar = Struct("<10f")

        unknown_01: float
        unknown_02: float
        unknown_03: float
        unknown_04: float
        unknown_05: float
        unknown_06: float
        unknown_07: float
        unknown_08: float
        unknown_09: float
        unknown_10: float

    class XTRVItem3(StructModel):
        struct: ClassVar = Struct("<10f")

        unknown_01: float
        unknown_02: float
        unknown_03: float
        unknown_04: float
        unknown_05: float
        unknown_06: float
        unknown_07: float
        unknown_08: float
        unknown_09: float
        unknown_10: float

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"XTRV")

    @cached_property
    def content_0(self) -> list[XTRVItem0]:
        return self.XTRVItem0.unpack_many(self.content)

    @cached_property
    def content_1(self) -> list[XTRVItem1]:
        return self.XTRVItem1.unpack_many(self.content)

    @cached_property
    def content_3(self) -> list[XTRVItem3]:
        return self.XTRVItem3.unpack_many(self.content)


class PMTLChunk(ilff.Chunk):
    class PMTLItem(StructModel):
        struct: ClassVar = Struct("<4H")

        unknown_01: int
        unknown_02: int
        unknown_03: int
        unknown_04: int

    content: list[PMTLItem]

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"PMTL")

    @classmethod
    def model_validate_content(cls, content: bytes) -> dict:
        return {"content": cls.PMTLItem.unpack_many(content)}


class TXANChunk(ilff.RawChunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"TXAN")


# Collision Mesh


class HSMCChunk(ilff.Chunk):
    """
    Collision Meshes.
    """

    class HSMCItem(StructModel):
        struct: ClassVar = Struct("<8I")

        ecfc_length: NonNegativeInt
        xtvc_length: NonNegativeInt
        tamc_length: NonNegativeInt
        hpsc_length: NonNegativeInt
        unknown_01: Literal[0]
        unknown_02: Literal[0]
        unknown_03: Literal[0]
        unknown_04: Literal[0]

    content: list[HSMCItem]

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"HSMC")

    @classmethod
    def model_validate_content(cls, content: bytes) -> dict:
        return {"content": cls.HSMCItem.unpack_many(content)}


class XTVCChunk(ilff.Chunk):
    """
    Collision Mesh Vertices.
    """

    class XTVCItem(StructModel):
        struct: ClassVar = Struct("<4f")

        unknown_01: float
        unknown_02: float
        unknown_03: float
        unknown_04: float

    content: list[XTVCItem]

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"XTVC")

    @classmethod
    def model_validate_content(cls, content: bytes) -> dict:
        return {"content": cls.XTVCItem.unpack_many(content)}


class ECFCChunk(ilff.Chunk):
    """
    Collision Mesh Faces.
    """

    class ECFCItem(StructModel):
        struct: ClassVar = Struct("<4H")

        unknown_01: NonNegativeInt
        unknown_02: NonNegativeInt
        unknown_03: NonNegativeInt
        unknown_04: NonNegativeInt

    content: list[ECFCItem]

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"ECFC")

    @classmethod
    def model_validate_content(cls, content: bytes) -> dict:
        return {"content": cls.ECFCItem.unpack_many(content)}


class TAMCChunk(ilff.Chunk):
    """
    Collision Mesh Material?
    """

    class TAMCItem(StructModel):
        struct: ClassVar = Struct("<6h")

        unknown_01: int
        unknown_02: int
        unknown_03: int
        unknown_04: int
        unknown_05: int
        unknown_06: int

    content: list[TAMCItem]

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"TAMC")

    @classmethod
    def model_validate_content(cls, content: bytes) -> dict:
        return {"content": cls.TAMCItem.unpack_many(content)}


class HPSCChunk(ilff.Chunk):
    """
    Collision Mesh Something?
    """

    class HPSCItem(StructModel):
        struct: ClassVar = Struct("<4f4h")

        unknown_01: float
        unknown_02: float
        unknown_03: float
        unknown_04: float
        unknown_05: int
        unknown_06: int
        unknown_07: int
        unknown_08: int

    content: list[HPSCItem]

    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"HPSC")

    @classmethod
    def model_validate_content(cls, content: bytes) -> dict:
        return {"content": cls.HPSCItem.unpack_many(content)}


# MEF Base


class MEFItem(BaseModel):
    xtvc: XTVCChunk
    ecfc: ECFCChunk
    tamc: TAMCChunk
    hpsc: HPSCChunk


# noinspection DuplicatedCode
class MEF(ilff.ILFF):
    chunk_mapping: ClassVar[dict[bytes, type[ilff.Chunk]]] = {
        b"HSEM": HSEMChunk,
        b"ATTA": ATTAChunk,
        b"XTVM": XTVMChunk,
        b"TROP": TROPChunk,
        b"XVTP": XVTPChunk,
        b"CFTP": CFTPChunk,
        b"D3DR": D3DRChunk,
        b"DNER": DNERChunk,
        b"XTRV": XTRVChunk,
        b"PMTL": PMTLChunk,
        b"HSMC": HSMCChunk,
        b"XTVC": XTVCChunk,
        b"ECFC": ECFCChunk,
        b"TAMC": TAMCChunk,
        b"HPSC": HPSCChunk,
        b"TXAN": TXANChunk,
    }

    hsem: HSEMChunk
    atta: ATTAChunk
    xtvm: XTVMChunk
    trop: TROPChunk
    xvtp: XVTPChunk
    cftp: CFTPChunk
    d3dr: D3DRChunk
    dner: DNERChunk
    xtrv: XTRVChunk
    pmtl: PMTLChunk | None = None
    hsmc: HSMCChunk | None = None
    txan: TXANChunk | None = None

    items: list[MEFItem]

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        header, content_type, content = super().model_validate_chunks(stream)

        if content_type != b"OCEM":
            raise ValueError("Invalid content type")

        field_mapping: dict[type[ilff.Chunk], str] = {
            HSEMChunk: "hsem",
            ATTAChunk: "atta",
            XTVMChunk: "xtvm",
            TROPChunk: "trop",
            XVTPChunk: "xvtp",
            CFTPChunk: "cftp",
            D3DRChunk: "d3dr",
            DNERChunk: "dner",
            XTRVChunk: "xtrv",
            PMTLChunk: "pmtl",
            HSMCChunk: "hsmc",
            XTVCChunk: "xtvc",
            ECFCChunk: "ecfc",
            TAMCChunk: "tamc",
            HPSCChunk: "hpsc",
            TXANChunk: "txan",
        }

        field_mapping_values: dict[str, list[ilff.Chunk]] = defaultdict(list)

        for chunk in content:
            field_mapping_values[field_mapping[type(chunk)]].append(chunk)

        instance_values = {}

        for field in ["hsem", "atta", "xtvm", "trop", "xvtp", "cftp", "d3dr", "dner", "xtrv"]:
            if len(field_mapping_values[field]) != 1:
                raise ValueError(f"Multiple {field} chunks found")

            instance_values[field] = field_mapping_values[field][0]

        for field in ["pmtl", "hsmc", "txan"]:
            if len(field_mapping_values[field]) > 1:
                raise ValueError(f"Multiple {field} chunks found")

            if len(field_mapping_values[field]) < 1:
                continue

            instance_values[field] = field_mapping_values[field][0]

        items_count_set = {len(field_mapping_values[field]) for field in ["xtvc", "ecfc", "tamc", "hpsc"]}

        if len(items_count_set) != 1:
            raise ValueError("Different count of items chunks found")

        items = []

        for i in range(items_count_set.pop()):
            # noinspection PyTypeChecker
            items.append(  # noqa: PERF401
                MEFItem(
                    xtvc=field_mapping_values["xtvc"][i],
                    ecfc=field_mapping_values["ecfc"][i],
                    tamc=field_mapping_values["tamc"][i],
                    hpsc=field_mapping_values["hpsc"][i],
                )
            )

        return cls(header=header, content_type=content_type, items=items, **instance_values)

    # noinspection PyNestedDecorators
    @model_validator(mode="after")
    @classmethod
    def model_validate(cls, instance: Self) -> Self:
        if instance.hsmc:
            if len(instance.hsmc.content) != len(instance.items):
                raise ValueError("hsmc chunk content length does not match items count")

            for i in range(len(instance.hsmc.content)):
                if instance.hsmc.content[i].ecfc_length != len(instance.items[i].ecfc.content):
                    raise ValueError(f"hsmc item {i} does not match ecfc {i} items count")

                if instance.hsmc.content[i].xtvc_length != len(instance.items[i].xtvc.content):
                    raise ValueError(f"hsmc item {i} does not match xtvc {i} items count")

                if instance.hsmc.content[i].tamc_length != len(instance.items[i].tamc.content):
                    raise ValueError(f"hsmc item {i} does not match tamc {i} items count")

                if instance.hsmc.content[i].hpsc_length != len(instance.items[i].hpsc.content):
                    raise ValueError(f"hsmc item {i} does not match hpsc {i} items count")

        return instance
