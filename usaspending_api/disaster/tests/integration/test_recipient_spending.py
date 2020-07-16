import pytest
from rest_framework import status

from usaspending_api.search.tests.data.utilities import setup_elasticsearch_test

url = "/api/v2/disaster/recipient/spending/"


@pytest.mark.django_db
def test_correct_response_defc_no_results(
    client, monkeypatch, helpers, elasticsearch_award_index, awards_and_transactions
):
    setup_elasticsearch_test(monkeypatch, elasticsearch_award_index)

    resp = helpers.post_for_spending_endpoint(client, url, def_codes=["N"])
    expected_results = []
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["results"] == expected_results


@pytest.mark.django_db
def test_correct_response_single_defc(client, monkeypatch, helpers, elasticsearch_award_index, awards_and_transactions):
    setup_elasticsearch_test(monkeypatch, elasticsearch_award_index)

    resp = helpers.post_for_spending_endpoint(client, url, def_codes=["L"])
    expected_results = [
        {
            "code": "987654321",
            "count": 2,
            "description": "RECIPIENT 3",
            "id": ["d2894d22-67fc-f9cb-4005-33fa6a29ef86-C", "d2894d22-67fc-f9cb-4005-33fa6a29ef86-R"],
            "obligation": 2200.0,
            "outlay": 1100.0,
        },
        {
            "code": "456789123",
            "count": 1,
            "description": "RECIPIENT 2",
            "id": ["3c92491a-f2cd-ec7d-294b-7daf91511866-R"],
            "obligation": 20.0,
            "outlay": 0.0,
        },
        {
            "code": "DUNS Number not provided",
            "count": 1,
            "description": "RECIPIENT 1",
            "id": ["5f572ec9-8b49-e5eb-22c7-f6ef316f7689-R"],
            "obligation": 2.0,
            "outlay": 0.0,
        },
    ]
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["results"] == expected_results


@pytest.mark.django_db
def test_correct_response_multiple_defc(
    client, monkeypatch, helpers, elasticsearch_award_index, awards_and_transactions
):
    setup_elasticsearch_test(monkeypatch, elasticsearch_award_index)

    resp = helpers.post_for_spending_endpoint(client, url, def_codes=["L", "M"])
    expected_results = [
        {
            "code": "987654321",
            "count": 3,
            "description": "RECIPIENT 3",
            "id": ["d2894d22-67fc-f9cb-4005-33fa6a29ef86-C", "d2894d22-67fc-f9cb-4005-33fa6a29ef86-R"],
            "obligation": 202200.0,
            "outlay": 1100.0,
        },
        {
            "code": "456789123",
            "count": 1,
            "description": "RECIPIENT 2",
            "id": ["3c92491a-f2cd-ec7d-294b-7daf91511866-R"],
            "obligation": 20.0,
            "outlay": 0.0,
        },
        {
            "code": "DUNS Number not provided",
            "count": 1,
            "description": "RECIPIENT 1",
            "id": ["5f572ec9-8b49-e5eb-22c7-f6ef316f7689-R"],
            "obligation": 2.0,
            "outlay": 0.0,
        },
        {
            "code": "096354360",
            "count": 1,
            "description": "MULTIPLE RECIPIENTS",
            "id": None,
            "obligation": 20000.0,
            "outlay": 0.0,
        },
        {
            "code": "DUNS Number not provided",
            "count": 1,
            "description": "MULTIPLE RECIPIENTS",
            "id": None,
            "obligation": 2000000.0,
            "outlay": 0.0,
        },
    ]
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["results"] == expected_results


@pytest.mark.django_db
def test_correct_response_with_query(client, monkeypatch, helpers, elasticsearch_award_index, awards_and_transactions):
    setup_elasticsearch_test(monkeypatch, elasticsearch_award_index)

    resp = helpers.post_for_spending_endpoint(client, url, def_codes=["L", "M"], query="GIBBERISH")
    expected_results = []
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["results"] == expected_results

    resp = helpers.post_for_spending_endpoint(client, url, def_codes=["L", "M"], query="3")
    expected_results = [
        {
            "code": "987654321",
            "count": 3,
            "description": "RECIPIENT 3",
            "id": ["d2894d22-67fc-f9cb-4005-33fa6a29ef86-C", "d2894d22-67fc-f9cb-4005-33fa6a29ef86-R"],
            "obligation": 202200.0,
            "outlay": 1100.0,
        }
    ]
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["results"] == expected_results


