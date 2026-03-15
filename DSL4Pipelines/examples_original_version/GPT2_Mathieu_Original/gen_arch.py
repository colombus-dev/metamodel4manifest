import yaml

def generate_plantuml(yaml_data):
    arch = yaml_data.get('architecture', {})
    tok = yaml_data.get('tokenizer', {})

    # Début du template PlantUML
    puml = ["@startuml", "skinparam componentStyle rectangle", f"title Architecture {yaml_data.get('name', 'Model')}"]

    # Phase Tokenizer
    puml.append('package "Tokenizer" {')
    puml.append(f"  [{tok.get('type')}] as T1")
    puml.append(f"  note right of T1 : Vocab: {tok.get('n_vocab')}")
    puml.append("}")

    # Phase Architecture
    puml.append('package "Transformer Stack" {')
    puml.append(f"  node \"{arch.get('n_transformers')} Layers\" {{")
    puml.append(f"    [Attention: {arch.get('transformer_attention', {}).get('n_heads')} Heads] as Attn")
    puml.append(f"    [FFN: {arch.get('transformer_ffn', {}).get('hidden_layer_size')}] as FFN")
    puml.append("    Attn -> FFN")
    puml.append("  }")
    puml.append("}")

    # Liaisons
    puml.append("T1 --> Attn : Embed Dim " + str(arch.get('n_embedding_dimensions')))
    puml.append("@enduml")

    return "\n".join(puml)

# Lecture du fichier
with open("llm.yaml", "r") as f:
    data = yaml.safe_load(f)

# Génération et affichage
plantuml_code = generate_plantuml(data)
print(plantuml_code)

# Optionnel : Sauvegarder dans un fichier .puml
with open("architecture.puml", "w") as f:
    f.write(plantuml_code)