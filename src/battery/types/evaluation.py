# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional

from .._models import BaseModel

__all__ = ["Evaluation", "Evaluations", "Usage"]


class Evaluations(BaseModel):
    critique: Union[str, float, List[int], List[str], object]

    score: int


class Usage(BaseModel):
    evaluation_tokens: int
    """The number of tokens produced by the model during the evaluation."""

    prompt_tokens: int
    """
    The number of tokens passed via the input, response fields aswell as the context
    or reference fields if provided.
    """

    total_tokens: int
    """The total number of tokens used in both the prompt and evaluation."""


class Evaluation(BaseModel):
    evaluations: Dict[str, Evaluations]
    """Evaluations generated by the model.

    This is an object where the key is the metric evaluated (as per the `metrics`
    field in the request) and the value is the evaluation object.

    The evaluation object contains the score (1-5) and critique of the models
    evaluation.

    Example:

    ```
    {
       'recall': {
           'score': 3,
           'critique': 'The model was able to recall some of the information but not all.'
       }
    }
    ```
    """

    model: str
    """The model version that performed the evaluation."""

    usage: Usage
    """Billing and rate-limit usage

    Atla's API is billed based on the number of evaluation tokens used.
    """

    id: Optional[str] = None
    """Unique identifier for the evaluation."""

    created: Optional[int] = None
    """Unix timestamp of when the evaluation was created."""