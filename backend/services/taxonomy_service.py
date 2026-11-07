"""Ingredient -> food component lookup for the trigger model (issue #127).

Data lives in backend/data/taxonomy/ as versioned files. They are loaded once per process and cached,
because routers create a new service per request.
"""

import csv
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

from services.ingredient_normalization import candidates, clean, strip_prep

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "taxonomy"
UNKNOWN = "unknown"


@dataclass
class IngredientMatch:
    raw: str | None
    normalized: str
    ingredient_id: str
    canonical_name: str = ""
    components: dict[str, int] = field(default_factory=dict)  # component -> level, levels > 0 only
    confidence: dict[str, str] = field(default_factory=dict)  # component -> high / medium / low
    allergen_sources: list[str] = field(default_factory=list)  # allergen components present at any level
    matched_by: str = ""

    @property
    def is_unknown(self) -> bool:
        return self.ingredient_id == UNKNOWN


@dataclass(frozen=True)
class TaxonomyData:
    components: dict  # component id -> components.yaml entry
    ingredients: dict  # ingredient id -> ingredients.csv row
    pairs: dict  # ingredient id -> ingredient_components.csv rows (dropped rows excluded)
    aliases: dict  # cleaned name or alias -> ingredient id
    allergen_components: frozenset


def load_taxonomy(data_dir: Path = DATA_DIR) -> TaxonomyData:
    """Read and index the three taxonomy files. Raises ValueError on alias collisions."""
    comp_yaml = yaml.safe_load((data_dir / "components.yaml").read_text(encoding="utf-8"))
    components = {c["id"]: c for c in comp_yaml["components"]}
    with open(data_dir / "ingredients.csv", encoding="utf-8") as f:
        ingredients = {r["id"]: r for r in csv.DictReader(f)}
    pairs: dict = {}
    with open(data_dir / "ingredient_components.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["confidence"] == "n/a":  # pairs dropped to match design doc worked examples
                continue
            pairs.setdefault(r["ingredient_id"], []).append(r)
    aliases: dict = {}
    for iid, r in ingredients.items():
        for name in [r["canonical_name"], *[a for a in r["aliases"].split(";") if a]]:
            key = clean(name)
            if key in aliases and aliases[key] != iid:
                raise ValueError(f"alias '{name}' cleans to '{key}', already used by {aliases[key]}")
            aliases[key] = iid
    allergens = frozenset(c for c, d in components.items() if "allergen" in (d.get("flags") or []))
    return TaxonomyData(components, ingredients, pairs, aliases, allergens)


@lru_cache(maxsize=1)
def get_taxonomy() -> TaxonomyData:
    return load_taxonomy()


class TaxonomyService:
    def __init__(self, data: TaxonomyData | None = None):
        self.data = data or get_taxonomy()
        self.unknown_hits: Counter = Counter()

    def _resolve(self, text: str) -> tuple[str | None, str]:
        for key, how in candidates(text):
            if key in self.data.aliases:
                return self.data.aliases[key], how
        return None, ""

    def lookup(self, raw: str | None) -> IngredientMatch:
        """Never raises. Unmatched strings return ingredient_id 'unknown' and are counted for review."""
        text = clean(raw)
        iid, how = self._resolve(text)
        if iid is None:
            stripped = strip_prep(text)
            if stripped != text:
                iid, how = self._resolve(stripped)
                how = f"{how}+prep_stripped" if how else ""
                text = stripped
        if iid is None:
            self.unknown_hits[text] += 1
            return IngredientMatch(raw=raw, normalized=text, ingredient_id=UNKNOWN, matched_by="none")
        rows = self.data.pairs.get(iid, [])
        return IngredientMatch(
            raw=raw,
            normalized=text,
            ingredient_id=iid,
            canonical_name=self.data.ingredients[iid]["canonical_name"],
            components={r["component"]: int(r["level"]) for r in rows if int(r["level"]) > 0},
            confidence={r["component"]: r["confidence"] for r in rows},
            allergen_sources=sorted({r["component"] for r in rows if r["component"] in self.data.allergen_components}),
            matched_by=how,
        )

    def lookup_many(self, raws: list[str]) -> list[IngredientMatch]:
        return [self.lookup(r) for r in raws]

    def write_unknowns(self, path: Path) -> None:
        """Save unmatched strings so scripts/taxonomy_review_report.py can list them."""
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["normalized_string", "count"])
            w.writerows(self.unknown_hits.most_common())
