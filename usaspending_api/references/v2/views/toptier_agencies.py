from django.db.models import F, Sum
from django.db.models.functions import Coalesce

from usaspending_api.common.helpers.date_helper import now
from usaspending_api.references.models import Agency, GTASSF133Balances
from usaspending_api.common.cache_decorator import cache_response
from usaspending_api.references.v2.views.agency import get_total_budgetary_resources
from usaspending_api.submissions.models import SubmissionAttributes

from rest_framework.response import Response
from rest_framework.views import APIView
from usaspending_api.common.exceptions import InvalidParameterException
from usaspending_api.accounts.models import AppropriationAccountBalances


def get_total_obligations_incurred(fiscal_year, fiscal_period):
    total_obligations_incurred = (
        GTASSF133Balances.objects.filter(fiscal_year=fiscal_year, fiscal_period=fiscal_period)
        .values("fiscal_year")
        .annotate(total_obligations=Sum("obligations_incurred_total_cpe"))
        .values("total_obligations")
    )
    return total_obligations_incurred[0]["total_obligations"] if len(total_obligations_incurred) > 0 else 0.0


class ToptierAgenciesViewSet(APIView):
    """
    This route sends a request to the backend to retrieve all toptier agencies and related, relevant data.
    """

    endpoint_doc = "usaspending_api/api_contracts/contracts/v2/references/toptier_agencies.md"

    @cache_response()
    def get(self, request, format=None):
        sortable_columns = [
            "agency_id",
            "agency_name",
            "active_fy",
            "active_fq",
            "outlay_amount",
            "obligated_amount",
            "budget_authority_amount",
            "current_total_budget_authority_amount",
            "percentage_of_total_budget_authority",
        ]

        sort = request.query_params.get("sort", "agency_name")
        order = request.query_params.get("order", "asc")
        response = {"results": []}

        if sort not in sortable_columns:
            raise InvalidParameterException(
                "The sort value provided is not a valid option. "
                "Please choose from the following: " + str(sortable_columns)
            )

        if order not in ["asc", "desc"]:
            raise InvalidParameterException(
                "The order value provided is not a valid option. Please choose from the following: ['asc', 'desc']"
            )

        # get agency queryset, distinct toptier id to avoid duplicates, take first ordered agency id for consistency
        agency_queryset = Agency.objects.order_by("toptier_agency_id", "id").distinct("toptier_agency_id")
        for agency in agency_queryset:
            toptier_agency = agency.toptier_agency
            # get corresponding submissions through cgac code
            queryset = SubmissionAttributes.objects.all()
            queryset = queryset.filter(
                toptier_code=toptier_agency.toptier_code, submission_window__submission_reveal_date__lte=now()
            )

            # get the most up to date fy and quarter
            queryset = queryset.order_by("-reporting_fiscal_year", "-reporting_fiscal_quarter")
            queryset = queryset.annotate(
                fiscal_year=F("reporting_fiscal_year"), fiscal_quarter=F("reporting_fiscal_quarter")
            )
            submission = queryset.first()
            if submission is None:
                continue
            active_fiscal_year = submission.reporting_fiscal_year
            active_fiscal_quarter = submission.fiscal_quarter
            active_fiscal_period = submission.reporting_fiscal_period

            queryset = AppropriationAccountBalances.objects.filter(submission__is_final_balances_for_fy=True)
            # get the incoming agency's toptier agency, because that's what we'll
            # need to filter on
            # (used filter() instead of get() b/c we likely don't want to raise an
            # error on a bad agency id)
            aggregate_dict = queryset.filter(
                submission__reporting_fiscal_year=active_fiscal_year,
                submission__reporting_fiscal_quarter=active_fiscal_quarter,
                treasury_account_identifier__funding_toptier_agency=toptier_agency,
            ).aggregate(
                budget_authority_amount=Coalesce(Sum("total_budgetary_resources_amount_cpe"), 0),
                obligated_amount=Coalesce(Sum("obligations_incurred_total_by_tas_cpe"), 0),
                outlay_amount=Coalesce(Sum("gross_outlay_amount_by_tas_cpe"), 0),
            )

            abbreviation = ""
            if toptier_agency.abbreviation is not None:
                abbreviation = toptier_agency.abbreviation

            cj = toptier_agency.justification if toptier_agency.justification else None
            # craft response
            total_obligated = get_total_obligations_incurred(active_fiscal_year, active_fiscal_period)
            response["results"].append(
                {
                    "agency_id": agency.id,
                    "toptier_code": toptier_agency.toptier_code,
                    "abbreviation": abbreviation,
                    "agency_name": toptier_agency.name,
                    "congressional_justification_url": cj,
                    "active_fy": str(active_fiscal_year),
                    "active_fq": str(active_fiscal_quarter),
                    "outlay_amount": float(aggregate_dict["outlay_amount"]),
                    "obligated_amount": float(aggregate_dict["obligated_amount"]),
                    "budget_authority_amount": float(aggregate_dict["budget_authority_amount"]),
                    "current_total_budget_authority_amount": float(
                        get_total_budgetary_resources(active_fiscal_year, active_fiscal_period)
                    ),
                    "percentage_of_total_budget_authority": (
                        (float(aggregate_dict["budget_authority_amount"]) / float(total_obligated))
                        if total_obligated > 0
                        else None
                    ),
                }
            )

        response["results"] = sorted(response["results"], key=lambda k: k[sort], reverse=(order == "desc"))

        return Response(response)
