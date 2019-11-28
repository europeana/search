from django.db import models
from django.db.models import Field

class Agent(models.Model):
    # fields are wdid, prefLabel, sex, place of birth, place of death, narrow set, broad set
    wdid = models.URLField(unique=True, primary_key=True)
    pref_label = models.CharField(max_length=500)
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"
    sex_choices = ((MALE, 'Male'),(FEMALE, 'Female'), (UNKNOWN, 'Unknown'))
    sex = models.CharField(max_length=7, choices=sex_choices)
    place_of_birth = models.CharField(max_length=500)
    place_of_death = models.CharField(max_length=500)
    europeana_narrow_set = models.URLField()
    europeana_broad_set = models.URLField()
    birthdate = models.CharField(max_length=20, null=True)
    deathdate = models.CharField(max_length=20, null=True)
    social_relation = models.ManyToManyField(
        "self",
        through="SocialRelation",
        through_fields=('active', 'passive'),
        symmetrical=False
    )

class AgentRole(models.Model):
    agent = models.ForeignKey(Agent, to_field="wdid")
    pref_label = models.CharField(max_length=100)

class AgentImage(models.Model):
    agent = models.OneToOneField(Agent, to_field="wdid", related_name='portrait', db_constraint=True, unique=True, null=True)
    image_url = models.URLField(max_length=401)

class EuropeanaWork(models.Model):
    euid = models.URLField(unique=True, primary_key=True)
    pref_label = models.CharField(max_length=250)
    subject = models.ManyToManyField(Agent, related_name='eu_work_subject')
    creator = models.ManyToManyField(Agent, related_name='eu_work_creator')

class Work(models.Model):
    wdid = models.URLField(unique=True, primary_key=True)
    pref_label = models.CharField(max_length=250)
    subject = models.ManyToManyField(Agent, related_name='work_subject')
    creator = models.ManyToManyField(Agent, related_name='work_creator')

class RelationshipType(models.Model):
    pref_label = models.CharField(max_length=100)

class SocialRelation(models.Model):
    relationship_type = models.ForeignKey(RelationshipType, related_name='rtype')
    active = models.ForeignKey(Agent, related_name='originator', to_field="wdid")
    passive = models.ForeignKey(Agent, related_name='recipient', to_field="wdid")



#    grep postgres /var/log/audit/audit.log | audit2allow -M mypol
# semodule -i mypol.pp
