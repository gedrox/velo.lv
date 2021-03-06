# coding=utf-8
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.forms.models import BaseInlineFormSet
from django.views.generic import DetailView
from django_tables2_reports.views import ReportTableView
from extra_views import InlineFormSet, NamedFormsetsMixin, UpdateWithInlinesView
import datetime
from core.models import Competition
from manager.forms import ManageTeamMemberForm, ManageTeamForm
from manager.tables import ManageMemberApplicationTable, ManageTeamTable
from manager.tables.tables import ManageTeamApplyTable
from manager.views.permission_view import ManagerPermissionMixin
from team.models import MemberApplication, Team, Member
from velo.mixins.views import SetCompetitionContextMixin, SingleTableViewWithRequest, RequestFormKwargsMixin
from velo.utils import load_class


__all__ = [
    'ManageAppliedTeamMembersList', 'ManageTeamList', 'ManageTeamAppliedUpdate', 'ManageTeams', 'ManageTeamApplyList'
]


class ManageTeamApplyList(ManagerPermissionMixin, SetCompetitionContextMixin, DetailView):
    model = Team
    template_name = 'manager/team_apply_list.html'
    pk_url_kwarg = 'pk2'

    def get_context_data(self, **kwargs):
        context = super(ManageTeamApplyList, self).get_context_data(**kwargs)

        competition = self.object.distance.competition
        child_competitions = competition.get_children()

        if child_competitions:
            competitions = child_competitions
        else:
            competitions = (competition, )

        final_competitions = []
        for competition in competitions:
            members = MemberApplication.objects.filter(competition=competition, member__team=self.object).order_by('kind')
            final_competitions.append((competition, members))
            if competition.competition_date > datetime.date.today():
                break

        context.update({'competitions': final_competitions})

        return context



class ManageTeams(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Team
    table_class = ManageTeamTable
    template_name = 'manager/table.html'

    def get_queryset(self):
        queryset = super(ManageTeams, self).get_queryset()
        queryset = queryset.filter(distance__competition_id__in=self.competition.get_ids()).distinct()
        queryset = queryset.select_related('distance', 'distance__competition')
        return queryset


class ManageAppliedTeamMembersList(ManagerPermissionMixin, SetCompetitionContextMixin, ReportTableView):
    model = MemberApplication
    table_class = ManageMemberApplicationTable
    template_name = 'manager/table.html'

    def get_queryset(self):
        queryset = super(ManageAppliedTeamMembersList, self).get_queryset()

        competition = Competition.objects.get(id=self.kwargs.get('pk'))
        distances = competition.get_distances().filter(can_have_teams=True)

        queryset = queryset.filter(member__team__distance__in=distances)
        queryset = queryset.select_related('member', 'member__team', 'participant', 'participant_unpaid', 'participant_potential')
        return queryset

class ManageTeamList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Team
    table_class = ManageTeamApplyTable
    template_name = 'manager/table.html'

    def get_queryset(self):
        queryset = super(ManageTeamList, self).get_queryset()
        queryset = queryset.filter(member__memberapplication__competition=self.competition).distinct()
        queryset = queryset.select_related('distance', )
        return queryset


class TeamMemberBaseInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.request_kwargs = kwargs.pop('request_kwargs', None)
        super(TeamMemberBaseInlineFormSet, self).__init__(*args, **kwargs)

    def get_queryset(self):
        queryset = super(TeamMemberBaseInlineFormSet, self).get_queryset()
        queryset = queryset.filter(memberapplication__competition_id=self.request_kwargs.get('pk'))
        queryset = queryset.order_by('memberapplication__kind').distinct()
        return queryset


class ManageTeamMemberInline(InlineFormSet):
    can_order = False
    model = Member
    form_class = ManageTeamMemberForm
    formset_class = TeamMemberBaseInlineFormSet
    extra = 0
    can_delete = False

    def get_extra_form_kwargs(self):
        kwargs = super(ManageTeamMemberInline, self).get_extra_form_kwargs()
        kwargs.update({'request': self.request})
        kwargs.update({'request_kwargs': self.kwargs})
        return kwargs

    def get_formset_kwargs(self):
        kwargs = super(ManageTeamMemberInline, self).get_formset_kwargs()
        kwargs.update({'request': self.request})
        kwargs.update({'request_kwargs': self.kwargs})
        return kwargs



class ManageTeamAppliedUpdate(ManagerPermissionMixin, SetCompetitionContextMixin, RequestFormKwargsMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    pk_url_kwarg = 'pk2'
    model = Team
    inlines = [ManageTeamMemberInline, ]
    inlines_names = ['member']
    form_class = ManageTeamForm
    template_name = 'manager/participant_form.html'

    def get_success_url(self):
        return reverse('manager:applied_team_list', kwargs={'pk': self.kwargs.get('pk')})


    def forms_valid(self, form, inlines):
        ret = super(ManageTeamAppliedUpdate, self).forms_valid(form, inlines)

        class_ = load_class(self.object.distance.competition.processing_class)
        competition_class = class_(competition_id=self.kwargs.get('pk'))
        competition_class.recalculate_team_result(team=self.object)

        return ret