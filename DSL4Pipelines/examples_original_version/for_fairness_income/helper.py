import tensorflow as tf
from tensorflow.python.data.ops.dataset_ops import DatasetV2
import pandas as pd

LABEL_KEY = 'PINCP'
LABEL_THRESHOLD = 50000.0

RANDOM_STATE = 200
BATCH_SIZE = 100

MIN_DIFF_BATCH_SIZE = 50

METRICS = [
    tf.keras.metrics.BinaryAccuracy(name='accuracy'),
    tf.keras.metrics.AUC(name='auc'),
    tf.keras.metrics.FalseNegatives(name='fn'),
    tf.keras.metrics.FalsePositives(name='fp')
]

SENSITIVE_ATTRIBUTE_VALUES = {1.0: "Male", 2.0: "Female"}
SENSITIVE_ATTRIBUTE_KEY = 'SEX'
PREDICTION_KEY = 'PRED'

def dataframe_to_dataset(df: pd.DataFrame) -> DatasetV2:
    copied_df = df.copy()
    labels = copied_df.pop(LABEL_KEY)
    dataset = tf.data.Dataset.from_tensor_slices(
        ((dict(copied_df), labels)))
    return dataset

def dataframe_to_tf_batches(df: pd.DataFrame) -> DatasetV2:
    result_df = dataframe_to_dataset(df)
    return result_df.batch(BATCH_SIZE)
