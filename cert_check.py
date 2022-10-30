#! /usr/bin/env python

import pycurl


curl = pycurl.Curl()
curl.setopt(pycurl.CAINFO, "scratch/server.crt")
#curl.setopt(pycurl.CAINFO, "scratch/_asset_certs_script_support/asset_serv.pem")
curl.setopt(pycurl.SSL_VERIFYPEER, 1)
curl.setopt(pycurl.SSL_VERIFYHOST, 2)
curl.setopt(pycurl.URL, "https://asset.server:8080/")

curl.perform()
