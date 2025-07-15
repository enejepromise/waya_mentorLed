import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Concept(models.Model):
    LEVEL_CHOICES = [
        (1, 'Savings'),
        (2, 'Budgeting'),
        (3, 'Investing'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    level = models.PositiveIntegerField(choices=LEVEL_CHOICES)
    order = models.PositiveIntegerField(default=1)  # For ordering lessons

    def __str__(self):
        return f"Lesson {self.level}: {self.title}"


# ✅ NEW: ConceptSection = content divided into pages/steps
class ConceptSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=100)
    content = models.TextField()
    order = models.PositiveIntegerField(default=1)  # Display order within the concept

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.concept.title} - {self.title}"


# ✅ NEW: Track which sections each child has viewed
class SectionProgress(models.Model):
    child = models.ForeignKey('children.Child', on_delete=models.CASCADE, related_name='section_progress')
    section = models.ForeignKey(ConceptSection, on_delete=models.CASCADE, related_name='viewed_by')
    viewed = models.BooleanField(default=False)
    viewed_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('child', 'section')

    def __str__(self):
        return f"{self.child.username} viewed {self.section}"


class ConceptProgress(models.Model):
    child = models.ForeignKey('children.Child', on_delete=models.CASCADE, related_name='concept_progress')
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='progress')
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    completed = models.BooleanField(default=False)
    unlocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('child', 'concept')

    def __str__(self):
        return f"{self.child.username} - {self.concept.title} ({self.progress_percentage}%)"


class Quiz(models.Model):
    concept = models.OneToOneField(Concept, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"Quiz for {self.concept.title}"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"


class QuizResult(models.Model):
    child = models.ForeignKey('children.Child', on_delete=models.CASCADE, related_name='quiz_results')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    passed = models.BooleanField(default=False)
    taken_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.child.username} - {self.quiz.concept.title} ({self.score}%)"


class Reward(models.Model):
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='rewards')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='rewards/', null=True, blank=True)
    points_required = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class RewardEarned(models.Model):
    child = models.ForeignKey('children.Child', on_delete=models.CASCADE, related_name='rewards_earned')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    earned_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('child', 'reward')

    def __str__(self):
        return f"{self.child.username} earned {self.reward.name}"


def default_streak():
    return {"mon": False, "tue": False, "wed": False, "thu": False, "fri": False, "sat": False, "sun": False}


class WeeklyStreak(models.Model):
    child = models.ForeignKey('children.Child', on_delete=models.CASCADE, related_name='weekly_streaks')
    week_start_date = models.DateField()
    streak = models.JSONField(default=default_streak)

    class Meta:
        unique_together = ("child", "week_start_date")

    def save(self, *args, **kwargs):
        if not self.week_start_date:
            today = timezone.now().date()
            self.week_start_date = today - timedelta(days=today.weekday())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.child.username} - Week starting {self.week_start_date}"
