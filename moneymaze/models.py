from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from children.models import Child  

# Financial Concepts
class Concept(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    level = models.PositiveIntegerField(default=1)  # Level-based unlocking

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['level']


# Track Progress
class ConceptProgress(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    progress_percentage = models.FloatField(default=0.0)
    unlocked = models.BooleanField(default=False)  # to unlock levels

    class Meta:
        unique_together = ('child', 'concept')


# Quiz
class Quiz(models.Model):
    concept = models.OneToOneField(Concept, on_delete=models.CASCADE)  # One quiz per concept
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"Quiz: {self.title}"


#  Questions
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return self.text


# Answer Choices
class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


# Quiz Results
class QuizResult(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    passed = models.BooleanField(default=False)
    taken_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('child', 'quiz')


#Rewards
class Reward(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='rewards/', blank=True, null=True)
    points_required = models.IntegerField(default=0)

    def __str__(self):
        return self.name


# Earned Rewards
class RewardEarned(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    earned_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('child', 'reward')