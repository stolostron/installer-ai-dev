#!/bin/bash
set -e

echo "installer-ai-dev" > /home/botuser/app/.instance-id

# Custom DNF installs must pin UBI repos; Dockerfile repo flags do not carry here.
# dnf --disableplugin=subscription-manager --disablerepo='*' --enablerepo='ubi-*' install -y --nodocs <package>

# --- envtest assets -------------------------------------------------------
# The Installer squad repos run `make test` through controller-runtime envtest,
# which needs etcd + kube-apiserver + kubectl binaries at runtime. The `go`
# env preset ships Go and golangci-lint only, so pre-populate the setup-envtest
# asset store during the build. Versions mirror each repo's ENVTEST_K8S_VERSION:
#   multiclusterhub-operator 1.30
#   backplane-operator       1.35.0
#   discovery                1.25
ENVTEST_STORE=/home/botuser/.local/share/kubebuilder-envtest/k8s
ENVTEST_VERSIONS="1.35.0 1.30.0 1.25.0"

mkdir -p "${ENVTEST_STORE}"
for version in ${ENVTEST_VERSIONS}; do
  target="${ENVTEST_STORE}/${version}-linux-amd64"
  if [ -d "${target}" ]; then
    continue
  fi

  tmpdir="$(mktemp -d)"
  url="https://github.com/kubernetes-sigs/controller-tools/releases/download/envtest-v${version}/envtest-v${version}-linux-amd64.tar.gz"

  if ! curl -fsSL "${url}" -o "${tmpdir}/envtest.tar.gz"; then
    echo "WARNING: no envtest release for ${version}; ${url}" >&2
    rm -rf "${tmpdir}"
    continue
  fi

  tar -xzf "${tmpdir}/envtest.tar.gz" -C "${tmpdir}"
  mkdir -p "${target}"
  for binary in etcd kube-apiserver kubectl; do
    src="$(find "${tmpdir}" -type f -name "${binary}" | head -n 1)"
    if [ -z "${src}" ]; then
      echo "WARNING: ${binary} missing from envtest-v${version} archive" >&2
      continue
    fi
    install -m 0755 "${src}" "${target}/${binary}"
  done
  rm -rf "${tmpdir}"
done

chown -R botuser:botuser /home/botuser/.local/share/kubebuilder-envtest 2>/dev/null || true

# --- setup-envtest --------------------------------------------------------
# Repos build this into ./bin on demand, but not every cycle has a reachable
# module proxy. Provide a shared copy on PATH as a fallback.
if command -v go >/dev/null 2>&1; then
  GOBIN=/usr/local/bin go install sigs.k8s.io/controller-runtime/tools/setup-envtest@release-0.19 || \
    echo "WARNING: setup-envtest install failed; repos will fetch it at cycle time" >&2
else
  echo "WARNING: go not on PATH during setup.sh; skipping setup-envtest install" >&2
fi

echo "Instance setup complete: installer-ai-dev"
