from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404, HttpResponse, HttpResponseNotAllowed
from django.template import loader
from django.urls import reverse_lazy
from django.template.defaultfilters import slugify
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from itertools import chain
from django.views import View, generic

from django.conf import settings
import json
from .models import Snippet, Tag, Langage, User, GroupTags

#List autoriser de tag en fonction du group de l'utilisateur
def tagsall(request): 
    user = request.user
    queryset = Tag.objects.all()
    if request.user.is_authenticated:
        if GroupTags.objects.filter(user = user).exists():
            group = GroupTags.objects.filter(user = user)
            queryset = queryset.filter(grouptags__user = user)
    queryset = queryset.distinct()
    return queryset

#List de snippet en fonction des tags autoriser 
def snippetall(request):
    snippetall = Snippet.objects.filter(tag__in = tagsall(request)).distinct()
    return snippetall

#Context du base.html
def contextbase(request):
    tags_list = tagsall(request)
    langages_list = Langage.objects.order_by("-nom")
    utilisateur = request.user.username
    context = {
        "tags_list" : tags_list,
        "utilisateur" : utilisateur,
        "langages_list" : langages_list,
    }
    if request.user.is_authenticated:
            group = GroupTags.objects.filter(user = request.user)
            context["verifgroup"] = bool(group)
    return context

class SnippetListView(LoginRequiredMixin, generic.ListView):
    """
    **Fonction :**

    Index comportant la liste de :model:`gestion.Snippet` 

    Barre de recherche globale gerer par :view:`gestion.views.Recherche`

    **Template**

    :template:`gestion/index.html`

    **Lien**

    :template:`gestion.base.html`

    snippet -> :view:`gestion.views.SnippetDetailView`
    """
    model = Snippet
    template_name = "gestion/index.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(object_list=snippetall(self.request),**kwargs) 
        context.update(contextbase(self.request))
        return context
         
class SnippetViaTag(LoginRequiredMixin, View): 
    """
    **Fonction:**

    Liste des :model:`gestion.Snippet` par :model:`gestion.Tag`

    **Template**

    :template:`gestion/snippet_tags.html`

    **Lien**

    :template:`gestion.base.html`

    snippet -> :view:`gestion.views.SnippetDetailView`
    """
    def get(self, request, tags_nom):
        context = contextbase(request)
        tags = get_object_or_404(Tag, nom = tags_nom)
        context['tags'] = tags
        snippet_tags = snippetall(request).filter(tag = tags)
        context['snippet_tags'] = snippet_tags
        return render(request, "gestion/snippet_tags.html", context)

class SnippetViaLangage(LoginRequiredMixin, View):
    """
    **Fonction:**

    Liste des :model:`gestion.Snippet` par :model:`gestion.Snippet` 

    **Template**
    
    :template:`gestion/snippet_langage.html`
    
    **Lien**

    :template:`gestion.base.html`

    snippet -> :view:`gestion.views.SnippetDetailView`
    """ 
    def get(self, request, langages_nom):
        context = contextbase(request)
        langages = get_object_or_404(Langage, nom = langages_nom)
        context["langages"] = langages
        snippet_langages = snippetall(request).filter(langage = langages)
        context["snippet_langages"] = snippet_langages
        return render(request, "gestion/snippet_langage.html",context)

class SnippetViaAuteur(LoginRequiredMixin, View): 
    """
    **Fonction:**

    Liste des :model:`gestion.Snippet` que l'utilisateur à crée

    **Template**
    
    :template:`gestion/snippet_utilisateur.html`

    **Lien**

    :template:`gestion.base.html`

    snippet -> :view:`gestion.views.SnippetDetailView`
    """
    def get(self, request, user_nom):
        context = contextbase(request)
        user = get_object_or_404(User, username = user_nom) 
        context["user"] = user
        createur = user.username
        context["createur"] = createur
        snippets_auteur = snippetall(request).filter(user = user)
        context["snippets_auteur"] = snippets_auteur
        return render(request, "gestion/snippet_utilisateur.html",context)


class SnippetDetailView(generic.DetailView):
    """
    **Fonction:**

    Details d'un snippet avec nom,description,code,tags,langage,auteur

    **Template**

    :template:`gestion/snippet_detail`

    **Lien**

    :template:`gestion.base.html`

    Auteur -> :view:`gestion.views.SnippetViaAuteur`

    langage -> :view:`gestion.views.SnippetViaLangage`

    tags -> :view:`gestion.views.SnippetViaTag`
    """
    def get(self, request, slug):
        context = contextbase(request)
        snippet = get_object_or_404(Snippet, slug=slug)
        context["snippet"] = snippet
        if snippet.statut == False :
            if not request.user.is_authenticated:
                return redirect('gestion:connexion')
        tags_snippet = tagsall(request).filter(snippets = snippet)
        context["tags_snippet"] = tags_snippet
        permiUser = snippet.userpermission.all()
        context["permiUser"] = permiUser
        return render(request, "gestion/snippet_detail.html", context)

     
