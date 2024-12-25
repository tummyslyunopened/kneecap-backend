from django.urls import path
from . import views

app_name = 'mirror'

urlpatterns = [
    path('<int:mirror_id>/', views.serve_mirror, name='serve_mirror'),
] 