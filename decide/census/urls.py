from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
<<<<<<< HEAD
    path('role/<int:voting_id>/', views.CensusRole.as_view(), name='census_role'),
=======
>>>>>>> central/integracion-votaciones
]
