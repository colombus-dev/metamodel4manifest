import yaml

def generate_rich_puml(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    puml = [
        "@startuml",
        "skinparam shadowing false",
        "skinparam PackageBackgroundColor #F9F9F9",
        f"title Architecture détaillée : {data.get('name', 'Modèle LLM')}",
        "left to right direction"
    ]

    for entry in data.get('pipeline', []):
        step = entry.get('step')
        if not step: continue

        s_type = step['type']

        # 1. Gestion de DataCollection
        if s_type == "dataCollection":
            puml.append(f'package "{s_type}" {{')
            for out in step.get('outputs', []):
                p_id = out['id']
                puml.append(f'  file "{p_id}" as {p_id} #lightgreen')
                if 'replication' in out:
                    puml.append(f'  note bottom of {p_id} : {out["replication"].get("location", "")}')
            puml.append('}')

        # 2. Gestion de Tokenization
        elif s_type == "tokenization":
            tk = step.get('tokenizer', {})
            puml.append(f'package "{s_type}" {{')
            puml.append(f'  component "Byte-BPE Engine" as {s_type}_logic {{')
            puml.append(f'    map Params_Tok {{')
            puml.append(f'      impl => {tk.get("implementation", "")[:30]}...')
            puml.append(f'    }}')
            puml.append('  }')
            puml.append('}')
            for out in step.get('outputs', []):
                puml.append(f'  file "{out["id"]}\\n(Vocab: {out.get("n_tokens")})" as {out["id"]} #lightgreen')
                puml.append(f'{s_type}_logic --> {out["id"]}')

        # 3. Gestion de PreTraining (Le plus riche)
        elif s_type == "preTraining":
            mc = step.get('model_config', {})
            tc = step.get('training_config', {})
            puml.append(f'package "PreTraining & Architecture" {{')
            puml.append(f'  component "GPT Decoder Stack" as {s_type}_model {{')
            puml.append(f'    map Model_Specs {{')
            puml.append(f'      Params => {mc.get("n_parameters")}')
            puml.append(f'      Layers => {mc.get("n_transformers")}')
            puml.append(f'      Embed_Dim => {mc.get("n_embedding_dimensions")}')
            puml.append(f'      FFN_Hidden => {mc.get("transformer_ffn", {}).get("hidden_layer_size")}')
            puml.append(f'    }}')
            puml.append('  }')

            puml.append(f'  component "Optimizer: {tc.get("optimizer", {}).get("type")}" as opt {{')
            puml.append(f'    map Opt_Params {{')
            puml.append(f'      weight_decay => {tc.get("optimizer", {}).get("weight_decay")}')
            puml.append(f'      beta1 => {tc.get("optimizer", {}).get("beta1")}')
            puml.append(f'    }}')
            puml.append('  }')
            puml.append('}')
            for out in step.get('outputs', []):
                puml.append(f'  file "{out["id"]}" as {out["id"]} #lightgreen')
                puml.append(f'{s_type}_model --> {out["id"]}')

        # 4. Connexions basées sur les REFS
        if 'input_data' in step:
            for inp in step['input_data']:
                ref = inp.get('refs')
                dest = s_type + "_logic" if s_type == "tokenization" else s_type + "_model"
                puml.append(f'{ref} --> {dest}')

    puml.append("@enduml")
    return "\n".join(puml)

# Sauvegarde
with open('rich_architecture.puml', 'w', encoding='utf-8') as f:
    f.write(generate_rich_puml('gpt2.yaml'))