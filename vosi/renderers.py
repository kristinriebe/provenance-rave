from __future__ import unicode_literals

from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.six.moves import StringIO
from django.utils.encoding import smart_text
from django.utils.encoding import smart_unicode
from rest_framework.renderers import BaseRenderer
from django.utils import timezone
import lxml.etree as etree  # for pretty printing xml

class VosiAvailabilityRenderer(BaseRenderer):
        """
        Returns an xmlstream for VOSI availability/ endpoint
        """

        charset = 'utf-8'

        # namespace declarations
        ns_vosiavail = 'http://www.ivoa.net/xml/VOSIAvailability/v1.0'
        version = '1.1'

        comment = "<!--\n"\
                + " !  Generated using Django with SimplerXMLGenerator\n"\
                + " !  at "+str(timezone.now())+"\n"\
                + " !-->\n"


        def render(self, data, prettyprint=False):
            """
            parameters:
              data = dictionary of the things to be shown
              prettyprint = flag for pretty printing the xml output (including whitespace and linebreaks)
            """

            stream = StringIO()
            xml = SimplerXMLGenerator(stream, self.charset)

            xml.startDocument()

            # add a comment
            xml._write(self.comment)

            # add namespace definitions
            nsattrs = {}
            nsattrs['version'] = self.version
            #nsattrs['encoding'] = charser
            nsattrs['xmlns:vosi'] = self.ns_vosiavail
            #nsattrs['xmlns:xsi'] = self.ns_xsi
            #nsattrs['xmlns:vs'] = self.ns_vs

            # add root node
            xml.startElement('vosi:availability', nsattrs)

            # add mandatory node:
            xml.startElement('vosi:available', {})
            xml.characters(smart_unicode(data['available']))
            xml.endElement('vosi:available')

            # remove available from data dict
            data.pop('available', None)

            # add possible optional nodes:
            for key in data.keys():
                xml.startElement('vosi'+key, {})
                xml.characters(smart_unicode(data[key]))
                xml.endElement('vosi'+key)

            xml.endElement('vosi:availability')

            xml.endDocument()

            xml_string = stream.getvalue()


            # make the xml pretty, i.e. use linebreaks and indentation
            # the sax XMLGenerator behind SimpleXMLGenerator does not seem to support this,
            # thus need a library that can do it.
            # TODO: since we use lxml anyway, maybe build the whole xml-tree with lxml.etree!
            # NOTE: This removes any possibly existing comments from the xml output!
            if prettyprint is True:
                parsed = etree.fromstring(xml_string)
                pretty_xml = etree.tostring(parsed, pretty_print=True)
                xml_string = pretty_xml

            return xml_string


class VosiCapabilityRenderer(BaseRenderer):
        """
        Takes capability data (from a queryset) and
        returns an xmlstream for VOSI capabilities/ endpoint
        """

        charset = 'utf-8'

        # namespace declarations
        ns_vosicap = 'http://www.ivoa.net/xml/VOSICapabilities/v1.0'
        ns_vs = 'http://www.ivoa.net/xml/VODataService/v1.1'
        ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
        ns_vr = "http://www.ivoa.net/xml/VOResource/v1.0"
        version = '1.1'

        comment = "<!--\n"\
                + " !  Generated using Django with SimplerXMLGenerator\n"\
                + " !  at "+str(timezone.now())+"\n"\
                + " !-->\n"

        def render(self, capabilities, prettyprint=False):
            """
            parameters:
              capabilities = queryset of voresource_capabilities
              prettyprint = flag for pretty printing the xml output (including whitespace and linebreaks)
            """

            stream = StringIO()
            xml = SimplerXMLGenerator(stream, self.charset)

            xml.startDocument()

            # add a comment
            xml._write(self.comment)

            # add namespace definitions
            nsattrs = {}
            nsattrs['version'] = self.version
            #nsattrs['encoding'] = charser
            nsattrs['xmlns:vosi'] = self.ns_vosicap
            nsattrs['xmlns:xsi'] = self.ns_xsi
            nsattrs['xmlns:vs'] = self.ns_vs
            nsattrs['xmlns:vr'] = self.ns_vr

            # add root node
            xml.startElement('vosi:capabilities', nsattrs)

            # Add all the capabilities, including those for VOSI endpoint,
            # extract them from the database using the provided queryset.
            # The following lookup is not efficient, since there is a database
            # call for each object, it would be more efficient to get a list of
            # all capabilities, interfaces and accessurls and then match them here.
            for capability in capabilities:
                attrs = {}
                if capability.standardID:
                    attrs['standardID'] = str(capability.standardID)
                xml.startElement('capability', attrs)

                interfaces = capability.voresource_interface_set.all()
                for interface in interfaces:
                    attrs = {}
                    if interface.type:
                        attrs['xsi:type'] = interface.type
                    xml.startElement('interface', attrs)

                    accessurls = interface.voresource_accessurl_set.all()
                    for accessurl in accessurls:
                        attrs = {}
                        attrs['use'] = accessurl.use  # throw error, if its not there?
                        xml.startElement('accessURL', attrs)
                        xml.characters(smart_unicode(accessurl.url))
                        xml.endElement('accessURL')

                    xml.endElement('interface')

                xml.endElement('capability')

            xml.endElement('vosi:capabilities')

            xml.endDocument()

            xml_string = stream.getvalue()


            # make the xml pretty, i.e. use linebreaks and indentation
            # the sax XMLGenerator behind SimpleXMLGenerator does not seem to support this,
            # thus need a library that can do it.
            # TODO: since we use lxml anyway, maybe build the whole xml-tree with lxml.etree!
            # NOTE: This removes any possibly existing comments from the xml output!
            if prettyprint is True:
                parsed = etree.fromstring(xml_string)
                pretty_xml = etree.tostring(parsed, pretty_print=True)
                xml_string = pretty_xml

            return xml_string

