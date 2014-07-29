# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from django.contrib.auth.hashers import get_hasher
from django.core import management
import django_pph
import django.utils.six as six
import getpass
import sys


class Migration(DataMigration):

    def forwards(self, orm):
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
	
        polypasswordhasher = get_hasher('pph')
        management.call_command('initialize_pph_context')
        next_available_share = 1
        threshold_total = polypasswordhasher.threshold
        threshold_count = 0
	
        for user in orm.User.objects.all():
            # TODO: IDENTIFY THE ALGORITHM FIRST. I am assuming this is a
            # pbkdf2_sha256 for the time being.
            algorithm, iterations, salt, hash = user.password.split('$')
            
            assert(algorithm=='pbkdf2_sha256')

            if user.is_superuser:
            # sharenumber = hasher.data['nextavailableshare']
            # hasher.data['nextavailableshare']
            # hasher.update()
            # newhash = hasher._polyhash_entry(hash
                new_hash, sharenumber = \
                        polypasswordhasher.update_hash_threshold(hash)
                new_password = "{}${}${}${}${}".format('pph',sharenumber,
                        iterations, salt, new_hash)
                threshold_count += 1
            else:
                new_hash = polypasswordhasher.update_hash_thresholdless(hash)
                new_password = "{}${}${}${}${}".format('pph',0,iterations,
                    salt, new_hash)
                
            user.password = new_password
            user.last_login = datetime.datetime.today()
            user.date_joined = datetime.datetime.today()
            user.save()

        # and orm['appname.ModelName'] for models in other applications.
        assert threshold_count >= threshold_total

    def backwards(self, orm):

        polypasswordhasher = get_hasher('pph')

        data = polypasswordhasher.data

        if not data['is_unlocked'] or data['secret'] is None or data['thresholdlesskey'] is None:
            print("context is locked, we will have to unlock it manually")
            print("Please provide at least {} usernames and passwords".format(
                polypasswordhasher.threshold))

            username = password = 'Dummy'

            while len(username) > 0:
                username = _prompt('Provide a username: ')
                password = _get_password('password: ')

                user = orm.User.objects.filter(username=username)
                if len(user) != 1:
                    print("this user is not available")

                user = user[0]
                polypasswordhasher.verify(password, user.password)

                
            
    
        for user in orm.User.object.all():
            print user.username

        "Write your backwards methods here."

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['auth']
    symmetrical = True


def _prompt(message, result_type=str):
  """
    Non-public function that prompts the user for input by loging 'message',
    converting the input to 'result_type', and returning the value to the
    caller.
  """

  return result_type(six.moves.input(message))





def _get_password(prompt='Password: ', confirm=False):
  """
    Non-public function that returns the password entered by the user.  If
    'confirm' is True, the user is asked to enter the previously entered
    password once again.  If they match, the password is returned to the caller.
  """

  while True:
    # getpass() prompts the user for a password without echoing
    # the user input.
    password = getpass.getpass(prompt, sys.stderr)
    
    if not confirm:
      return password
    password2 = getpass.getpass('Confirm: ', sys.stderr)
    
    if password == password2:
      return password
    
    else:
      print('Mismatch; try again.')




