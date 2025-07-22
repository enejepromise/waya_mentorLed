# import nested_admin
# from django.contrib import admin
# from .models import (
#     Concept, ConceptSection, ConceptDescription,
#     Quiz, Question, AnswerChoice,
#     ConceptProgress, QuizResult,
#     Reward, RewardEarned, WeeklyStreak,
# )

# # Inline for Answer Choices under each Question
# class AnswerChoiceInline(nested_admin.NestedTabularInline):
#     model = AnswerChoice
#     extra = 4

# # Inline for Questions under a Quiz
# class QuestionInline(nested_admin.NestedTabularInline):
#     model = Question
#     inlines = [AnswerChoiceInline]
#     extra = 3

# # Inline for Quiz under a Concept
# class QuizInline(nested_admin.NestedStackedInline):
#     model = Quiz
#     inlines = [QuestionInline]
#     extra = 1

# # Inline for ConceptDescriptions under ConceptSection
# class ConceptDescriptionInline(nested_admin.NestedTabularInline):
#     model = ConceptDescription
#     extra = 3
#     ordering = ['order']
#     fields = ('text', 'order')

# # Inline for ConceptSections under Concept
# class ConceptSectionInline(nested_admin.NestedTabularInline):
#     model = ConceptSection
#     extra = 2
#     ordering = ['order']
#     fields = ('title', 'order')
#     inlines = [ConceptDescriptionInline]  # Nested inline for descriptions

# @admin.register(Concept)
# class ConceptAdmin(nested_admin.NestedModelAdmin):
#     inlines = [
#         ConceptSectionInline,
#         QuizInline,
#     ]
#     list_display = ['title', 'level']
#     ordering = ['level', 'title']
#     search_fields = ['title']

# @admin.register(ConceptProgress)
# class ConceptProgressAdmin(admin.ModelAdmin):
#     list_display = ['child', 'concept', 'progress_percentage', 'completed', 'unlocked']
#     list_filter = ['completed', 'unlocked']
#     search_fields = ['child__username', 'concept__title']

# @admin.register(QuizResult)
# class QuizResultAdmin(admin.ModelAdmin):
#     list_display = ['child', 'quiz', 'score', 'passed', 'taken_on']
#     list_filter = ['passed']
#     search_fields = ['child__username', 'quiz__concept__title']
#     date_hierarchy = 'taken_on'

# @admin.register(Reward)
# class RewardAdmin(admin.ModelAdmin):
#     list_display = ['name', 'concept', 'points_required']
#     search_fields = ['name', 'concept__title']

# @admin.register(RewardEarned)
# class RewardEarnedAdmin(admin.ModelAdmin):
#     list_display = ['child', 'reward', 'earned_on']
#     search_fields = ['child__username', 'reward__name']
#     date_hierarchy = 'earned_on'

# @admin.register(WeeklyStreak)
# class WeeklyStreakAdmin(admin.ModelAdmin):
#     list_display = ['child', 'week_start_date']
#     list_filter = ['week_start_date']
#     search_fields = ['child__username']



# import nested_admin
# from django.contrib import admin
# from .models import (
#     Concept, ConceptSection, ConceptDescription,
#     Quiz, Question, AnswerChoice, QuizResult,
#     ConceptProgress, SectionProgress,
#     Reward, RewardEarned,
#     WeeklyStreak
# )

# # Inline for AnswerChoices under a Question
# class AnswerChoiceInline(nested_admin.NestedTabularInline):
#     model = AnswerChoice
#     extra = 4
#     fields = ('text', 'is_correct')

# # Inline for Questions under a Quiz
# class QuestionInline(nested_admin.NestedTabularInline):
#     model = Question
#     inlines = [AnswerChoiceInline]
#     extra = 3
#     fields = ('text',)

# # Inline for Quiz under a Concept
# class QuizInline(nested_admin.NestedStackedInline):
#     model = Quiz
#     inlines = [QuestionInline]
#     extra = 1
#     fields = ('title',)

# # Inline for ConceptDescription under ConceptSection
# class ConceptDescriptionInline(nested_admin.NestedTabularInline):
#     model = ConceptDescription
#     extra = 3
#     ordering = ['order']
#     fields = ('text', 'order')

# # Inline for ConceptSection under Concept, nesting ConceptDescriptions inside
# class ConceptSectionInline(nested_admin.NestedTabularInline):
#     model = ConceptSection
#     extra = 2
#     ordering = ['order']
#     fields = ('title', 'order')
#     inlines = [ConceptDescriptionInline]

