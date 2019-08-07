from django.urls import path


from . import views


urlpatterns = [
    path('form/', views.submit_sim_params, name='form'),
    path('sim_process/', views.sim_process, name='sim_process'),
    path('sim_result_view/', views.sim_result_view, name='sim_result_view')
]
