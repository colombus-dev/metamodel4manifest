from typing import List

from DSL4Pipelines.src.metamodel.artefacts.ml_artefacts import Data
from DSL4Pipelines.src.metamodel.artefacts.metrics import Metric

from DSL4Pipelines.src.metamodel.pipelines.workflow import Step, Task, Pipeline

from DSL4Pipelines.src.metamodel.relations.relations import Relationship

from DSL4Pipelines.src.metamodel.catalogs.vocabulary import RelationshipType
from DSL4Pipelines.src.metamodel.manifests.manifests import Manifest
from DSL4Pipelines.src.tools.queries.manifest_query import ManifestQuery
from DSL4Pipelines.src.metamodel.artefacts.artefacts import Artefact

ds1 = Data(name="ds1")
ds2 = Data(name="ds2")
metric1 = Metric(name="metric1")
metric2 = Metric(name="metric2")

step1 = Step(name="step1")
step2 = Step(name="step2")
step3 = Step(name="step3")
step4 = Step(name="step4")
task1 = Task(name="task1", steps=[step1, step2])
task2 = Task(name="task2", steps=[step3, step4])
pipeline = Pipeline(name="pipeline1", tasks=[task1, task2])
'''rel_1_ds1_t1 = Relationship(
    name="relation1",
    from_=ds1,
    to_=[task1, step3],
    relationship_type=RelationshipType.USED_BY,
)
'''
rel_1_t1_ds1 = Relationship(
    name="relation1",
    from_=task1,
    to_=[ds1],
    relationship_type=RelationshipType.USES,
)
rel_1_st3_ds1 = Relationship(
    name="relation1",
    from_=step3,
    to_=[ds1],
    relationship_type=RelationshipType.USES,
)
'''
rel_2_ds2_t1 = Relationship(
    name="relation2",
    from_=ds2,
    to_=[task1],
    relationship_type=RelationshipType.USED_BY,
)
'''

rel_2_t1_ds2 = Relationship(
    name="relation2",
    from_=task1,
    to_=[ds2],
    relationship_type=RelationshipType.USES,
)

rel_3_t1_m1 = Relationship(
    name="relation3",
    from_=task1,
    to_=[metric1],
    relationship_type=RelationshipType.PRODUCES,
)
''' rel_3_m1_t1 = Relationship(
    name="relation3",
    from_=metric1,
    to_=[task1],
    relationship_type=RelationshipType.PRODUCES,
)
'''
rel_4_t1_t2 = Relationship(
    name="relation4",
    from_=task1,
    to_=[task2],
    relationship_type=RelationshipType.NEXT,
)
rel_5_s4_m2 = Relationship(
    name="relation5",
    from_=step4,
    to_=[metric2],
    relationship_type=RelationshipType.PRODUCES,
)

'''rel_6_m2_t2 = Relationship(
    name="relation6",
    from_=metric2,
    to_=[task2],
    relationship_type=RelationshipType.USED_BY,
)
'''
rel_6_t2_m2 = Relationship(
    name="relation6",
    from_=task2,
    to_=[metric2],
    relationship_type=RelationshipType.PRODUCES,
)

manifest = Manifest(
    name="manifest1",
    artefacts=[ds1, ds2, metric1, metric2],
    pipeline=pipeline,
    relations=[
#        rel_1_ds1_t1,
        rel_1_t1_ds1,
        rel_1_st3_ds1,
        #rel_2_ds2_t1,
        rel_2_t1_ds2,
        #rel_3_m1_t1,
        rel_3_t1_m1,
        rel_4_t1_t2,
        rel_5_s4_m2,
        rel_6_t2_m2
        #rel_6_m2_t2,
    ],
)
mq = ManifestQuery(manifest)


def test_get_input_relations():
    input_relations = mq.get_input_relations(task1)
    assert len(input_relations) == 0
#    assert rel_1_ds1_t1 in input_relations
#    assert rel_2_ds2_t1 in input_relations
   # assert rel_3_m1_t1 in input_relations
   # assert rel_3_t1_m1 in input_relations

    input_relations = mq.get_input_relations(step4)
    assert len(input_relations) == 0

    input_relations = mq.get_input_relations(step3)
    assert len(input_relations) == 0
    input_relations = mq.get_input_relations(ds1)
    assert rel_1_st3_ds1 in input_relations

    input_relations = mq.get_input_relations(step1)
    assert len(input_relations) == 0


def test_get_input_artefacts_on_tasks():
    input_artefacts: List[Artefact] = mq.get_input_artefacts(task1)
    assert len(input_artefacts) == 0
    #assert ds1 in input_artefacts
    #assert ds2 in input_artefacts
    input_artefacts: List[Artefact] = mq.get_input_artefacts(step4)
    assert len(input_artefacts) == 0
    input_artefacts: List[Artefact] = mq.get_input_artefacts(step3)
    assert len(input_artefacts) == 0
#    assert ds1 in input_artefacts
    input_artefacts: List[Artefact] = mq.get_input_artefacts(step1)
    assert len(input_artefacts) == 0


def test_get_input_artefacts_of_manifest():
    input_artefacts: List[Artefact] = mq.get_input_artefacts()
    assert len(input_artefacts) == 0
#    assert metric1 in input_artefacts
#    assert ds2 in input_artefacts
#    assert ds1 in input_artefacts
