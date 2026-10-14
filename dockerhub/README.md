# LeTTo Plugin Demo (Python) – UhrPy

Demo-Plugin-Service für die Lernplattform [LeTTo](https://letto.at), geschrieben in Python mit [FastAPI](https://fastapi.tiangolo.com).
Es ist eine Portierung des [Referenz-Plugins in Java](https://github.com/LeTTo-GmbH/plugin-demo-java) und implementiert dieselbe REST-Schnittstelle.
Das Image dient als Vorlage für die Entwicklung eigener LeTTo-Plugins in Python – es ist **nicht für den Unterrichtseinsatz** gedacht.

Das enthaltene Plugin **UhrPy** zeigt ein Uhrblatt, auf dem Schülerinnen und Schüler durch Klicken die Zeiger stellen.
Die eingestellte Uhrzeit wird als Antwort (`HH:MM`) an LeTTo übergeben und vom Plugin bewertet (mit relativer oder absoluter Toleranz).

## Links

| | |
|---|---|
| Quellcode (Python) | <https://github.com/LeTTo-GmbH/plugin-demo-python> |
| Referenz-Plugin (Java) | <https://github.com/LeTTo-GmbH/plugin-demo-java> |
| Dokumentation dieses Plugins (Python) | <https://doc.letto.at/wiki/Plugins/referenz-plugin-python/> |
| Eigenes Plugin in Python erstellen | <https://doc.letto.at/wiki/Plugins/referenz-plugin-python/eigenes-plugin/> |
| Unterschiede zur Java-Version (REST) | <https://doc.letto.at/wiki/Plugins/referenz-plugin-python/rest-schnittstelle/> |
| Dokumentation Referenz-Plugin (Java) | <https://doc.letto.at/wiki/Plugins/referenz-plugin-java/> |
| REST-Schnittstelle | <https://doc.letto.at/wiki/Plugins/referenz-plugin-java/rest-schnittstelle/> |
| DTOs | <https://doc.letto.at/wiki/Plugins/referenz-plugin-java/dtos/> |
| Enums | <https://doc.letto.at/wiki/Plugins/referenz-plugin-java/enums/> |
| LeTTo-Wiki: Plugins | <https://doc.letto.at/wiki/Plugins/> |
| LeTTo | <https://letto.at> |

## Installation am LeTTo-Server

Der Container läuft im Docker-Netzwerk `nw-letto` neben den übrigen LeTTo-Services und registriert sich beim Start selbst am Setup-Service.

1. [`yml/docker-service-plugindemopython.yml`](https://github.com/LeTTo-GmbH/plugin-demo-python/blob/master/yml/docker-service-plugindemopython.yml)
   nach `/opt/letto/docker/compose/letto/` kopieren und starten:
   ```bash
   docker compose -f /opt/letto/docker/compose/letto/docker-service-plugindemopython.yml up -d
   ```
2. Proxy-Konfiguration [`proxy/plugindemopython.conf`](https://github.com/LeTTo-GmbH/plugin-demo-python/blob/master/proxy/plugindemopython.conf)
   nach `/opt/letto/docker/proxy/` kopieren und den Proxy neu starten:
   ```bash
   docker restart letto-proxy
   ```

## Endpoints

| Pfad | Beschreibung |
|---|---|
| `https://<servername>/plugindemopython/help` | Hilfeseite des Plugins |
| `https://<servername>/plugindemopython/docs` | API-Dokumentation (Swagger UI) mit Links zur Referenz-Doku |
| `https://<servername>/plugindemopython/openapi.json` | OpenAPI-Spezifikation |
| `/open/*` | Interne Plugin-API, wird von LeTTo im Docker-Netz aufgerufen |
| `/plugindemopython/open/*` | Derselbe Satz an Endpoints über den Proxy |
| `/plugindemopython/api/open/*` | Externe Open-API für den Browser |
| `/ping`, `/info`, `/version` | Erreichbarkeit und Service-Informationen |

## Ports

| Port | Verwendung |
|---|---|
| `8080` | REST-API (uvicorn) |
| `5080` | Debugger (debugpy), nur bei `debug=true` |

## Wichtige Umgebungsvariablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `SERVICEPATH` | `/plugindemopython` | Pfad des Services am Proxy, muss zur `location` in der Proxy-Konfiguration passen |
| `letto_setup_uri` | `http://letto-setup.nw-letto:8096` | URI des Setup-Services für die Registrierung |
| `letto_user_user_password` | – | Passwort für die Registrierung am Setup-Service |
| `letto_plugin_uri_intern` | `http://letto-plugindemopython.nw-letto:8080` | Interne URI des Plugins im Docker-Netz |
| `letto_plugin_uri_extern` | – | Externe URI des Servers (`https://<servername>`) |
| `debug` | `false` | Startet den Service mit debugpy auf Port 5080 |

## Tags

- `latest` – aktueller Stand des `master`-Branches
