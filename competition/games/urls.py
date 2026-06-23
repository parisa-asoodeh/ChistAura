from django.urls import path
from . import views

urlpatterns = [
    path('create-team/', views.create_team, name='create_team'),
    path('teams/', views.team_list, name='team_list'),
    path('team/<int:team_id>/',views.team_detail,name='team_detail'),
    path('my-team/',views.my_team,name='my_team'),
    path('matches/',views.match_list,name='match_list'),
    path('leaderboard/',views.leaderboard,name='leaderboard'),
    path('team/<int:team_id>/members/',views.manage_team_members,name='manage_team_members'),
    path('matches/<int:match_id>/',views.match_detail,name='match_detail'),
    path('players/',views.player_leaderboard,name='player_leaderboard'),
]
