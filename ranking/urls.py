from django.urls import path
from . import views

app_name = 'ranking'

urlpatterns = [
    # Multi-step create flow
    path('create/step-1/', views.create_project_step1, name='project_step1'),
    path('create/step-2/', views.create_project_step2, name='project_step2'),
    path('create/step-3/', views.create_project_step3, name='project_step3'),
    path('create/step-2/ajax-add/', views.ajax_add_search_engine, name='ajax_add_search_engine'),
    path('ajax/delete-search-engine/', views.ajax_delete_search_engine, name='ajax_delete_search_engine'),
    path('ajax/add-keyword/', views.ajax_add_keyword, name='ajax_add_keyword'),
    path('ajax/delete-keyword/', views.ajax_delete_keyword, name='ajax_delete_keyword'),




    # Other views
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path("project/<int:project_id>/report/", views.project_report, name="project_report"),
    path('projects/<int:project_id>/upload-rankings/', views.upload_rankings, name='upload_rankings'),


    path('reports/', views.ranking_reports, name='reports'),  
    path('project/<int:project_id>/fetch-rankings/', views.fetch_rankings, name='fetch_rankings'),
    path("project/<int:project_id>/ranking-report/", views.project_ranking_pdf_report, name="project_ranking_pdf_report"),

    path('generatereport/', views.generate_baseline_report, name='generate_report'),

# Placeholder view
]
