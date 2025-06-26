from django.urls import path
from .views import (
    ConceptListView, ConceptProgressListView, QuizDetailView, SubmitQuizView,
    RewardListView, DashboardView, AdminConceptCreateView, AdminQuizCreateView,
    AdminAnswerChoiceCreateView, AdminRewardCreateView, AdminQuestionCreateView,         
    AdminAnswerChoiceCreateView,     
    AdminRewardCreateView   
)

urlpatterns = [
    path('concepts/', ConceptListView.as_view(), name='concept-list'),
    path('concepts/progress/', ConceptProgressListView.as_view(), name='concept-progress'),
    path('quiz/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quiz/submit/', SubmitQuizView.as_view(), name='quiz-submit'),
    path('rewards/', RewardListView.as_view(), name='reward-list'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('admin/concepts/', AdminConceptCreateView.as_view(), name='admin-concept-create'),
    path('admin/quizzes/', AdminQuizCreateView.as_view(), name='admin-quiz-create'),
    path('admin/questions/', AdminQuestionCreateView.as_view(), name='admin-question-create'),
    path('admin/choices/', AdminAnswerChoiceCreateView.as_view(), name='admin-choice-create'),
    path('admin/rewards/', AdminRewardCreateView.as_view(), name='admin-reward-create'),

]

from .views import (
    # ...existing views
    AdminQuizCreateView, AdminQuestionCreateView,
    AdminAnswerChoiceCreateView, AdminRewardCreateView
)

urlpatterns += [
    path('admin/quizzes/', AdminQuizCreateView.as_view(), name='admin-quiz-create'),
    path('admin/questions/', AdminQuestionCreateView.as_view(), name='admin-question-create'),
    path('admin/choices/', AdminAnswerChoiceCreateView.as_view(), name='admin-choice-create'),
    path('admin/rewards/', AdminRewardCreateView.as_view(), name='admin-reward-create'),
]