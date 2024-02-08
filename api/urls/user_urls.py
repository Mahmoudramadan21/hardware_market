from django.urls import path
from api.views import user_views as views

urlpatterns = [
    path('login/', views.MyTokenObtainPairView.as_view(),
            name='token_obtain_pair'),

    path('register/', views.registerUser, name='register'),

    path('profile/', views.getUserProfile, name='user-profile'),
    path('profile/update/', views.updateUserProfile, name='user-profile-update'),

    path('', views.getUsers, name='users'),
    path('<int:pk>/', views.getUserById, name='user'),

    path('update/<int:pk>/', views.updateUser, name='user-update'),
    path('delete/<int:pk>/', views.deleteUser, name='user-delete')

]