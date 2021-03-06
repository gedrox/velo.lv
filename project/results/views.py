# coding=utf-8
from __future__ import unicode_literals
import datetime
from django.db.models import Q, Min
from django.http import Http404, HttpResponse
from django.template.defaultfilters import slugify
from django.views.generic import ListView, TemplateView, DetailView
from django_tables2 import SingleTableView
from core.models import Competition, Distance
from results.models import Result, SebStandings, TeamResultStandings
from results.tables import ResultTeamStandingTable
from team.models import MemberApplication
from velo.mixins.views import SetCompetitionContextMixin
from velo.utils import load_class
from django.db import connection
from django.core.cache import cache


class ResultAllView(TemplateView):
    template_name = 'results/all_view.html'

    def get_context_data(self, **kwargs):
        context = super(ResultAllView, self).get_context_data(**kwargs)

        start_year = datetime.date.today().year
        end_year = Result.objects.aggregate(Min('competition__competition_date')).values()[0].year

        competitions = []
        for year in range(end_year, start_year+1):
            year_comp = Competition.objects.filter(Q(competition_date__year=year) | Q(children__competition_date__year=year)).filter(level=1).distinct().extra(
                select={
                    'have_results': 'Select count(*) from results_result rr left outer join core_competition cc1 on rr.competition_id = cc1.id left outer join core_competition cc2 on cc1.parent_id = cc2.id where cc1.id = core_competition.id or cc2.id = core_competition.id',
                })
            competitions.append((year, year_comp))

        context.update({'competitions': competitions})

        return context



class ResultList(SetCompetitionContextMixin, SingleTableView):
    """
    Class used to display participant result.
    Optimized view
    """
    model = Result
    template_name = 'results/participant.html'

    def get_table_class(self):
        return self.get_competition_class().get_result_table_class(self.distance, self.request.GET.get('group', None))

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        self.set_distances(have_results=True)  # Based on self.competition
        self.set_distance(self.request.GET.get('distance', None))

        return super(ResultList, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ResultList, self).get_context_data(**kwargs)
        context.update({'groups': self.get_competition_class().groups.get(self.distance.id, ())})
        return context

    def get_queryset(self):
        queryset = super(ResultList, self).get_queryset()

        if self.distance:
            queryset = queryset.filter(number__distance=self.distance)

        if self.request.GET.get('group', None):
            queryset = queryset.filter(participant__group=self.request.GET.get('group', None))

        search = self.request.GET.get('search', None)
        if search:
            search_slug = slugify(search)
            queryset = queryset.filter(
                Q(participant__slug__icontains=search_slug) | Q(number__number__icontains=search_slug)  | Q(participant__team_name__icontains=search.upper()))



        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        if self.competition.id == 34:
            if self.distance.id == 28:
                queryset = queryset.extra(
                    select={
                        'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
                        'l2': 'SELECT time FROM results_lapresult l2 WHERE l2.result_id = results_result.id and l2.index=2',
                        'l3': 'SELECT time FROM results_lapresult l3 WHERE l3.result_id = results_result.id and l3.index=3',
                        'l4': 'SELECT time FROM results_lapresult l4 WHERE l4.result_id = results_result.id and l4.index=4',
                    },
                )
            else:
                queryset = queryset.extra(
                    select={
                        'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
                    },
                )

        queryset = queryset.select_related('competition', 'distance', 'participant', 'participant__bike_brand',
                                           'participant__team', 'number', 'leader')

        return queryset


class SebStandingResultList(SetCompetitionContextMixin, SingleTableView):
    """
    Class used to display participant standings.
    Optimized view
    """
    model = SebStandings
    template_name = 'results/participant_standing.html'

    def get_table_class(self):
        return self.get_competition_class().get_standing_table_class(self.distance, self.request.GET.get('group', None))

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        self.set_distances(have_results=True)  # Based on self.competition
        self.set_distance(self.request.GET.get('distance', None))

        return super(SebStandingResultList, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SebStandingResultList, self).get_context_data(**kwargs)
        context.update({'groups': self.get_competition_class().groups.get(self.distance.id, ())})
        return context

    def get_queryset(self):
        queryset = super(SebStandingResultList, self).get_queryset()

        if self.distance:
            queryset = queryset.filter(distance=self.distance)

        if self.request.GET.get('group', None):
            queryset = queryset.filter(participant__group=self.request.GET.get('group', None))

        search = self.request.GET.get('search', None)
        if search:
            search_slug = slugify(search)
            queryset = queryset.filter(Q(participant__slug__icontains=search_slug) | Q(
                participant__primary_number__number__icontains=search_slug)   | Q(participant__team_name__icontains=search.upper()))

        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        queryset = queryset.select_related('competition', 'distance', 'participant', 'participant__primary_number',
                                           'participant__team')

        return queryset


