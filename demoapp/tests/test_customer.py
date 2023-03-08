import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from demoapp.models import Customer
from typing import Dict

TEST_DATA_1: Dict[str, str] = {
    "email": "testuser@example.com",
    "password": "password",
    "first_name": "John",
    "last_name": "Doe",
    "middle_name": "M",
    "pan_number": "1A2B3C4D5E",
    "full_name": "John M Doe",
}

TEST_DATA_2 = {
    "email": "testuser2@example.com",
    "password": "password",
    "first_name": "John",
    "last_name": "Doe",
    "pan_number": "1A2B3C4D5F",
    "full_name": "John Doe",
}

def create_test_customer(test_data: Dict[str, str]) -> Customer:
    return Customer.objects.create_user(
        email=test_data.get("email"),
        password=test_data.get("password"),
        first_name=test_data.get("first_name"),
        last_name=test_data.get("last_name"),
        middle_name=test_data.get("middle_name"),
        pan_number=test_data.get("pan_number")
    )


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def customer() -> Customer:
    return create_test_customer(TEST_DATA_1)


@pytest.mark.django_db
def test_create_customer(customer: Customer) -> None:
    # Check that the customer was created successfully
    assert customer.first_name == TEST_DATA_1['first_name']
    assert customer.last_name == TEST_DATA_1['last_name']
    assert customer.email == TEST_DATA_1['email']

    # Cleanup
    customer.delete()


@pytest.mark.django_db
def test_create_customer_null_required_fields() -> None:
    """
    Tests whether ValueError is returned in case a required field is
    NOT specified.
    """
    fields = ("email", "password", "first_name", "last_name", "pan_number")
    error_regexes = (
        r"email", r"password", r"first name", r"last name", r"PAN number"
    )

    for field, regex in zip(fields, error_regexes):
        with pytest.raises(ValueError, match=regex):
            test_data = TEST_DATA_1.copy()
            test_data.pop(field)
            create_test_customer(test_data)


@pytest.mark.django_db
def test_create_customer_blank_required_fields() -> None:
    """
    Tests whether ValueError is returned in case a required field is
    specified as empty (blank string).
    """
    fields = ("email", "password", "first_name", "last_name", "pan_number")
    error_regexes = (
        r"email", r"password", r"first name", r"last name", r"PAN number"
    )

    for field, regex in zip(fields, error_regexes):
        with pytest.raises(ValueError, match=regex):
            test_data = TEST_DATA_1.copy()
            test_data[field] = ""
            create_test_customer(test_data)


@pytest.mark.django_db
def test_create_customer_validate_fields() -> None:
    """
    Tests whether ValidationError is returned in case a field validation fails
    """
    fields = ("email",)
    error_regexes = (r"email",)

    for field, regex in zip(fields, error_regexes):
        with pytest.raises(ValidationError, match=regex):
            test_data = TEST_DATA_1.copy()
            test_data[field] = "testuser"
            create_test_customer(test_data)


@pytest.mark.django_db
def test_customer_str() -> None:
    for test_data in (TEST_DATA_1, TEST_DATA_2):
        # Create Customer object
        customer: Customer = create_test_customer(test_data)

        # Check that the __str__ method returns the expected string
        assert str(customer) == test_data['full_name']


@pytest.mark.django_db
def test_api_create_customer(client: APIClient) -> None:
    # Ensure that we can create a new customer without any kind of
    # authentication.
    response = client.post(reverse("customer-list"), data=TEST_DATA_1)
    assert response.status_code == 201
    assert response.data["email"] == "testuser@example.com"
    assert response.data["first_name"] == "John"
    assert response.data["last_name"] == "Doe"
    assert response.data["middle_name"] == "M"
    assert response.data["pan_number"] == "1A2B3C4D5E"


@pytest.mark.django_db
def test_api_create_duplicate_customer(
    client: APIClient,
    customer: Customer
) -> None:
    # Ensure that we can NOT create a duplicate customer
    response = client.post(reverse("customer-list"), data=TEST_DATA_1)
    assert response.status_code == 400
    assert "email" in response.data
    assert "pan_number" in response.data


@pytest.mark.django_db
def test_api_retrieve_customer(client: APIClient, customer: Customer) -> None:
    client.force_authenticate(user=customer)
    response = client.get(reverse("customer-list"))
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["email"] == customer.email
    assert response.data[0]["first_name"] == customer.first_name
    assert response.data[0]["last_name"] == customer.last_name
    assert response.data[0]["pan_number"] == customer.pan_number


@pytest.mark.django_db
def test_api_update_customer(client: APIClient, customer: Customer) -> None:
    client.force_authenticate(user=customer)
    response = client.patch(
        reverse("customer-detail", args=(customer.id,)),        # type: ignore
        data={
            "first_name": "Filthy",
            "last_name": "Frank",
            "pan_number": "GQZPA7298D",
        }
    )
    assert response.status_code == 200
    assert response.data["email"] == customer.email
    assert response.data["first_name"] == "Filthy"
    assert response.data["last_name"] == "Frank"
    assert response.data["pan_number"] == "GQZPA7298D"
