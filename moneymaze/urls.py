from django.urls import path
from .views import (
    ConceptListView,
    ConceptProgressListView,
    QuizDetailView,
    SubmitQuizView,
    RewardListView,
    DashboardView,
    AdminConceptCreateView,
    AdminQuizCreateView,
    AdminQuestionCreateView,
    AdminAnswerChoiceCreateView,
    AdminRewardCreateView,
)

urlpatterns = [
    # Public / Child-facing endpoints
    path('concepts/', ConceptListView.as_view(), name='concept-list'),
    path('concepts/progress/', ConceptProgressListView.as_view(), name='concept-progress-list'),
    path('quizzes/<uuid:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/submit/', SubmitQuizView.as_view(), name='quiz-submit'),
    path('rewards/', RewardListView.as_view(), name='reward-list'),
    path('dashboard/', DashboardView.as_view(), name='child-dashboard'),

    # Admin endpoints for managing content
    path('admin/concepts/', AdminConceptCreateView.as_view(), name='admin-concept-list-create'),
    path('admin/quizzes/', AdminQuizCreateView.as_view(), name='admin-quiz-create'),
    path('admin/questions/', AdminQuestionCreateView.as_view(), name='admin-question-create'),
    path('admin/answer-choices/', AdminAnswerChoiceCreateView.as_view(), name='admin-answer-choice-create'),
    path('admin/rewards/', AdminRewardCreateView.as_view(), name='admin-reward-list-create'),
]
