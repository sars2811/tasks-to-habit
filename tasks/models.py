from django.db import models


class TaskList(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    to_track = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TaskStatus(models.TextChoices):
    NEEDS_ACTION = "needsAction", "Needs Action"
    COMPLETED = "completed", "Completed"


class Task(models.Model):
    task_id = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    due = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=TaskStatus.choices, default=TaskStatus.NEEDS_ACTION
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    task_list = models.ForeignKey(
        TaskList, related_name="taskslist", on_delete=models.CASCADE
    )
    deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["task_id", "due"]),
        ]

        get_latest_by = "due"
        unique_together = [["task_list", "task_id", "due"]]

    def __str__(self):
        return f"{self.title}_{self.due}"
