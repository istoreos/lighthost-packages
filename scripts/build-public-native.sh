#!/bin/sh
# Builds public upstream Incus plus pinned LightHost native patches in an owned
# builder directory. Never installs packages, starts a daemon or touches devices.
set -eu
run=$1
case "$run" in /builders/projects/lighthost/work/public-feed-inputs-*) ;; *) exit 2 ;; esac
stage=$run/staging_dir
source=$run/incus
compiler=$stage/toolchain-x86_64_gcc-13.3.0_musl/bin/x86_64-openwrt-linux-musl-gcc
[ ! -e "$source" ]
printf '%s  %s\n' 129a1323605d427c46c8358844f5f9447d7e2cebe0f4ada242c93cf002fb44ea "$run/inputs/incus-6.0.6.tar.xz" | sha256sum -c -
curl --fail --location --retry 3 https://dl.google.com/go/go1.25.14.linux-amd64.tar.gz -o "$run/inputs/go1.25.14.linux-amd64.tar.gz"
printf '%s  %s\n' a21ae5633a269bcd7e90cf767e48225633795e99d831742cbf3397064fee7712 "$run/inputs/go1.25.14.linux-amd64.tar.gz" | sha256sum -c -
mkdir "$source" "$run/toolchain"
tar -xJf "$run/inputs/incus-6.0.6.tar.xz" --strip-components=1 -C "$source"
tar -xzf "$run/inputs/go1.25.14.linux-amd64.tar.gz" -C "$run/toolchain"
for patch_file in "$run"/inputs/native-patches/*.patch; do
  patch -d "$source" -p1 --batch --forward < "$patch_file"
done
export STAGING_DIR=$stage/target-x86_64_musl
export STAGING_DIR_HOST=$stage/host
export STAGING_DIR_HOSTPKG=$stage/hostpkg
export STAGING_PREFIX=$STAGING_DIR/usr
export PKG_CONFIG_LIBDIR=$STAGING_DIR/usr/lib/pkgconfig
export PKG_CONFIG=$STAGING_DIR_HOST/bin/pkg-config
export PATH=$run/toolchain/go/bin:$STAGING_DIR_HOST/bin:$PATH
export GOOS=linux GOARCH=amd64 GOAMD64=v1 GOTOOLCHAIN=local
export GOPROXY=off GOSUMDB=off GOFLAGS=-mod=vendor
export GOCACHE=$run/go-cache GOTMPDIR=$run/go-tmp
export CC=$compiler CXX=$stage/toolchain-x86_64_gcc-13.3.0_musl/bin/x86_64-openwrt-linux-musl-g++
export CGO_CFLAGS="-O2 -pipe -fPIC -Wno-error=format-nonliteral -I$STAGING_DIR/usr/include"
export CGO_CPPFLAGS="-I$STAGING_DIR/usr/include"
export CGO_LDFLAGS="-L$STAGING_DIR/usr/lib -L$stage/toolchain-x86_64_gcc-13.3.0_musl/lib"
export CGO_LDFLAGS_ALLOW='(-Wl,-wrap,pthread_create)|(-Wl,-z,now)'
mkdir "$GOCACHE" "$GOTMPDIR"
cd "$source"
for lane in first repeat; do
  mkdir "$run/bin-$lane"
  for program in incus incusd; do
    CGO_ENABLED=1 go build -buildvcs=false -trimpath -tags libsqlite3 \
      -ldflags '-s -w -X github.com/lxc/incus/v6/internal/version.Version=6.0.6-lighthost.public.20261014' \
      -o "$run/bin-$lane/$program" "./cmd/$program"
  done
  CGO_ENABLED=0 go build -buildvcs=false -trimpath -tags agent,netgo \
    -ldflags '-s -w -X github.com/lxc/incus/v6/internal/version.Version=6.0.6-lighthost.public.20261014' \
    -o "$run/bin-$lane/incus-agent" ./cmd/incus-agent
  (cd "$run/bin-$lane" && sha256sum incus incusd incus-agent) > "$run/logs/native-$lane.sha256"
done
cmp "$run/logs/native-first.sha256" "$run/logs/native-repeat.sha256"
file "$run/bin-first/"*
for program in incus incusd; do
  readelf -d "$run/bin-first/$program" > "$run/logs/$program.dynamic.txt"
  readelf -l "$run/bin-first/$program" > "$run/logs/$program.program.txt"
done
printf 'native_two_builds=BYTE_IDENTICAL\n'
