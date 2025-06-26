from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Concept, ConceptProgress, Quiz, Question, AnswerChoice,
    QuizResult, Reward, RewardEarned
)

admin.site.register(Concept)
admin.site.register(ConceptProgress)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(AnswerChoice)
admin.site.register(QuizResult)
admin.site.register(Reward)
admin.site.register(RewardEarned)
