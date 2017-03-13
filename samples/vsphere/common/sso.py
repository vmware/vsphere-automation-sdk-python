"""
* *******************************************************
* Copyright VMware, Inc. 2013, 2016. All Rights Reserved.
* SODX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright 2013, 2016 VMware, Inc. All rights reserved.'


# Standard library imports.
try:
    import httplib
except ImportError:
    import http.client as httplib
import base64
import cgi
import hashlib
import re
import sys
import time
from uuid import uuid4

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

# Third-party imports.
from lxml import etree


def _extract_certificate(cert):
    """
    Extract DER certificate/private key from DER/base64-ed DER/PEM string.

    @type           cert: C{str}
    @param          cert: Certificate/private key in one of three supported formats.

    @rtype: C{str}
    @return: Certificate/private key in DER (binary ASN.1) format.
    """
    if not cert:
        raise IOError('Empty certificate')
    signature = cert[0]
    # DER certificate is sequence.  ASN.1 sequence is 0x30.
    if signature == '\x30':
        return cert
    # PEM without preamble.  Base64-encoded 0x30 is 0x4D.
    if signature == '\x4D':
        return base64.b64decode(cert)
    # PEM with preamble.  Starts with '-'.
    if signature == '-':
        return base64.b64decode(re.sub('-----[A-Z ]*-----', '', cert))
    # Unknown format.
    raise IOError('Invalid certificate file format')


class SoapException(Exception):
    """
    Exception raised in case of STS request failure.
    """
    def __init__(self, soap_msg, fault_code, fault_string):
        """
        Initializer for SoapException.

        @type      soap_msg: C{str}
        @param     soap_msg: the soap fault XML returned by STS
        @type    fault_code: C{str}
        @param   fault_code: The fault code returned by STS.
        @type  fault_string: C{str}
        @param fault_string: The fault string returned by STS.
        """
        self._soap_msg = soap_msg
        self._fault_code = fault_code
        self._fault_string = fault_string
        Exception.__init__(self)

    def __str__(self):
        """
        Returns the string representation of SoapException.

        @rtype: C{str}
        @return: string representation of SoapException
        """
        return ("SoapException:\nfaultcode: %(_fault_code)s\n"
                "faultstring: %(_fault_string)s\n"
                "faultxml: %(_soap_msg)s" % self.__dict__)


class SSOHTTPSConnection(httplib.HTTPSConnection):
    """
    An HTTPS class that verifies server's certificate on connect.
    """
    def __init__(self, *args, **kwargs):
        """
        Initializer.  See httplib.HTTPSConnection for other arguments
        than thumbprint and server_cert.

        At least one of thumbprint, server_cert should be provided,
        otherwise server certificate is not validated.

        @type           thumbprint: C(str)
        @param          thumbprint: Expected SHA-1 thumbprint of the server
                                    certificate.  May be None.

        @type          server_cert: C(str)
        @param         server_cert: File with expected server certificate.
                                    May be None.
        """
        self.server_thumbprint = kwargs.pop('thumbprint')
        if self.server_thumbprint is not None:
            self.server_thumbprint = re.sub(':', '',
                                            self.server_thumbprint.lower())
        server_cert_path = kwargs.pop('server_cert')
        if server_cert_path is not None:
            with open(server_cert_path, 'rb') as f:
                server_cert = f.read()
            self.server_cert = _extract_certificate(server_cert)
        else:
            self.server_cert = None
        httplib.HTTPSConnection.__init__(self, *args, **kwargs)

    def _check_cert(self, peerCert):
        """
        Verify that peer certificate matches one we expect.

        @type             peerCert: C(str)
        @param            peerCert: Server certificate in DER format.

        @rtype: boolean
        @return: True if peerCert is acceptable.  False otherwise.
        """
        if self.server_cert is not None:
            if peerCert != self.server_cert:
                return False
        if self.server_thumbprint is not None:
            thumbprint = hashlib.sha1(peerCert).hexdigest().lower()  # pylint: disable=E1101
            if thumbprint != self.server_thumbprint:
                return False
        return True

    def connect(self):
        """
        Connect method: connects to the remote system, and upon
        successful connection validates certificate.

        Throws an exception when something is wrong.  See
        httplib.HTTPSConnection.connect() for details.
        """
        httplib.HTTPSConnection.connect(self)
        if not self._check_cert(self.sock.getpeercert(True)):
            self.sock.close()
            self.sock = None
            raise IOError('Invalid certificate')


class SsoAuthenticator(object):
    """
    A class to handle the transport layer communication between the client and
    the STS service.
    """

    def __init__(self,
                 sts_url,
                 sts_cert=None,
                 thumbprint=None
                 ):
        """
        Initializer for SsoAuthenticator.

        @type           sts_url: C{str}
        @param          sts_url: URL for the Security Token Service. Usually
                                 obtained by querying Component Manager.
        @type          sts_cert: C{str}
        @param         sts_cert: The file with public key of the Security
                                 Token Service.  Usually obtained from
                                 Component Manager and written to the file.
        @type        thumbprint: C{str}
        @param       thumbprint: The SHA-1 thumbprint of the certificate used
                                 by the Security Token Service.  It is same
                                 thumbprint you can pass to pyVmomi SoapAdapter.
        """
        self._sts_cert = sts_cert
        self._sts_url = sts_url
        self._sts_thumbprint = thumbprint

    def perform_request(self,
                        soap_message,
                        public_key=None,
                        private_key=None,
                        ssl_context=None):
        """
        Performs a Holder-of-Key SAML token request using the service user's
        certificates or a bearer token request using the user credentials.

        @type      soap_message: C{str}
        @param     soap_message: Authentication SOAP request.
        @type        public_key: C{str}
        @param       public_key: File containing the public key for the service
                                 user registered with SSO, in PEM format.
        @type       private_key: C{str}
        @param      private_key: File containing the private key for the service
                                 user registered with SSO, in PEM format.
        @type       ssl_context: ssl.SSLContext
        @param      ssl_context: Context describing the various SSL options.
        @rtype: C{str}
        @return: Response received from the STS after the HoK request.
        """
        parsed = urlparse(self._sts_url)
        host = parsed.netloc  # pylint: disable=E1101

        import ssl
        if ssl_context and hasattr(ssl, '_create_unverified_context'):
            # Python 2.7.9 has stronger SSL certificate validation, so we need
            # to pass in a context when dealing with self-signed certificates.
            webservice = SSOHTTPSConnection(host=host,
                                            key_file=private_key,
                                            cert_file=public_key,
                                            server_cert=self._sts_cert,
                                            thumbprint=self._sts_thumbprint,
                                            context=ssl_context)
        else:
            # Versions of Python before 2.7.9 don't support the context
            # parameter, so if it wan't provided, don't pass it on.
            webservice = SSOHTTPSConnection(host=host,
                                            key_file=private_key,
                                            cert_file=public_key,
                                            server_cert=self._sts_cert,
                                            thumbprint=self._sts_thumbprint)

        webservice.putrequest("POST", parsed.path, skip_host=True)  # pylint: disable=E1101
        webservice.putheader("Host", host)
        webservice.putheader("User-Agent", "VMware/pyVmomi")
        webservice.putheader("Accept", "text/xml, multipart/related")
        webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
        webservice.putheader("Content-length", "%d" % len(soap_message))
        webservice.putheader("Connection", "keep-alive")
        webservice.putheader("SOAPAction",
                             "http://docs.oasis-open.org/ws-sx/ws-trust/200512/RST/Issue")
        webservice.endheaders()
        if sys.version_info[0] >= 3:  # Python 3
            webservice.send(bytes(soap_message, 'UTF-8'))
        else:
            webservice.send(soap_message)

        saml_response = webservice.getresponse()
        if saml_response.status != 200:
            fault = saml_response.read()
            # Best effort at figuring out a SOAP fault.
            if saml_response.status == 500 and fault and 'faultcode' in fault:
                fault_xml = etree.fromstring(fault)
                parsed_fault = fault_xml.xpath("//text()")
                if len(parsed_fault) == 2:
                    raise SoapException(fault, *parsed_fault)
            raise Exception("Got response %s: %s\n%s" %
                            (saml_response.status, saml_response.msg, fault))
        return saml_response.read()

    def get_bearer_saml_assertion(self,
                                  username,
                                  password,
                                  public_key=None,
                                  private_key=None,
                                  request_duration=60,
                                  token_duration=600,
                                  delegatable=False,
                                  renewable=False,
                                  ssl_context=None):
        """
        Extracts the assertion from the Bearer Token received from the Security
        Token Service.

        @type          username: C{str}
        @param         username: Username for the user for which bearer token
                                 needs to be requested.
        @type          password: C{str}
        @param         password: Password for the user for which bearer token
                                 needs to be requested.
        @type        public_key: C{str}
        @param       public_key: File containing the public key for the service
                                 user registered with SSO, in PEM format.
        @type       private_key: C{str}
        @param      private_key: File containing the private key for the service
                                 user registered with SSO, in PEM format.

        @type  request_duration: C{long}
        @param request_duration: The duration for which the request is valid. If
                                 the STS receives this request after this
                                 duration, it is assumed to have expired. The
                                 duration is in seconds and the default is 60s.
        @type    token_duration: C{long}
        @param   token_duration: The duration for which the SAML token is issued
                                 for. The duration is specified in seconds and
                                 the default is 600s.
        @type       delegatable: C{boolean}
        @param      delegatable: Whether the generated token is delegatable or not
                                 The default value is False
        @type       ssl_context: ssl.SSLContext
        @param      ssl_context: Context describing the various SSL options.
        @rtype: C{str}
        @return: The SAML assertion.
        """
        request = SecurityTokenRequest(username=username,
                                       password=password,
                                       public_key=public_key,
                                       private_key=private_key,
                                       request_duration=request_duration,
                                       token_duration=token_duration)
        soap_message = request.construct_bearer_token_request(
            delegatable=delegatable, renewable=renewable)
        bearer_token = self.perform_request(soap_message,
                                            public_key,
                                            private_key,
                                            ssl_context)
        if sys.version_info[0] >= 3:
            return etree.tostring(
                                  _extract_element(etree.fromstring(bearer_token),
                                                   'Assertion',
                                                   {'saml2': "urn:oasis:names:tc:SAML:2.0:assertion"}),
                                  pretty_print=False).decode('utf-8')
        else:
            return etree.tostring(
                                  _extract_element(etree.fromstring(bearer_token),
                                                   'Assertion',
                                                   {'saml2': "urn:oasis:names:tc:SAML:2.0:assertion"}),
                                  pretty_print=False)


class SecurityTokenRequest(object):
    """
    SecurityTokenRequest class handles the serialization of request to the STS
    for a SAML token.
    """

    # pylint: disable=R0902
    def __init__(self,
                 username=None,
                 password=None,
                 public_key=None,
                 private_key=None,
                 request_duration=60,
                 token_duration=600):
        """
        Initializer for the SecurityToken Request class.

        @type          username: C{str}
        @param         username: Username for the user for which bearer token
                                 needs to be requested.
        @type          password: C{str}
        @param         password: Password for the user for which bearer token
                                 needs to be requested.
        @type        public_key: C{str}
        @param       public_key: The file containing the public key of the
                                 service account requesting the SAML token.
        @type       private_key: C{str}
        @param      private_key: The file containing the private key of the
                                 service account requesting the SAML token.
        @type  request_duration: C{long}
        @param request_duration: The duration for which the request is valid. If
                                 the STS receives this request after this
                                 duration, it is assumed to have expired. The
                                 duration is specified in seconds and default is
                                 60s.
        @type    token_duration: C{long}
        @param   token_duraiton: The duration for which the SAML token is issued
                                 for. The duration is specified in seconds and
                                 the default is 600s.
        """
        self._timestamp_id = _generate_id()
        self._signature_id = _generate_id()
        self._request_id = _generate_id()
        self._security_token_id = _generate_id()
        current = time.time()
        self._created = time.strftime(TIME_FORMAT,
                                      time.gmtime(current))
        self._expires = time.strftime(TIME_FORMAT,
                                      time.gmtime(current + token_duration))
        self._request_expires = time.strftime(TIME_FORMAT,
                                              time.gmtime(current +
                                                          request_duration))
        self._timestamp = TIMESTAMP_TEMPLATE % self.__dict__
        self._username = cgi.escape(username) if username else username
        self._password = cgi.escape(password) if password else password
        self._public_key_file = public_key
        self._private_key_file = private_key
        self._act_as_token = None
        self._renewable = str(False).lower()
        self._delegatable = str(False).lower()
        self._use_key = ''
        self._private_key = None
        self._binary_exchange = None
        self._public_key = None

    def construct_bearer_token_request(self, delegatable=False, renewable=False):
        """
        Constructs the actual Bearer token SOAP request.

        @type  delegatable: C{boolean}
        @param delegatable: Whether the generated token is delegatable or not
        @type    renewable: C{boolean}
        @param   renewable: Whether the generated token is renewable or not
                            The default value is False
        @rtype:  C{str}
        @return: Bearer token SOAP request.
        """
        self._key_type = "http://docs.oasis-open.org/ws-sx/ws-trust/200512/Bearer"
        self._security_token = USERNAME_TOKEN_TEMPLATE % self.__dict__
        self._delegatable = str(delegatable).lower()
        self._renewable = str(renewable).lower()
        return _canonicalize(REQUEST_TEMPLATE % self.__dict__)


def _generate_id():
    """
    An internal helper method to generate UUIDs.

    @rtype: C{str}
    @return: UUID
    """
    return "_%s" % uuid4()


def _canonicalize(xml_string):
    """
    Given an xml string, canonicalize the string per
    U{http://www.w3.org/2001/10/xml-exc-c14n#}

    @type  xml_string: C{str}
    @param xml_string: The XML string that needs to be canonicalized.

    @rtype: C{str}
    @return: Canonicalized string.
    """
    string = StringIO(xml_string)
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(string, parser=parser)
    # io.StringIO only accepts Unicode input (i.e. u"multibyte string"), while StringIO.StringIO accepts either 8 bit input or unicode input.
    if sys.version_info[0] >= 3:
        from io import BytesIO
        string = BytesIO()
        tree.write_c14n(string, exclusive=True, with_comments=False)
        return string.getvalue().decode('utf-8')
    else:
        string = StringIO()
        tree.write_c14n(string, exclusive=True, with_comments=False)
        return string.getvalue()


def _extract_element(xml, element_name, namespace):
    """
    An internal method provided to extract an element from the given XML.

    @type           xml: C{str}
    @param          xml: The XML string from which the element will be extracted.
    @type  element_name: C{str}
    @param element_name: The element that needs to be extracted from the XML.
    @type     namespace: dict
    @param    namespace: A dict containing the namespace of the element to be
                         extracted.

    @rtype: etree element.
    @return: The extracted element.
    """
    assert(len(namespace) == 1)
    result = xml.xpath("//%s:%s" % (list(namespace.keys())[0], element_name),  # python 3.x dict.keys() returns a view
                       namespaces=namespace)
    if result:
        return result[0]
    else:
        raise KeyError('%s does not seem to be present in the XML.' %
                       element_name)


TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.987Z"


# Template container for user's credentials when requesting a bearer token.
USERNAME_TOKEN_TEMPLATE = """\
<ns2:UsernameToken xmlns:ns2="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
<ns2:Username>%(_username)s</ns2:Username>
<ns2:Password>%(_password)s</ns2:Password>
</ns2:UsernameToken>"""


# Template containing the anchor to the signature.
USE_KEY_TEMPLATE = """\
<UseKey Sig="%(_signature_id)s"/>"""


# The follwoing template is used to create a timestamp for the various messages.
# The timestamp is used to indicate the duration of the request itself.
TIMESTAMP_TEMPLATE = """\
<ns3:Timestamp xmlns:ns3="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" ns3:Id="%(_timestamp_id)s">
<ns3:Created>%(_created)s</ns3:Created><ns3:Expires>%(_request_expires)s</ns3:Expires></ns3:Timestamp>"""


# The following template is used to construct the token requests to the STS.
REQUEST_TEMPLATE = """\
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header>
<ns6:Security xmlns="http://docs.oasis-open.org/ws-sx/ws-trust/200512"
              xmlns:ns2="http://www.w3.org/2005/08/addressing"
              xmlns:ns3="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
              xmlns:ns6="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
%(_timestamp)s
%(_security_token)s
</ns6:Security>
</SOAP-ENV:Header>
<SOAP-ENV:Body xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:Id="%(_request_id)s">
<RequestSecurityToken xmlns="http://docs.oasis-open.org/ws-sx/ws-trust/200512"
                      xmlns:ns2="http://www.w3.org/2005/08/addressing"
                      xmlns:ns3="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
                      xmlns:ns6="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
<TokenType>urn:oasis:names:tc:SAML:2.0:assertion</TokenType>
<RequestType>http://docs.oasis-open.org/ws-sx/ws-trust/200512/Issue</RequestType>
<Lifetime>
<ns3:Created>%(_created)s</ns3:Created>
<ns3:Expires>%(_expires)s</ns3:Expires>
</Lifetime>
<Renewing Allow="%(_renewable)s" OK="%(_renewable)s"/>
<Delegatable>%(_delegatable)s</Delegatable>
<KeyType>%(_key_type)s</KeyType>
<SignatureAlgorithm>http://www.w3.org/2001/04/xmldsig-more#rsa-sha256</SignatureAlgorithm>%(_use_key)s</RequestSecurityToken>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""
