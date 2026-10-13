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