class SebTeamResultList(SetCompetitionContextMixin, ListView):
    """
    This class is used to view team results for one competition/stage.
    This is fully optimized view.
    """
    model = TeamResultStandings
    template_name = 'results/team.html'

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        self.set_distances(only_w_teams=True)  # Based on self.competition
        self.set_distance(self.request.GET.get('distance', None))

        return super(SebTeamResultList, self).get(*args, **kwargs)

    def get_queryset(self):
        queryset = super(SebTeamResultList, self).get_queryset()
        queryset = queryset.filter(team__member__memberapplication__competition=self.competition,
                                   team__member__memberapplication__kind=MemberApplication.KIND_PARTICIPANT,
                                   team__member__memberapplication__participant__result__competition=self.competition)

        queryset = queryset.filter(team__distance=self.distance)

        index = self.get_competition_class().competition_index  # Get stage index
        queryset = queryset.order_by('-points%i' % index, '-team__is_featured', 'team__title',
                                     '-team__member__memberapplication__participant__result__points_distance',
                                     'team__member__memberapplication__participant__primary_number__number',)

        queryset = queryset.values_list('team__id', 'team__title', 'team__is_featured',
                                        'team__teamresultstandings__points%i' % index,
                                        'team__member__first_name', 'team__member__last_name', 'team__member__birthday',
                                        'team__member__memberapplication__participant__primary_number__number',
                                        'team__member__memberapplication__participant__result__points_distance',
                                        )
        return queryset



class SebTeamResultStandingList(SetCompetitionContextMixin, SingleTableView):
    """
    This class is used to view team standings.
    Optimized class.
    """
    model = TeamResultStandings
    template_name = 'results/team_standing.html'

    def get_table_class(self):
        return ResultTeamStandingTable

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        self.set_distances(only_w_teams=True)  # Based on self.competition
        self.set_distance(self.request.GET.get('distance', None))

        return super(SebTeamResultStandingList, self).get(*args, **kwargs)

    def get_queryset(self):
        queryset = super(SebTeamResultStandingList, self).get_queryset()
        queryset = queryset.filter(team__distance=self.distance).order_by('-points_total', '-team__is_featured', 'team__title')
        queryset = queryset.select_related('team')

        return queryset


class TeamResultsByTeamName(SetCompetitionContextMixin, TemplateView):
    """
    This class is used to view team results for one competition/stage.
    This is fully optimized view.
    """
    template_name = 'results/team_by_teamname.html'

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        self.set_distances(only_w_teams=True)  # Based on self.competition
        self.set_distance(self.request.GET.get('distance', None))

        return super(TeamResultsByTeamName, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(TeamResultsByTeamName, self).get_context_data(**kwargs)

        cache_key = 'team_results_by_name_%i_%i' % (self.competition.id, self.distance.id)

        default_timeout = 60*30
        if self.competition.competition_date == datetime.date.today():
            default_timeout = 60
        print default_timeout

        object_list = cache.get(cache_key)
        if not object_list:
            cursor = connection.cursor()
            cursor.execute("""
    Select *, DATE_TRUNC('second', total) from (
    Select kopa.team_name_slug, count(*) counter, sum(kopa.time) total
    from (
    Select p.team_name_slug, p.time from (
    SELECT
        a.team_name_slug,
        r.time,
        row_number() OVER (PARTITION BY team_name_slug ORDER BY r.time) AS row
    FROM
        registration_participant a
        left outer join results_result r on r.participant_id = a.id
        where a.team_name_slug <> '' and a.team_name_slug <> '-' and r.time is not null and a.is_competing is true and a.distance_id = %s
        order by a.team_name_slug, r.time
    ) p where p.row <= 4
    ) kopa group by kopa.team_name_slug
    having count(*)>1
    order by total
    ) team
    left outer join
    (
    Select p.team_name, p.team_name_slug, p.time,p.first_name,p.last_name,p.birthday,p.team_name,p.number from (
    SELECT
        a.*,
        r.time,
        nr.number,
        row_number() OVER (PARTITION BY team_name_slug ORDER BY r.time) AS row
    FROM
        registration_participant a
        left outer join results_result r on r.participant_id = a.id
        left outer join registration_number nr on nr.id = a.primary_number_id
        where a.team_name_slug <> '' and a.team_name_slug <> '-' and r.time is not null and a.is_competing is true and a.distance_id = %s
        order by a.team_name_slug, r.time
    ) p where p.row <= 4
    ) participant on team.team_name_slug = participant.team_name_slug
    order by counter desc, total, team.team_name_slug, time
    """, [self.distance.id, self.distance.id])
            object_list = cursor.fetchall()
            cache.set(cache_key, object_list, default_timeout)

        context.update({
            'object_list': object_list,
        })
        return context


class ResultDiplomaPDF(DetailView):
    pk_url_kwarg = 'pk2'
    model = Result

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        if self.object.competition.processing_class:
            _class = load_class(self.object.competition.processing_class)
        else:
            raise Http404
        try:
            processing_class = _class(self.object.competition_id)
            file_obj = processing_class.generate_diploma(self.object)
        except:
            raise Http404
        response = HttpResponse(mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s.pdf' % self.object.participant.slug
        response.write(file_obj.getvalue())
        file_obj.close()
        return response
