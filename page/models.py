
from django.db import models
from django.utils import timezone

class StudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def all_with_deleted(self):
        return super().get_queryset()

class Student(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    address = models.CharField(max_length=30)
    state = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = StudentManager()

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)  # This will permanently delete the record



class StudentHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
   
#    used for test (json data) 
class details (models.Model):
    student_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    student_class = models.CharField(max_length=10)
    mark = models.IntegerField()
    phone=models.CharField(max_length=15)

    def __str__(self):
        return self.name