#!/usr/bin/python3

import requests
import docker
import logging
import sys
import time
import subprocess
import yaml


def read_config():
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


def pull_image(src_url, repo, tag):
    subprocess.run(["docker pull " + src_url + "/" + repo + ":" + tag], shell=True)


def tag_image(src_url, dst_url, repo, tag):
    subprocess.run(["docker tag " + src_url + "/" + repo + ":" + tag + " " + dst_url + "/" + repo + ":" + tag], shell=True)


def push_image(dst_url, repo, tag):
    subprocess.run(["docker push " + dst_url + "/" + repo + ":" + tag], shell=True)


def clean_up(src_url, dst_url, repo, tag):
    subprocess.run(["docker rmi " + src_url + "/" + repo + ":" + tag], shell=True)
    subprocess.run(["docker rmi " + dst_url + "/" + repo + ":" + tag], shell=True)
