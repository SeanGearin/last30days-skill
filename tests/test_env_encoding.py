from lib import env


def test_load_env_file_strips_utf8_bom(tmp_path):
    # A Windows editor (e.g. Notepad) commonly saves .env with a UTF-8 BOM.
    # Without an explicit encoding, open() prepends the BOM to the first key,
    # corrupting it (KeyError below). utf-8-sig transparently strips the BOM.
    env_path = tmp_path / ".env"
    env_path.write_bytes("DISPLAY_NAME=café\nREAL_KEY=ok\n".encode("utf-8-sig"))

    loaded = env.load_env_file(env_path)

    assert loaded["DISPLAY_NAME"] == "café"
    assert loaded["REAL_KEY"] == "ok"


def test_load_env_file_falls_back_for_locale_encoded(tmp_path):
    # A pre-existing .env saved in a legacy codepage (e.g. cp1252 on Windows)
    # loaded fine when open() used the locale decoder. A strict UTF-8 read would
    # raise UnicodeDecodeError on those bytes; the locale fallback must keep it
    # loading rather than crash config loading.
    env_path = tmp_path / ".env"
    env_path.write_bytes("DISPLAY_NAME=Jos\xe9\nREAL_KEY=ok\n".encode("cp1252"))

    loaded = env.load_env_file(env_path)

    # The value decodes via the fallback (exact glyph depends on the runner's
    # locale); what matters is no crash and the ASCII key/value survive intact.
    assert "DISPLAY_NAME" in loaded
    assert loaded["REAL_KEY"] == "ok"
