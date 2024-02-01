import json
import requests
from pathlib import Path
from threading import Thread


LINEAGE_HOME = Path().home() / ".lineage"
LINEAGE_CONFIG_DIR = LINEAGE_HOME / ".config"
LINEAGE_AUTOSAVE_DIR = LINEAGE_HOME / "autosave"
alternate_spells_web_url = (
    "https://aqdasak.github.io/lineage_list/alternate_spells.json"
)


alternate_spells = []

config = {
    "print_all_ancestors": False,
    "print_id_with_person": False,
    "print_id_with_parent": False,
    # Possible: 0(Expand female only), 1(Expand male only), 2(Complete)
    "print_expanded_tree": 2,
    "print_spouse_in_tree": True,
}


def load_config():
    """
    Load the config from storage
    """

    file = LINEAGE_CONFIG_DIR / "lineage_config.json"

    global config
    try:
        with open(file) as f:
            config.update(json.load(f))
            if not isinstance(config.get("print_all_ancestors"), bool):
                config["print_all_ancestors"] = False
            if not isinstance(config.get("print_id_with_person"), bool):
                config["print_id_with_person"] = False
            if not isinstance(config.get("print_id_with_parent"), bool):
                config["print_id_with_parent"] = False
            if not 0 <= config.get("print_expanded_tree") <= 2:
                config["print_expanded_tree"] = 2
            if not isinstance(config.get("print_spouse_in_tree"), bool):
                config["print_spouse_in_tree"] = True
    except Exception:
        pass


def save_config():
    """
    Save the config to storage
    """

    file = LINEAGE_CONFIG_DIR / "lineage_config.json"

    with open(file, "w") as f:
        json.dump(
            # Here dict is built so that any extra key-value loaded
            # does not get save again
            {
                "print_all_ancestors": config["print_all_ancestors"],
                "print_id_with_person": config["print_id_with_person"],
                "print_id_with_parent": config["print_id_with_parent"],
                "print_expanded_tree": config["print_expanded_tree"],
                "print_spouse_in_tree": config["print_spouse_in_tree"],
            },
            f,
        )


def load_alternate_spells():
    """
    Load alternate_spells from storage
    """

    file = LINEAGE_CONFIG_DIR / "alternate_spells.json"
    global alternate_spells
    try:
        with open(file) as f:
            # If `[:]` is not used, new variable is created and data is
            # not written in global variable. Other solution is using `+=`
            alternate_spells[:] = json.load(f)
    except Exception:
        pass


def fetch_alternate_spells_from_web():
    """
    Download alternate_spells from the web, update the currently using alternate_spells and save to storage
    """

    def _fetch_alternate_spells_from_web():
        global alternate_spells
        file = LINEAGE_CONFIG_DIR / "alternate_spells.json"

        try:
            result = requests.get(alternate_spells_web_url).text
            if result:
                alternate_spells[:] = json.loads(result)
                with open(file, "w") as f:
                    f.write(result)

        except Exception:
            pass

    Thread(target=_fetch_alternate_spells_from_web, daemon=True).start()


def initialize_save_directories():
    """Create the directories if not already present"""

    LINEAGE_HOME.mkdir(parents=True, exist_ok=True)
    LINEAGE_AUTOSAVE_DIR.mkdir(parents=True, exist_ok=True)
    LINEAGE_CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def setup():
    """Setup the program state, load the config and required variables"""

    initialize_save_directories()
    load_config()
    load_alternate_spells()
    fetch_alternate_spells_from_web()
