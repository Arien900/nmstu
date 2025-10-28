from django.db import models

class GradeRecord(models.Model):
    student = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    grade = models.IntegerField()

    class Meta:
        unique_together = ('student', 'subject', 'grade')