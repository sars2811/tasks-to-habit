from django.shortcuts import render
from google_apis import get_google_tasks_list
from tasks.models import TaskList
from .forms import TaskListTrackingForm
from django.http import HttpResponseRedirect
from django.forms import formset_factory


def get_task_lists_view(request):
    TaskListFormSet = formset_factory(TaskListTrackingForm, extra=0)

    task_lists = get_google_tasks_list(request.user)
    stored_task_lists = TaskList.objects.filter(user=request.user).all()
    task_list_aggregated = []
    for task_list in task_lists:
        stored_task_list = stored_task_lists.filter(id=task_list["id"]).first()
        if stored_task_list:
            TaskList.objects.filter(id=task_list["id"]).update(
                name=task_list.get("title", ""),
            )
        task_list_aggregated.append(
            {
                "id": task_list["id"],
                "name": task_list.get("title", ""),
                "to_track": stored_task_list.to_track if stored_task_list else False,
                "is_active": True,
            }
        )
    for stored_task_list in stored_task_lists:
        if not any(tl["id"] == stored_task_list.id for tl in task_lists):
            TaskList.objects.filter(id=stored_task_list.id).update(
                is_active=False,
            )

    if request.method == "POST":
        forms = TaskListFormSet(request.POST, initial=task_list_aggregated)
        forms.is_valid()
        print(forms.errors)
        if forms.is_valid():
            for form in forms:
                cd = form.cleaned_data
                print(cd)
                to_track = cd["to_track"]
                if to_track:
                    TaskList.objects.update_or_create(
                        id=cd["id"],
                        defaults={
                            "user": request.user,
                            "name": cd["name"],
                            "to_track": to_track,
                            "is_active": True,
                        },
                    )
                else:
                    TaskList.objects.filter(id=cd["id"]).update(to_track=to_track)
            print("Updated task list tracking preferences")
            return HttpResponseRedirect("/habits")
        return HttpResponseRedirect("/tasks/lists")
    else:
        forms = TaskListFormSet(initial=task_list_aggregated)
        context = {"task_lists": task_list_aggregated, "forms": forms}
        return render(request, "tasks/task_lists.html", context)
