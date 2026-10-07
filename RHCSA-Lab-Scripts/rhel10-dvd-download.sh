#!/bin/bash
# RHEL downloads require a personal entitlement. No hardcoded credentials.
set -euo pipefail
printf '%s\n' 'Download the aarch64 DVD ISO through your Red Hat account:' \
 'https://developers.redhat.com/products/rhel/download' \
 'Or download Rocky Linux 10 aarch64 DVD and verify the published SHA256:' \
 'https://rockylinux.org/download' \
 'Use that local DVD with fusion-lab.py --iso. Boot/minimal ISOs lack the package trees.'
