from polish_pdf_loader.postprocess import PostprocessConfig, postprocess


def test_ligature_fi():
    assert postprocess("ﬁlm") == "film"


def test_ligature_fl():
    assert postprocess("ﬂaga") == "flaga"


def test_normalize_whitespace():
    assert postprocess("słowo  następne") == "słowo następne"


def test_join_hyphens_enabled():
    cfg = PostprocessConfig(join_hyphens=True)
    assert postprocess("słow-\nne zdanie", cfg) == "słowne zdanie"


def test_join_hyphens_disabled_by_default():
    result = postprocess("słow-\nne zdanie")
    assert "słow-\n" in result


def test_no_mutation_of_clean_text():
    text = "Już w samo południe słońce praży mocno."
    assert postprocess(text) == text
