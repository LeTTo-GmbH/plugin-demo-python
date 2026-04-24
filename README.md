# plugin-python (Port von plugin-java)

Dieses Projekt ist eine Python/FastAPI-Portierung der REST-API aus `plugin-java`.
Der Fokus liegt auf denselben Endpoints + dem Demo-Plugin **Uhr1**.

## Build des Docker-Containers (build.bat)
```bash
docker build -t letto-plugin-python:latest -f Dockerfile .
```

## Installation am LeTTo-Server
* Installation des Docker-Containers:
  * kopiere yml/docker-service-pluginpython.yml in /opt/letto/docker/compose/letto/ am LeTTo-Server 
  * starte den Container (docker compose -f /opt/letto/docker/compose/letto/ docker-service-pluginpython.yml up -d)
* Proxy Konfiguration:
  * kopiere proxy/pluginpython.conf in /opt/letto/docker/proxy/ am LeTTo-Server 
  * restarte den Proxy (docker restart letto-proxy)
* Ressourcen-Synchronisierung:
  * Beim Start kopiert der Service automatisch `RESOURCE_DIR/plugins` in die gesetzten Zielpfade:
    * `${letto_pathPlugins}` (z. B. `/opt/letto/plugins`)
    * `${letto_pathImages}/plugins` (z. B. `/opt/letto/images/plugins`)

## Wichtige Endpoints
- `GET /ping`  → `pong`
- `GET /pluginpython/open/ping` → `pong`
- `GET /info` und `GET /pluginpython/open/info` → `ServiceInfoDTO`

Interne Plugin-API (wie Java `@RequestMapping("/open")`):
- `GET  /open/pluginlist`
- `GET  /open/generalinfolist`
- `POST /open/generalinfo` (Body ist **String** wie in Java)
- `POST /open/gethtml`
- `POST /open/angabe`
- `POST /open/image`
- `POST /open/loadplugindto`
- `POST /open/score`
- ...

Für Proxy-Setups wird zusätzlich derselbe Satz unter `/pluginpython/open/*` angeboten.

Externe Open-API (wie Java `@RequestMapping("/pluginpython/api/open")`):
- `GET  /pluginpython/api/open/pluginlist`
- `GET  /pluginpython/api/open/generalinfolist`
- `POST /pluginpython/api/open/generalinfo`
- `POST /pluginpython/api/open/reloadplugindto`
