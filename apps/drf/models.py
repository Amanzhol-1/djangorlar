from django.core.validators import MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from apps.abstracts.models import AbstractBaseModel


TITLE_MAX_LENGTH = 50
ORDER_MAX_LEN = 10
ORDER_DECIMAL_PLACES = 2
INDENTATION_MAX_VALUE = 50

User = get_user_model()

class Course(AbstractBaseModel):
    """
    Course model
    """
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    description = models.TextField()
    owner = models.ForeignKey(User, related_name='owned_courses', on_delete=models.CASCADE)


class Lesson(AbstractBaseModel):
    """
    Lesson model
    """
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    content = models.TextField()
    order = models.DecimalField(max_digits=ORDER_MAX_LEN, decimal_places=ORDER_DECIMAL_PLACES)
    indentation = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(INDENTATION_MAX_VALUE)]
    )
    is_published = models.BooleanField(default=False)
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} ({self.course.title})"
