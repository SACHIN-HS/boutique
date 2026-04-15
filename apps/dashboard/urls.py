from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    # Vendor
    path("vendor/add/", views.vendor_add, name="vendor_add"),
    path("vendor/", views.vendor_view, name="vendor_view"),
    path("vendor/delete/<int:pk>/", views.vendor_delete, name="vendor_delete"),
    # Product
    path("product/add/", views.product_add, name="product_add"),
    path("product/", views.product_view, name="product_view"),
    path("product/edit/<int:pk>/", views.product_edit, name="product_edit"),
    path("product/delete/<int:pk>/", views.product_delete, name="product_delete"),
    # Purchase Order
    path("po/", views.po_list, name="po_list"),
    path("po/create/", views.po_create, name="po_create"),
    path("po/receive/<int:pk>/", views.po_receive, name="po_receive"),
    # SKU
    path("sku/", views.sku_center, name="sku_center"),
    path(
        "sku/mark-printed/<int:item_pk>/",
        views.sku_mark_printed,
        name="sku_mark_printed",
    ),
    # Inventory
    path("inventory/", views.inventory, name="inventory"),
    # Orders
    path("orders/", views.order_list, name="order_list"),
    path(
        "orders/send-to-tailor/<int:item_pk>/",
        views.order_send_to_tailor,
        name="order_send_to_tailor",
    ),
    # Tailoring
    path("tailoring/add/", views.tailor_add, name="tailor_add"),
    path("tailoring/", views.tailor_view, name="tailor_view"),
    path(
        "tailoring/job/<int:job_pk>/action/",
        views.tailor_job_action,
        name="tailor_job_action",
    ),
    # Accounting
    path("accounting/pl/", views.accounting_pl, name="accounting_pl"),
    path("accounting/expenses/", views.accounting_expenses, name="accounting_expenses"),
    path(
        "accounting/expenses/delete/<int:pk>/",
        views.expense_delete,
        name="expense_delete",
    ),
    # Legacy
    path("add-product/", views.add_product, name="add_product"),
    path("add-category/", views.add_category, name="add_category"),
]
