from ats_simulator.parsers import UnsupportedFormatError, extract_text_from_bytes


def test_extract_text_from_txt_bytes():
    data = "Expérience\nPython SQL\n5 ans".encode("utf-8")
    text = extract_text_from_bytes("cv.txt", data)
    assert "Python SQL" in text


def test_doc_extension_returns_conversion_error():
    try:
        extract_text_from_bytes("legacy.doc", b"binary")
    except UnsupportedFormatError as exc:
        assert "Convertissez" in str(exc)
    else:
        raise AssertionError("UnsupportedFormatError attendu")
