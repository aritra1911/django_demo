from rest_framework import permissions

class IsCustomerAuthenticated(permissions.BasePermission):
    """
    Custom permission to allow authenticated customers to perform CRUD
    operations on Customer and also allow unauthenticated customers to
    create a Customer.
    """

    def has_permission(self, request, view) -> bool:
        # Anyone can create a customer, but one needs to be
        # authenticated in order to list it.
        return request.method == 'POST' or (
            request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj) -> bool:
        # Allow only authenticated customers to retrieve and update
        # their information.
        return request.user and request.user.is_authenticated