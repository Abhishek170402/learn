from django.urls import path
from . import views  

urlpatterns = [
    path("", views.index, name="index"),
    path("table/", views.table, name="table"),  # Added trailing slash
    path("page/", views.page, name="page"),      # Added trailing slash
    path("display/", views.display, name="display"),  # Added trailing slash
    path("view_list/", views.view_list, name="view_list"),  # Added trailing slash
    path("your_view/", views.your_view, name="your_view"),  # Added trailing slash

    path("soft_delete/<int:pk>/", views.soft_delete, name="soft_delete"),
    path("restore/<int:pk>/", views.restore_view, name="restore"),
    path("hard_delete/<int:pk>/", views.hard_delete, name="hard_delete"),  # Hard delete URL
    path("search_students/", views.search_students, name="search_students"),  # Corrected to match view name
    path("load_students/", views.load_students, name="load_students"),
    path("save_students/", views.save_students, name="save_students"),
    path("test/", views.test, name="test"),
]