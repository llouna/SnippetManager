from django.db import models
from django.shortcuts import redirect
from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import slugify 
from django.urls import reverse

class Langage(models.Model):
    """
    Correspond au language informatique de :model:`gestion.Snippet`.
    """
    nom = models.CharField(max_length=100)
    nomCodeMirror = models.CharField(max_length = 100, null=True, help_text="Nom reconnu pour mettre en surbrillance le code en fonction du language pour ajouter un snippet")
    date_ajout =  models.DateTimeField("date d'ajout", auto_now_add = True)

    def __str__(self):
        return self.nom

class User(AbstractUser):
    """
    Utilisateur //
    Peut posséder un groupe avec :model:̀ gestion.GroupTags`
    """
    pass

class Snippet(models.Model):
    """
    Morceau de code associé à :model:`gestion.Tag` et à :model:`gestion.user`//
    Le language est specifier avec :model:`gestion.Langage` 
    """
    nom = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    code = models.TextField()
    statut = models.BooleanField(default=False, verbose_name = "Public" )
    date_ajout =  models.DateTimeField("date d'ajout", auto_now_add = True)
    date_maj = models.DateTimeField("date de modificafion", null=True, blank=True, auto_now_add = True)
    slug = models.SlugField(null=True, unique=True, help_text="Le nom du snippet sans espace et sans accents (pour les urls)")
    langage = models.ForeignKey(Langage, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="createur")
    userpermission = models.ManyToManyField(User)
    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs): 
        """Le slug est crée automatiquement"""
        if not self.slug:
            self.slug = slugify(self.nom)
        return super().save(*args, **kwargs)


class Tag(models.Model):
    """
    Un tag permet de filtrer les snippets
    """
    snippets = models.ManyToManyField(Snippet)
    nom = models.CharField(max_length=50)
    date_ajout =  models.DateTimeField("date d'ajout", auto_now_add=True)
    
    def __str__(self):
        return self.nom

class GroupTags(models.Model):
    """
    Permet de définir les snippets que l'utilisateur peut voire grâce au tag (:model:`gestion:Tag`)
    """
    tags = models.ManyToManyField(Tag)
    user = models.ManyToManyField(User)
    nom = models.CharField(max_length=50)
    date_ajout =  models.DateTimeField("date d'ajout", auto_now_add=True)

    def __str__(self):
        return self.nom

