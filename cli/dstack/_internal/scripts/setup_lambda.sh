#!/bin/bash
set -e
RUNNER_VERSION=${RUNNER_VERSION:-latest}

function install_stgn {
  sudo curl --output /usr/local/bin/dstack-runner "https://dstack-runner-downloads-stgn.s3.eu-west-1.amazonaws.com/${RUNNER_VERSION}/binaries/dstack-runner-linux-amd64"
  sudo chmod +x /usr/local/bin/dstack-runner
  dstack-runner --version
}

function install_prod {
  sudo curl --output /usr/local/bin/dstack-runner "https://dstack-runner-downloads.s3.eu-west-1.amazonaws.com/latest/binaries/dstack-runner-linux-amd64"
  sudo chmod +x /usr/local/bin/dstack-runner
  dstack-runner --version
}

if [[ $DSTACK_STAGE == "PROD" ]]; then
  install_prod
else
  install_stgn
fi