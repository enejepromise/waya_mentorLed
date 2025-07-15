from django.urls import path
from .views import (
    ConceptListView, ConceptProgressListView, QuizDetailView,
    SubmitQuizView, RewardListView, DashboardView,
    AdminConceptCreateView, AdminQuizCreateView,
    AdminQuestionCreateView, AdminAnswerChoiceCreateView,
    AdminRewardCreateView, WeeklyStreakView,
    ConceptSectionDetailView, ConceptSectionListView,
    CanAccessQuizView  
)

urlpatterns = [
    # Concept & Progress
    path('concepts/', ConceptListView.as_view(), name='concept-list'),
    path('concepts/progress/', ConceptProgressListView.as_view(), name='concept-progress'),

    # Concept Sections
    path('concepts/<uuid:concept_id>/sections/', ConceptSectionListView.as_view(), name='concept-section-list'),
    path('concepts/<uuid:concept_id>/sections/<int:section_order>/', ConceptSectionDetailView.as_view(), name='concept-section-detail'),

    # Quiz
    path('quizzes/<uuid:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/submit/', SubmitQuizView.as_view(), name='submit-quiz'),

    # ✅ Check if user can access quiz
    path('concepts/<uuid:concept_id>/can-access-quiz/', CanAccessQuizView.as_view(), name='can-access-quiz'),

    # Rewards
    path('rewards/', RewardListView.as_view(), name='rewards-earned'),

    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Admin
    path('admin/concepts/', AdminConceptCreateView.as_view(), name='admin-create-concept'),
    path('admin/quizzes/', AdminQuizCreateView.as_view(), name='admin-create-quiz'),
    path('admin/questions/', AdminQuestionCreateView.as_view(), name='admin-create-question'),
    path('admin/answers/', AdminAnswerChoiceCreateView.as_view(), name='admin-create-answer'),
    path('admin/rewards/', AdminRewardCreateView.as_view(), name='admin-create-reward'),

    # Weekly Streak
    path('weekly-streak/', WeeklyStreakView.as_view(), name='weekly-streak'),
]
