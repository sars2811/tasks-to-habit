from django.core.management.base import BaseCommand
from users.models import User
from tasks.models import TaskList, Task, TaskStatus
from google_apis import get_tasks_in_tasklist, get_task
from django.core.paginator import Paginator
from habits.models import Habit
from django.utils import timezone

USER_BATCH_SIZE = 10


class Command(BaseCommand):
    help = "Fetch tasks for monitored tasks_list for all active users"

    def handle(self, *args, **kwargs):
        users = User.objects.filter(is_active=True, is_staff=False).order_by("id").all()
        users_paginator = Paginator(users, USER_BATCH_SIZE)
        for i in users_paginator.page_range:
            users_page = users_paginator.page(i)
            self.stdout.write(f"Processing user batch {i}/{users_paginator.num_pages}")
            for user in users_page:
                habits = Habit.objects.filter(user=user).all()
                for habit in habits:
                    self.stdout.write(
                        f"Fetching for Habit: {habit.name}, Title String: {habit.title_string}"
                    )
                    latest_task = Task.objects.filter(
                        associated_habit=habit, deleted=False
                    ).latest()

                    if latest_task.due.date() != timezone.localdate():
                        continue

                    latest_task_data = get_task(
                        user, latest_task.task_list.id, latest_task.task_id
                    )
                    if latest_task_data["title"] != habit.title_string:
                        habit.title_string = latest_task_data["title"]
                        habit.save()
                        self.stdout.write(
                            f"Updated title_string for habit: {habit.name}, new title: {habit.title_string}"
                        )

                    if latest_task.completed:
                        continue

                    latest_task.title = latest_task_data["title"]
                    latest_task.completed = (
                        latest_task_data.get("status", TaskStatus.NEEDS_ACTION)
                        == TaskStatus.COMPLETED
                    )
                    latest_task.completed_at = latest_task_data.get("completed")
                    latest_task.status = latest_task_data.get("status")
                    latest_task.save()

                task_lists = TaskList.objects.filter(
                    user=user, to_track=True, is_active=True
                ).all()
                for task_list in task_lists:
                    self.stdout.write(
                        f"Fetching tasks for user: {user.username}, Task List: {task_list.name}"
                    )

                    upstream_tasks = get_tasks_in_tasklist(user, task_list.id)
                    for task_data in upstream_tasks:
                        existing_task = Task.objects.filter(
                            task_id=task_data["id"], task_list=task_list
                        ).first()

                        if existing_task and existing_task.associated_habit:
                            continue

                        associated_habit = Habit.objects.filter(
                            user=user, title_string=task_data.get("title", "")
                        ).first()

                        if associated_habit:
                            defaults = {
                                "title": task_data.get("title", ""),
                                "due": task_data.get("due", None),
                                "status": task_data.get("status", ""),
                                "completed": task_data.get("status", "needsAction")
                                == TaskStatus.COMPLETED,
                                "completed_at": task_data.get("completed", None),
                                "task_list": task_list,
                                "associated_habit": associated_habit,
                                "deleted": False,
                            }
                            Task.objects.update_or_create(
                                task_id=task_data["id"],
                                defaults=defaults,
                            )
                        else:
                            new_habit = Habit.objects.create(
                                name=task_data.get("title", "")[:100],
                                title_string=task_data.get("title", ""),
                                user=user,
                            )
                            new_habit.save()
                            task_defaults = {
                                "title": task_data.get("title", ""),
                                "due": task_data.get("due", None),
                                "status": task_data.get("status", ""),
                                "completed": task_data.get("status", "needsAction")
                                == TaskStatus.COMPLETED,
                                "completed_at": task_data.get("completed", None),
                                "task_list": task_list,
                                "associated_habit": new_habit,
                                "deleted": False,
                            }
                            Task.objects.update_or_create(
                                task_id=task_data["id"],
                                defaults=task_defaults,
                            )

                self.stdout.write(
                    f"Completed fetching tasks and habits for Task List: {task_list.name}"
                )
