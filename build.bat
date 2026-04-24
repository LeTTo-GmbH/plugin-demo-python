docker build -t lettohub/letto-plugin-python:latest -f Dockerfile .
docker compose -f /opt/letto/docker/compose/letto/docker-service-pluginpython.yml down
copy yml\docker-service-pluginpython.yml \opt\letto\docker\compose\letto\
docker compose -f /opt/letto/docker/compose/letto/docker-service-pluginpython.yml up -d