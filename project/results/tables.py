from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
import django_tables2 as tables
from django.utils.translation import ugettext_lazy as _
import itertools
from registration.models import Participant
from results.models import SebStandings, TeamResultStandings
from django.utils.html import strip_tags


__all__ = [
    'ResultChildrenGroupTable', 'ResultGroupTable', 'ResultDistanceTable', 'ResultDistanceStandingTable', 'ResultGroupStandingTable', 'ResultChildrenGroupStandingTable', 'ResultTeamStandingTable'
]

LEADER_TOOLTIP = ' <span class="label rounded label-%s"><span class="tooltips" data-icon="&#xe006;" data-toggle="tooltip" data-original-title="%s"></span></span>'

class ResultTeamStandingTable(tables.Table):
    place = tables.Column(empty_values=(), verbose_name='#', orderable=False)
    team_name = tables.Column(empty_values=(), verbose_name=_('Team Name'), accessor="team.title")

    def __init__(self, *args, **kwargs):
        super(ResultTeamStandingTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count(start=1)

    def render_place(self):
        return '%d' % next(self.counter)

    class Meta:
        model = TeamResultStandings
        attrs = {"class": "table table-striped table-hover"}
        fields = ("points_total", "points1", 'points2', 'points3', 'points4', 'points5', 'points6', 'points7')
        sequence = ("place", "team_name", "points_total", "points1", "points2", "points3", "points4", "points5", "points6", 'points7', )
        empty_text = _("There are no results")
        order_by = ("-points_total",)
        per_page = 200
        template = "bootstrap/table.html"



class ResultChildrenGroupStandingTable(tables.Table):
    group_place = tables.Column(empty_values=(), verbose_name='#', accessor="group_place")
    first_name = tables.Column(empty_values=(), verbose_name=_('First Name'), accessor="participant.first_name")
    last_name = tables.Column(empty_values=(), verbose_name=_('Last Name'), accessor="participant.last_name")
    year = tables.Column(empty_values=(), verbose_name=_('Year'), accessor="participant.birthday.year", order_by="participant.birthday")
    team = tables.Column(empty_values=(), verbose_name=_('Team'), accessor="participant.team_name")
    group = tables.Column(empty_values=(), verbose_name=_('Group'), accessor="participant.group")
    group_total = tables.Column(empty_values=(), verbose_name=_('Points Group'), accessor="group_total")
    number = tables.Column(empty_values=(), verbose_name=_('Number'), accessor="participant.primary_number")

    def render_number(self, record, **kwargs):
        return str(record.participant.primary_number.number)


    class Meta:
        model = SebStandings
        attrs = {"class": "table table-striped table-hover"}
        fields = ("group_points1", "group_points2", 'group_points3', 'group_points4', 'group_points5', 'group_points6', 'group_points7', 'group_total')  # all_numbers
        sequence = ("group_place", "number", "first_name", "last_name", "year", "group", "team", "group_points1", "group_points2", 'group_points3', 'group_points4', 'group_points5', 'group_points6', 'group_points7', 'group_total', )
        empty_text = _("There are no results")
        order_by = ("group", "group_place", "last_name")
        per_page = 200
        template = "bootstrap/table.html"



class ResultGroupStandingTable(tables.Table):
    group_place = tables.Column(empty_values=(), verbose_name='#', accessor="group_place")
    first_name = tables.Column(empty_values=(), verbose_name=_('First Name'), accessor="participant.first_name")
    last_name = tables.Column(empty_values=(), verbose_name=_('Last Name'), accessor="participant.last_name")
    year = tables.Column(empty_values=(), verbose_name=_('Year'), accessor="participant.birthday.year", order_by="participant.birthday")
    number = tables.Column(empty_values=(), verbose_name=_('Number'), accessor="participant.primary_number")
    team = tables.Column(empty_values=(), verbose_name=_('Team'), accessor="participant.team")
    group = tables.Column(empty_values=(), verbose_name=_('Group'), accessor="participant.group")

    def render_team(self, record, *args, **kwargs):
        if record.participant.team:
            return mark_safe('<a href="#">%s</a>' % record.participant.team)
        elif record.participant.team_name:
            return '%s' % record.participant.team_name
        else:
            return '-'

    class Meta:
        model = SebStandings
        attrs = {"class": "table table-striped table-hover"}
        fields = ("group_points1", "group_points2", 'group_points3', 'group_points4', 'group_points5', 'group_points6', 'group_points7', 'group_total')  # all_numbers
        sequence = ("group_place", "number", "group", "first_name", "last_name", "year", "team", "group_points1", "group_points2", 'group_points3', 'group_points4', 'group_points5', 'group_points6', 'group_points7', 'group_total', )
        empty_text = _("There are no results")
        order_by = ("group_place",)
        per_page = 200
        template = "bootstrap/table.html"


class ResultDistanceStandingTable(tables.Table):
    distance_place = tables.Column(empty_values=(), verbose_name='#', accessor="distance_place")
    first_name = tables.Column(empty_values=(), verbose_name=_('First Name'), accessor="participant.first_name")
    last_name = tables.Column(empty_values=(), verbose_name=_('Last Name'), accessor="participant.last_name")
    year = tables.Column(empty_values=(), verbose_name=_('Year'), accessor="participant.birthday.year", order_by="participant.birthday")
    number = tables.Column(empty_values=(), verbose_name=_('Number'), accessor="participant.primary_number")
    team = tables.Column(empty_values=(), verbose_name=_('Team'), accessor="participant.team")

    def render_team(self, record, *args, **kwargs):
        if record.participant.team:
            return mark_safe('<a href="#">%s</a>' % record.participant.team)
        elif record.participant.team_name:
            return '%s' % record.participant.team_name
        else:
            return '-'

    class Meta:
        model = SebStandings
        attrs = {"class": "table table-striped table-hover"}
        fields = ("distance_points1", "distance_points2", 'distance_points3', 'distance_points4', 'distance_points5', 'distance_points6', 'distance_points7', 'distance_total')  # all_numbers
        sequence = ("distance_place", "number", "first_name", "last_name", "year", "team", "distance_points1", "distance_points2", 'distance_points3', 'distance_points4', 'distance_points5', 'distance_points6', 'distance_points7', 'distance_total', )
        empty_text = _("There are no results")
        order_by = ("distance_place",)
        per_page = 200
        template = "bootstrap/table.html"



class ResultChildrenGroupTable(tables.Table):
    result_group = tables.Column(empty_values=(), verbose_name='#', accessor="result_group")
    first_name = tables.Column(empty_values=(), verbose_name=_('First Name'), accessor="participant.first_name")
    last_name = tables.Column(empty_values=(), verbose_name=_('Last Name'), accessor="participant.last_name")
    year = tables.Column(empty_values=(), verbose_name=_('Year'), accessor="participant.birthday.year", order_by="participant.birthday")
    team_name = tables.Column(empty_values=(), verbose_name=_('Team'), accessor="participant.team_name")
    group = tables.Column(empty_values=(), verbose_name=_('Group'), accessor="participant.group")
    points_group = tables.Column(empty_values=(), verbose_name=_('Points Group'), accessor="points_group")

    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = ("number", "status") # all_numbers
        sequence = ("result_group", "number", 'first_name', 'last_name', 'year', 'team_name', 'group', 'points_group', 'status')
        empty_text = _("There are no results")
        order_by = ("group", "result_group", "last_name")
        per_page = 200
        template = "bootstrap/table.html"


class ResultGroupTable(tables.Table):
    result_group = tables.Column(empty_values=(), verbose_name='#', accessor="result_group")
    first_name = tables.Column(empty_values=(), verbose_name=_('First Name'), accessor="participant.first_name")
    last_name = tables.Column(empty_values=(), verbose_name=_('Last Name'), accessor="participant.last_name")
    year = tables.Column(empty_values=(), verbose_name=_('Year'), accessor="participant.birthday.year", order_by="participant.birthday")
    team = tables.Column(empty_values=(), verbose_name=_('Team'), accessor="participant.team")
    bike_brand = tables.Column(empty_values=(), verbose_name=_('Bike Brand'), accessor="participant.bike_brand2")
    time = tables.Column(empty_values=(), verbose_name=_('Time'), accessor="time")
    group = tables.Column(empty_values=(), verbose_name=_('Group'), accessor="participant.group")
    points_group = tables.Column(empty_values=(), verbose_name=_('Points Group'), accessor="points_group")

    def render_last_name(self, record):
        text = strip_tags(record.participant.last_name)
        if record.leader:
            text += LEADER_TOOLTIP % (record.leader.color, record.leader.text)
        return mark_safe(text)


    def render_bike_brand(self, record):
        if record.participant.bike_brand:
            return record.participant.bike_brand
        else:
            return '-'

    def render_team(self, record, *args, **kwargs):
        if record.participant.team:
            return mark_safe('<a href="#">%s</a>' % record.participant.team)
        elif record.participant.team_name:
            return '%s' % record.participant.team_name
        else:
            return '-'

    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = ("number", "status") # all_numbers
        sequence = ("result_group", "number", 'first_name','last_name', 'year', 'team', 'bike_brand', 'time', 'group', 'points_group', 'status')
        empty_text = _("There are no results")
        order_by = ("time")
        # ordering = ('created')
        per_page = 200
        template = "bootstrap/table.html"


class ResultDistanceTable(tables.Table):
    result_distance = tables.Column(empty_values=(), verbose_name='#', accessor="result_distance")
    first_name = tables.Column(empty_values=(), verbose_name=_('First Name'), accessor="participant.first_name")
    last_name = tables.Column(empty_values=(), verbose_name=_('Last Name'), accessor="participant.last_name")
    year = tables.Column(empty_values=(), verbose_name=_('Year'), accessor="participant.birthday.year", order_by="participant.birthday")
    team = tables.Column(empty_values=(), verbose_name=_('Team'), accessor="participant.team")
    bike_brand = tables.Column(empty_values=(), verbose_name=_('Bike Brand'), accessor="participant.bike_brand2")
    time = tables.Column(empty_values=(), verbose_name=_('Time'), accessor="time")
    points_distance = tables.Column(empty_values=(), verbose_name=_('Points Distance'), accessor="points_distance")

    def render_last_name(self, record):
        text = strip_tags(record.participant.last_name)
        if record.leader:
            text += LEADER_TOOLTIP % (record.leader.color, record.leader.text)
        return mark_safe(text)

    def render_bike_brand(self, record):
        if record.participant.bike_brand:
            return record.participant.bike_brand
        else:
            return '-'

    def render_team(self, record, *args, **kwargs):
        if record.participant.team:
            return mark_safe('<a href="#">%s</a>' % record.participant.team)
        elif record.participant.team_name:
            return '%s' % record.participant.team_name
        else:
            return '-'

    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = ("number", "status") # all_numbers
        sequence = ("result_distance", "number", 'first_name','last_name', 'year', 'team', 'bike_brand', 'time', 'points_distance', 'status')
        empty_text = _("There are no results")
        order_by = ("time")
        # ordering = ('created')
        per_page = 200
        template = "bootstrap/table.html"


class ResultRMDistanceTable(tables.Table):
    result_distance = tables.Column(empty_values=(), verbose_name='#', accessor="result_distance")
    first_name = tables.Column(empty_values=(), verbose_name=_('First Name'), accessor="participant.first_name")
    last_name = tables.Column(empty_values=(), verbose_name=_('Last Name'), accessor="participant.last_name")
    year = tables.Column(empty_values=(), verbose_name=_('Year'), accessor="participant.birthday.year", order_by="participant.birthday")
    team = tables.Column(empty_values=(), verbose_name=_('Team'), accessor="participant.team")
    bike_brand = tables.Column(empty_values=(), verbose_name=_('Bike Brand'), accessor="participant.bike_brand2")
    time = tables.Column(empty_values=(), verbose_name=_('Time'), accessor="time")
    # points_distance = tables.Column(empty_values=(), verbose_name=_('Points Distance'), accessor="points_distance")


    def _lap_render(self, value):
        if value:
            return mark_safe("<small>%s</small>" % str(value.strftime("%H:%M:%S")))
        return '-'

    def render_last_name(self, record):
        text = strip_tags(record.participant.last_name)
        if record.leader:
            text += LEADER_TOOLTIP % (record.leader.color, record.leader.text)

        if record.competition.params.get('have_diploma', False):
            text = '<a href="%s">%s</a>' % (reverse('competition:result_diploma', kwargs={'pk': record.competition_id, 'pk2': record.id}), text)

        return mark_safe(text)

    def render_bike_brand(self, record):
        if record.participant.bike_brand2:
            return record.participant.bike_brand2
        else:
            return '-'

    def render_team(self, record, *args, **kwargs):
        if record.participant.team:
            return mark_safe('<a href="#">%s</a>' % record.participant.team)
        elif record.participant.team_name:
            return '%s' % record.participant.team_name
        else:
            return '-'

    def render_time(self, value, record, *args, **kwargs):
        return self._lap_render(value)


    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = ("number", "status") # all_numbers
        sequence = ("result_distance", "number", 'first_name', 'last_name', 'year', 'team', 'bike_brand', 'time', 'status')
        empty_text = _("There are no results")
        order_by = ("time")
        # ordering = ('created')
        per_page = 200
        template = "bootstrap/table.html"


class ResultRMTautaDistanceTable(ResultRMDistanceTable):
    l1 = tables.Column(empty_values=(), verbose_name=_('L1'), accessor="l1")

    def render_l1(self, value, record, *args, **kwargs):
        return self._lap_render(value)

    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = ("number", "status") # all_numbers
        sequence = ("result_distance", "number", 'first_name', 'last_name', 'year', 'team', 'bike_brand', 'l1', 'time', 'status')
        empty_text = _("There are no results")
        order_by = ("time", "l1")
        # ordering = ('created')
        per_page = 200
        template = "bootstrap/table.html"


class ResultRMSportsDistanceTable(ResultRMDistanceTable):
    l1 = tables.Column(empty_values=(), verbose_name=_('L1'), accessor="l1")
    l2 = tables.Column(empty_values=(), verbose_name=_('L2'), accessor="l2")
    l3 = tables.Column(empty_values=(), verbose_name=_('L3'), accessor="l3")
    l4 = tables.Column(empty_values=(), verbose_name=_('L4'), accessor="l4")

    def render_l1(self, value, record, *args, **kwargs):
        return self._lap_render(value)

    def render_l2(self, value, record, *args, **kwargs):
        return self._lap_render(value)

    def render_l3(self, value, record, *args, **kwargs):
        return self._lap_render(value)

    def render_l4(self, value, record, *args, **kwargs):
        return self._lap_render(value)

    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = ("number", "status") # all_numbers
        sequence = ("result_distance", "number", 'first_name', 'last_name', 'year', 'team', 'bike_brand', 'l1', 'l2', 'l3', 'l4', 'time', 'status')
        empty_text = _("There are no results")
        order_by = ("time", "l4", "l3", "l2", "l1")
        # ordering = ('created')
        per_page = 200
        template = "bootstrap/table.html"



class ResultRMGroupTable(tables.Table):
    result_group = tables.Column(empty_values=(), verbose_name='#', accessor="result_group")
    first_name = tables.Column(empty_values=(), verbose_name=_('First Name'), accessor="participant.first_name")
    last_name = tables.Column(empty_values=(), verbose_name=_('Last Name'), accessor="participant.last_name")
    year = tables.Column(empty_values=(), verbose_name=_('Year'), accessor="participant.birthday.year", order_by="participant.birthday")
    team = tables.Column(empty_values=(), verbose_name=_('Team'), accessor="participant.team")
    bike_brand = tables.Column(empty_values=(), verbose_name=_('Bike Brand'), accessor="participant.bike_brand2")
    time = tables.Column(empty_values=(), verbose_name=_('Time'), accessor="time")
    group = tables.Column(empty_values=(), verbose_name=_('Group'), accessor="participant.group")

    def render_last_name(self, record):
        text = strip_tags(record.participant.last_name)
        if record.leader:
            text += LEADER_TOOLTIP % (record.leader.color, record.leader.text)
        return mark_safe(text)


    def render_bike_brand(self, record):
        if record.participant.bike_brand2:
            return record.participant.bike_brand2
        else:
            return '-'

    def render_team(self, record, *args, **kwargs):
        if record.participant.team:
            return mark_safe('<a href="#">%s</a>' % record.participant.team)
        elif record.participant.team_name:
            return '%s' % record.participant.team_name
        else:
            return '-'

    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = ("number", "status") # all_numbers
        sequence = ("result_group", "number", 'first_name','last_name', 'year', 'team', 'bike_brand', 'time', 'group', 'status')
        empty_text = _("There are no results")
        order_by = ("time")
        # ordering = ('created')
        per_page = 200
        template = "bootstrap/table.html"
