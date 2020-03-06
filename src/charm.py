#!/usr/bin/env python3

import sys
sys.path.append('lib')

import yaml
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

    @staticmethod
    def _get_pod_spec(config={}):
        with open('metallb.yaml') as f_in:
            spec = yaml.load(f_in)
            spec.update(config)
            return spec

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
        self.model.pod.set_spec(self._get_pod_spec())

        self.model.unit.status = ActiveStatus()


if __name__ == '__main__':
    main(MetalLBCharm)
