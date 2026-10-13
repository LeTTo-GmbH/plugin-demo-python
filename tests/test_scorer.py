import pytest
from fastapi.testclient import TestClient

from app.main import (
    CalcErgebnisDto,
    PluginAnswerDto,
    PluginDemo,
    ToleranzDto,
    app,
    clock_diff_seconds,
    clock_equals_with_tolerance,
    parse_time_seconds,
)


def score(antwort, richtig, toleranz=None, mode="RELATIV", ergebnis=None, ze="", grade=1.0):
    tol = ToleranzDto(toleranz=toleranz, mode=mode) if toleranz is not None else None
    erg = CalcErgebnisDto(string=ergebnis) if ergebnis is not None else None
    answer = PluginAnswerDto(answerText=richtig, ergebnis=erg, ze=ze)
    return PluginDemo("p", "").score(antwort, tol, answer, grade)


# --------------------------
# parse_time_seconds
# --------------------------
@pytest.mark.parametrize("text, sekunden", [
    ("0:00", 0.0),
    ("3:15", 3 * 3600 + 15 * 60),
    (" 3:15 ", 3 * 3600 + 15 * 60),
    ("15:15", 15 * 3600 + 15 * 60),
    ("3:15:36", 3 * 3600 + 15 * 60 + 36),
    ("3:15:36.5", 3 * 3600 + 15 * 60 + 36.5),
])
def test_parse_time_seconds(text, sekunden):
    assert parse_time_seconds(text) == pytest.approx(sekunden)


@pytest.mark.parametrize("text", ["", "315", "3.15", "3:15:", "a:b", "3:15 Uhr", None])
def test_parse_time_seconds_ungueltig(text):
    with pytest.raises(ValueError):
        parse_time_seconds(text)


# --------------------------
# clock_diff_seconds
# --------------------------
@pytest.mark.parametrize("a, b, diff", [
    ("3:15", "3:15", 0),
    ("3:15", "15:15", 0),          # 12/24 Stunden, gleiche Zeigerstellung
    ("12:00", "0:00", 0),
    ("23:30", "11:30", 0),
    ("3:15", "3:16", 60),
    ("11:59", "0:01", 120),        # über 12 Uhr hinweg
    ("23:59", "0:01", 120),
    ("0:00", "6:00", 6 * 3600),    # größter möglicher Abstand
    ("3:00", "21:00", 6 * 3600),
])
def test_clock_diff_seconds(a, b, diff):
    sa, sb = parse_time_seconds(a), parse_time_seconds(b)
    assert clock_diff_seconds(sa, sb) == pytest.approx(diff)
    assert clock_diff_seconds(sb, sa) == pytest.approx(diff)


# --------------------------
# clock_equals_with_tolerance
# --------------------------
def test_toleranz_relativ_bezieht_sich_auf_eine_stunde():
    # 1% von einer Stunde = 36 s, unabhängig von der Uhrzeit
    assert clock_equals_with_tolerance(0, 36, 0.01, "RELATIV")
    assert not clock_equals_with_tolerance(0, 37, 0.01, "RELATIV")
    elf_uhr = 11 * 3600
    assert clock_equals_with_tolerance(elf_uhr, elf_uhr + 36, 0.01, "RELATIV")
    assert not clock_equals_with_tolerance(elf_uhr, elf_uhr + 37, 0.01, "RELATIV")


def test_toleranz_relativ_ist_standard():
    assert clock_equals_with_tolerance(0, 36, 0.01, "")
    assert not clock_equals_with_tolerance(0, 37, 0.01, "")


def test_toleranz_absolut_in_sekunden():
    assert clock_equals_with_tolerance(0, 120, 120, "ABSOLUT")
    assert not clock_equals_with_tolerance(0, 121, 120, "ABSOLUT")


