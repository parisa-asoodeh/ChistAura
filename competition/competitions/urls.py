from django.urls import path
from . import views


urlpatterns = [

     path('',views.tournament_list,
          name='tournament_list'),
     path('<int:tournament_id>/',views.tournament_detail,
          name='tournament_detail'),
     path('<int:tournament_id>/leaderboard/',views.tournament_leaderboard,
          name='tournament_leaderboard'),
     path('<int:tournament_id>/register-team/',views.register_team_in_tournament,
          name='register_team_in_tournament'),
]