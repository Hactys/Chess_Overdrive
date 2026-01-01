import os
from fastapi.templating import Jinja2Templates

# détecter dossier racine du projet GUI
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

templates_path = os.path.join(ROOT_DIR, "templates")

templates = Jinja2Templates(directory=templates_path)

# Ajout filtres Jinja
def probacolor(prob):
    r = int(255 * (1 - prob))
    g = int(255 * prob)
    return f"rgb({r},{g},0)"

templates.env.filters["probacolor"] = probacolor
