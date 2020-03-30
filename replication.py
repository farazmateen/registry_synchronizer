#!/usr/bin/python3

import requests
import docker
import logging
import sys
import time
import subprocess
import yaml

def read_config()
    return yaml.load(open('config/config.yml'))


def get_logger():
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


def fetch_tags_list(registry_url, repo_name):
    log.info('Fetching all tags from % for %' % (c))
    return requests.get(registry_url + "/v2/" + repo_name + "/tags/list", verify=False).json()


def get_disjoint(src_list, dst_list):
    return list(set(src_list) - set(dst_list))


            subprocess.run(["docker pull registry1:5000/"+repo+":"+tag], shell=True)
            subprocess.run(["docker tag registry1:5000/"+repo+":"+tag + " registry2:5000/"+repo+":"+tag], shell=True)
            subprocess.run(["docker push "+ "reegistry2:5000/"+repo+":"+tag], shell=True)
            log.info("Image pushed sucessfully.")
        for tag in tags_list:
            if tag not in ignored:
                subprocess.run(["docker rmi "+ "registry2:5000/"+repo+":"+tag], shell=True)
                subprocess.run(["docker rmi registry1/"+repo+":"+tag], shell=True)

