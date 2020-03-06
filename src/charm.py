#!/usr/bin/env python3

import sys
sys.path.append('lib')

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus
from oci_image import OCIImageResource, ResourceError


class MetalLBSpeakerCharm(CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.speaker_image = OCIImageResource(self, 'speaker-image')
        self.framework.observe(self.on.install, self.set_pod_spec)
        self.framework.observe(self.on.upgrade_charm, self.set_pod_spec)

    def set_pod_spec(self, event):
        if not self.model.unit.is_leader():
            print('Not a leader, skipping set_pod_spec')
            self.model.unit.status = ActiveStatus()
            return

        try:
            speaker_details = self.speaker_image.fetch()
        except ResourceError as e:
            self.model.unit.status = e.status
            return

        self.model.unit.status = MaintenanceStatus('Setting pod spec')
        self.model.pod.set_spec({
            'version': 3,
            'containers': [{
                'name': 'metallb-speaker',
                'imageDetails': speaker_details,
                'command': ['/entrypoint.sh'],
                'args': [
                    '--port=7472',
                    '--config=config'
                ],
                'kubernetes': {
                    'securityContext': {
                        'allowPrivilegeEscalation': False,
                        'capabilities': {
                            'add': [
                              'NET_ADMIN',
                              'NET_RAW',
                              'SYS_ADMIN'
                            ],
                            'drop': [
                              'ALL'
                            ]
                        },
                        'readOnlyRootFilesystem': True
                    }
                }
            }],
            'serviceAccount': {
                'global': True,
                'rules': [
                    {
                        'apiGroups': [''],
                        'resources': [
                            'services',
                            'endpoints',
                            'nodes'
                        ],
                        'verbs': [
                            'get',
                            'list',
                            'watch'
                        ]
                    },
                    {
                        'apiGroups': [''],
                        'resources': [
                            'events'
                        ],
                        'verbs': [
                            'create',
                            'patch'
                        ]
                    },
                    {
                        'apiGroups': ['policy'],
                        'resources': [
                            'podsecuritypolicies'
                        ],
                        'verbs': [
                            'use'
                        ]
                    }
                ]
            },
            'kubernetesResources': {
                'pod': {
                    'hostNetwork': True
                },
                'customResourceDefinitions': {
                    'network-attachment-definitions.k8s.cni.cncf.io': {
                        'group': 'k8s.cni.cncf.io',
                        'scope': 'Namespaced',
                        'names': {
                            'plural': 'network-attachment-definitions',
                            'singular': 'network-attachment-definition',
                            'kind': 'NetworkAttachmentDefinition',
                            'shortNames': ['net-attach-def']
                        },
                        'versions': [{
                            'name': 'v1',
                            'served': True,
                            'storage': True
                        }],
                        'validation': {
                            'openAPIV3Schema': {
                                'type': 'object',
                                'properties': {
                                    'spec': {
                                        'type': 'object',
                                        'properties': {
                                            'config': {
                                                'type': 'string'
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })

        self.model.unit.status = ActiveStatus()


if __name__ == '__main__':
    main(MetalLBCharm)
