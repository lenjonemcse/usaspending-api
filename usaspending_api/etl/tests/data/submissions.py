import pytest

from model_mommy import mommy


@pytest.fixture
def submissions(db):
    mommy.make(
        "submissions.DABSSubmissionWindowSchedule",
        id=2020061,
        submission_fiscal_year=2020,
        submission_fiscal_month=6,
        submission_reveal_date="2020-04-01",
        is_quarter=True,
    )
    mommy.make(
        "submissions.DABSSubmissionWindowSchedule",
        id=2020091,
        submission_fiscal_year=2020,
        submission_fiscal_month=9,
        submission_reveal_date="2020-07-01",
        is_quarter=True,
    )
    mommy.make(
        "submissions.DABSSubmissionWindowSchedule",
        id=2030031,
        submission_fiscal_year=2030,
        submission_fiscal_month=3,
        submission_reveal_date="2030-01-01",
        is_quarter=True,
    )
    mommy.make(
        "submissions.DABSSubmissionWindowSchedule",
        id=2020080,
        submission_fiscal_year=2020,
        submission_fiscal_month=8,
        submission_reveal_date="2020-06-01",
        is_quarter=False,
    )
    mommy.make(
        "submissions.DABSSubmissionWindowSchedule",
        id=2020090,
        submission_fiscal_year=2020,
        submission_fiscal_month=9,
        submission_reveal_date="2020-07-01",
        is_quarter=False,
    )
    mommy.make(
        "submissions.DABSSubmissionWindowSchedule",
        id=2020100,
        submission_fiscal_year=2020,
        submission_fiscal_month=10,
        submission_reveal_date="2020-08-01",
        is_quarter=False,
    )
    mommy.make(
        "submissions.DABSSubmissionWindowSchedule",
        submission_fiscal_year=2030,
        submission_fiscal_month=3,
        id=2030030,
        submission_reveal_date="2030-01-01",
        is_quarter=False,
    )

    mommy.make(
        "submissions.SubmissionAttributes",
        submission_id=20,
        reporting_period_start="2020-08-01",
        is_final_balances_for_fy=False,
        submission_window_id=2020061,
    )
    mommy.make(
        "submissions.SubmissionAttributes",
        submission_id=21,
        reporting_period_start="2020-08-01",
        is_final_balances_for_fy=True,
        submission_window_id=2020091,
    )
    mommy.make(
        "submissions.SubmissionAttributes",
        submission_id=22,
        reporting_period_start="2030-08-01",
        is_final_balances_for_fy=True,
        submission_window_id=2030031,
    )
    mommy.make(
        "submissions.SubmissionAttributes",
        submission_id=9,
        reporting_period_start="2020-06-01",
        is_final_balances_for_fy=False,
        submission_window_id=2020080,
    )
    mommy.make(
        "submissions.SubmissionAttributes",
        submission_id=10,
        reporting_period_start="2020-07-01",
        is_final_balances_for_fy=False,
        submission_window_id=2020090,
    )
    mommy.make(
        "submissions.SubmissionAttributes",
        submission_id=11,
        reporting_period_start="2020-08-01",
        is_final_balances_for_fy=True,
        submission_window_id=2020100,
    )
    mommy.make(
        "submissions.SubmissionAttributes",
        submission_id=12,
        reporting_period_start="2030-02-01",
        is_final_balances_for_fy=True,
        submission_window_id=2030030,
    )
