from dataclasses import dataclass
from typing import Callable, List, Any

@dataclass
class Rule:
    name: str
    weight: float
    func: Callable  # La fonction de l'expert

# C'est ici que toutes les règles seront "stockées" automatiquement
RULE_REGISTRY: List[Rule] = []

def eval_rule(name: str, weight: float = 1.0) -> Callable[[Callable], Callable]:
    """Le décorateur qui enregistre les fonctions des experts."""
    def decorator(func: Callable):
        # On crée l'entrée dans le registre
        metadata = Rule(name=name, weight=weight, func=func)
        RULE_REGISTRY.append(metadata)

        # On renvoie la fonction originale sans la modifier
        return func
    return decorator

#La structure de résultat que chaque règle doit retourner

@dataclass
class EvaluationResult:
    label: str
    success: bool
    score: float  # Entre 0.0 et 1.0
    evidence: str # Justification (ex: "J'ai trouvé 12 fichiers FR")
    def __str__(self):
        icon = "✅" if self.success else "❌"
        return f"{icon} {self.label}: {self.evidence} (score: {self.score:.2f})"

@dataclass
class RuleReport:
    rule: Rule
    results: List[EvaluationResult]
    avg_score: float
    status: str

    def __str__(self):
        icon = "🟢" \
            if self.status == "Green" \
            else "🟠" if self.status == "Orange" else "🔴"
        details = "\n    ".join(str(r) for r in self.results)
        return f"{icon} {self.rule.name:<25} | Score: {self.avg_score:.2f} | \n Details:\n    {details} "