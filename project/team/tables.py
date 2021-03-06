from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
import django_tables2 as tables
from team.models import Team
from django.utils.translation import ugettext, ugettext_lazy as _
from django_tables2.utils import A


class TeamTable(tables.Table):
    def render_title(self, record, **kwargs):
        url = reverse('competition:team', kwargs={'pk': self.request_kwargs.get('pk'), 'pk2': record.id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.title))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.request_kwargs = kwargs.pop('request_kwargs', None)
        super(TeamTable, self).__init__(*args, **kwargs)

    class Meta:
        model = Team
        attrs = {"class": "table table-striped table-hover"}
        fields = ("is_featured", "title", "country", "contact_person")
        empty_text = _("There are no teams")
        per_page = 200
        template = "bootstrap/table.html"


class TeamMyTable(tables.Table):
    title = tables.LinkColumn('accounts:team', args=[A('id')])
    competition = tables.Column(verbose_name=_('Competition'), accessor='distance.competition.get_full_name', order_by='distance.competition.name')
    apply = tables.Column(verbose_name=" ", empty_values=())

    def render_apply(self, record, **kwargs):
        if record.distance.competition.params.get('teams_should_apply', False):
            return mark_safe("<a href='%s'>%s</a>" % (reverse('accounts:team_apply_list', kwargs={'pk2': record.id}), ugettext('Apply')))
        else:
            return ''

    class Meta:
        model = Team
        attrs = {"class": "table table-striped table-hover"}
        fields = ("title", "is_featured", "distance")
        sequence = ("title", "competition", "distance", "is_featured", "apply")
        empty_text = _("You haven't created any official team.")
        order_by = ("-id")
        per_page = 20
        template = "bootstrap/table.html"