class RechercheTag(LoginRequiredMixin, View):  

    def get(self, request):
        context = contextbase(request)
        nomTags = request.GET.get('rechercheTags')

        if nomTags is not None:
            tags_list_result = tagsall(request).filter(nom__icontains = nomTags)
        
        context["tags_list_result"] = tags_list_result

        hx_request = request.headers.get("Hx-Request")
        if hx_request:
            return render(request, "gestion/rechercheTag.html", context)
            
        return redirect('gestion:index')


class RechercheGlo(LoginRequiredMixin, View):  
    """
    **Fonction:**

    -Fonction de recherche pour les tags // Pour la recherche global

    **Template**

    :template:`gestion/base.html` //
    :template:`gestion/index.html`

   **Lien**

    :template:`gestion.base.html`
 
    Depends de la reponse 

    """
    def get(self, request):
        context = contextbase(request)
        snippet = snippetall(request)
        recherche = request.GET.get('rechercheGlobal')
        context["recherche"] = recherche

        if recherche is not None:
            reponseRecherche = list(chain())
           
            if Tag.objects.filter(nom__icontains = recherche):
                tagG = tagsall(request).filter(nom__icontains = recherche)
                context["tagG"] = tagG
                reponseRecherche = reponseRecherche + list(chain(tagG))

            if Snippet.objects.filter(nom__icontains = recherche):
                sNomG = snippet.filter(nom__icontains = recherche)
                context["sNomG"] = sNomG
                reponseRecherche = reponseRecherche + list(chain(sNomG))
                
            if Snippet.objects.filter(description__icontains = recherche):
                sdescriptionG = snippet.filter(description__icontains = recherche)
                context["sdescriptionG"] = sdescriptionG
                reponseRecherche = reponseRecherche + list(chain(sdescriptionG))
                
            if Snippet.objects.filter(code__icontains = recherche):
                sCodeG = snippet.filter(code__icontains = recherche)
                context["sCodeG"] = sCodeG
                reponseRecherche = reponseRecherche + list(chain(sCodeG))
                
            if Langage.objects.filter(nom__icontains = recherche):
                langageG = Langage.objects.filter(nom__icontains = recherche)
                context["langageG"] = langageG
                reponseRecherche = reponseRecherche + list(chain(langageG))
                
            if User.objects.filter(username__icontains = recherche):
                userG = User.objects.filter(username__icontains = recherche)
                context["userG"] = userG
                reponseRecherche = reponseRecherche + list(chain(userG))
            
            reponseRecherche = list(set(reponseRecherche))
            paginator = Paginator(reponseRecherche, 15)
            pagerep_number = request.GET.get("page")
            paginator_global = paginator.get_page(pagerep_number)
            
            context["paginator_global"] = paginator_global
                
        hx_request = request.headers.get("Hx-Request")
        if hx_request:
            return render(request, "gestion/rechercheGlo.html", context)
            
        return render(request, "gestion/index.html", context)


class Autocompletion(LoginRequiredMixin, View): 
    def get(self, request):
        list_tags = [t.nom for t in tagsall(request)]
        if "nom" in request.GET:
            nom = request.GET.get('nom')
            list_tags = tagsall(request).filter(nom__istartswith = nom)
            list_tags = [t.nom for t in list_tags]
            tags = json.dumps(list_tags)
        return HttpResponse(tags)


class Ajouter(LoginRequiredMixin, View): 
    """
    **Fonction:**

    Ajout d'un snippet 

    Utilisateur, date et slug son ajouter automatiquement 

    Si la longueur d'une reponse est inferieur à 5 on renvoie une erreur 

    **Template**

    :template:`gestion/snippet_form.html`

    **Redirect**

    :view:`gestion.views.SnippetListView`

    **Lien**

    :template:`gestion/base.html`

    """
    def post(self,request):
        context = contextbase(request)
        snippet_nom = request.POST.get('nom')
        description = request.POST.get('description')
        code = request.POST.get('code')
        tags_saisie = request.POST.get('listtags')
        langage = request.POST.get('langage')
        statut = request.POST.get('statut') 
        permiUser = request.POST.getlist('permissionUser')
        permiUser.append(request.user.username)
        if statut == 'on':
            sta = True
        else:
            sta = False
        tags_add = tags_saisie.split(',')
        if len(snippet_nom) < 5:
            erreurs1 = "!Le nom du snippet est trop court"
            context["erreurs1"] = erreurs1
        if len(description) < 5:
            erreurs2 = "!La description est trop courte"
            context["erreurs2"] = erreurs2
        if len(code) < 5:
            erreurs3 = "!Le code est trop court"
            context["erreurs3"] = erreurs3
        if langage == 'None':
            erreurs4 = "!Veuillez renseigner le language de vôtre code"
            context["erreurs4"] = erreurs4
        for k in context:
            if k.startswith('erreurs'):
                return render(request, "gestion/snippet_form.html", context)
        la = Langage.objects.get(nomCodeMirror__icontains=langage)
        s = Snippet(nom=snippet_nom, description=description, code=code, date_ajout=timezone.now(), langage=la, statut=sta, user=request.user)
        s.save()
        for p in permiUser:
            print(p)
            pUser = User.objects.get(username__icontains = p)
            s.userpermission.add(pUser)
        for t in tags_add:
            t = t.strip()
            if len(t) < 2:
                continue
            if Tag.objects.filter(nom__icontains=t).exists():
                ta = Tag.objects.get(nom__icontains=t)
                s.tag_set.add(ta)
            else:
                ta = Tag(nom=t, date_ajout=timezone.now())
                ta.save()
                s.tag_set.add(ta)
        context["snippet"] = s
        return redirect('gestion:detail', s.slug)
 
    def get(self, request):
        context = contextbase(request)
        permissionUser = User.objects.exclude(username = request.user.username)
        langages = Langage.objects.all()
        context["langages"] = langages
        context["permissionUser"] = permissionUser
        group = GroupTags.objects.filter(user = request.user)
        verifgroup = bool(group)
        context["verifgroup"] = verifgroup
        if verifgroup == False:
            return render(request, "gestion/snippet_form.html", context)
        return redirect('gestion:index')

