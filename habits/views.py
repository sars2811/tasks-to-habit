from django.shortcuts import render

from .models import Habit
from tasks.models import Task


def index(request):
    habits = Habit.objects.filter(user=request.user)
    habits_data = []
    for habit in habits:
        habit_tasks = Task.objects.filter(associated_habit=habit).order_by("due")[0:30]
        habits_data.append((habit.name, [task.completed for task in habit_tasks]))
    return render(request, "habits/index.html", {"habits": habits_data})
