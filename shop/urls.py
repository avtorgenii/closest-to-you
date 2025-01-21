from django.contrib.auth.views import LogoutView
from django.urls import path

from shop.views import users, workers, clients

urlpatterns = [
    # USERS
    path('', users.home, name='home'),
    path('login/', users.LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'), # after logging out see `settings.py` where user will be redirected after

    # CLIENTS
    path('client_dashboard/', clients.client_dashboard, name='client_dashboard'),

    # WORKERS
    path('support_dashboard/', workers.support_dashboard, name='support_dashboard'),

    # Complaints
    path('support_dashboard/complaint/<int:c_id>/', workers.complaint, name='complaint'),
    path('support_dashboard/decline_complaint/<int:c_id>/', workers.decline_complaint, name='decline_complaint'),
    path('support_dashboard/accept_complaint/<int:c_id>/', workers.accept_complaint, name='accept_complaint'),

    # Deliveries
    path('delivery/<int:d_id>/', workers.delivery, name='delivery'),
    path('confirm_incident/<int:d_id>/', workers.confirm_incident, name='confirm_incident'),
    path('delivery/courier_compensation/<int:c_id>/', workers.courier_compensation, name='courier_compensation'),
    path('delivery/client_compensation/<int:c_id>/', workers.client_compensation, name='client_compensation'),
    path('delivery/confirm_order_and_delivery/<int:d_id>/', workers.confirm_order_and_delivery, name='confirm_order_and_delivery')
]
