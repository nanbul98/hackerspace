from django.contrib import admin

from django_summernote.admin import SummernoteModelAdmin

# Register your models here.
from prerequisites.admin import PrereqInline

from .models import Quest, Category, QuestSubmission, CommonData


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quest')


# class TaggedItemInline(GenericTabularInline):
#     model = TaggedItem

class CommonDataAdmin(SummernoteModelAdmin):
    pass


class QuestSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quest', 'is_completed', 'is_approved', 'semester')
    list_filter = ['is_completed', 'is_approved', 'semester']
    search_fields = ['user']

    # default queryset doesn't return other semesters, or submissions for archived quests, or not visible to students
    def get_queryset(self, request):
        qs = QuestSubmission.objects.get_queryset(active_semester_only=False,
                                                  exclude_archived_quests=False,
                                                  exclude_quests_not_visible_to_students=False)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class QuestAdmin(SummernoteModelAdmin):  # use SummenoteModelAdmin
    list_display = ('id', 'name', 'xp', 'archived', 'visible_to_students', 'max_repeats', 'date_expired',
                    'common_data', 'campaign',)
    list_filter = ['archived', 'visible_to_students', 'max_repeats', 'verification_required']
    search_fields = ['name']
    inlines = [
        # TaggedItemInline
        PrereqInline,
    ]

    change_list_filter_template = "admin/filter_listing.html"

    # default queryset doesn't include archived quests
    def get_queryset(self, request):
        qs = Quest.objects.get_queryset(include_archived=True)
        return qs

    # fieldsets = [
    #     ('Available', {'fields': ['date_available', 'time_available']}),
    # ]


admin.site.register(Quest, QuestAdmin)
admin.site.register(Category)
admin.site.register(CommonData, CommonDataAdmin)
admin.site.register(QuestSubmission, QuestSubmissionAdmin)
# admin.site.register(Prereq)
# admin.site.register(Feedback, FeedbackAdmin)
# admin.site.register(TaggedItem)
