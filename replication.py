#!/usr/bin/python3

import requests
import docker
import logging
import sys
import time
import subprocess
import yaml


def read_config():
    return yaml.load(open('config.yml', 'r'))


def get_logger():
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

logger = get_logger()

def fetch_tags_list(registry_url, repo_name):
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

config = read_config()

servers_dict = {}

for server in config["registeries"]:
    servers_dict.update(server)

for rule in config["rules"]:
    repo = config["rules"][rule]["repo"]
    source = servers_dict[config["rules"][rule]["source"]]
    destination_list = [servers_dict[registry] for registry in config["rules"][rule]["destination"]]
    tags = config["rules"][rule]["tags"]
    src_resp = fetch_tags_list(source, repo)
    if "tags" in src_resp:
        src_tags = src_resp["tags"]
    # add else condition

    # add check for existence
    for destination in destination_list:
        dst_resp = fetch_tags_list(destination, repo)
        dst_tags = []
        if tags in dst_resp:
            dst_tags = dst_resp["tags"]
        for tag in tags:
            if tag not in dst_tags:
                pull_image(source, repo, tag)
                tag_image(source, destination, repo, tag)
                push_image(dst_url, repo, tag)

        for tag in tags:
            clean_up(source, destination, repo, tag)