# --------------------------
# PluginDemo.score
# --------------------------
@pytest.mark.parametrize("antwort, richtig", [
    ("3:15", "3:15"),
    (" 3:15", "3:15"),             # Format aus dem JavaScript (führendes Leerzeichen)
    ("3:15", "15:15"),
    ("15:15", "3:15"),
    ("12:00", "0:00"),
    ("3:15", "3:15:00"),
])
def test_score_richtig(antwort, richtig):
    info = score(antwort, richtig)
    assert info.status == "OK"
    assert info.punkteIst == 1.0


@pytest.mark.parametrize("antwort, richtig", [
    ("3:15", "3:16"),              # ohne Toleranz muss die Zeit exakt stimmen
    ("3:15", "9:15"),
    ("", "3:15"),
    ("   ", "3:15"),
    ("abc", "3:15"),
    ("3:15", ""),
    ("3:15", "abc"),
])
def test_score_falsch(antwort, richtig):
    info = score(antwort, richtig)
    assert info.status == "FALSCH"
    assert info.punkteIst == 0.0


def test_score_leere_antwort_ohne_loesung_ist_falsch():
    info = score("", "", ergebnis="")
    assert info.status == "FALSCH"
    assert info.punkteIst == 0.0


@pytest.mark.parametrize("antwort, ok", [("3:15:36", True), ("3:15:37", False), ("3:14:24", True), ("3:14:23", False)])
def test_score_toleranz_relativ(antwort, ok):
    info = score(antwort, "3:15", toleranz=0.01, mode="RELATIV")
    assert (info.status == "OK") is ok


@pytest.mark.parametrize("antwort, ok", [("0:01", True), ("0:02", False), ("12:01", True)])
def test_score_toleranz_absolut_ueber_zwoelf_uhr(antwort, ok):
    info = score(antwort, "11:59", toleranz=120, mode="ABSOLUT")
    assert (info.status == "OK") is ok


def test_score_toleranz_ohne_mode_ist_relativ():
    assert score("3:15:36", "3:15", toleranz=0.01, mode=None).status == "OK"


def test_score_vergleich_mit_ergebnis_string():
    # stimmt die Antwort mit ergebnis.string überein, ist sie auch ohne answerText richtig
    info = score("3:15", "", ergebnis="3:15")
    assert info.status == "OK"
    assert info.punkteIst == 1.0


def test_score_felder():
    info = score(" 3:15", "15:15", ze="h", grade=2.5)
    assert info.punkteIst == 2.5
    assert info.punkteSoll == 2.5
    assert info.zielEinheit == "h"
    assert info.schuelerErgebnis.string == "3:15"
    assert info.htmlScoreInfo == "Wert:3:15"


def test_score_falsch_punkte_soll():
    info = score("9:00", "3:15", grade=2.0)
    assert info.punkteIst == 0.0
    assert info.punkteSoll == 2.0


def test_score_ohne_answer_dto():
    info = PluginDemo("p", "").score("3:15", None, None, 1.0)
    assert info.status == "FALSCH"
    assert info.punkteIst == 0.0


# --------------------------
# REST-Endpoint /open/score
# --------------------------
client = TestClient(app)


@pytest.mark.parametrize("prefix", ["/open", "/plugindemopython/open"])
def test_endpoint_score(prefix):
    r = client.post(f"{prefix}/score", json={
        "typ": "UhrPy",
        "antwort": " 3:15",
        "answerDto": {"answerText": "15:15"},
        "toleranz": {"toleranz": 0.01, "mode": "RELATIV"},
        "grade": 2.0,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "OK"
    assert body["punkteIst"] == 2.0


def test_endpoint_score_falsch():
    r = client.post("/open/score", json={"typ": "UhrPy", "antwort": "4:15", "answerDto": {"answerText": "3:15"}})
    assert r.status_code == 200
    assert r.json()["status"] == "FALSCH"


def test_endpoint_score_unbekanntes_plugin():
    r = client.post("/open/score", json={"typ": "Unbekannt", "antwort": "3:15", "answerDto": {"answerText": "3:15"}})
    assert r.status_code == 200
    assert r.json()["status"] == "FALSCH"
    assert r.json()["punkteIst"] == 0.0
