"""
Pipeline
"""

from __future__ import annotations


import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple, Type

import pandas
from pandas import array
from shapely.geometry import Polygon

from .dataset import AbstractDataSet
from .dataset_radiocells import DataSetRadioCells
from .dataset_safecast import DataSetSafecast
from .defense import AbstractDefense
from .defense_geoindtraces import DefenseGeoIndTraces
from .defense_lap_remapped import DefenseLapRemapped
from .defense_lap_simple import DefenseLapSimple
from .defense_random import DefenseRandom
from .defense_release import DefenseRelease
from .defense_rounding import DefenseRounding


DEFENSES_MAP: Dict[str, Type[AbstractDefense]] = {
    "geoindtraces": DefenseGeoIndTraces,
    "lap_remapped": DefenseLapRemapped,
    "lap_simple": DefenseLapSimple,
    "random": DefenseRandom,
    "release": DefenseRelease,
    "rounding": DefenseRounding,
}

REQUIRE_PRECOMPUTATION: Tuple[Type[AbstractDefense], ...] = (
    DefenseLapRemapped
)

DATASETS_MAP: Dict[str, Type[AbstractDataSet]] = {
    "Radiocells": DataSetRadioCells,
    "Safecast": DataSetSafecast,
}


def gen_defense_mechanisms(defenses_params: List[Dict[str, Any]]) -> List[AbstractDefense]:
    """
    Parse a defense mechanism from pipeline configuration.
    """

    defenses = list()

    for defense_params in defenses_params:
        defense_type = defense_params["defense"]
        params = defense_params.copy()
        del params["defense"]

        if defense_type not in DEFENSES_MAP:
            raise ValueError(f"Unknown defense '{defense_type}'!")

        defense_class, = DEFENSES_MAP[defense_type]

        defense = defense_class(**params)
        defenses.append(defense)

    return defenses


def gen_dataset(dataset_params: Dict[str, str]) -> AbstractDataSet:
    """
    Parse the dataset from the pipeline configuration.
    """

    dataset_type = dataset_params["name"]
    dataset_file = Path(dataset_params["input"])

    if dataset_type not in DATASETS_MAP:
        raise ValueError(f"Unknown dataset '{dataset_type}'!")

    if not dataset_file.is_file():
        raise ValueError(f"File '{str(dataset_file)}' does not exists!")

    dataset = pandas.read_csv(dataset_file)

    dataset_class = DATASETS_MAP[dataset_type]
    return dataset_class(dataset)


@dataclass
class Pipeline:
    """
    Pipeline configuration for the experiment.
    """

    place: str
    dataset_used: str
    dataset: AbstractDataSet = field(default_factory=gen_dataset)
    polygons = field(default_factory=Polygon)
    min_points: int
    max_pois: int
    time_start: int
    time_end: int
    advanced_clustering: bool
    min_allowed_points: int
    max_allowed_distance: int
    original_min_points: int
    defenses: List[AbstractDefense] = field(default_factory=gen_defense_mechanisms)

    dir_project: Path = field(default_factory=Path)
    priors: array = field(default_factory=pandas.read_csv)


    @classmethod
    def from_json(cls, json_file: Path) -> Pipeline:
        """
        Load pipeline configuration from JSON file.
        """
        return json.load(str(json_file.resolve()), object_hook=cls)


    @classmethod
    def precompute(cls) -> None:
        """
        Compute prior coordinates is required by the pipeline.
        """

        # As of now, only DefenseLapRemapped requires precomputations.
        if any(isinstance(defense, REQUIRE_PRECOMPUTATION) for defense in cls.defenses):
            DefenseLapRemapped.precompute(cls.priors)

        cls.dataset.precompute()


    def compute_defense(self):
        """
        """
        for defense in self.defenses:
            defense.compute(self.dataset.dataset)