# # Register Concept with nested inlines: Sections + Descriptions + Quiz + Questions + AnswerChoices
# @admin.register(Concept)
# class ConceptAdmin(nested_admin.NestedModelAdmin):
#     inlines = [
#         ConceptSectionInline,
#         QuizInline,
#     ]
#     list_display = ['title', 'level']
#     ordering = ['level', 'title']
#     search_fields = ['title']

# @admin.register(ConceptProgress)
# class ConceptProgressAdmin(admin.ModelAdmin):
#     list_display = ['child', 'concept', 'progress_percentage', 'completed', 'unlocked']
#     list_filter = ['completed', 'unlocked']
#     search_fields = ['child__username', 'concept__title']

# @admin.register(SectionProgress)
# class SectionProgressAdmin(admin.ModelAdmin):
#     list_display = ['child', 'section', 'viewed', 'viewed_on']
#     list_filter = ['viewed']
#     search_fields = ['child__username', 'section__title']

# @admin.register(QuizResult)
# class QuizResultAdmin(admin.ModelAdmin):
#     list_display = ['child', 'quiz', 'score', 'passed', 'taken_on']
#     list_filter = ['passed']
#     search_fields = ['child__username', 'quiz__concept__title']
#     date_hierarchy = 'taken_on'

# @admin.register(Reward)
# class RewardAdmin(admin.ModelAdmin):
#     list_display = ['name', 'concept', 'points_required']
#     search_fields = ['name', 'concept__title']

# @admin.register(RewardEarned)
# class RewardEarnedAdmin(admin.ModelAdmin):
#     list_display = ['child', 'reward', 'earned_on']
#     search_fields = ['child__username', 'reward__name']
#     date_hierarchy = 'earned_on'

# @admin.register(WeeklyStreak)
# class WeeklyStreakAdmin(admin.ModelAdmin):
#     list_display = ['child', 'week_start_date']
#     list_filter = ['week_start_date']
#     search_fields = ['child__username']
import nested_admin
from django.contrib import admin
from .models import (
    Concept, ConceptSection, ConceptDescription,
    Quiz, Question, AnswerChoice,
    ConceptProgress, QuizResult,
    Reward, RewardEarned, WeeklyStreak,
)

# Inline for Answer Choices under each Question
class AnswerChoiceInline(nested_admin.NestedTabularInline):
    model = AnswerChoice
    extra = 4

# Inline for Questions under a Quiz
class QuestionInline(nested_admin.NestedTabularInline):
    model = Question
    inlines = [AnswerChoiceInline]
    extra = 3

# Inline for Quiz under a Concept
class QuizInline(nested_admin.NestedStackedInline):
    model = Quiz
    inlines = [QuestionInline]
    extra = 1

# ✅ Inline for ConceptDescriptions under ConceptSection
class ConceptDescriptionInline(nested_admin.NestedTabularInline):
    model = ConceptDescription
    extra = 2
    fields = ('text',)

# ✅ Inline for ConceptSections under Concept
class ConceptSectionInline(nested_admin.NestedStackedInline):
    model = ConceptSection
    extra = 1
    fields = ('title', 'order')
    inlines = [ConceptDescriptionInline]

# ✅ Admin for Concept with sections and quizzes
@admin.register(Concept)
class ConceptAdmin(nested_admin.NestedModelAdmin):
    inlines = [ConceptSectionInline, QuizInline]
    list_display = ['title', 'level']
    ordering = ['level', 'title']
    search_fields = ['title']

# Other admin models (unchanged)
@admin.register(ConceptProgress)
class ConceptProgressAdmin(admin.ModelAdmin):
    list_display = ['child', 'concept', 'progress_percentage', 'completed', 'unlocked']
    list_filter = ['completed', 'unlocked']
    search_fields = ['child__username', 'concept__title']

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['child', 'quiz', 'score', 'passed', 'taken_on']
    list_filter = ['passed']
    search_fields = ['child__username', 'quiz__concept__title']
    date_hierarchy = 'taken_on'

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['name', 'concept', 'points_required']
    search_fields = ['name', 'concept__title']

@admin.register(RewardEarned)
class RewardEarnedAdmin(admin.ModelAdmin):
    list_display = ['child', 'reward', 'earned_on']
    search_fields = ['child__username', 'reward__name']
    date_hierarchy = 'earned_on'

@admin.register(WeeklyStreak)
class WeeklyStreakAdmin(admin.ModelAdmin):
    list_display = ['child', 'week_start_date']
    list_filter = ['week_start_date']
    search_fields = ['child__username']

