#!/usr/bin/env python

import ssl
from datetime import datetime
from M2Crypto import X509


def main():
    cert_pem = ssl.get_server_certificate(('127.0.0.1', 443),
                                          ssl_version=ssl.PROTOCOL_TLSv1)
    x509 = X509.load_cert_string(cert_pem, X509.FORMAT_PEM)
    not_after = x509.get_not_after().get_datetime().strftime('%s')
    now = datetime.now().strftime('%s')
    cert_end_in = int(not_after) - int(now)
    print('metric cert_end_in int %s' % cert_end_in)

if __name__ == '__main__':
    main()