@pytest.mark.django_db
def test_correct_response_with_award_type_codes(
    client, monkeypatch, helpers, elasticsearch_award_index, awards_and_transactions
):
    setup_elasticsearch_test(monkeypatch, elasticsearch_award_index)

    resp = helpers.post_for_spending_endpoint(client, url, def_codes=["L", "M"], award_type_codes=["IDV_A"])
    expected_results = []
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["results"] == expected_results

    resp = helpers.post_for_spending_endpoint(client, url, def_codes=["L", "M"], award_type_codes=["07", "A", "B"])
    expected_results = [
        {
            "code": "987654321",
            "count": 1,
            "description": "RECIPIENT 3",
            "id": ["d2894d22-67fc-f9cb-4005-33fa6a29ef86-C", "d2894d22-67fc-f9cb-4005-33fa6a29ef86-R"],
            "obligation": 2000.0,
            "outlay": 1000.0,
        },
        {
            "code": "456789123",
            "count": 1,
            "description": "RECIPIENT 2",
            "id": ["3c92491a-f2cd-ec7d-294b-7daf91511866-R"],
            "obligation": 20.0,
            "outlay": 0.0,
        },
        {
            "code": "DUNS Number not provided",
            "count": 1,
            "description": "RECIPIENT 1",
            "id": ["5f572ec9-8b49-e5eb-22c7-f6ef316f7689-R"],
            "obligation": 2.0,
            "outlay": 0.0,
        },
        {
            "code": "096354360",
            "count": 1,
            "description": "MULTIPLE RECIPIENTS",
            "id": None,
            "obligation": 20000.0,
            "outlay": 0.0,
        },
    ]
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["results"] == expected_results


@pytest.mark.django_db
def test_invalid_defc(client, monkeypatch, helpers, elasticsearch_award_index, awards_and_transactions):
    setup_elasticsearch_test(monkeypatch, elasticsearch_award_index)

    resp = helpers.post_for_spending_endpoint(client, url, def_codes=["ZZ"])
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data["detail"] == "Field 'filter|def_codes' is outside valid values ['L', 'M', 'N']"


@pytest.mark.django_db
def test_invalid_defc_type(client, monkeypatch, helpers, elasticsearch_award_index, awards_and_transactions):
    setup_elasticsearch_test(monkeypatch, elasticsearch_award_index)

    resp = helpers.post_for_spending_endpoint(client, url, def_codes="100")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data["detail"] == "Invalid value in 'filter|def_codes'. '100' is not a valid type (array)"


@pytest.mark.django_db
def test_missing_defc(client, monkeypatch, helpers, elasticsearch_award_index, awards_and_transactions):
    setup_elasticsearch_test(monkeypatch, elasticsearch_award_index)

    resp = helpers.post_for_spending_endpoint(client, url)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert resp.data["detail"] == "Missing value: 'filter|def_codes' is a required field"


@pytest.mark.django_db
def test_pagination_page_and_limit(client, monkeypatch, helpers, elasticsearch_award_index, awards_and_transactions):
    setup_elasticsearch_test(monkeypatch, elasticsearch_award_index)

    resp = helpers.post_for_spending_endpoint(client, url, def_codes=["L", "M"], page=2, limit=1)
    expected_results = {
        "results": [
            {
                "code": "456789123",
                "count": 1,
                "description": "RECIPIENT 2",
                "id": ["3c92491a-f2cd-ec7d-294b-7daf91511866-R"],
                "obligation": 20.0,
                "outlay": 0.0,
            }
        ],
        "page_metadata": {
            "page": 2,
            "total": 5,
            "limit": 1,
            "next": 3,
            "previous": 1,
            "hasNext": True,
            "hasPrevious": True,
        },
        "message": "Notice! API Request to sort on 'id' field isn't fully "
        "implemented. Results were actually sorted using 'description' "
        "field.",
    }

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == expected_results
