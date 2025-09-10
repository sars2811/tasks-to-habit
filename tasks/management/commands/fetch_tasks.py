from django.core.management.base import BaseCommand
from users.models import User
from tasks.models import TaskList, Task, TaskStatus
from google_apis import get_tasks_in_tasklist, get_task
from django.core.paginator import Paginator
from datetime import date as Date
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
                task_lists = TaskList.objects.filter(
                    user=user, to_track=True, is_active=True
                ).all()
                for task_list in task_lists:
                    self.stdout.write(
                        f"Fetching tasks for user: {user.username}, Task List: {task_list.name}"
                    )

                    fetched_tasks = Task.objects.filter(
                        task_list=task_list,
                        due__date=timezone.localdate(),
                        deleted=False,
                    )

                    fetched_tasks_ids = [task.task_id for task in fetched_tasks]
                    upstream_tasks = get_tasks_in_tasklist(user, task_list.id)

                    for task in fetched_tasks:
                        updated_task_data = get_task(user, task_list.id, task.task_id)
                        task.status = updated_task_data.get("status", task.status)
                        task.completed = (
                            updated_task_data.get("status", task.status)
                            == TaskStatus.COMPLETED
                        )
                        task.completed_at = updated_task_data.get(
                            "completed", task.completed_at
                        )
                        task.save()

                    for task_data in upstream_tasks:
                        if (
                            task_data["id"] not in fetched_tasks_ids
                            and task_data["due"]
                            and Date.fromisoformat(task_data["due"][:10])
                            == timezone.localdate()
                        ):
                            Task.objects.create(
                                task_id=task_data["id"],
                                title=task_data.get("title", ""),
                                due=task_data.get("due", None),
                                status=task_data.get("status", ""),
                                completed=task_data.get("status", "needsAction")
                                == TaskStatus.COMPLETED,
                                completed_at=task_data.get("completed", None),
                                task_list=task_list,
                                deleted=False,
                            ).save()
                    self.stdout.write(
                        f"Completed fetching tasks for Task List: {task_list.name}"
                    )
