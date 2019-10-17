#!/usr/bin/env bash
#
# Copyright 2017 The Cockroach Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License. See the AUTHORS file
# for names of contributors.
#
# Author: Nikhil Benesch (nikhil.benesch@gmail.com)

# This file is largely cargo-culted from cockroachdb/cockroach/build/builder.sh.

set -euo pipefail

image=cockroachdb/cockroach-django-builder:latest

gopath=$(go env GOPATH)
gopath0=${gopath%%:*}

# Absolute path to this repository.
repo_root=$(cd "$(dirname "${0}")" && pwd)

# Make a fake passwd file for the invoking user.
#
# This setup is so that files created from inside the container in a mounted
# volume end up being owned by the invoking user and not by root.
# We'll mount a fresh directory owned by the invoking user as /root inside the
# container because the container needs a $HOME (without one the default is /)
# and because various utilities (e.g. bash writing to .bash_history) need to be
# able to write to there.
username=$(id -un)
uid_gid=$(id -u):$(id -g)
container_root=${repo_root}/docker_root
mkdir -p "${container_root}"/{etc,home,home/"${username}"/go/src}
echo "${username}:x:${uid_gid}::/home/${username}:/bin/bash" > "${container_root}/etc/passwd"

exec docker run \
  --volume="${container_root}/etc/passwd:/etc/passwd" \
  --volume="${container_root}/home/${username}:/home/${username}" \
  --volume="${repo_root}:${repo_root}" \
  --workdir="${repo_root}" \
  --env=PIP_USER=1 \
  --env=GEM_HOME="/home/${username}/.gems" \
  --user="${uid_gid}" \
  "$image" \
  "$@"
