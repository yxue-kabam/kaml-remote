#!/usr/bin/env python

from __future__ import print_function
from argparse import ArgumentParser
from os import environ

import logging
import os
import re
import sys
import uuid
import warnings

try:
    from kubernetes import client, config
except ImportError:
    raise ImportError('Failed to import Python Kubernetes client. Install it by running: sudo pip install kubernetes')

def create_job_object(job_arguments, size, docker_image, docker_image_tag, affinity):

    user = os.environ['USER']
    job = client.V1Job(metadata=client.V1ObjectMeta(
                    name='kaml-remote-{}-{}'.format(user, uuid.uuid1())
                ),
                spec=client.V1JobSpec(
                    template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    name='kaml-remote-{}-{}'.format(user, uuid.uuid1()),
                    labels={'type': size}

                ),
                spec=client.V1PodSpec(
                    containers=[client.V1Container(
                        name='kaml-remote',
                        args=job_arguments,
                        image='{}:{}'.format(docker_image, docker_image_tag),
                        image_pull_policy='Always',
                        env=[
                            client.V1EnvVar(
                                name='KAML_HOME',
                                value='/app'
                            )
                        ],
                        volume_mounts=[
                            client.V1VolumeMount(
                                name = 'kaml-cfg-volume',
                                read_only = True,
                                mount_path = '/app/kaml.cfg',
                                sub_path = 'kaml.cfg'),
                            client.V1VolumeMount(
                                name = 'gcp-service-account',
                                read_only = True,
                                mount_path = '/app/service-key.json',
                                sub_path = 'service-key.json'),
                            ]
                        )],
                        affinity=affinity,
                    volumes=[
                        client.V1Volume(
                            name = 'kaml-cfg-volume',
                            config_map = client.V1ConfigMapVolumeSource(
                                name = 'kaml-cfg'
                            )
                        ),
                        client.V1Volume(
                            name='gcp-service-account',
                                secret=client.V1SecretVolumeSource(
                                    secret_name='gcp-service-account',
                                        items=[
                                            client.V1KeyToPath(
                                                key='service-key.json',
                                                path='service-key.json')
                                        ]
                                )
                        )
                    ],
                    restart_policy='Never'
                )
            )
        )
    )

    return(job)

def set_affinity(size):

    affinity = {
        'nodeAffinity': {
            'requiredDuringSchedulingIgnoredDuringExecution': {
                'nodeSelectorTerms': [{
                    'matchExpressions': [{
                        'key': 'cloud.google.com/gke-nodepool',
                        'operator': 'In',
                        'values': [size]
                    }]
                }]
            }
        },
        "podAntiAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": [
                {
                    "labelSelector": {
                        "matchExpressions": [
                            {
                                "key": "type",
                                "operator": "In",
                                "values": [size]
                            },
                        ]
                    },
                    "topologyKey": "kubernetes.io/hostname"
                }, ]
                }
        }

    return(affinity)

def run_job(api_instance, job, size, docker_image, docker_image_tag):
  # run job
  api_response = api_instance.create_namespaced_job(
    namespace="default",
    body=job)
  print("-----")
  print("Kaml docker image: {}. Set environment variable \"KAML_IMAGE\" to override it.".format(docker_image))
  print("Kaml docker tag: {}. Set environment variable \"KAML_IMAGE_TAG\" to override it.".format(docker_image_tag))
  print("Kaml docker image: {}. Set environment variable \"INSTANCE_SIZE\" to override.".format(size))
  print("-----")
  print("Job Created: => {}".format(str(api_response.metadata.name)))

def get_parser():

    if len(sys.argv[1:])==0:
        sys.exit('No arguments have been passed. Exiting ...')

    # using sys.argv to get args since the both kaml-remote script and the k8s job needs to take arguments  
    job_args = sys.argv[1:]

    if environ.get('KAML_IMAGE') is not None:
        image = os.environ['KAML_IMAGE']
    else:
        image = 'gcr.io/kaml-dev/kaml'

    if environ.get('KAML_IMAGE_TAG') is not None:
        tag = os.environ['KAML_IMAGE_TAG']
    else:
        tag = 'develop'

    if environ.get('INSTANCE_SIZE') is not None:
        size = os.environ['INSTANCE_SIZE']
    else:
        size = 'small'

    return(job_args, size, image, tag)

def main():

  logging.basicConfig(stream=sys.stdout, level=logging.INFO)
  warnings.filterwarnings('ignore', 'Your application has authenticated using end user credentials')

  # Parse arguments
  job_arguments, size, docker_image, docker_image_tag = get_parser()

  # TODO Check contexts to ensure we are in the right project
  config.load_kube_config()
  api_instance = client.BatchV1Api()

  # Set affinity
  affinity = set_affinity(size)

  job = create_job_object(job_arguments, size, docker_image, docker_image_tag, affinity)

  run_job(api_instance, job, size, docker_image, docker_image_tag)

if __name__ == '__main__':
  main()
