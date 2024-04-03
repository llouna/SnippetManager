from django.urls import path, re_path
from . import views


app_name = "gestion"
urlpatterns = [
    path("connexion/", views.Connexion.as_view(), name="connexion"),
    path("deconnexion", views.Deconnexion.as_view(), name="deconnexion"),
    path("", views.SnippetListView.as_view(), name="index"),
    path("supprimer/<slug:slug>/", views.SnippetDeleteView.as_view(), name="supprimer"),
    path("modifier/<slug:slug>/", views.Modifier.as_view(), name="modifier"),
    re_path("rechercheGlo/", views.RechercheGlo.as_view(), name="rechercheGlo"),
    re_path("rechercheTag/", views.RechercheTag.as_view(), name="rechercheTag"),
    path("snippet/detail/<slug:slug>/", views.SnippetDetailView.as_view(), name="detail"),
    path("snippet/add/", views.Ajouter.as_view(), name="ajouter"),
    path("snippet/tags/<tags_nom>/", views.SnippetViaTag.as_view(), name="viaTags"),
    path("snippet/langages/<langages_nom>/", views.SnippetViaLangage.as_view(), name="viaLangages"),
    path("snippet/auteur/<user_nom>/", views.SnippetViaAuteur.as_view(), name="viaAuteur"),
    re_path("auto/", views.Autocompletion.as_view(), name="autocomplition"),
    path("rss/", views.Rss.as_view(), name="rss"),
]