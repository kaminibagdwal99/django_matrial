from django.shortcuts import render, redirect

from .forms import RankingProjectForm, SearchEngineFormSet, KeywordFormSet
from .models import RankingProject, SearchEngine, Keyword, RankingSnapshot

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import random
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
import os
from django.conf import settings
import pandas as pd




from django.views.decorators.http import require_POST
from .utils import get_rank_using_google_cse, get_ranks_for_multiple_keywords 

from .utils import get_ranks_for_multiple_keywords
from .models import Keyword, RankingSnapshot
from datetime import date





def update_project_rankings(project):
    keywords = Keyword.objects.filter(project=project)
    domain = project.url.replace("https://", "").replace("http://", "").strip("/")
    keyword_list = [k.keyword for k in keywords]
    region = SearchEngine.objects.filter(project= project)

    ranks = get_ranks_for_multiple_keywords(keyword_list, target_domain=domain)

    for kw in keywords:
        rank = ranks.get(kw.keyword)
        if rank is not None:
            RankingSnapshot.objects.create(
                keyword=kw,
                date=date.today(),
                position=rank
            )


@require_POST
def fetch_rankings(request, project_id):
    try:
        project = get_object_or_404(RankingProject, id=project_id)
        
        update_project_rankings(project)
        return JsonResponse({"success": True})
    except Exception as e:
        import traceback
        print("Error in fetch_rankings:", traceback.format_exc())  # This will help you debug
        return JsonResponse({"success": False, "error": str(e)})


def create_project_step1(request):

    if request.method == 'POST':
        form = RankingProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            request.session['project_id'] = project.id
            return redirect('ranking:project_step2')
        else:
            # ✅ Print form errors to console
            print("Project form errors:", form.errors)
    else:
        request.session.pop('project_id', None)

        form = RankingProjectForm()

    return render(request, 'ranking/create_project_step1.html', {
        'form': form,
        'step': "project_step1"
    })


def create_project_step2(request):
    project_id = request.session.get('project_id')
    if not project_id:
        return redirect('ranking:project_step1')

    if request.method == 'POST':
        formset = SearchEngineFormSet(request.POST, queryset=SearchEngine.objects.none())
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    search_engine = form.save(commit=False)
                    search_engine.project_id = project_id
                    search_engine.save()
            return redirect('ranking:project_step3')
    else:
        formset = SearchEngineFormSet(queryset=SearchEngine.objects.none())
    return render(request, 'ranking/create_project_step2.html', {
        'formset': formset,
        'step': "project_step2"
    })

def create_project_step3(request):
    project_id = request.session.get('project_id')
    if not project_id:
        return redirect('ranking:project_step1')

    if request.method == 'POST':
        formset = KeywordFormSet(request.POST, queryset=Keyword.objects.none())
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    keyword = form.save(commit=False)
                    keyword.project_id = project_id
                    keyword.save()
            del request.session['project_id']
            return redirect('ranking:project_list')
    else:
        formset = KeywordFormSet(queryset=Keyword.objects.none())
    return render(request, 'ranking/create_project_step3.html', {
        'formset': formset,
        'step': "project_step3"
    })


def project_list(request):
    projects = RankingProject.objects.all().order_by('-created_at')
    return render(request, 'ranking/project_list.html', {'projects': projects})

def ranking_reports(request):
    return render(request, 'ranking/reports.html')  # Placeholder for now


@require_POST
def ajax_delete_search_engine(request):
    engine_id = request.POST.get('engine_id')
    try:
        engine = SearchEngine.objects.get(id=engine_id)
        engine.delete()
        return JsonResponse({'success': True})
    except SearchEngine.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Search engine not found'})

