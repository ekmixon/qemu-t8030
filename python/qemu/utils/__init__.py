"""
QEMU development and testing utilities

This package provides a small handful of utilities for performing
various tasks not directly related to the launching of a VM.
"""

# Copyright (C) 2021 Red Hat Inc.
#
# Authors:
#  John Snow <jsnow@redhat.com>
#  Cleber Rosa <crosa@redhat.com>
#
# This work is licensed under the terms of the GNU GPL, version 2.  See
# the COPYING file in the top-level directory.
#

import re
from typing import Optional

# pylint: disable=import-error
from .accel import kvm_available, list_accel, tcg_available


__all__ = (
    'get_info_usernet_hostfwd_port',
    'kvm_available',
    'list_accel',
    'tcg_available',
)


def get_info_usernet_hostfwd_port(info_usernet_output: str) -> Optional[int]:
    """
    Returns the port given to the hostfwd parameter via info usernet

    :param info_usernet_output: output generated by hmp command "info usernet"
    :return: the port number allocated by the hostfwd option
    """
    regex = r'TCP.HOST_FORWARD.*127\.0\.0\.1\s+(\d+)\s+10\.'
    for line in info_usernet_output.split('\r\n'):
        match = re.search(regex, line)
        if match is not None:
            return int(match[1])
    return None
