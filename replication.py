#!/usr/bin/python3

import requests
import docker
import logging
import sys
import time
import subprocess

log = logging.getLogger()
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

log.info('Fetching repositories list')

list_repos = requests.get('https://registry1:5000/v2/_catalog?n=1000', verify=False)
log.info("List of available repos: %s" % list_repos.json())

tags_dict = {}
ignored = []
start = time.time()
for repo in list_repos.json()['repositories']:
    log.info("Getting tags for repo: %s" % repo)
    tags = requests.get("https://registry1:5000/v2/" + repo + "/tags/list", verify=False)
    if "tags" in tags.json():
        tags_dict.update({repo: tags.json()["tags"]})
    else:
        log.info("No tags found for repo: %s" % repo)
        ignored.append(repo)

log.info("Fetch all tags. Time Taken = %s" % (time.time() - start))
list_repos_2 = requests.get('http://registry2:5000/v2/_catalog?n=1000', verify=False)
tags_dict2 = {}


for repo in list_repos_2.json()['repositories']:
    log.info("Getting tags for repo: %s" % repo)
    tags = requests.get("http://registry2:5000/v2/" + repo + "/tags/list", verify=False)
    if "tags" in tags.json():
        tags_dict2.update({repo: tags.json()["tags"]})
    else:
        log.info("No tags found for repo: %s" % repo)
        ignored.append(repo)

client = docker.from_env()

for repo, tags_list in tags_dict.items():
    #if 'latest' in tags_list:
    #log.info("Getting latest image for repo: %s" % repo
    if isinstance(tags_list, list):
        for tag in tags_list:
            if repo in tags_dict2:
                if tag in tags_dict2[repo]:
                    ignored.append(tag)
                    continue
            subprocess.run(["docker pull registry1:5000/"+repo+":"+tag], shell=True)
            subprocess.run(["docker tag registry1:5000/"+repo+":"+tag + " registry2:5000/"+repo+":"+tag], shell=True)
            subprocess.run(["docker push "+ "reegistry2:5000/"+repo+":"+tag], shell=True)
            log.info("Image pushed sucessfully.")
        for tag in tags_list:
            if tag not in ignored:
                subprocess.run(["docker rmi "+ "registry2:5000/"+repo+":"+tag], shell=True)
                subprocess.run(["docker rmi registry1/"+repo+":"+tag], shell=True)

