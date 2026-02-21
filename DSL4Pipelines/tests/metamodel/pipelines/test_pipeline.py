from DSL4Pipelines.src.metamodel.pipelines.workflow import Pipeline, Task


def test_pipeline():
    pipeline = Pipeline(name="Test Pipeline", uid="pipeline-123")
    assert pipeline.name == "Test Pipeline"
    assert pipeline.uid == "pipeline-123"
    assert pipeline.type == "Pipeline"


def test_pipelineWithTasks() -> Pipeline:
    pipeline = Pipeline(
        uid="pipeline-01",
        name="Example Pipeline",
        tasks=[Task(uid="task-01", name="Data Preprocessing")],
    )
    assert len(pipeline.tasks) == 1
    assert pipeline.tasks[0].uid == "task-01"
    assert pipeline.tasks[0].name == "Data Preprocessing"
    return pipeline
