from django.urls import path
from . import views

urlpatterns = [
    # Concepts
    path('concepts/', views.ConceptListView.as_view(), name='concept-list'),

    # Concept Progress for current user (no param)
    path('concept-progress/', views.ConceptProgressListView.as_view(), name='concept-progress-list'),

    # Quiz detail by quiz UUID
    path('quizzes/<uuid:pk>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/', views.QuizListView.as_view(), name='quiz-list'),


    # Submit quiz answers (POST)
    path('quizzes/submit/', views.SubmitQuizView.as_view(), name='submit-quiz'),

    # Reward list for current user (no param)
    path('rewards/', views.RewardListView.as_view(), name='reward-list'),

    # Dashboard - summary stats for current user
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Weekly streak for current user
    path('weekly-streak/', views.WeeklyStreakView.as_view(), name='weekly-streak'),

    # List sections for a Concept by concept_id (UUID)
    path('concepts/<uuid:concept_id>/sections/', views.ConceptSectionListView.as_view(), name='concept-section-list'),

    # Detail of a ConceptSection by section UUID
    path('sections/<uuid:pk>/', views.ConceptSectionDetailView.as_view(), name='concept-section-detail'),

    # Check if user can access quiz for concept (concept_id UUID)
    path('concepts/<uuid:concept_id>/can-access-quiz/', views.CanAccessQuizView.as_view(), name='can-access-quiz'),

    # Admin Views
    path('admin/concepts/', views.AdminConceptCreateView.as_view(), name='admin-concept-list-create'),

    path('admin/quizzes/', views.AdminQuizCreateView.as_view(), name='admin-quiz-create'),

    path('admin/questions/', views.AdminQuestionCreateView.as_view(), name='admin-question-create'),

    path('admin/answer-choices/', views.AdminAnswerChoiceCreateView.as_view(), name='admin-answer-choice-create'),

    path('admin/rewards/', views.AdminRewardCreateView.as_view(), name='admin-reward-list-create'),
]
