import os
import sys

# Beim Import von app.main keine Registrierung am Setup starten und Ressourcen aus dem Projekt lesen
os.environ.setdefault("PLUGIN_REGISTER_ON_READY", "false")
os.environ.setdefault("RESOURCE_DIR", os.path.join(os.path.dirname(__file__), "..", "resources"))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