def ajax_add_search_engine(request):
    if request.method == "POST":
        project_id = request.session.get('project_id')
        if not project_id:
            return JsonResponse({'success': False, 'error': 'No project in session'})

        try:
            project = RankingProject.objects.get(id=project_id)
            name = request.POST.get('name')
            country = request.POST.get('country')
            language = request.POST.get('language')

            engine = SearchEngine.objects.create(
                project=project,
                name=name,
                country=country,
                language=language
            )

            return JsonResponse({
                'success': True,
                'engine': {
                    'name': engine.name,
                    'country': engine.country,
                    'language': engine.language
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid method'})

@require_POST
def ajax_add_keyword(request):
    project_id = request.session.get('project_id')
    if not project_id:
        return JsonResponse({'success': False, 'error': 'No project in session'})

    keyword_text = request.POST.get('keyword')
    if not keyword_text:
        return JsonResponse({'success': False, 'error': 'Keyword is required'})

    keyword = Keyword.objects.create(project_id=project_id, keyword=keyword_text)
    return JsonResponse({'success': True, 'keyword': {'id': keyword.id, 'keyword': keyword.keyword}})

@require_POST
def ajax_delete_keyword(request):
    keyword_id = request.POST.get('keyword_id')
    try:
        keyword = Keyword.objects.get(id=keyword_id)
        keyword.delete()
        return JsonResponse({'success': True})
    except Keyword.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Keyword not found'})



def project_detail(request, project_id):
    project = get_object_or_404(RankingProject, id=project_id)

    metrics = [
        {
            "label": "Organic Traffic",
            "value": 677,
            "change": -470,
            "change_type": "danger",
            "icon": "trending_down"
        },
        {
            "label": "Organic Keywords",
            "value": "6.9K",
            "change": -185,
            "change_type": "danger",
            "icon": "key"
        },
        {
            "label": "Referring Domains",
            "value": 336,
            "change": None,
            "icon": "link"
        },
        {
            "label": "Search Visibility",
            "value": "0%",
            "change": None,
            "icon": "visibility"
        },
        {
            "label": "Health Score",
            "value": "Updating",
            "change": None,
            "icon": "health_and_safety"
        },
    ]

    # Dummy chart data
    chart_data = {
        "labels": ["Jul 1", "Jul 8", "Jul 15", "Jul 22", "Jul 29"],
        "keyword_trend": [50, 62, 75, 60, 80],
        "traffic_trend": [200, 220, 190, 250, 260],
    }

    keywords = Keyword.objects.filter(project=project)
    search_engines = SearchEngine.objects.filter(project=project)

    return render(request, "ranking/project_detail.html", {
        "project": project,
        "metrics": metrics,
        "chart_data": chart_data,
        "keywords": keywords,
        "search_engines": search_engines
    })




from collections import defaultdict

def project_report(request, project_id):
    project = get_object_or_404(RankingProject, id=project_id)
    keywords = Keyword.objects.filter(project=project)
    engines = SearchEngine.objects.filter(project=project)

    snapshots = RankingSnapshot.objects.filter(keyword__in=keywords).order_by('date')

    unique_dates = sorted(set(s.date for s in snapshots))
    chart_labels = [d.strftime('%Y-%m-%d') for d in unique_dates]

    keyword_data_map = defaultdict(dict)  # engine_name -> { keyword -> [positions] }
    chart_data = {}  # engine_name -> chart config

    for engine in engines:
        engine_label = f"{engine.name} {engine.country}"
        engine_keywords = {}
        datasets = []

        for kw in keywords:
            trend = []
            for d in unique_dates:
                snap = RankingSnapshot.objects.filter(keyword=kw, search_engine=engine, date=d).first()
                trend.append(snap.position if snap else None)
            engine_keywords[kw.keyword] = trend

        # Sort keywords by latest known rank
        sorted_kw = sorted(engine_keywords.items(), key=lambda item: next((v for v in reversed(item[1]) if v is not None), float('inf')))
        sorted_kw_dict = dict(sorted_kw)

        keyword_data_map[engine_label] = sorted_kw_dict

        # Chart datasets
        colors = ['#5e72e4', '#2dce89', '#f5365c', '#fb6340', '#11cdef']
        datasets = [
            {
                "label": kw,
                "data": trend,
                "borderColor": colors[i % len(colors)],
                "backgroundColor": "transparent",
                "tension": 0.4
            }
            for i, (kw, trend) in enumerate(sorted_kw_dict.items())
        ]

        chart_data[engine_label] = {
            "labels": chart_labels,
            "datasets": datasets
        }

    return render(request, "ranking/project_rankings.html", {
        "project": project,
        "chart_data": chart_data,
        "keyword_data_map": dict(keyword_data_map)
    })






import pandas as pd
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import RankingProject, Keyword, SearchEngine, RankingSnapshot
from datetime import datetime

def upload_rankings(request, project_id):
    if request.method == "POST" and request.FILES.get("ranking_file"):
        file = request.FILES["ranking_file"]
        project = get_object_or_404(RankingProject, id=project_id)

        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file, engine="openpyxl")

            df.columns = [col.strip() for col in df.columns]
            date_columns = [col for col in df.columns if col not in ["Keyword", "Engine"]]

            print("📊 Parsed Columns:", df.columns.tolist())
            print("📆 Date Columns:", date_columns)

            created_count = 0

            for _, row in df.iterrows():
                keyword_text = str(row["Keyword"]).strip()
                engine_name = str(row["Engine"]).strip()

                keyword_obj = Keyword.objects.filter(project=project, keyword__iexact=keyword_text).first()
                if not keyword_obj:
                    print(f"❌ Keyword not found in DB: '{keyword_text}'")
                    continue

                engine_obj = SearchEngine.objects.filter(project=project, name__iexact=engine_name).first()
                if not engine_obj:
                    print(f"❌ Engine not found in DB: '{engine_name}'")
                    continue

                for date_str in date_columns:
                    try:
                        date_obj = datetime.strptime(date_str.strip(), "%b-%d-%Y").date()
                        position_val = row[date_str]

                        if pd.isna(position_val) or str(position_val).strip() in ["-", ""]:
                            continue

                        position_int = int(position_val)
                        _, created = RankingSnapshot.objects.update_or_create(
                            keyword=keyword_obj,
                            search_engine=engine_obj,
                            date=date_obj,
                            defaults={"position": position_int}
                        )

                        if created:
                            created_count += 1

                    except Exception as e:
                        print(f"[!] Failed on: {keyword_text}, {engine_name}, {date_str}, Error: {e}")
                        continue

            messages.success(request, f"✅ {created_count} ranking entries uploaded successfully.")

        except Exception as e:
            messages.error(request, f"Error uploading file: {e}")

    return redirect("ranking:project_detail", project_id=project_id)





def calculate_change(jul_02, jul_30):
    try:
        if jul_02 == '-' or jul_30 == '-':
            return '-'
        return int(jul_02) - int(jul_30)
    except:
        return '-'

from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
import os
from django.conf import settings

def link_callback(uri, rel):
    path = finders.find(uri.replace(settings.STATIC_URL, ""))
    if path:
        return path
    return uri


def generate_baseline_report(request):
    rankings = {
        "Google Singapore": [
            {"keyword": "mole and wart removal near me", "jul_02": 2, "jul_30": 1},
            {"keyword": "wart mole removal", "jul_02": 1, "jul_30": 2},
            {"keyword": "wart mole ", "jul_02": 13, "jul_30": 20},
            {"keyword": "laser pigmentation treatment", "jul_02": 21, "jul_30": 31},
        ],
        "Yahoo Singapore": [
            {"keyword": "skin tag removal singapore gp", "jul_02": "41", "jul_30": "39"},
            {"keyword": "laser pigmentation treatment", "jul_02": "-", "jul_30": "-"},
        ]
    }

    # Add 'change' and 'logo_filename' fields
    for engine, rows in rankings.items():
        logo_name = engine.lower().replace(" singapore", "-logo") + ".jpg"  # e.g., google-singapore.png
        for row in rows:
            row["change"] = calculate_change(row["jul_02"], row["jul_30"])
        rankings[engine] = {
            "logo": logo_name,
            "rows": rows
        }
    print("logo_name is " , logo_name)

    context = {
        "site_url": "https://www.limclinicandsurgery.com/",
        "date_range": "JUL-02 2025 - JUL-31 2025",
        "generated_on": datetime.datetime.now().strftime("%b-%d %Y"),
        "company_name": "Webplause Technology Pvt. Ltd.",
        "rankings": rankings,
    }

    html = render_to_string("ranking/ranking_report_template.html", context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Baseline-Report.pdf"'
    pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    return response

from collections import defaultdict
from django.utils import timezone

def get_rank_change(old, new):
    if old is None or new is None:
        return None
    return old - new

from collections import defaultdict
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa

def project_ranking_pdf_report(request, project_id):
    project = get_object_or_404(RankingProject, id=project_id)
    keywords = Keyword.objects.filter(project=project)
    search_engines = SearchEngine.objects.filter(project=project)

    snapshots = RankingSnapshot.objects.filter(keyword__in=keywords).order_by("date")

    # Get last 2 unique dates
    unique_dates = sorted(set(s.date for s in snapshots))
    if len(unique_dates) < 2:
        return HttpResponse("Not enough data for report.")

    date1 = unique_dates[-2]
    date2 = unique_dates[-1]

    snapshot_map = {}
    for s in snapshots:
        snapshot_map[(s.keyword_id, s.search_engine_id, s.date)] = s.position

    rankings = defaultdict(lambda: {"logo": "", "rows": []})

    for engine in search_engines:
        engine_label = f"{engine.name} {engine.country}"
        logo = f"{engine.name.lower().replace(' ', '-')}-logo.jpg"

        rows = []
        for keyword in keywords:
            rank1 = snapshot_map.get((keyword.id, engine.id, date1))
            rank2 = snapshot_map.get((keyword.id, engine.id, date2))
            change = get_rank_change(rank1, rank2)

            rows.append({
                "keyword": keyword.keyword,
                "rank_date1": rank1 if rank1 is not None else "-",
                "rank_date2": rank2 if rank2 is not None else "-",
                "change": change
            })

        # ✅ Sort rows by rank2 (last date), None/"-" goes to bottom
        def sort_key(row):
            val = row["rank_date2"]
            try:
                return int(val)
            except (TypeError, ValueError):
                return float("inf")  # push "-" to bottom

        rows = sorted(rows, key=sort_key)

        rankings[engine_label]["logo"] = logo
        rankings[engine_label]["rows"] = rows

    context = {
        "date_range": f"{date1.strftime('%b-%d')} - {date2.strftime('%b-%d')}",
        "date1": date1.strftime('%b-%d'),
        "date2": date2.strftime('%b-%d'),
        "generated_on": timezone.now().strftime("%b-%d %Y"),
        "rankings": dict(rankings),
        "project": project,
    }

    html = render_to_string("ranking/ranking_report_template.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{project.name}-ranking-report.pdf"'
    pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    return response
