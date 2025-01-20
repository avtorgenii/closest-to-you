from django.contrib.auth.views import LogoutView
from django.urls import path

from shop.views import users, workers, clients

urlpatterns = [
    path('login/', users.LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),  # after logging out see `settings.py` where user will be redirected after

    # Clients
    path('client_dashboard/',clients.client_dashboard , name='client_dashboard'),

    # Workers
    path('support_dashboard/',workers.support_dashboard , name='support_dashboard'),

    # Complaints
    path('support_dashboard/complaint/<int:c_id>', workers.complaint, name='complaint'),
    path('support_dashboard/decline_complaint/<int:c_id>', workers.decline_complaint, name='decline_complaint'),
    path('support_dashboard/accept_complaint/<int:c_id>', workers.accept_complaint, name='accept_complaint'),


    # Deliveries
    path('delivery/<int:d_id>', workers.delivery, name='delivery'),
]