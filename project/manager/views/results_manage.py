from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.utils.text import slugify
from django.views.generic import UpdateView, TemplateView
from extra_views import NamedFormsetsMixin, UpdateWithInlinesView, InlineFormSet, CreateWithInlinesView
from core.formsets import CustomBaseInlineFormSet
from manager.forms import ResultListSearchForm, ResultForm, ManageLapResultForm, UrlSyncForm
from manager.pdfreports import PDFReports
from manager.tables import ManageResultTable
from manager.tables.tables import UrlSyncTable
from manager.views.participant_manage import ManagerPermissionMixin
from results.models import Result, LapResult, UrlSync
from velo.mixins.views import SingleTableViewWithRequest, SetCompetitionContextMixin, RequestFormKwargsMixin


__all__ = ['ManageResultList', 'ManageResultUpdate', 'ManageResultCreate', 'ManageResultReports', 'ManageUrlSyncList', 'ManageUrlSyncUpdate']


class ManageResultList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Result
    table_class = ManageResultTable
    template_name = 'manager/table.html'

    def get_context_data(self, **kwargs):
        context = super(ManageResultList, self).get_context_data(**kwargs)
        context.update({'search_form': ResultListSearchForm(request=self.request, competition=self.competition)})
        return context

    def get_queryset(self):
        queryset = super(ManageResultList, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        query_attrs = self.request.GET

        if query_attrs.get('distance'):
            queryset = queryset.filter(participant__distance_id=query_attrs.get('distance'))

        if query_attrs.get('group'):
            queryset = queryset.filter(participant__group=query_attrs.get('group'))

        if query_attrs.get('status'):
            queryset = queryset.filter(status=query_attrs.get('status'))

        if query_attrs.get('number'):
            try:
                number = int(query_attrs.get('number'))
                queryset = queryset.filter(participant__primary_number__number=number)
            except ValueError:
                messages.error(self.request, 'In number field you can enter only number')

        if query_attrs.get('search'):
            slug = slugify(query_attrs.get('search'))
            queryset = queryset.filter(
                Q(participant__slug__icontains=slug) |
                Q(participant__ssn__icontains=query_attrs.get('search'))
            )

        return queryset.select_related('competition', 'participant', 'number', 'participant__distance')


class ManagLapResultInline(InlineFormSet):
    can_order = False
    model = LapResult
    form_class = ManageLapResultForm
    extra = 0
    formset_class = CustomBaseInlineFormSet

    def get_extra_form_kwargs(self):
        kwargs = super(ManagLapResultInline, self).get_extra_form_kwargs()
        kwargs.update({'request': self.request})
        kwargs.update({'request_kwargs': self.kwargs})
        return kwargs

    def get_formset_kwargs(self):
        kwargs = super(ManagLapResultInline, self).get_formset_kwargs()
        kwargs.update({'empty_form_class': self.form_class})
        return kwargs




class ManageResultUpdate(ManagerPermissionMixin, SetCompetitionContextMixin, RequestFormKwargsMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    pk_url_kwarg = 'pk2'
    model = Result
    template_name = 'manager/form.html'
    form_class = ResultForm
    inlines = [ManagLapResultInline, ]
    inlines_names = ['lap']

    def get_success_url(self):
        return reverse('manager:result_list', kwargs={'pk': self.kwargs.get('pk')})


class ManageResultCreate(ManagerPermissionMixin, SetCompetitionContextMixin, RequestFormKwargsMixin, NamedFormsetsMixin, CreateWithInlinesView):
    pk_url_kwarg = 'pk2'
    model = Result
    template_name = 'manager/form.html'
    form_class = ResultForm
    inlines = [ManagLapResultInline, ]
    inlines_names = ['lap']

    def get_success_url(self):
        messages.success(self.request, 'Result created. Update it if required.')
        return reverse('manager:result', kwargs={'pk': self.kwargs.get('pk'), 'pk2': self.object.id})


class ManageResultReports(ManagerPermissionMixin, SetCompetitionContextMixin, TemplateView):
    template_name = 'manager/result_reports.html'

    def post(self, request, *args, **kwargs):
        pdf_class = PDFReports(competition=self.set_competition(kwargs.get('pk')))

        action = request.POST.get('action')

        if action == 'results_groups':
            pdf_class.results_groups()
        elif action == 'results_groups_top20':
            pdf_class.results_groups(20)
        elif action == 'results_gender':
            pdf_class.results_gender()
        elif action == 'results_distance':
            pdf_class.results_distance()
        elif action == 'results_distance_top20':
            pdf_class.results_distance(20)
        elif action == 'results_standings':
            pdf_class.results_standings()
        elif action == 'results_standings_top20':
            pdf_class.results_standings(20)
        elif action == 'results_standings_groups':
            pdf_class.results_standings_groups()
        elif action == 'results_standings_groups_top20':
            pdf_class.results_standings_groups(20)
        elif action == 'results_team':
            pdf_class.results_team()
        elif action == 'results_team_standings':
            pdf_class.results_team_standings()
        else:
            raise Http404

        file_obj = pdf_class.build()

        response = HttpResponse(mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s.pdf' % action
        response.write(file_obj.getvalue())
        file_obj.close()
        return response


class ManageUrlSyncList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = UrlSync
    table_class = UrlSyncTable
    template_name = 'manager/table.html'


class ManageUrlSyncUpdate(ManagerPermissionMixin, SetCompetitionContextMixin, RequestFormKwargsMixin, UpdateView):
    pk_url_kwarg = 'pk2'
    model = UrlSync
    template_name = 'manager/participant_form.html'
    form_class = UrlSyncForm

    def get_success_url(self):
        return reverse('manager:urlsync', kwargs={'pk': self.kwargs.get('pk')})

