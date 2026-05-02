# from django.http import HttpResponse

from django.conf.urls.static import static
from django.conf import settings
from django.urls import path

from .modules.backoffice.views.backoffice_view import backoffice_view, backoffice_create_product_view, backoffice_customer_edit_view, backoffice_create_employee_view, backoffice_edit_product_view, backoffice_edit_employee_view, backoffice_create_provider, backoffice_edit_provider, backoffice_add_stock_entry_view
from .modules.account.user.views import signin_view, signout_view, signup_view
from .modules.account.user.views.view_web_preferences import preferences_user_view
from .modules.store.views.category_view import store_category_view
from .views import storefront_electronic_section, storefront_Health_and_Household_section, categories_view
from .modules.store.views.product_view import storefront_product_page,store_front_buy_product

from .modules.store.views.storefront.storefront import home_view

urlpatterns = [
    path("", home_view, name="home"),
    path("backoffice/",backoffice_view, name="backoffice"),
    path("backoffice/createproduct",backoffice_create_product_view, name="backoffice_create_product_view" ),
    path("backoffice/customer/<int:customer_id>/", backoffice_customer_edit_view, name="customer_edit"),
    path("backoffice/createemployee/", backoffice_create_employee_view, name="backoffice_create_employee_view"),
    path("backoffice/product/<int:product_id>/edit/", backoffice_edit_product_view, name="product_edit"),
    path("backoffice/createprovider/", backoffice_create_provider, name="backoffice_createprovider"),
    path("providers/<int:provider_id>/edit/", backoffice_edit_provider, name="edit_provider"),
    path("backoffice/employee/edit/<int:employee_id>/",
     backoffice_edit_employee_view,
     name="employee_edit"),

    path("backoffice/add_stock_entry", backoffice_add_stock_entry_view, name="add_stock_entry"),

    path("electronics/",storefront_electronic_section,name="storefront_electronic_section"),
    path("health_and_household", storefront_Health_and_Household_section, name="storefront_Health_and_Household_section"),
    path("product/<int:product_id>",storefront_product_page, name="product_page"),
    path("buy/<int:product_id>/", store_front_buy_product, name="buy_product"),

    path("categories/",categories_view, name="categories"),
    path("signin/",signin_view,name="signin"),
    path("signup/", signup_view, name="signup"),
    path("signout/", signout_view, name="signout"),
    path("settings/",preferences_user_view, name="settings"),
    path("account/",preferences_user_view, name="account"),
    path("category/<str:name>/",store_category_view),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # add this to the end of ] so it saves to the storage
