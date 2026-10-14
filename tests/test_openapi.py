from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def openapi():
    r = client.get("/plugindemopython/openapi.json")
    assert r.status_code == 200
    return r.json()


def test_pfade_alphabetisch_sortiert():
    paths = list(openapi()["paths"].keys())
    assert paths
    assert paths == sorted(paths)


def test_methoden_je_pfad_alphabetisch_sortiert():
    for path, ops in openapi()["paths"].items():
        assert list(ops.keys()) == sorted(ops.keys()), path


def test_schemas_alphabetisch_sortiert():
    schemas = list(openapi()["components"]["schemas"].keys())
    assert schemas
    assert schemas == sorted(schemas, key=str.lower)


def test_swagger_ui_sortiert_endpoints():
    html = client.get("/plugindemopython/docs").text
    assert '"operationsSorter": "alpha"' in html


DOC_BASE = "https://doc.letto.at/wiki/Plugins/referenz-plugin-java/"


def test_alle_endpoints_verlinken_doku():
    for path, ops in openapi()["paths"].items():
        for method, op in ops.items():
            assert op.get("externalDocs", {}).get("url", "").startswith(DOC_BASE + "rest-schnittstelle/"), (method, path)


def test_alle_dtos_verlinken_doku():
    for name, dto in openapi()["components"]["schemas"].items():
        if name in ("HTTPValidationError", "ValidationError"):
            continue
        assert dto["externalDocs"]["url"] == f"{DOC_BASE}dtos/{name}/", name


def test_enum_felder_verlinken_doku():
    schemas = openapi()["components"]["schemas"]
    assert f"({DOC_BASE}enums/TOLERANZMODE/)" in schemas["ToleranzDto"]["properties"]["mode"]["description"]
    assert f"({DOC_BASE}enums/Score/)" in schemas["PluginScoreInfoDto"]["properties"]["status"]["description"]


def test_hilfeseite_verlinkt_referenz_doku():
    assert DOC_BASE in client.get("/plugindemopython/help").text
