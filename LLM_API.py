from typing import Tuple
from openai import OpenAI
import os

CLIENT = OpenAI(
    api_key=os.getenv('OPENAI_KEY')
)


def correct_text(text: str, prev_id: str | None = None) -> Tuple[str, str]:
    response = CLIENT.responses.create(
        model='gpt-4.1-nano',
        instructions="Korrigiere ausschließlich Rechtschreib- und Grammatikfehler im Eingabetext, ohne weitere Änderungen. Gib nur den korrigierten Text zurück.",
        input=text,
        temperature=0.0,
        top_p=1.0,
        previous_response_id=prev_id
    )

    return response.output_text, response.id
