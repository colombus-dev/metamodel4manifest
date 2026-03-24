from DSL4Pipelines.src.tools.transformations.toJson import yaml_to_json
from DSL4Pipelines.src.tools.toFile import print_cwd


def test_to_json():
    print_cwd()
    #read yaml file and transform it to json
    file = "examples/sources/nanoGPT_manifest3.yaml"
    output_dir = "examples/outputs/"
    outputPath = yaml_to_json(file,output_dir)
    print(f"Json file generated in : {outputPath}")

