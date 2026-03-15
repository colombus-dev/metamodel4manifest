# Cette partie est principalement inspirée de cyclone.
"""This module defines the metamodel for representing
workflows, tasks, steps, and commands in a structured way.
It is inspired by the CycloneDX model, but adapted to fit the specific needs of
representing pipelines in the context of machine learning and data science workflows.
The roots of the model are based on the concepts defined by Activity Diagrams in UML"""

from dataclasses import dataclass, field
from typing import List, Optional

from DSL4Pipelines.src.metamodel.core.structure import Element


@dataclass
class ActityNode:
    """ActivityNode represents a node in the activity graph,
    which can be a Task, Step, or Command."""


@dataclass
class Activity:
    """Activity represents a collection of ActivityNodes"""


@dataclass
class Command(ActityNode,Element):
    """Command represents a command to be executed, including the command string,
    optional shell and working directory, associated properties, and an optional external reference.
    It's directly inspired by the Command class of CycloneDX.
    We can consider that a command corresponds to an instruction in our model,
    but we can also have other types of commands, such as a command to execute a script, or a command to execute a notebook."""

    shell: Optional[str] = "python"  # python, bash, powershell, etc.
    working_directory: Optional[str] = None


#    properties: List[Property] = field(default_factory=list)
# je simplifie pour l'instant
#    external_reference: Optional[ExternalReference] = None


@dataclass
class Instruction(Command):
    """Instruction represents a specific type of Command
    that is directly related to the execution of a step in a task."""

    code: Optional[str] = None
    type: str = "Instruction"


@dataclass
class Task(ActityNode,Element):
    """Task represents a task within a workflow,
    which can contain ordered multiple steps."""

    type: str = "Task"
    steps: List[Step] = field(default_factory=list)

    def find_steps(self, **criteria) -> List[Step]:
        """
        Loop through all steps in the task
        and check if they match the given criteria.
        The criteria are passed as keyword arguments,
        where the key is the name of the property to check,
        and the value is the expected value of that property.
        Exemple: task.find_steps(name="Data Preprocessing", description="This step is responsible for preprocessing the data")
        """
        results = []

        for step in self.steps:
            match = True
            for key, expected_value in criteria.items():
                # we use our get_value method to get the value of the property, which will check both the actual attributes and the properties field of the artefact.
                actual_value = step.get_value(key)

                if actual_value != expected_value:
                    match = False
                    break

            if match:
                results.append(step)
        return results


## Je ne courcircuite pas le Modele de CycloneDX qui introduit un niveau en plus de nous...
## je choisis pour l'instant de rester dessus j'aurais un lien un à un entre STep et Task
@dataclass
class Step(ActityNode, Element):
    """Step represents a step in a task,
    which can contain multiple commands to be executed sequentially.
    Each step has a name and a list of commands associated with it."""

    type: str = "Step"
    commands: List[Command] = field(default_factory=list)


# The Workflow class represents a workflow, which can contain multiple tasks.
# As we only work on pipelines, we can consider that a workflow corresponds to a pipeline, and a task corresponds to a step in the pipeline.
# Should be translated as a workflow ...
@dataclass
class Pipeline(Activity,Element):
    """Pipeline represents a pipeline, which can contain multiple tasks.
    Each pipeline has a name and a list of tasks associated with it."""

    type: str = "Pipeline"
    #    bom_ref: str
    tasks: List[Task] = field(default_factory=list)

    def find_task(self, **criteria) -> List[Task]:
        """
        Loop through all tasks in the pipeline and check if they match the given criteria.
        The criteria are passed as keyword arguments, where the key is the name of the property to check, and the value is the expected value of that property.
        Exemple: pipeline.find_task(name="Data Preprocessing", description="This task is responsible for preprocessing the data")
        """
        results = []
        for task in self.tasks:
            match = True
            for key, expected_value in criteria.items():
                # we use our get_value method to get the value of the property, which will check both the actual attributes and the properties field of the artefact.
                actual_value = task.get_value(key)

                if actual_value != expected_value:
                    match = False
                    break

            if match:
                results.append(task)
        return results
