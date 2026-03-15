

##----------
# Define the metrics used to monitor model performance while training.
METRICS = [
    tf.keras.metrics.BinaryAccuracy(name='accuracy'),
    tf.keras.metrics.AUC(name='auc'),
    tf.keras.metrics.FalseNegatives(name='fn'),
    tf.keras.metrics.FalsePositives(name='fp'),
]

# Configure the model for training using a stochastic gradient descent
# optimizer, cross-entropy loss between true labels and predicted labels, and
# the metrics defined above to evaluate the base model during training.
base_model.compile(
    optimizer='adam',
    loss=tf.keras.losses.BinaryCrossentropy(),
    metrics=METRICS)
##----------------------------




# Save model
baseModelName = 'base_model3.keras'
base_model.save(baseModelName)

#telecharger le model sur la machine
from google.colab import files
# Cela va ouvrir une fenêtre de téléchargement sur ta machine
files.download(baseModelName)

#charger le model depuis la machine
loaded_base_model = tf.keras.models.load_model(baseModelName)

# Vérifier que le modèle chargé fonctionne correctement
loaded_base_model.summary()

#pour que la suite continue à fonctionner, on remplace le modèle de base par le modèle chargé
base_model = loaded_base_model

#pour évaluer le modele chargé : c'est dans le notebook.
# Use the indices from the training set to create the test set, which represents
# 20% of the original dataset; then convert it to a tf.data.Dataset object, and
# evaluate the base model using the converted test set.
acs_test_df = acs_df.drop(acs_train_df.index).sample(frac=1.0)
acs_test_ds = dataframe_to_dataset(acs_test_df)
acs_test_batches = acs_test_ds.batch(BATCH_SIZE)

base_model.evaluate(acs_test_batches, batch_size=BATCH_SIZE)

## EVALUATION..
Specify Fairness Indicators using eval_config.
eval_config_pbtxt = """
  model_specs {
    prediction_key: "%s"
    label_key: "%s" }
  metrics_specs {
    metrics { class_name: "ExampleCount" }
    metrics { class_name: "BinaryAccuracy" }
    metrics { class_name: "AUC" }
    metrics { class_name: "ConfusionMatrixPlot" }
    metrics {
      class_name: "FairnessIndicators"
      config: '{"thresholds": [0.50]}'
    }
  }
  slicing_specs {
    feature_keys: "%s"
  }
  slicing_specs {}
""" % (PREDICTION_KEY, LABEL_KEY, SENSITIVE_ATTRIBUTE_KEY)
eval_config = text_format.Parse(eval_config_pbtxt, tfma.EvalConfig())

# Run TensorFlow Model Analysis.
base_model_eval_result = tfma.analyze_raw_data(base_model_analysis, eval_config)

#----------------------------
#@todo tenter des evalutions directement sur ces données
# Lister toutes les tranches (slices) calculées
for slice_key, metrics_data in base_model_eval_result.slicing_metrics:
    print(f"Slice trouvée : {slice_key}")





def extract_metrics_to_dict(eval_result):
    summary = {}

    for slice_key, metrics_data in eval_result.slicing_metrics:
        # On transforme le tuple de la slice en string lisible (ex: 'gender:Male')
        slice_name = str(slice_key) if slice_key else "Global"

        # Accès profond aux métriques (structure standard TFMA)
        # metrics_data est un dictionnaire où les clés sont les noms des sorties du modèle
        all_metrics = metrics_data['']['']

        summary[slice_name] = {
            'accuracy': all_metrics['binary_accuracy']['doubleValue'],
            'auc': all_metrics['auc']['doubleValue'],
            'count': all_metrics['example_count']['doubleValue']
        }
    return summary
metrics_dict = extract_metrics_to_dict(base_model_eval_result)
print(metrics_dict['Global'])

{'accuracy': 0.8052057674977471, 'auc': 0.8826337069400935, 'count': 332900.0}


import pandas as pd

def get_metrics_by_slice(eval_result):
    rows = []

    # Parcourir chaque slice calculée par TFMA
    for slice_key, metrics_data in eval_result.slicing_metrics:
        # 1. Identifier le nom de la slice (ex: 'gender: Male' ou 'Overall')
        slice_label = str(slice_key) if slice_key else "Overall"

        # 2. Accéder aux métriques (on descend dans la structure TFMA)
        # On cible la sortie par défaut ('') et la classe par défaut ('')
        m = metrics_data['']['']

        # 3. Extraire les métriques souhaitées de façon sécurisée
        row = {
            'Slice': slice_label,
            'Count': m.get('example_count', {}).get('doubleValue', 0),
            'Accuracy': m.get('binary_accuracy', {}).get('doubleValue', 0),
            'AUC': m.get('auc', {}).get('doubleValue', 0),
        }

        # Extraction du FNR (False Negative Rate) si présent
        if 'false_negatives' in m and 'true_positives' in m:
            fn = m['false_negatives']['doubleValue']
            tp = m['true_positives']['doubleValue']
            row['FNR'] = fn / (fn + tp) if (fn + tp) > 0 else 0

        rows.append(row)

    return pd.DataFrame(rows)

# --- Utilisation ---
df_metrics = get_metrics_by_slice(base_model_eval_result)
print(df_metrics)

Slice     Count  Accuracy       AUC
0               Overall  332900.0  0.805206  0.882634
1    (('SEX', 'Male'),)  173245.0  0.786938  0.872834
2  (('SEX', 'Female'),)  159655.0  0.825029  0.884376

