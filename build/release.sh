#!/usr/bin/env bash
cd ..
if [[ -d target/ubuntu ]]
then
	echo "Remove target/ubuntu directory before running, it's probably owned by root due to docker"
	exit 1
fi


mkdir releases/$1

# build ubuntu
fbs buildvm ubuntu

# build docker run command identical to fbs, but sneakily inject our own bashrc
docker_run="docker run -it"
for i in `ls -A | grep -v target` ; do
 docker_run="$docker_run -v `readlink -f $i`:/root/cadmus/$i"
done
docker_run="$docker_run -v `readlink -f ./target/ubuntu`:/root/cadmus/target -v `readlink -f ./build/.bashrc`:/root/.bashrc cadmus/ubuntu "
echo $docker_run
eval $docker_run

# copy artifacts to released directory
cp target/ubuntu/cadmus.deb releases/$1
cd target/ubuntu
zip -r ../../releases/$1/cadmus.zip cadmus
cd ../../

# build AppImage
cd build
git clone https://github.com/AppImage/pkg2appimage.git
cp Cadmus.yml ./pkg2appimage/recipes
cd pkg2appimage
cp ../../releases/$1/cadmus.deb .
./pkg2appimage recipes/Cadmus.yml
cp out/* ../../releases/$1/cadmus.AppImage
cd ..
rm -rf pkg2appimage
echo "Release artifacts are in: ../releases/$1"

# todo: create GitHub release & upload artifats