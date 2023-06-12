import dataclasses
from typing import List

from pydantic import BaseModel

from hmmer_tables.csv_iter import csv_iter
from hmmer_tables.interval import PyInterval, RInterval
from hmmer_tables.path_like import PathLike

__all__ = [
    "DomTBLCoord",
    "DomTBLDomScore",
    "DomTBLIndex",
    "DomTBLRow",
    "DomTBLSeqScore",
    "read_domtbl",
]


class DomTBLIndex(BaseModel):
    name: str
    accession: str
    length: int


class DomTBLSeqScore(BaseModel):
    e_value: str
    score: str
    bias: str


class DomTBLDomScore(BaseModel):
    id: int
    size: int
    c_value: str
    i_value: str
    score: str
    bias: str


class DomTBLCoord(BaseModel):
    """
    Coordinates.

    Parameters
    ----------
    start
        Start coordinate, starting from 1. Consider using :method:`.interval` instead.
    stop
        Stop coordinate. `(start, stop)` form a closed interval. Consider using
        :method:`.interval` instead.
    """

    start: int
    stop: int

    @property
    def interval(self) -> PyInterval:
        """
        0-start, half-open interval.

        Returns
        -------
        PyInterval
            Interval.
        """
        rinterval = RInterval(self.start, self.stop)
        return rinterval.to_pyinterval()


class DomTBLRow(BaseModel):
    target: DomTBLIndex
    query: DomTBLIndex
    full_sequence: DomTBLSeqScore
    domain: DomTBLDomScore
    hmm_coord: DomTBLCoord
    ali_coord: DomTBLCoord
    env_coord: DomTBLCoord
    acc: str
    description: str

    def _asdict(self):
        return dataclasses.asdict(self)

    def __iter__(self):
        return iter(self._asdict().values())

    def _field_types(self):
        return {f.name: f.type for f in dataclasses.fields(self)}


def read_domtbl(filename: PathLike) -> List[DomTBLRow]:
    """
    Read domtbl file type.

    Parameters
    ----------
    file
        File path or file stream.
    """
    rows = []
    with open(filename, "r") as file:
        for x in csv_iter(file):
            row = DomTBLRow(
                target=DomTBLIndex(name=x[0], accession=x[1], length=int(x[2])),
                query=DomTBLIndex(name=x[3], accession=x[4], length=int(x[5])),
                full_sequence=DomTBLSeqScore(e_value=x[6], score=x[7], bias=x[8]),
                domain=DomTBLDomScore(
                    id=int(x[9]),
                    size=int(x[10]),
                    c_value=x[11],
                    i_value=x[12],
                    score=x[13],
                    bias=x[14],
                ),
                hmm_coord=DomTBLCoord(start=int(x[15]), stop=int(x[16])),
                ali_coord=DomTBLCoord(start=int(x[17]), stop=int(x[18])),
                env_coord=DomTBLCoord(start=int(x[19]), stop=int(x[20])),
                acc=x[21],
                description=" ".join(x[22:]),
            )
            rows.append(row)
    return rows