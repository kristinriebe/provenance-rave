# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.db import models

@python_2_unicode_compatible
class RaveObsids(models.Model):
    rave_obs_id = models.TextField(db_column='RAVE_OBS_ID', blank=True, null=True)
    obsdate = models.TextField(db_column='Obsdate', blank=True, null=True)
    fieldname = models.TextField(db_column='FieldName', blank=True, null=True)
    platenumber = models.TextField(db_column='PlateNumber', blank=True, null=True)
    fibernumber = models.TextField(db_column='FiberNumber', blank=True, null=True)
    id_2mass = models.TextField(db_column='ID_2MASS', blank=True, null=True)
    id_denis = models.TextField(db_column='ID_DENIS', blank=True, null=True)
    obs_collection = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rave_obsids'

    def __str__(self):
        return "rave_obs_id=%s; obsdate=%s; fieldname=%s; id_2mass=%s; obs_collection=%s" % (str(self.rave_obs_id), self.obsdate, self.fieldname, self.id_2mass, self.obs_collection)


    def get_sparvfile(self, rave_obs_id):
        basepath = "corvus.aip.de:/store/01/RAVE/Processing/DR4"
        namesplit = rave_obs_id.split('_')
        date = namesplit[0]
        fieldname = namesplit[1]
        platenumber = namesplit[2]
        filepath = date + "/"

        stn_file = filepath + fieldname + ".stn"
        uncorrspec_file = filepath + filedname + ".rvsun." + platenumber + ".nocont.txt"
        corrspec_file = filepath + filedname + ".rvsun." + platenumber + ".cont.txt"

        # would need more metadata here!
        return {'stn_file': stn_file, 'uncorrspec_file': uncorrspec_file,
                'corrspec_file': corrspec_file}


    def get_reducedfile(self, rave_obs_id):
        # extract year, month and day from the file name:
        namesplit = rave_obs_id.split('_')
        year = namesplit[0][0:4]
        month = namesplit[0][4:6]
        day = namesplit[0][6:8]
        field = namesplit[1]
        num = namesplit[2]
        basepath = "corvus.aip.de:/store/01/Data_RAVE_s"
        filepath = basepath + "/" + "RAVE/reduced_IRAF/" + str(year) + "/"\
            + namesplit[0] + "/" + field
        reduced_file = filepath + ".rvsun.fts"
        sky_file = filepath + ".sky.fts"
        usky_file = filepath + ".usky.fts"
        return {'reduced_file': reduced_file, 'sky_file': sky_file,
                'usky_file': usky_file}


    def get_originalfiles(self, rave_obs_id):
        namesplit = rave_obs_id.split('_')
        date = namesplit[0]
        fieldname = namesplit[1]
        platenumber = namesplit[2]

        basepath = "corvus.aip.de:/store/01/Data_RAVE_s/RAVE_ORIG"
        filepath = basepath + "/" + date + "/" + fieldname + "*.fits"

        return {'originalfiles': filepath}

#
#class Entity(prov_vo.Entity):
#    dataType= models.CharField(max_length=128, null=True, blank=True)
#    # maybe use obscore_access_format?
#    storageLocation = models.CharField('storage location', max_length=1024, null=True, blank=True)
#    # may be use obscore_access_url here? But this is not the same as dorectory path on a server ...
