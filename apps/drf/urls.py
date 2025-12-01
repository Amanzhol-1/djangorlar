from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, LessonViewSet


app_name = "drf"

router: DefaultRouter = DefaultRouter(trailing_slash=False)

router.register('courses', CourseViewSet, basename='course')
router.register('lessons', LessonViewSet, basename='lesson')

urlpatterns = router.urls