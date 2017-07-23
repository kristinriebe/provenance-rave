# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import generic

class IndexView(generic.TemplateView):
    template_name = 'core/index.html'
