from children.authentication import ChildJWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from .models import (
    Concept, ConceptProgress, Quiz, QuizResult,
    Reward, RewardEarned, Question, AnswerChoice,
    ConceptSection, SectionProgress, WeeklyStreak
)
from .serializers import (
    ConceptSerializer, ConceptProgressSerializer, QuizSerializer,
    QuizSubmissionSerializer, QuizResultSerializer, RewardEarnedSerializer,
    RewardSerializer, QuestionSerializer, AnswerChoiceSerializer,
    DashboardSerializer, ConceptSectionSerializer, WeeklyStreakSerializer
)


class ConceptListView(generics.ListAPIView):
    queryset = Concept.objects.all().order_by('level')
    serializer_class = ConceptSerializer
    authentication_classes = [ChildJWTAuthentication]
    permission_classes = [IsAuthenticated]


class ConceptProgressListView(generics.ListAPIView):
    serializer_class = ConceptProgressSerializer
    authentication_classes = [ChildJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        child = self.request.user
        if not child:
            return ConceptProgress.objects.none()
        return ConceptProgress.objects.filter(child=child)


class QuizDetailView(generics.RetrieveAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    authentication_classes = [ChildJWTAuthentication]
    permission_classes = [IsAuthenticated]


class SubmitQuizView(APIView):
    authentication_classes = [ChildJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSubmissionSerializer

    def post(self, request):
        serializer = QuizSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            quiz_id = serializer.validated_data['quiz_id']
            answers = serializer.validated_data['answers']

            try:
                quiz = Quiz.objects.get(id=quiz_id)
            except Quiz.DoesNotExist:
                return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)

            child = request.user
            if not child:
                return Response({"detail": "Child not found."}, status=status.HTTP_400_BAD_REQUEST)

            total_questions = quiz.questions.count()
            correct_answers = 0

            for question in quiz.questions.all():
                selected_choice_id = answers.get(str(question.id))
                if not selected_choice_id:
                    continue
                try:
                    selected_choice = AnswerChoice.objects.get(id=selected_choice_id, question=question)
                    if selected_choice.is_correct:
                        correct_answers += 1
                except AnswerChoice.DoesNotExist:
                    continue

            score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            passed = score >= 70

            with transaction.atomic():
                quiz_result, created = QuizResult.objects.get_or_create(
                    child=child,
                    quiz=quiz,
                    defaults={'score': score, 'passed': passed}
                )
                if not created:
                    return Response({"detail": "Quiz already submitted."}, status=status.HTTP_400_BAD_REQUEST)

                concept_progress, _ = ConceptProgress.objects.get_or_create(
                    child=child, concept=quiz.concept
                )
                concept_progress.progress_percentage = score
                if passed:
                    concept_progress.completed = True
                    concept_progress.progress_percentage = 100
                    concept_progress.save()

                    next_level = quiz.concept.level + 1
                    next_concepts = Concept.objects.filter(level=next_level)
                    for next_concept in next_concepts:
                        ConceptProgress.objects.get_or_create(
                            child=child,
                            concept=next_concept,
                            defaults={'unlocked': True}
                        )

                    rewards = Reward.objects.filter(concept=quiz.concept)
                    for reward in rewards:
                        RewardEarned.objects.get_or_create(
                            child=child, reward=reward
                        )
                else:
                    concept_progress.save()

            return Response({
                "score": score,
                "passed": passed,
                "message": "Quiz submitted successfully."
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RewardListView(generics.ListAPIView):
    serializer_class = RewardEarnedSerializer
    authentication_classes = [ChildJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        child = self.request.user
        if not child:
            return RewardEarned.objects.none()
        return RewardEarned.objects.filter(child=child)


class DashboardView(APIView):
    serializer_class = DashboardSerializer
    authentication_classes = [ChildJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        child = request.user
        if not child:
            return Response({"detail": "Child not found."}, status=status.HTTP_400_BAD_REQUEST)

        total_concepts = Concept.objects.count()
        completed_concepts = ConceptProgress.objects.filter(child=child, completed=True).count()
        total_rewards = RewardEarned.objects.filter(child=child).count()

        progress_percentage = round((completed_concepts / total_concepts) * 100, 2) if total_concepts else 0

        return Response({
            "concepts_completed": completed_concepts,
            "total_concepts": total_concepts,
            "progress_percentage": progress_percentage,
            "rewards_earned": total_rewards
        })


class WeeklyStreakView(APIView):
    """
    GET /api/moneymaze/weekly-streak/
    Returns the child's streak for the current week (Mon to Sun).
    """
    authentication_classes = [ChildJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        child = request.user
        if not child:
            return Response({"detail": "Child not found."}, status=400)

        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())  # Monday

        streak, created = WeeklyStreak.objects.get_or_create(
            child=child,
            week_start_date=week_start
        )

        serializer = WeeklyStreakSerializer(streak)
        return Response(serializer.data)


class ConceptSectionListView(generics.ListAPIView):
    serializer_class = ConceptSectionSerializer
    authentication_classes = [ChildJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        concept_id = self.kwargs['concept_id']
        return ConceptSection.objects.filter(concept_id=concept_id).order_by('order')


class ConceptSectionDetailView(generics.RetrieveAPIView):
    serializer_class = ConceptSectionSerializer
    authentication_classes = [ChildJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ConceptSection.objects.all().order_by('order')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        child = request.user

        if child:
            SectionProgress.objects.get_or_create(
                child=child,
                section=instance,
                defaults={'viewed': True}
            )

            # Mark concept progress as completed if all viewed
            concept_id = instance.concept_id
            all_sections = ConceptSection.objects.filter(concept_id=concept_id)
            viewed_sections = SectionProgress.objects.filter(
                child=child,
                section__concept_id=concept_id,
                viewed=True
            ).count()
            if viewed_sections == all_sections.count():
                concept_progress, _ = ConceptProgress.objects.get_or_create(child=child, concept_id=concept_id)
                concept_progress.unlocked = True
                concept_progress.progress_percentage = 100
                concept_progress.completed = True
                concept_progress.save()

        return super().retrieve(request, *args, **kwargs)


class CanAccessQuizView(APIView):
    authentication_classes = [ChildJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, concept_id):
        child = request.user
        if not child:
            return Response({"detail": "Child not found"}, status=400)

        try:
            concept = Concept.objects.get(id=concept_id)
        except Concept.DoesNotExist:
            return Response({"detail": "Concept not found"}, status=404)

        total_sections = concept.sections.count()
        viewed_sections = SectionProgress.objects.filter(
            child=child,
            section__concept=concept,
            viewed=True
        ).count()

        can_access_quiz = (viewed_sections == total_sections)

        return Response({
            "total_sections": total_sections,
            "viewed_sections": viewed_sections,
            "can_access_quiz": can_access_quiz
        })

# ========== ADMIN VIEWS ==========

class AdminConceptCreateView(generics.ListCreateAPIView):
    queryset = Concept.objects.all().order_by('level')
    serializer_class = ConceptSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminQuizCreateView(generics.CreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminQuestionCreateView(generics.CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminAnswerChoiceCreateView(generics.CreateAPIView):
    queryset = AnswerChoice.objects.all()
    serializer_class = AnswerChoiceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdminRewardCreateView(generics.ListCreateAPIView):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
