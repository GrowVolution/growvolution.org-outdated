from .. import DB
from website.utils import normalize_timestamp
from website.utils.llm_api import correct_text
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta
from calendar import isleap
from num2words import num2words


class UserJourney:
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

    text_correct = DB.Column(DB.Boolean, default=False)

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
    last_updated = DB.Column(DB.DateTime)

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
    def interval_border(self) -> bool:
        if self.last_updated and datetime.now() - self.last_updated <= timedelta(days=3):
            return False

        today = datetime.now().date()
        start = self.journey_started_at.date()
        delta_days = (today - start).days

        def within_days(target):
            return abs(delta_days - target) <= 3

        five_year_halfpoints = [sum([
            366 if isleap(start.year + y) else 365
            for y in range(i)
        ]) // 2 for i in range(1, 6)]

        return any([
            within_days(365 * (self.years_done + 1)),
            any(within_days(d) for d in five_year_halfpoints),
            within_days(90 * (self.quarters_done + 1)),
            within_days(30 * (self.months_done + 1) - 15),
            within_days(30 * (self.months_done + 1))
        ])

    @hybrid_property
    def interval_border_data(self) -> list[str] | None:
        if not self.interval_border:
            return None

        today = datetime.now().date()
        start = self.journey_started_at.date()
        delta_days = (today - start).days

        result = []

        def within_days(target):
            return abs(delta_days - target) <= 3

        if within_days(365 * (self.years_done + 1)):
            result.extend(["goal_10y", "intention"])

        five_year_halfpoints = [sum([
            366 if isleap(start.year + y) else 365
            for y in range(i)
        ]) // 2 for i in range(1, 6)]

        if any(within_days(d) for d in five_year_halfpoints):
            result.append("goal_5y")

        if within_days(90 * (self.quarters_done + 1)):
            result.append("goal_1y")

        if within_days(30 * (self.months_done + 1) - 15):
            result.extend(["goal_quarter", "goal_month"])

        if within_days(30 * (self.months_done + 1)):
            result.extend(["discipline_rating", "focus_rating", "energy_rating"])

        return result or None

    @hybrid_property
    def milestone_reached(self) -> bool:
        return self.progress >= 1

    def start_journey(self, vision: str, intention: str, discipline: int, energy: int, focus: int,
                      goal_5y: str, goal_1y: str, goal_quarter: str, goal_month: str, goal_week: str,
                      text_correct: bool):
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

        self.text_correct = text_correct

        self.journey_started = True
        self.journey_started_at = normalize_timestamp(datetime.now())

        if self.text_correct:
            self.journey_text_correct()

    def journey_text_correct(self):
        self.goal_10y, resp_id = correct_text(self.goal_10y)
        self.intention, resp_id = correct_text(self.intention, resp_id)

        self.goal_5y, resp_id = correct_text(self.goal_5y, resp_id)
        self.goal_1y, resp_id = correct_text(self.goal_1y, resp_id)
        self.goal_quarter, resp_id = correct_text(self.goal_quarter, resp_id)
        self.goal_month, resp_id = correct_text(self.goal_month, resp_id)
        self.goal_week, resp_id = correct_text(self.goal_week, resp_id)

    def new_day_tracked(self):
        now = datetime.now()
        delta = now - self.last_tracked_at if self.last_tracked_at else timedelta(days=0)

        if delta > timedelta(days=1):
            self.current_streak = 1
        else:
            self.current_streak += 1

        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        self.days_tracked += 1
        self.days_tracked_week += 1
        self.last_tracked_at = normalize_timestamp(now)

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
