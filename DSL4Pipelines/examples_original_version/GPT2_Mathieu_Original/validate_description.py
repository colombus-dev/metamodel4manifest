import yaml

def validate_llm_pipeline(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    produced_outputs = set()
    errors = []
    warnings = []

    print(f"--- Analyse du pipeline : {data.get('name')} ---")

    # Premier passage : Collecter tous les IDs produits et vérifier les nulls
    for entry in data.get('pipeline', []):
        step = entry.get('step')
        if not step: continue

        step_type = step.get('type', 'Unknown')

        # 1. Test des valeurs à null dans toute l'étape
        def check_nulls(obj, path):
            if obj is None:
                warnings.append(f"[NULL] {path} est à null.")
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    check_nulls(v, f"{path} > {k}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_nulls(item, f"{path}[{i}]")

        check_nulls(step, step_type)

        # 2. Enregistrement des sorties produites
        for output in step.get('outputs', []):
            out_id = output.get('id')
            if out_id:
                produced_outputs.add(out_id)

    # Deuxième passage : Vérifier si les références existent
    for entry in data.get('pipeline', []):
        step = entry.get('step')
        if not step: continue

        step_type = step.get('type')
        for inp in step.get('input_data', []):
            ref_name = inp.get('refs')
            if ref_name not in produced_outputs:
                errors.append(f"[MISSING REF] L'étape '{step_type}' attend '{ref_name}', mais cet ID n'est produit par aucune étape précédente.")
            else:
                print(f"[OK] Référence trouvée : {ref_name} (utilisée par {step_type})")

    # Affichage du rapport final
    print("\n--- RAPPORT DE VALIDATION ---")

    if warnings:
        print(f"\n⚠️  AVERTISSEMENTS ({len(warnings)}):")
        for w in warnings: print(f"  {w}")

    if errors:
        print(f"\n❌ ERREURS ({len(errors)}):")
        for e in errors: print(f"  {e}")
    else:
        print("\n✅ Toutes les références sont valides.")

# Lancement
validate_llm_pipeline('gpt2.yaml')