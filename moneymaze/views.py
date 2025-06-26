from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Concept, ConceptProgress, Quiz, QuizResult, Reward, RewardEarned, Question, AnswerChoice
from .serializers import (
    ConceptSerializer, ConceptProgressSerializer, QuizSerializer,
    QuizSubmissionSerializer, QuizResultSerializer, RewardEarnedSerializer,
    RewardSerializer,  QuestionSerializer, AnswerChoiceSerializer
)

from children.models import Child


class ConceptListView(generics.ListAPIView):
    queryset = Concept.objects.all()
    serializer_class = ConceptSerializer
    permission_classes = [IsAuthenticated]


class ConceptProgressListView(generics.ListAPIView):
    serializer_class = ConceptProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ConceptProgress.objects.filter(child=self.request.user)


class QuizDetailView(generics.RetrieveAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]


class SubmitQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuizSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            quiz_id = serializer.validated_data['quiz_id']
            answers = serializer.validated_data['answers']
            quiz = Quiz.objects.get(id=quiz_id)
            correct = 0
            total = quiz.questions.count()

            for q in quiz.questions.all():
                selected_choice_id = answers.get(str(q.id))
                try:
                    selected_choice = AnswerChoice.objects.get(id=selected_choice_id)
                    if selected_choice.is_correct:
                        correct += 1
                except AnswerChoice.DoesNotExist:
                    pass

            score = (correct / total) * 100
            passed = score >= 70

            result, created = QuizResult.objects.get_or_create(
                child=request.user,
                quiz=quiz,
                defaults={'score': score, 'passed': passed}
            )

            if not created:
                return Response({'message': 'Quiz already submitted.'}, status=400)

            # Mark concept as completed if passed
            concept_progress, _ = ConceptProgress.objects.get_or_create(
                child=request.user,
                concept=quiz.concept
            )
            if passed:
                concept_progress.completed = True
                concept_progress.progress_percentage = 100
                concept_progress.save()

                # Unlock next concept
                next_concepts = Concept.objects.filter(level=quiz.concept.level + 1)
                for c in next_concepts:
                    ConceptProgress.objects.get_or_create(
                        child=request.user,
                        concept=c,
                        defaults={'unlocked': True}
                    )

            return Response({
                'score': score,
                'passed': passed
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RewardListView(generics.ListAPIView):
    serializer_class = RewardEarnedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RewardEarned.objects.filter(child=self.request.user)


# Dashboard view for a child user
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        child = request.user
        total_concepts = Concept.objects.count()
        progress = ConceptProgress.objects.filter(child=child, completed=True).count()
        total_rewards = RewardEarned.objects.filter(child=child).count()

        return Response({
            'concepts_completed': progress,
            'total_concepts': total_concepts,
            'progress_percentage': round((progress / total_concepts) * 100, 2) if total_concepts else 0,
            'rewards_earned': total_rewards
        })


# Admin-only view to list or create concepts
class AdminConceptCreateView(generics.ListCreateAPIView):
    queryset = Concept.objects.all()
    serializer_class = ConceptSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# Admin-only view to create quizzes
class AdminQuizCreateView(generics.CreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# Admin-only view to create questions
class AdminQuestionCreateView(generics.CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# Admin-only view to create answer choices
class AdminAnswerChoiceCreateView(generics.CreateAPIView):
    queryset = AnswerChoice.objects.all()
    serializer_class = AnswerChoiceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# Admin-only view to create rewards
class AdminRewardCreateView(generics.ListCreateAPIView):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
