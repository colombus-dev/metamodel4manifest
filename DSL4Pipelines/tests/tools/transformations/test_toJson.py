from DSL4Pipelines.src.tools.transformations.toJson import yaml_to_json
from DSL4Pipelines.src.tools.toFile import print_cwd
from pathlib import Path

def test_to_json():
    print_cwd()
    # Cela récupère le dossier où se trouve le fichier .py actuel
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    print(f"Base directory: {BASE_DIR}")
    # Ensuite, tu construis ton chemin à partir de la racine du projet
    #read yaml file and transform it to json
    file = BASE_DIR /"tests/examples/sources/nanoGPT_manifest3.yaml"
    output_dir = "examples/outputs/"
    outputPath = yaml_to_json(file,output_dir)
    print(f"Json file generated in : {outputPath}")

