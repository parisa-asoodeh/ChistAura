from django.urls import path
from .views import *

urlpatterns = [
    path('create-team/', create_team, name='create_team'),
    path('teams/', team_list, name='team_list'),
    path('team/<int:team_id>/',team_detail,name='team_detail'),
    path('my-team/',my_team,name='my_team'),
    path('matches/',match_list,name='match_list'),
    path('leaderboard/',leaderboard,name='leaderboard'),
    path('team/<int:team_id>/members/',manage_team_members,name='manage_team_members'),
    path('matches/<int:match_id>/',match_detail,name='match_detail'),
    path('players/',player_leaderboard,name='player_leaderboard'),
    path('sessions/<int:session_id>/play/',game_play,name='game_play'),
]