fprn = 'fairness_indicators_metrics/false_positive_rate@0.5'
fnrn = 'fairness_indicators_metrics/false_negative_rate@0.5'
tnrn = 'fairness_indicators_metrics/true_negative_rate@0.5'
tprn = 'fairness_indicators_metrics/true_positive_rate@0.5'

def extract_detailed_fairness_metrics(eval_result):
    rows = []
    for slice_key, metrics_data in eval_result.slicing_metrics:
        slice_label = str(slice_key) if slice_key else "Overall"

        # Accès à la structure TFMA (Output vide, Class vide)
        m = metrics_data['']['']

        # Extraction des valeurs brutes de la matrice de confusion
        # Note : TFMA les nomme souvent ainsi selon ta config
        fn = m.get(fnrn, {}).get('doubleValue', 0)
        tp = m.get(tprn, {}).get('doubleValue', 0)
        fp = m.get(fprn, {}).get('doubleValue', 0)
        tn = m.get(tnrn, {}).get('doubleValue', 0)

        # Calcul du False Negative Rate (FNR) : FN / (FN + TP)
        # C'est la proportion de "Gagnants" manqués par le modèle
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0

        rows.append({
            'Slice': slice_label,
            'Total': m.get('example_count', {}).get('doubleValue', 0),
            'FN (Faux Négatifs)': fn,
            'TP (Vrais Positifs)': tp,
            'FNR (Taux de manqués)': round(fnr, 4),
            'Accuracy': round(m.get('binary_accuracy', {}).get('doubleValue', 0), 4)
        })

    return pd.DataFrame(rows)

# Exécution
df_fairness = extract_detailed_fairness_metrics(base_model_eval_result)
print(df_fairness)




Slice     Total  FN (Faux Négatifs)  TP (Vrais Positifs) \
    0               Overall  332900.0            0.277667             0.722333
1    (('SEX', 'Male'),)  173245.0            0.232726             0.767274
2  (('SEX', 'Female'),)  159655.0            0.351260             0.648740

FNR (Taux de manqués)  Accuracy
0                 0.2777    0.8052
1                 0.2327    0.7869
2                 0.3513    0.8250


def validate_model_compliance(df_metrics, max_fnr_gap=0.10, min_accuracy=0.75):
    """
    Vérifie si le modèle respecte les seuils de performance et d'équité.
    """
    # 1. Extraction des tranches (en ignorant la ligne 'Overall' si elle existe)
    # On suppose que l'index 1 et 2 sont tes groupes (ex: Male/Female)
    group_a_fnr = df_metrics.iloc[1]['FNR (Taux de manqués)']
    group_b_fnr = df_metrics.iloc[2]['FNR (Taux de manqués)']
    overall_acc = df_metrics.iloc[0]['Accuracy']

    # 2. Calcul du Gap
    fnr_gap = abs(group_a_fnr - group_b_fnr)

    # 3. Vérification des conditions
    is_fair = fnr_gap <= max_fnr_gap
    is_performant = overall_acc >= min_accuracy

    print("=== RAPPORT D'AUDIT AUTOMATISÉ ===")
    print(f"Gap de FNR détecté : {fnr_gap:.4f} (Seuil max: {max_fnr_gap})")
    print(f"Accuracy Globale    : {overall_acc:.4f} (Seuil min: {min_accuracy})")
    print("-----------------------------------")

    if is_fair and is_performant:
        print("✅ RÉSULTAT : MODÈLE CONFORME")
        return True
    else:
        reasons = []
        if not is_fair: reasons.append(f"Biais trop élevé (Gap > {max_fnr_gap})")
        if not is_performant: reasons.append(f"Précision insuffisante (< {min_accuracy})")
        print(f"❌ RÉSULTAT : MODÈLE REJETÉ ({', '.join(reasons)})")
        return False

# Utilisation :
# compliance_passed = validate_model_compliance(df_fairness)

=== RAPPORT D'AUDIT AUTOMATISÉ ===
Gap de FNR détecté : 0.1186 (Seuil max: 0.1)
Accuracy Globale    : 0.8052 (Seuil min: 0.75)
-----------------------------------
❌ RÉSULTAT : MODÈLE REJETÉ (Biais trop élevé (Gap > 0.1))



### ----

base_model_eval_result.get_metric_names()
base_model_eval_result.get_slice_names()


# sauvegarder les modeles après remediation
mitigated_model_name_original = 'rm_original.keras'
mitigated_model_name = 'rm.keras'
# On extrait le modèle Keras standard qui est à l'intérieur du wrapper MinDiff
model_to_export = min_diff_model.original_model

# On le sauvegarde (format .keras recommandé pour Keras 3 / TF 2.16+)
model_to_export.save(mitigated_model_name_original)
min_diff_model.save(mitigated_model_name)

# Pour le téléchargement
from google.colab import files
files.download(mitigated_model_name_original)
files.download(mitigated_model_name)

#------------------------
#travail sur les resultats

# On suppose que tu as un DataFrame 'test_df' qui contient les données brutes
# On crée deux masques pour filtrer
mask_male = test_df['gender'] == 'Male'
mask_female = test_df['gender'] == 'Female'

# Note : Il faut transformer ces sous-ensembles en datasets compatibles avec ton modèle
# (C'est l'étape un peu technique dépendant du preprocessing du notebook)

def eval_by_gender(model, df_subset):
    # Transformation du DataFrame en Dataset (simplifié)
    ds = tf.data.Dataset.from_tensor_slices(dict(df_subset)).batch(128)
    return model.evaluate(ds, verbose=0)

# Exemple de logique :
# results_male = eval_by_gender(min_diff_model.original_model, test_df[mask_male])
# results_female = eval_by_gender(min_diff_model.original_model, test_df[mask_female])