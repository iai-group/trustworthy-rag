"""Class for detecting information nuggets in passage given a query."""

import re
from abc import ABC, abstractmethod
from typing import Dict

from openai import OpenAI

from response_generation.config import DEFAULT_GPT_VERSION, OPENAI_API_KEY
from response_generation.utilities.generation import num_tokens_from_messages

_DEFAULT_PROMPT = [
    {
        "role": "system",
        "content": (
            "Generate two lists of aspects, points of view or facets "
            "that are related to the topic of the provided passage. The first list "
            "should contain 2-5 items that are covered in the passage. The second "
            "list should contain 2-5 items that are not covered in the passage."
        ),
    },
]


class AspectsDetector(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def detect_aspects(self, passage: str,) -> Dict[str, int]:
        """Lists aspects covered and not covered in a passage.

        Args:
            passage: Passage to detect aspects in.

        Returns:
            List of aspects/points of view/facets covered and not covered in the
            passage.
        """
        raise NotImplementedError


class GTPAspectsDetector(AspectsDetector):
    def __init__(
        self,
        api_key: str = OPENAI_API_KEY,
        gpt_version: str = DEFAULT_GPT_VERSION,
    ) -> None:
        """Instantiates an aspect detector using OpenAI GPT model.

        Args:
            api_key: OpenAI API key.
            gpt_version (optional): OpenAI GPT model version. Defaults to
              file-level constant DEFAULT_GPT_VERSION.
        """  # noqa
        self._openai_client = OpenAI(api_key=api_key)
        self._gpt_version = gpt_version

    def detect_aspects(
        self, passage: str, prompt: str = _DEFAULT_PROMPT,
    ) -> Dict[str, int]:
        """Lists aspects covered and not covered in a passage.

        Args:
            passage: Passage to detect aspects in.
            prompt (optional): Prompt to use for the OpenAI GPT model.
              Defaults to file-level constant _DEFAULT_PROMPT.
            
        Returns:
            List of aspects/points of view/facets covered and not covered in the
            passage.
        """
        input_sample = {
            "role": "user",
            "content": "Passage: {}".format(passage),
        }
        if (
            num_tokens_from_messages(
                prompt + [input_sample], model=self._gpt_version
            )
            > 4095
        ):
            return "-1"
        else:
            response = self._openai_client.chat.completions.create(
                model=self._gpt_version, messages=prompt + [input_sample],
            )
            system_response = response.choices[0].message.content

            response_list = system_response.split("\n")
            covered = 1
            aspects = {}

            for item in response_list:
                if "not covered in the passage" in item.lower():
                    covered = 0
                if len(re.findall("[1-9]\.", item)) > 0:
                    aspects[re.sub("[1-9]\. ", "", item)] = covered

            return aspects


if __name__ == "__main__":
    # Example usage
    aspects_detector = GTPAspectsDetector(api_key=OPENAI_API_KEY)

    passage = """The process involves helping individuals identify their 
    negative self-talk stemmed from past experiences, reframing mistakes 
    into learning opportunities, pinpointing trigger thoughts that cause 
    low self-esteem, and building positive thought patterns and perspectives. 
    Encourage your teen to convert negative self-talk into positive 
    affirmations, altering detrimental early childhood messages, fostering 
    self-empathy, and enhancing their self-understanding and self-esteem. 
    Spending quality time with your teenager fosters their self-esteem, 
    treating them with the respect they deserve as near-adults strengthens 
    your relationship, and avoiding criticism protects their self-confidence, 
    hence any disagreements should be addressed through open discussions."""

    information_nuggets = aspects_detector.detect_aspects(passage)

    for k, i in information_nuggets.items():
        print(k, i)