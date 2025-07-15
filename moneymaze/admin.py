import nested_admin
from django.contrib import admin
from .models import (
    Concept, Quiz, Question, AnswerChoice,
    ConceptProgress, QuizResult,
    Reward, RewardEarned, WeeklyStreak,
    ConceptSection  
)

# Inline for Answer Choices under each Question
class AnswerChoiceInline(nested_admin.NestedTabularInline):
    model = AnswerChoice
    extra = 4


# 🧠 Inline for Questions under a Quiz
class QuestionInline(nested_admin.NestedTabularInline):
    model = Question
    inlines = [AnswerChoiceInline]
    extra = 3


# Inline for Quiz under a Concept
class QuizInline(nested_admin.NestedStackedInline):
    model = Quiz
    inlines = [QuestionInline]
    extra = 1


# Inline for Concept Sections under a Concept
class ConceptSectionInline(nested_admin.NestedTabularInline):
    model = ConceptSection
    extra = 2
    ordering = ['order']


# Full Admin: Concept + Quiz + Questions + AnswerChoices + Sections
@admin.register(Concept)
class ConceptAdmin(nested_admin.NestedModelAdmin):
    inlines = [ConceptSectionInline, QuizInline]  # ✅ Include both Sections and Quizzes
    list_display = ['title', 'level', 'order']
    ordering = ['level', 'order']
    search_fields = ['title', 'description']


# Register Other Models
@admin.register(ConceptProgress)
class ConceptProgressAdmin(admin.ModelAdmin):
    list_display = ['child', 'concept', 'progress_percentage', 'completed', 'unlocked']
    list_filter = ['completed', 'unlocked']


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['child', 'quiz', 'score', 'passed', 'taken_on']


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['name', 'concept', 'points_required']
    search_fields = ['name', 'concept__title']


@admin.register(RewardEarned)
class RewardEarnedAdmin(admin.ModelAdmin):
    list_display = ['child', 'reward', 'earned_on']


@admin.register(WeeklyStreak)
class WeeklyStreakAdmin(admin.ModelAdmin):
    list_display = ['child', 'week_start_date']
