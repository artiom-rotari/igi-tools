from typing import ClassVar

from igipy.formats import ilff


class HSEMChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"HSEM")


class ATTAChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"ATTA")


class XTVMChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"XTVM")


class TROPChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"TROP")


class XVTPChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"XVTP")


class CFTPChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"CFTP")


class D3DRChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"D3DR")


class DNERChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"DNER")


class XTRVChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"XTRV")


class PMTLChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"PMTL")


class HSMCChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"HSMC")


class XTVCChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"XTVC")


class ECFCChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"ECFC")


class TAMCChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"TAMC")


class HPSCChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"HPSC")


class TXANChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"TXAN")


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

    content: list[
        HSEMChunk
        | ATTAChunk
        | XTVMChunk
        | TROPChunk
        | XVTPChunk
        | CFTPChunk
        | D3DRChunk
        | DNERChunk
        | XTRVChunk
        | PMTLChunk
        | HSMCChunk
        | XTVCChunk
        | ECFCChunk
        | TAMCChunk
        | HPSCChunk
        | TXANChunk
    ]
