# -*- coding: utf-8 -*-

import re

from time import strptime, mktime

from pycurl import REFERER

from pyload.plugins.Account import Account


class OneFichierCom(Account):
    __name    = "OneFichierCom"
    __type    = "account"
    __version = "0.11"

    __description = """1fichier.com account plugin"""
    __license     = "GPLv3"
    __authors     = [("Elrick69", "elrick69[AT]rocketmail[DOT]com"),
                       ("Walter Purcaro", "vuolter@gmail.com")]


    VALID_UNTIL_PATTERN = r'Your Premium Status will end the (\d+/\d+/\d+)'


    def loadAccountInfo(self, user, req):
        validuntil = None
        trafficleft = -1
        premium = None

        html = req.load("https://1fichier.com/console/abo.pl")

        m = re.search(self.VALID_UNTIL_PATTERN, html)
        if m:
            expiredate = m.group(1)
            self.logDebug("Expire date: " + expiredate)

            try:
                validuntil = mktime(strptime(expiredate, "%d/%m/%Y"))
            except Exception, e:
                self.logError(e)
            else:
                premium = True

        return {'validuntil': validuntil, 'trafficleft': trafficleft, 'premium': premium or False}


    def login(self, user, data, req):
        req.http.c.setopt(REFERER, "https://1fichier.com/login.pl?lg=en")

        html = req.load("https://1fichier.com/login.pl?lg=en",
                        post={'mail': user, 'pass': data['password'], 'It': "on", 'purge': "off", 'valider': "Send"})

        if '>Invalid email address' in html or '>Invalid password' in html:
            self.wrongPassword()