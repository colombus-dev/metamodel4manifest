import os

import logging
logging.basicConfig(
    level=logging.INFO, # Niveau par défaut pour TOUT le monde
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def save_in_file(path: str, file_name: str, input: str):
    file_path = os.path.join(path, file_name)
    # 2. On crée le dossier s'il n'existe pas
    # exist_ok=True évite une erreur si le dossier est déjà là
    os.makedirs(path, exist_ok=True)
    # 3. On écrit le fichier
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(input)

    logger.debug(f"Fichier sauvegardé dans : {file_path}")


# Print the current working directory
def print_cwd():
    cwd = os.getcwd()
    logger.debug(f"\nCurrent working directory: {cwd}")


#check if the file or directory exists
def check_file_or_dict_exists(file_path: str) -> bool:
    if os.path.exists(file_path):
        logger.debug(f"✅ The file or directory '{file_path}' exists.")
        return True
    else:
        logger.warning(f"❌ The file or directory '{file_path}' does not exist.")
        return False