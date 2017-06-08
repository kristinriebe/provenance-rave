from __future__ import unicode_literals

import json

from django.utils.encoding import smart_text
from django.utils.encoding import smart_unicode
from django.utils import timezone
from rest_framework.renderers import BaseRenderer


class PROVJSONRenderer(BaseRenderer):
    def render(self, data):
        # remove empty dicts
        for key, value in data.iteritems():
            if len(value) == 0:
                data.pop(key)

        string = json.dumps(data,
                #sort_keys=True,
                indent=4
            )

        return string


class PROVNBaseRenderer(BaseRenderer):

    def get_value(self, obj, key):
        marker = "-"

        if key in obj:
            return str(obj.pop(key))
        else:
            return marker

    def add_relation_id(self, string, obj):

        value = None
        if "prov:id" in obj:
            value = str(obj.pop("prov:id"))
            if ":" not in value:
                # Then this id is just an internal id here,
                # skip it in PROV-N serialization.
                # (Adding a blank as identifier namespace will not validate in ProvStore, thus don't use it)
                # value = "%s:%s" % (namespace, value)
                value = None

        if value is not None:
            string += "%s; " % value
        # else: return original string

        return string

    def add_optional_attributes(self, string, obj):
        # construct string for optional attributes,
        # and add to provn-string (just before final closing ")" )
        attributes = ""
        for key, val in obj.iteritems():
            attributes += '%s="%s", ' % (key, val)

        # add to string (and remove final comma)
        if attributes:
            string = string.replace(")", ", [%s])" % attributes.rstrip(', '))

        return string


class ActivityPROVNRenderer(PROVNBaseRenderer):

    def render(self, activity):
        string = "activity("\
            + self.get_value(activity, "prov:id") + ", "\
            + self.get_value(activity, "prov:startTime") + ", "\
            + self.get_value(activity, "prov:endTime")\
            + ")"

        string = self.add_optional_attributes(string, activity)

        return string


class EntityPROVNRenderer(PROVNBaseRenderer):

    def render(self, entity):
        string = "entity(" + self.get_value(entity, "prov:id") + ")"
        string = self.add_optional_attributes(string, entity)

        return string


class AgentPROVNRenderer(PROVNBaseRenderer):

    def render(self, agent):
        string = "agent(" + self.get_value(agent, "prov:id") + ")"
        string = self.add_optional_attributes(string, agent)

        return string


class UsedPROVNRenderer(PROVNBaseRenderer):

    def render(self, used):
        string = "used("

        # id is optional, but we have an id in the database, thus include it
        string = self.add_relation_id(string, used)

        # activity is mandatory:
        string += self.get_value(used, "prov:activity") + ", "

        # entity is optional in W3C, but it's a positional argument
        string += self.get_value(used, "prov:entity") + ", "

        # time is optional in W3C, but it's a positional argument
        string += self.get_value(used, "prov:time") + ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, used)

        return string


class WasGeneratedByPROVNRenderer(PROVNBaseRenderer):

    def render(self, wasGeneratedBy):
        string = "wasGeneratedBy("

        # id is optional
        string = self.add_relation_id(string, wasGeneratedBy)

        # entity is mandatory:
        string += self.get_value(wasGeneratedBy, "prov:entity") + ", "

        # activity is optional in W3C, but it's a positional argument
        string += self.get_value(wasGeneratedBy, "prov:activity") + ", "

        # time is optional in W3C, but it's a positional argument
        string += self.get_value(wasGeneratedBy, "prov:time")
        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, wasGeneratedBy)

        return string


class WasAssociatedWithPROVNRenderer(PROVNBaseRenderer):

    def render(self, wasAssociatedWith):
        string = "wasAssociatedWith("

        # id is optional
        string = self.add_relation_id(string, wasAssociatedWith)
        string += self.get_value(wasAssociatedWith, "prov:activity") + ", "
        string += self.get_value(wasAssociatedWith, "prov:agent") + ", "
        string += self.get_value(wasAssociatedWith, "prov:plan")
        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, wasAssociatedWith)

        return string


class WasAttributedToPROVNRenderer(PROVNBaseRenderer):

    def render(self, wasAttributedTo):
        string = "wasAttributedTo("

        # id is optional, but I have an id in the database, thus include it
        string = self.add_relation_id(string, wasAttributedTo)
        string += self.get_value(wasAttributedTo, "prov:entity") + ", "
        string += self.get_value(wasAttributedTo, "prov:agent")
        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, wasAttributedTo)

        return string


class HadMemberPROVNRenderer(PROVNBaseRenderer):

    def render(self, hadMember):
        string = "hadMember("

        # does not have an id nor optional attributes in W3C
        string += self.get_value(hadMember, "prov:collection") + ", "
        string += self.get_value(hadMember, "prov:entity")

        string += ")"

        return string


class WasDerivedFromPROVNRenderer(PROVNBaseRenderer):

    def render(self, wasDerivedFrom):
        string = "wasDerivedFrom("

        # does not have an id nor optional attributes in W3C
        string = self.add_relation_id(string, wasDerivedFrom)
        string += self.get_value(wasDerivedFrom, "prov:generatedEntity") + ", "
        string += self.get_value(wasDerivedFrom, "prov:usedEntity") + ", "
        string += self.get_value(wasDerivedFrom, "prov:activity") + ", "
        string += self.get_value(wasDerivedFrom, "prov:generation") + ", "
        string += self.get_value(wasDerivedFrom, "prov:usage")
        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, wasDerivedFrom)

        return string


class PROVNRenderer(PROVNBaseRenderer):
    """
    Takes a list of ordered Python dictionaries (serialized data)
    and returns a PROV-N string
    """

    def render(self, data):

        string = "document\n"
        for p_id, p in data['prefix'].iteritems():
            string += "prefix %s <%s>\n" % (p_id, p)
        string += "\n"

        for a_id, a in data['activity'].iteritems():
            string += ActivityPROVNRenderer().render(a) + "\n"

        for e_id, e in data['entity'].iteritems():
            string += EntityPROVNRenderer().render(e) + "\n"

        for a_id, a in data['agent'].iteritems():
            string += AgentPROVNRenderer().render(a) + "\n"

        for u_id, u in data['used'].iteritems():
            string += UsedPROVNRenderer().render(u) + "\n"

        for w_id, w in data['wasGeneratedBy'].iteritems():
            string += WasGeneratedByPROVNRenderer().render(w) + "\n"

        for w_id, w in data['wasAssociatedWith'].iteritems():
            string += WasAssociatedWithPROVNRenderer().render(w) + "\n"

        for w_id, w in data['wasAttributedTo'].iteritems():
            string += WasAttributedToPROVNRenderer().render(w) + "\n"

        for h_id, h in data['hadMember'].iteritems():
            string += HadMemberPROVNRenderer().render(h) + "\n"

        for w_id, w in data['wasDerivedFrom'].iteritems():
            string += WasDerivedFromPROVNRenderer().render(w) + "\n"

        string += "endDocument"

        return string