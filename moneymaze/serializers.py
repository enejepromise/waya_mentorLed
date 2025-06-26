from rest_framework import serializers

from .models import (
    Concept, ConceptProgress, Quiz, Question,
    AnswerChoice, QuizResult, Reward, RewardEarned
)

class ConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concept
        fields = ['id', 'title', 'description', 'video_url', 'level']


class ConceptProgressSerializer(serializers.ModelSerializer):
    concept = ConceptSerializer(read_only=True)

    class Meta:
        model = ConceptProgress
        fields = ['id', 'child', 'concept', 'progress_percentage', 'completed', 'unlocked']
        read_only_fields = ['child']
class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ['id', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    choices = AnswerChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True, source='questions')

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'questions']
class QuizSubmissionSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    answers = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="question_id: answer_choice_id"
    )


class QuizResultSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)

    class Meta:
        model = QuizResult
        fields = ['id', 'child', 'quiz', 'score', 'passed', 'taken_on']
        read_only_fields = ['child', 'score', 'passed', 'taken_on']
class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['id', 'name', 'description', 'image', 'points_required']


class RewardEarnedSerializer(serializers.ModelSerializer):
    reward = RewardSerializer(read_only=True)

    class Meta:
        model = RewardEarned
        fields = ['id', 'child', 'reward', 'earned_on']
        read_only_fields = ['child', 'earned_on']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text']

    def validate(self, data):
        quiz = data.get('quiz')
        text = data.get('text').strip().lower()

        if Question.objects.filter(quiz=quiz, text__iexact=text).exists():
            raise serializers.ValidationError("This question already exists for this quiz.")

        return data

class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ['id', 'question', 'text', 'is_correct']

    def validate(self, data):
        question = data.get('question')
        text = data.get('text').strip().lower()

        if AnswerChoice.objects.filter(question=question, text__iexact=text).exists():
            raise serializers.ValidationError("This answer already exists for this question.")

        return data

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
    
class ConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concept
        fields = ['id', 'title', 'description', 'video_url', 'level']

    def validate_title(self, value):
        if Concept.objects.filter(title__iexact=value.strip()).exists():
            raise serializers.ValidationError("A concept with this title already exists.")
        return value


