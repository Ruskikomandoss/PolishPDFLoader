from polish_pdf_loader.encoding import (
    detect_and_repair,
    is_polish_garbled,
    repair_cp1250_as_latin1,
)

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


def test_garbled_text_containing_o_acute_is_repaired():
    # 'ó' is byte 0xF3 in both CP1250 and CP1252, so it survives the
    # mis-decoding intact and must not count as "already clean" evidence.
    garbled = "Kto ciê straci³. Dziœ piêknoœæ tw¹ w ca³ej ozdobie, gród zamkowy"
    assert is_polish_garbled(garbled) is True
    assert detect_and_repair(garbled) == (
        "Kto cię stracił. Dziś piękność twą w całej ozdobie, gród zamkowy"
    )


def test_garbled_page_without_s_acute_is_repaired():
    # A page can be garbled yet contain no ś/Ś/ź (no œ Œ Ÿ anchors).
    # ³ ¹ ¿ embedded inside a word are unambiguous garbling evidence.
    garbled = "Zabra³ g³os, wymawiaj¹c z wolna ka¿de s³owo, a g³upi wy!"
    assert detect_and_repair(garbled) == (
        "Zabrał głos, wymawiając z wolna każde słowo, a głupi wy!"
    )


def test_superscript_after_word_still_not_garbled():
    text = "Area is 5 m³ per unit and see note¹, also footnote³ here; x² too."
    assert is_polish_garbled(text) is False
