import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from demoapp.models import Customer, Bank, CustomerBankAccount
from typing import Dict


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def customer() -> Customer:
    return Customer.objects.create(
        email='testuser@example.com',
        password='testpass',
        first_name='John',
        last_name='Doe'
    )


@pytest.fixture
def bank() -> Bank:
    return Bank.objects.create(
        name='Test Bank'
    )


@pytest.fixture
def account(customer: Customer, bank: Bank) -> CustomerBankAccount:
    return CustomerBankAccount.objects.create(
        customer=customer,
        bank=bank,
        account_number='1234567890',
        ifsc_code='ABCD1234567',
        is_active=True
    )


@pytest.mark.django_db
def test_create_account(
    client: APIClient,
    customer: Customer,
    bank: Bank
) -> None:
    # Ensure we can create a new account
    client.force_authenticate(user=customer)
    data: Dict[str, str] = {
        "bank": str(bank.id),                           # type: ignore
        "account_number": "9876543210",
        "ifsc_code": "WXYZ7654321",
        "branch_name": "Test Branch",
        "name_as_per_bank_record": "test",
    }
    response = client.post(reverse("active-bank-list"), data)
    assert response.status_code == 201
    assert response.data["bank"] == bank.id             # type: ignore
    assert response.data["account_number"] == "9876543210"
    assert response.data["ifsc_code"] == "WXYZ7654321"
    assert response.data["is_active"] is True


@pytest.mark.django_db
def test_create_duplicate_active_account(
    client: APIClient,
    customer: Customer,
    bank: Bank,
    account: CustomerBankAccount
) -> None:
    # Ensure we can't create a duplicate account
    client.force_authenticate(user=customer)
    data: Dict[str, str] = {
        "bank": str(bank.id),                           # type: ignore
        "account_number": account.account_number,
        "ifsc_code": account.ifsc_code,
        "branch_name": "Test Branch",
        "name_as_per_bank_record": "test",
    }
    response = client.post(reverse("active-bank-list"), data)
    assert response.status_code == 400
    assert "non_field_errors" in response.data


@pytest.mark.django_db
def test_retrieve_active_account(
    client: APIClient,
    customer: Customer,
    account: CustomerBankAccount
) -> None:
    # Ensure we can retrieve the active account
    client.force_authenticate(user=customer)
    response = client.get(reverse("active-bank-list"))
    assert response.status_code == 200
    assert response.data["bank"] == account.bank.id
    assert response.data["account_number"] == account.account_number
    assert response.data["ifsc_code"] == account.ifsc_code
    assert response.data["is_active"] is True


@pytest.mark.django_db
def test_update_account(
    client: APIClient,
    customer: Customer,
    account: CustomerBankAccount
) -> None:
    # Ensure we can update the active account
    client.force_authenticate(user=customer)
    data: Dict[str, str] = {
        "bank": str(account.bank.id),
        "name_as_per_bank_record": "test2",
    }
    response = client.patch(reverse("active-bank-list"), data)
    assert response.status_code == 200
    assert response.data["bank"] == account.bank.id
    assert response.data["account_number"] == account.account_number
    assert response.data["ifsc_code"] == account.ifsc_code
    assert response.data["is_active"] == account.is_active
    assert response.data["name_as_per_bank_record"] == "test2"
