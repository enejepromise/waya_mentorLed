from rest_framework import serializers
from decimal import Decimal
from django.db import transaction as db_transaction

from .models import (
    Concept, ConceptProgress, Quiz, Question,
    AnswerChoice, QuizResult, Reward, RewardEarned
)

class ConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concept
        fields = ['id', 'title', 'description','level']

    def validate_title(self, value):
        if Concept.objects.filter(title__iexact=value.strip()).exists():
            raise serializers.ValidationError("A concept with this title already exists.")
        return value


class ConceptProgressSerializer(serializers.ModelSerializer):
    concept = ConceptSerializer(read_only=True)

    class Meta:
        model = ConceptProgress
        fields = ['id', 'child', 'concept', 'progress_percentage', 'completed', 'unlocked']
        read_only_fields = ['child']


class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ['id', 'question', 'text', 'is_correct']

    def validate(self, data):
        question = data.get('question')
        text = data.get('text').strip().lower()
        is_correct = data.get('is_correct')

        if AnswerChoice.objects.filter(question=question, text__iexact=text).exists():
            raise serializers.ValidationError("This answer already exists for this question.")

        if is_correct:
            # Ensure only one correct answer per question
            if AnswerChoice.objects.filter(question=question, is_correct=True).exists():
                raise serializers.ValidationError("This question already has a correct answer.")

        return data


class QuestionSerializer(serializers.ModelSerializer):
    choices = AnswerChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'choices']

    def validate(self, data):
        quiz = data.get('quiz')
        text = data.get('text').strip().lower()

        if Question.objects.filter(quiz=quiz, text__iexact=text).exists():
            raise serializers.ValidationError("This question already exists for this quiz.")

        return data


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'questions']


class QuizSubmissionSerializer(serializers.Serializer):
    quiz_id = serializers.UUIDField()
    answers = serializers.DictField(
        child=serializers.UUIDField(),
        help_text="Mapping of question_id to answer_choice_id"
    )

    def validate(self, data):
        quiz_id = data.get('quiz_id')
        answers = data.get('answers')

        # Validate quiz exists
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            raise serializers.ValidationError("Quiz does not exist.")

        # Validate all question_ids belong to quiz
        quiz_question_ids = set(quiz.questions.values_list('id', flat=True))
        submitted_question_ids = set(answers.keys())

        if not submitted_question_ids.issubset(quiz_question_ids):
            raise serializers.ValidationError("One or more questions do not belong to the quiz.")

        # Validate answer choices belong to respective questions
        for question_id, answer_choice_id in answers.items():
            try:
                answer_choice = AnswerChoice.objects.get(id=answer_choice_id)
            except AnswerChoice.DoesNotExist:
                raise serializers.ValidationError(f"Answer choice {answer_choice_id} does not exist.")

            if str(answer_choice.question_id) != question_id:
                raise serializers.ValidationError(f"Answer choice {answer_choice_id} does not belong to question {question_id}.")

        return data


class QuizResultSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)

    class Meta:
        model = QuizResult
        fields = ['id', 'child', 'quiz', 'score', 'passed', 'taken_on']
        read_only_fields = ['child', 'score', 'passed', 'taken_on']


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['id', 'concept', 'name', 'description', 'image', 'points_required']


class RewardEarnedSerializer(serializers.ModelSerializer):
    reward = RewardSerializer(read_only=True)

    class Meta:
        model = RewardEarned
        fields = ['id', 'child', 'reward', 'earned_on']
        read_only_fields = ['child', 'earned_on']
class DashboardSerializer(serializers.Serializer):
    concepts_completed = serializers.IntegerField()
    total_concepts = serializers.IntegerField()
    progress_percentage = serializers.FloatField()
    rewards_earned = serializers.IntegerField()
