import csv

import pytest

from services.ingredient_normalization import candidates, clean, singular, strip_prep
from services.taxonomy_service import UNKNOWN, TaxonomyService, get_taxonomy, load_taxonomy


@pytest.fixture
def service():
    return TaxonomyService()


@pytest.mark.parametrize(
    ("raw", "expected_id"),
    [
        ("2 cups diced yellow onion", "onion"),
        ("3 cloves garlic, minced", "garlic"),
        ("1/2 tsp kosher salt", "salt"),
        ("½ cup heavy cream", "heavy_cream"),
        ("1 (14 oz) can diced tomatoes", "canned_tomatoes"),
        ("salt to taste", "salt"),
        ("freshly grated parmesan", "parmesan"),
    ],
)
def test_strips_quantities_units_and_prep_words(service, raw, expected_id):
    # Act
    match = service.lookup(raw)
    # Assert
    assert match.ingredient_id == expected_id


@pytest.mark.parametrize(
    ("raw", "expected_id"),
    [
        ("Tomatoes", "tomato"),
        ("garbanzo beans", "chickpeas"),
        ("courgette", "zucchini"),
        ("prawns", "shrimp"),
        ("green onions", "scallion"),
        ("Splenda", "sucralose"),
        ("bread", "wheat_bread"),
        ("1 cup cheddar, shredded", "cheese"),
        ("fresh mozzarella", "fresh_cheese"),
        ("greek yogurt", "yogurt"),
        ("2 egg whites", "eggs"),
        ("3 russet potatoes", "potato"),
        ("balsamic vinegar", "wine_vinegar"),
        ("tortillas", "flour_tortillas"),
        ("tortilla chips", "corn_tortillas"),
    ],
)
def test_resolves_plurals_synonyms_and_brand_names(service, raw, expected_id):
    assert service.lookup(raw).ingredient_id == expected_id


@pytest.mark.parametrize(
    ("raw", "expected_id"),
    [
        ("3 large eggs", "eggs"),
        ("1 red bell pepper, seeded", "bell_pepper"),
        ("organic baby spinach", "spinach"),
        ("1/2 tsp ground cloves", "cloves"),
        ("coconut milk", UNKNOWN),  # must not fall back to "milk"
        ("sweet potato", "sweet_potato"),  # must not fall back to "potato"
        ("minced beef", "ground_beef"),  # an alias, not "beef" with a prep word
    ],
)
def test_drops_only_safe_modifiers(service, raw, expected_id):
    assert service.lookup(raw).ingredient_id == expected_id


def test_keeps_numbers_inside_additive_names(service):
    assert service.lookup("red 40").ingredient_id != service.lookup("red 3").ingredient_id
    assert service.lookup("polysorbate 80").ingredient_id != service.lookup("polysorbate 60").ingredient_id


def test_compound_ingredients_map_to_several_components(service):
    assert service.lookup("2 tbsp soy sauce").components == {"gluten": 2, "soy": 2, "biogenic_amines": 2}
    assert {"fructans_allium", "milk_protein", "tree_nuts"} <= set(service.lookup("pesto").components)
    assert "fructans_allium" in service.lookup("4 cups chicken stock").components


def test_match_carries_confidence_per_component(service):
    match = service.lookup("shrimp")
    assert match.confidence["shellfish"] == "high"
    assert match.confidence["sulfites"] in {"low", "medium"}


@pytest.mark.parametrize("raw", ["unobtainium", "", "   ", None, "!!!"])
def test_unknown_fallback_never_raises(service, raw):
    match = service.lookup(raw)
    assert match.is_unknown
    assert match.components == {}


def test_unknowns_are_counted_and_written(service, tmp_path):
    # Arrange
    service.lookup_many(["unobtainium", "unobtainium", "onion"])
    out = tmp_path / "unknowns.csv"
    # Act
    service.write_unknowns(out)
    # Assert
    with open(out, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows == [{"normalized_string": "unobtainium", "count": "2"}]


def test_allergen_flag_is_independent_of_dose(service):
    ghee = service.lookup("ghee")
    assert ghee.components == {}
    assert ghee.allergen_sources == ["milk_protein"]
    assert service.lookup("sesame oil").allergen_sources == ["sesame"]


def test_taxonomy_is_cached_across_service_instances():
    assert TaxonomyService().data is TaxonomyService().data is get_taxonomy()


def test_alias_collision_raises(tmp_path):
    # Arrange: copy real files, then give two ingredients the same alias
    src = get_taxonomy()
    for name in ("components.yaml", "ingredient_components.csv"):
        (tmp_path / name).write_text((_data_dir() / name).read_text(encoding="utf-8"), encoding="utf-8")
    text = (_data_dir() / "ingredients.csv").read_text(encoding="utf-8")
    text = text.replace(",onion,yellow onion;", ",onion,garlic;yellow onion;", 1)
    (tmp_path / "ingredients.csv").write_text(text, encoding="utf-8")
    # Act / Assert
    with pytest.raises(ValueError, match="already used"):
        load_taxonomy(tmp_path)
    assert src.aliases["onion"] == "onion"


def test_normalization_helpers():
    assert clean("2 Tbsp Soy Sauce (low sodium)") == "soy sauce"
    assert strip_prep("onion diced") == "onion"
    assert singular("berries") == "berry"
    assert singular("tomatoes") == "tomato"
    assert singular("glass") == "glass"
    assert candidates("") == []


def _data_dir():
    from services.taxonomy_service import DATA_DIR

    return DATA_DIR
