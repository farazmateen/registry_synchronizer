#!/usr/bin/python3

import requests
from urllib.parse import urlparse
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
    src_url = strip_scheme(src_url)
    subprocess.run(["docker pull " + src_url + "/" + repo + ":" + tag], shell=True)


def tag_image(src_url, dst_url, repo, tag):
    src_url = strip_scheme(src_url)
    dst_url = strip_scheme(dst_url)
    subprocess.run(["docker tag " + src_url + "/" + repo + ":" + tag + " " + dst_url + "/" + repo + ":" + tag], shell=True)


def push_image(dst_url, repo, tag):
    dst_url = strip_scheme(dst_url)
    subprocess.run(["docker push " + dst_url + "/" + repo + ":" + tag], shell=True)


def clean_up(src_url, dst_url, repo, tag):
    src_url = strip_scheme(src_url)
    dst_url = strip_scheme(dst_url)
    subprocess.run(["docker rmi " + src_url + "/" + repo + ":" + tag], shell=True)
    subprocess.run(["docker rmi " + dst_url + "/" + repo + ":" + tag], shell=True)

def strip_scheme(url):
    parsed_url = urlparse(url)
    scheme = "%s://" % parsed_url.scheme
    return parsed_url.geturl().replace(scheme, '', 1)

def get_image_digests_map(addr, repo, tags_list):
    tags_digest_map = {}
    for tag in tags_list:
        resp = requests.get(addr + "/v2/" + repo + "/manifests/" + tag)
        tags_digest_map.update({tag: resp.headers["Docker-Content-Digest"]}) 
    return tags_digest_map


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

    else:
        # src repo is empty
        continue
    if tags is None:
        tags = src_tags
    source_tags_map = get_image_digests_map(source, repo, src_tags)

    # add check for existence
    for destination in destination_list:
        dst_resp = fetch_tags_list(destination, repo)
        dst_tags = []
        if "tags" in dst_resp:
            dst_tags = dst_resp["tags"]
        dest_tags_map = get_image_digests_map(destination, repo, dst_tags)
        
        for tag in tags:
            if tag not in src_tags:
                continue
            if tag not in dst_tags:
                pull_image(source, repo, tag)
                tag_image(source, destination, repo, tag)
                push_image(destination, repo, tag)
            elif tag in dst_tags:
                if source_tags_map[tag] == dest_tags_map[tag]:
                    continue
                else:
                    pull_image(source, repo, tag)
                    tag_image(source, destination, repo, tag)
                    push_image(destination, repo, tag)

        for tag in tags:
            clean_up(source, destination, repo, tag)
