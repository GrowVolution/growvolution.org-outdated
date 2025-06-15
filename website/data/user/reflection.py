from .. import DB
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta, time
from num2words import num2words


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


    # User Journey
    journey_started = DB.Column(DB.Boolean, default=False)
    journey_started_at = DB.Column(DB.DateTime)

    goal_10y = DB.Column(DB.Text)
    intention = DB.Column(DB.Text)

    discipline_rating = DB.Column(DB.Integer)
    energy_rating = DB.Column(DB.Integer)
    focus_rating = DB.Column(DB.Integer)

    goal_5y = DB.Column(DB.Text)
    goal_1y = DB.Column(DB.Text)
    goal_quarter = DB.Column(DB.Text)
    goal_month = DB.Column(DB.Text)
    goal_week = DB.Column(DB.Text)

    days_tracked = DB.Column(DB.Integer, default=0)
    days_tracked_week = DB.Column(DB.Integer, default=0)
    days_tracked_month = DB.Column(DB.Integer, default=0)
    days_tracked_quarter = DB.Column(DB.Integer, default=0)
    days_tracked_year = DB.Column(DB.Integer, default=0)
    days_tracked_5y = DB.Column(DB.Integer, default=0)
    last_tracked_at = DB.Column(DB.DateTime)

    weeks_done = DB.Column(DB.Integer, default=0)
    months_done = DB.Column(DB.Integer, default=0)
    quarters_done = DB.Column(DB.Integer, default=0)
    years_done = DB.Column(DB.Integer, default=0)

    current_streak = DB.Column(DB.Integer, default=0)
    longest_streak = DB.Column(DB.Integer, default=0)

    journey_count = DB.Column(DB.Integer, default=1)

    @hybrid_property
    def journey_number(self) -> str:
        return num2words(self.journey_count, lang='de', to='ordinal')

    @hybrid_property
    def days_since_started(self) -> int:
        return (datetime.now().date() - self.journey_started_at.date()).days

    @hybrid_property
    def progress(self) -> float:
        ratio = self.days_since_started / 3652
        return ratio * 100

    @hybrid_property
    def tracked_today(self) -> bool:
        return self.last_tracked_at and datetime.now() - self.last_tracked_at < timedelta(days=1)

    @hybrid_property
    def week_done(self) -> bool:
        days = 7 * (self.weeks_done + 1)
        return datetime.now() - self.journey_started_at >= timedelta(days=days)

    @hybrid_property
    def month_done(self) -> bool:
        days = 30 * (self.months_done + 1)
        exception = self.quarter_done
        return datetime.now() - self.journey_started_at >= timedelta(days=days) and not exception

    @hybrid_property
    def quarter_done(self) -> bool:
        days = 90 * (self.quarters_done + 1)
        exception = (self.quarters_done + 1) % 4 == 0
        return datetime.now() - self.journey_started_at >= timedelta(days=days) and not exception

    @hybrid_property
    def year_done(self) -> bool:
        days = 365 * (self.years_done + 1)
        exception = self.years_done + 1 == 5
        return datetime.now() - self.journey_started_at >= timedelta(days=days) and not exception

    @hybrid_property
    def five_years_done(self) -> bool:
        return datetime.now() - self.journey_started_at >= timedelta(days=1826)

    @hybrid_property
    def tracking_properties(self) -> list[str]:
        btn_when_done = 'success'

        if self.week_done:
            return ["🔥 Woche abschließen", 'trackWeekModal', 'week_modal', btn_when_done]
        if self.month_done:
            return ["🏅 Monat abschließen", 'trackMonthModal', 'month_modal', btn_when_done]
        if self.quarter_done:
            return ["🎯 Quartal abschließen", 'trackQuarterModal', 'quarter_modal', btn_when_done]
        if self.year_done:
            return ["🥇 Jahr abschließen", 'trackYearModal', 'year_modal', btn_when_done]
        if self.five_years_done:
            return ["🏆 Fünf Jahre abschließen", 'track5yModal', 'five_year_modal', btn_when_done]

        return ["✅ Fortschritt festhalten", 'trackModal', 'track_modal', 'secondary']

    @hybrid_property
    def milestone_reached(self) -> bool:
        return self.progress >= 1

    def start_journey(self, vision: str, intention: str, discipline: int, energy: int, focus: int,
                      goal_5y: str, goal_1y: str, goal_quarter: str, goal_month: str, goal_week: str):
        self.goal_10y = vision
        self.intention = intention

        self.discipline_rating = discipline
        self.energy_rating = energy
        self.focus_rating = focus

        self.goal_5y = goal_5y
        self.goal_1y = goal_1y
        self.goal_quarter = goal_quarter
        self.goal_month = goal_month
        self.goal_week = goal_week

        self.journey_started = True
        self.journey_started_at = datetime.combine(datetime.now().date(), time.min)

    def new_day_tracked(self):
        now = datetime.now()
        delta = now - self.last_tracked_at if self.last_tracked_at else timedelta(days=0)

        if delta > timedelta(days=1):
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
            self.current_streak = 1

        self.days_tracked += 1
        self.days_tracked_week += 1
        self.current_streak += 1
        self.last_tracked_at = now

    def update_counters(self):
        if self.week_done:
            self.days_tracked_month += self.days_tracked_week
            self.days_tracked_week = 0
            self.weeks_done += 1

        if self.month_done:
            self.days_tracked_quarter += self.days_tracked_month
            self.days_tracked_month = 0
            self.months_done += 1

        if self.quarter_done:
            self.days_tracked_year += self.days_tracked_quarter
            self.days_tracked_quarter = 0
            self.quarters_done += 1

        if self.year_done:
            self.days_tracked_5y += self.days_tracked_year
            self.days_tracked_year = 0
            self.years_done += 1

        if self.five_years_done:
            self.days_tracked_5y = 0

        if self.milestone_reached:
            self.journey_count += 1

            self.days_tracked = 0
            self.days_tracked_week = 0
            self.days_tracked_month = 0
            self.days_tracked_quarter = 0
            self.days_tracked_year = 0
            self.days_tracked_5y = 0

            self.weeks_done = 0
            self.months_done = 0
            self.quarters_done = 0
            self.years_done = 0

            self.current_streak = 0
            self.longest_streak = 0
