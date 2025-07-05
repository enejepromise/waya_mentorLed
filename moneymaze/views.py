from django.db import transaction
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import (
    Concept, ConceptProgress, Quiz, QuizResult,
    Reward, RewardEarned, Question, AnswerChoice
)
from .serializers import (
    ConceptSerializer, ConceptProgressSerializer, QuizSerializer,
    QuizSubmissionSerializer, QuizResultSerializer, RewardEarnedSerializer,
    RewardSerializer, QuestionSerializer, AnswerChoiceSerializer
)


class ConceptListView(generics.ListAPIView):
    queryset = Concept.objects.all().order_by('level')
    serializer_class = ConceptSerializer
    permission_classes = [IsAuthenticated]


class ConceptProgressListView(generics.ListAPIView):
    serializer_class = ConceptProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retrieve the Child profile linked to the logged-in user
        child = getattr(self.request.user, 'child_profile', None)
        if not child:
            return ConceptProgress.objects.none()
        return ConceptProgress.objects.filter(child=child)


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

            try:
                quiz = Quiz.objects.get(id=quiz_id)
            except Quiz.DoesNotExist:
                return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)

            child = getattr(request.user, 'child_profile', None)
            if not child:
                return Response({"detail": "Child profile not found."}, status=status.HTTP_400_BAD_REQUEST)

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
                # Create or update quiz result
                quiz_result, created = QuizResult.objects.get_or_create(
                    child=child,
                    quiz=quiz,
                    defaults={'score': score, 'passed': passed}
                )
                if not created:
                    return Response({"detail": "Quiz already submitted."}, status=status.HTTP_400_BAD_REQUEST)

                # Update concept progress
                concept_progress, _ = ConceptProgress.objects.get_or_create(
                    child=child,
                    concept=quiz.concept
                )
                concept_progress.progress_percentage = score
                if passed:
                    concept_progress.completed = True
                    concept_progress.progress_percentage = 100
                    concept_progress.save()

                    # Unlock next level(s)
                    next_level = quiz.concept.level + 1
                    next_concepts = Concept.objects.filter(level=next_level)
                    for next_concept in next_concepts:
                        ConceptProgress.objects.get_or_create(
                            child=child,
                            concept=next_concept,
                            defaults={'unlocked': True}
                        )

                    # Award reward(s) for completed concept
                    rewards = Reward.objects.filter(concept=quiz.concept)
                    for reward in rewards:
                        RewardEarned.objects.get_or_create(
                            child=child,
                            reward=reward
                        )
                else:
                    # Save progress even if not passed
                    concept_progress.save()

            return Response({
                "score": score,
                "passed": passed,
                "message": "Quiz submitted successfully."
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RewardListView(generics.ListAPIView):
    serializer_class = RewardEarnedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        child = getattr(self.request.user, 'child_profile', None)
        if not child:
            return RewardEarned.objects.none()
        return RewardEarned.objects.filter(child=child)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        child = getattr(request.user, 'child_profile', None)
        if not child:
            return Response({"detail": "Child profile not found."}, status=status.HTTP_400_BAD_REQUEST)

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


# Admin-only views for managing content

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
