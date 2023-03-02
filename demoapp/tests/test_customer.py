import pytest
from django.core.exceptions import ValidationError
from demoapp.models import Customer
from typing import Dict

TEST_DATA_1 = {
    'email': 'testuser@example.com',
    'password': 'password',
    'first_name': 'John',
    'last_name': 'Doe',
    'middle_name': 'M',
    'pan_number': '1A2B3C4D5E',
    'full_name': 'John M Doe',
}

TEST_DATA_2 = {
    'email': 'testuser2@example.com',
    'password': 'password',
    'first_name': 'John',
    'last_name': 'Doe',
    'pan_number': '1A2B3C4D5F',
    'full_name': 'John Doe',
}

def create_test_customer(test_data: Dict[str, str]) -> Customer:
    return Customer.objects.create_user(
        email=test_data.get('email'),
        password=test_data.get('password'),
        first_name=test_data.get('first_name'),
        last_name=test_data.get('last_name'),
        middle_name=test_data.get('middle_name'),
        pan_number=test_data.get('pan_number')
    )

@pytest.mark.django_db
def test_create_customer() -> None:
    test_data: Dict[str, str] = TEST_DATA_1
    customer: Customer = create_test_customer(test_data)

    # Check that the customer was created successfully
    assert customer.first_name == test_data['first_name']
    assert customer.last_name == test_data['last_name']
    assert customer.email == test_data['email']

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
