from polish_pdf_loader.encoding import repair_cp1250_as_latin1, detect_and_repair, is_polish_garbled

GARBLED = "Litwo! ty jesteœ jak zdrowie. Ile ciê trzeba ceniæ, kto ciê straci³."
CORRECT = "Litwo! ty jesteś jak zdrowie. Ile cię trzeba cenić, kto cię stracił."
CLEAN_UTF8 = "Już w samo południe słońce praży mocno."


def test_repair_cp1250_as_latin1():
    assert repair_cp1250_as_latin1(GARBLED) == CORRECT


def test_detect_and_repair_fixes_garbled():
    assert detect_and_repair(GARBLED) == CORRECT


def test_detect_and_repair_preserves_utf8():
    assert detect_and_repair(CLEAN_UTF8) == CLEAN_UTF8


def test_is_polish_garbled_true():
    assert is_polish_garbled(GARBLED) is True


def test_is_polish_garbled_false():
    assert is_polish_garbled(CLEAN_UTF8) is False


def test_superscript_digits_not_garbled():
    # ¹ and ³ are common in academic PDFs (footnotes, exponents).
    # Without an anchor marker (œ, Ÿ, Œ) they must NOT trigger repair.
    scientific = "See Smith et al.¹ The methodology³ is described in section two."
    assert is_polish_garbled(scientific) is False
    assert detect_and_repair(scientific) == scientific


def test_type3_unusual_chars_not_garbled():
    # Text with unusual Unicode (Greek, symbols) that is not garbled Polish
    # must pass through unchanged regardless of density.
    greek = "The variable Ω represents the sample space in probability theory."
    assert is_polish_garbled(greek) is False
    assert detect_and_repair(greek) == greek
