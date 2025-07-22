from shared.data import DB
from sqlalchemy.ext.hybrid import hybrid_property
import json


class UserReflection:

    # Initial Reflection
    reflection_shown = DB.Column(DB.Boolean, default=False)

    current_state = DB.Column(DB.Text)
    basic_goal = DB.Column(DB.Text)
    main_focus = DB.Column(DB.String(128))
    basic_steps = DB.Column(DB.String(128))
    step_thoughts = DB.Column(DB.Text)

    reflection_done = DB.Column(DB.Boolean, default=False)

    @hybrid_property
    def focus(self) -> list[str]:
        return self.main_focus.split('|')

    @hybrid_property
    def steps(self) -> list[str]:
        return self.basic_steps.split('|')

    def initial_reflection(self, state: str, goal: str, focus: list[str], steps: list[str], step_thoughts: str):
        self.current_state = state
        self.basic_goal = goal
        self.main_focus = '|'.join(focus)
        self.basic_steps = '|'.join(steps)
        self.step_thoughts = step_thoughts

        self.reflection_done = True

    # User Journal
    journal_created = DB.Column(DB.Boolean, default=False)
    journal_setup = DB.Column(DB.Text)

    @hybrid_property
    def journal_setup_data(self) -> dict | None:
        try:
            return json.loads(self.journal_setup)
        except ValueError:
            return None

    def set_journal(self, journal_json_str: str):
        self.journal_created = True
        self.journal_setup = journal_json_str
