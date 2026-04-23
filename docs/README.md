# Documentations

This directory contains documentation for the metamodel and its environment.

Under the `docs` directory, you will find:
- [images](./images): This directory contains all the images used in the documentation.
- [plantuml](./plantuml): This directory contains all the plantuml diagrams used in the documentation.
   - The first version of these diagrams was generated using commands like:     
   `pyreverse -o plantuml -p mlartefacts -A -S -my ./DSL4Pipelines/src/metamodel/artefacts/ml_artefacts.py`
     - [architecture](plantuml/architecture): This directory contains the architecture of the project described as plantuml diagrams.
     - [usecases](./usecases): This directory contains the use cases of the project described as plantuml diagrams.
- [documents](./documents): This directory contains all the documents related to the project, such as the report of the internship and the work-link training.
