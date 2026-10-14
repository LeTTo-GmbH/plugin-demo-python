import base64
import os

import pytest
from fastapi.testclient import TestClient

from app.main import app, save_plugin_image, SERVICEPATH

client = TestClient(app)


@pytest.fixture
def bildablage(tmp_path, monkeypatch):
    monkeypatch.setenv("letto_pathPlugins", str(tmp_path))
    monkeypatch.setenv("letto_webPathPlugins", "server.example.at/images/plugins")
    return tmp_path


def request(config=""):
    return {"typ": "UhrPy", "name": "uhr", "config": config, "params": "", "q": None}


@pytest.mark.parametrize("prefix", ["/open", f"{SERVICEPATH}/open"])
def test_imageurl_speichert_bild_und_liefert_url(bildablage, prefix):
    r = client.post(f"{prefix}/imageurl", json=request())
    assert r.status_code == 200
    data = r.json()
    info = data["imageInfoDto"]
    filename = info["filename"]
    assert filename.endswith(".png")
    assert data["imageUrl"] == f"https://server.example.at/images/plugins{SERVICEPATH}/{filename[:2]}/{filename}"
    assert info["url"] == data["imageUrl"]
    assert info["pluginTyp"] == "UhrPy"
    assert data["error"] == ""
    datei = bildablage / SERVICEPATH.strip("/") / filename[:2] / filename
    assert datei.is_file()
    assert datei.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_imageurl_gleiches_bild_gleiche_datei(bildablage):
    a = client.post("/open/imageurl", json=request()).json()
    b = client.post("/open/imageurl", json=request()).json()
    c = client.post("/open/imageurl", json=request("bgcolor=green")).json()
    assert a["imageUrl"] == b["imageUrl"]
    assert a["imageUrl"] != c["imageUrl"]


def test_imageurl_bild_entspricht_base64_bild(bildablage):
    data = client.post("/open/imageurl", json=request()).json()
    image = client.post("/open/image", json=request()).json()
    datei = bildablage / SERVICEPATH.strip("/") / data["imageInfoDto"]["filename"][:2] / data["imageInfoDto"]["filename"]
    assert datei.read_bytes() == base64.b64decode(image["base64Image"])


def test_imageurl_ohne_bildablage_liefert_keine_url(monkeypatch):
    monkeypatch.delenv("letto_pathPlugins", raising=False)
    monkeypatch.delenv("letto_webPathPlugins", raising=False)
    data = client.post("/open/imageurl", json=request()).json()
    assert data["imageUrl"] == ""
    assert "nicht gesetzt" in data["error"]


def test_imageurl_unbekanntes_plugin(bildablage):
    data = client.post("/open/imageurl", json={**request(), "typ": "Unbekannt"}).json()
    assert data["imageUrl"] == ""
    assert data["error"] == "unknown plugin"


def test_save_plugin_image_url_ohne_doppelte_schraegstriche(tmp_path, monkeypatch):
    monkeypatch.setenv("letto_pathPlugins", str(tmp_path))
    monkeypatch.setenv("letto_webPathPlugins", "https://server.example.at//images/plugins/")
    _, url, error = save_plugin_image(b"test")
    assert error == ""
    assert url.startswith("https://server.example.at/images/plugins/")
    assert "//" not in url[len("https://"):]