class Connexion(View):
    """
    **Fonction:**

    Authentification

    **Redirecrion**

    :view:`gestion.views.SnippetListView`
    """
    def get(self, request):
        return render(request, "gestion/login.html")

    def post(self, request):
        nom = request.POST.get('username')
        mdp = request.POST.get('password')
        user = authenticate(request, username=nom, password=mdp)
        if user is not None:
            login(request, user)
            return redirect('gestion:index')
        else:
            erreurs = "! l'authentification n'est pas correct !"
            context = {
            "erreurs" : erreurs,
            }
            return render(request, "gestion/login.html", context)
    
class Deconnexion(View):
    """
    **Fonction:**

    Deconnexion

    **Redirection**

    :view:`gestion.views.Connexion` 
    """
    def get(sel, request):
        logout(request)
        return redirect('gestion:connexion')

class SnippetDeleteView(LoginRequiredMixin, generic.DeleteView):
    """
    Supprimer le snippet

    **Template**

    :template:`gestion/snippet_detail.html`

    **Redirect**

    :view:`gestion.views.SnippetListView` 

    **Lien**

    :template:`gestion/base.html`
    """
    model = Snippet
    success_url = reverse_lazy('gestion:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context.update(contextbase(self.request))
        return context
   
class Modifier(LoginRequiredMixin, View):
    """
    **Fonction:**

    modifier un snippet

    **Template**

    :template:`gestion/modifier.html`

    **Redirect**
    
    :view:`gestion.views.SnippetDetailsView`  

    **Lien**

    :template:`gestion/base.html`
    """
    def post(self, request, slug):
        context = contextbase(request)
        snippet = get_object_or_404(Snippet, slug=slug)
        permiUser = snippet.userpermission.all()
        context["permiUser"] = permiUser
        snippet.nom = request.POST.get('nom')
        snippet.description = request.POST.get('description')
        snippet.code = request.POST.get('code')
        snippet.date_maj = timezone.now()
        langage = request.POST.get('langage')
        snippet.langage = Langage.objects.get(nomCodeMirror = langage)
        print(snippet.langage)
        tags_saisie = request.POST.get('listtags')
        tags_add = tags_saisie.split(',')
        for t in tags_add:
            t = t.strip()
            if len(t) < 2:
                continue
            if Tag.objects.filter(nom__icontains=t).exists():
                ta = Tag.objects.get(nom__icontains=t)
                snippet.tag_set.add(ta)
            else:
                ta = Tag(nom=t, date_ajout=timezone.now())
                ta.save()
                snippet.tag_set.add(ta)
        snippet.save()
        return redirect('gestion:detail', snippet.slug)
    
   
    def get(self, request, slug):
        context = contextbase(request)
        snippet = get_object_or_404(Snippet, slug=slug)
        tags_snippet = snippet.tag_set.all()
        permissionUser = User.objects.exclude(username = request.user.username)
        permiUser = snippet.userpermission.all()
        langages = Langage.objects.exclude(nom = snippet.langage.nom)
        context['langages'] = langages
        context["permiUser"] = permiUser
        context["permissionUser"] = permissionUser
        context["tags_snippet"] = tags_snippet
        context['snippet'] = snippet
        for p in permissionUser: 
            if p or request.user == snippet.user:
                return render(request, "gestion/modifier.html", context)
        return redirect('gestion:index')


class Rss(View):
    """
    **Fonction:**

    Flux Rss
    """
    def get(self, request):
        snippets = Snippet.objects.order_by("-date_ajout")[:10]
        context = {
            "snippets" : snippets,
            "settings" : settings
        }
        return render(request, "gestion/flux.xml", context)
