#!/bin/sh
# Build the frozen product snapshot; no install, daemon startup or device use.
set -eu
run=$1
stage=$run/staging_dir
source=$run/product
[ ! -e "$source" ]
mkdir "$source"
tar -xzf "$run/inputs/backend-build-input-v1.tar.gz" -C "$source"
export GOOS=linux GOARCH=amd64 GOAMD64=v1 GOTOOLCHAIN=local
export GOPROXY=off GOSUMDB=off GOFLAGS=-mod=vendor
export GOCACHE=$run/go-cache GOTMPDIR=$run/go-tmp
export STAGING_DIR=$stage/target-x86_64_musl
export CC=$stage/toolchain-x86_64_gcc-13.3.0_musl/bin/x86_64-openwrt-linux-musl-gcc
export CGO_CFLAGS="-O2 -pipe -fPIC -I$STAGING_DIR/usr/include"
export CGO_CPPFLAGS="-I$STAGING_DIR/usr/include"
export CGO_LDFLAGS="-L$STAGING_DIR/usr/lib -L$stage/toolchain-x86_64_gcc-13.3.0_musl/lib"
export PATH=$run/toolchain/go/bin:$PATH
cd "$source/backend"
for lane in first repeat; do
  mkdir "$run/product-bin-$lane"
  CGO_ENABLED=1 go build -buildvcs=false -trimpath -ldflags '-s -w -X main.releaseID=0.3.0-r82' \
    -o "$run/product-bin-$lane/lighthost" ./cmd/lighthost
  CGO_ENABLED=0 go build -buildvcs=false -trimpath -ldflags '-s -w' \
    -o "$run/product-bin-$lane/lighthost-vm-pilot-policy" ./cmd/lighthost-vm-pilot-policy
  (cd "$run/product-bin-$lane" && sha256sum *) > "$run/logs/product-$lane.sha256"
done
cmp "$run/logs/product-first.sha256" "$run/logs/product-repeat.sha256"
file "$run/product-bin-first/"*
readelf -d "$run/product-bin-first/lighthost" > "$run/logs/lighthost.dynamic.txt"
readelf -l "$run/product-bin-first/lighthost" > "$run/logs/lighthost.program.txt"
printf 'product_two_builds=BYTE_IDENTICAL\n'
