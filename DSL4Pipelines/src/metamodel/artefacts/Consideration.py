import uuid
from dataclasses import field
from typing import Optional


class Consideration:
    uid: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: Optional[str] = "Consideration"  # To distinguish from other types of artefacts

    def __init__(self, use_cases=None, limitations=None, ethical_risks=None, intended_users=None):
        # On utilise "or []" pour s'assurer d'avoir une liste même si on reçoit None
        self.use_cases = use_cases or [] # use_cases is a list of strings describing the use cases for which the model is suitable (e.g., "Classification d'images médicales", "Génération de texte créatif", etc.)
        self.limitations = limitations or [] #limitations is a list of strings describing the known limitations of the model (e.g., "Ne fonctionne pas bien sur les images de mauvaise qualité", "Tendance à halluciner des faits", etc.)

        self.ethical_risks = ethical_risks or [] #ethical_risks is a list of strings describing the potential ethical risks associated with the model (e.g., "Risque de biais si les données d'entraînement ne sont pas diversifiées", "Risque de génération de contenu inapproprié", etc.)
        self.intended_users = intended_users or [] #intended_users is a list of strings describing the intended users of the model (e.g., "Chercheurs en imagerie médicale", "Artistes numériques", etc.)


def test_consideration_one():
    cons = Consideration()
    cons.use_cases.append("Classification d'images médicales")
    cons.limitations.append("Ne fonctionne pas bien sur les images de mauvaise qualité")
    cons.ethical_risks.append("Risque de biais si les données d'entraînement ne sont pas diversifiées")

    assert len(cons.use_cases) == 1, "Expected 1 use case"
    assert len(cons.limitations) == 1, "Expected 1 limitation"
    assert len(cons.ethical_risks) == 1, "Expected 1 ethical risk"

    print("All tests passed for Considerations class !")

def test_consideration_empty():
    cons = Consideration()
    assert len(cons.use_cases) == 0, "Expected no use cases"
    assert len(cons.limitations) == 0, "Expected no limitations"
    assert len(cons.ethical_risks) == 0, "Expected no ethical risks"

    print("All tests passed for empty Considerations !")

def test_consideration_other():
    consideration = Consideration(
        use_cases=[
            "Génération d'images de personnages pour jeux de rôle",
            "Aide à la conception artistique (concept art)"
        ],
        limitations=[
            "Difficulté avec le rendu des mains et de l'anatomie complexe",
            "Ne convient pas pour du photoréalisme architectural"
        ],
        ethical_risks=[
            "Risque de reproduction de styles artistiques sans consentement",
            "Biais potentiel sur les stéréotypes de genre dans la fantasy"
        ],
        intended_users=[
            "Artistes numériques",
            "Maîtres de jeu (MJ)"
        ]
    )

