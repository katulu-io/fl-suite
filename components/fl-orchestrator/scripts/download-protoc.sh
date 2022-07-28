#!/usr/bin/env sh

set -o errexit
set -o nounset

version=$1

os=$(uname -s)
case $os in
	Darwin) os="osx" ;;
	Linux) os="linux" ;;
esac

arch=$(uname -m)
case arch in
	x86) arch="x86_32" ;;
	i686) arch="x86_32" ;;
	i386) arch="x86_32" ;;
	aarch64) arch="aarch_64" ;;
esac

curl -LO "https://github.com/protocolbuffers/protobuf/releases/download/v${version}/protoc-${version}-${os}-${arch}.zip"
unzip "protoc-${version}-${os}-${arch}.zip" bin/protoc
rm "protoc-${version}-${os}-${arch}.zip"
