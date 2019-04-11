#!/usr/bin/env bash

tag=vrdp:$USER
name=vrdp_$USER
target=base
data=
run=/var/run/nginx
unix=$run/vrdp.is.mediocreatbest.xyz.sock
registry=
xauth=
entrypoint=
ipc=
net=
user=1
cwd=1
interactive=1
script=
port=8800
restart=unless-stopped

build() {
	docker build \
		${target:+--target $target} \
		-t $tag .
}

run() {
	if [ -n "$xauth" ]; then
		rm -f $xauth
		xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $xauth nmerge -
	fi
	docker run --rm \
		${interactive:+-it} \
		${script:+-a stdin -a stdout -a stderr --sig-proxy=true} \
		${ipc:+--ipc=$ipc} \
		${net:+--net=$net} \
		${user:+-u $(id -u):$(id -g)} \
		${cwd:+-v $PWD:$PWD -w $PWD} \
		${port:+-p $port:$port} \
		${data:+-v $data:$data} \
		${run:+-v $run:$run} \
		${xauth:+-e DISPLAY -v /etc/group:/etc/group:ro -v /etc/passwd:/etc/passwd:ro -v /etc/shadow:/etc/shadow:ro -v /etc/sudoers.d:/etc/sudoers.d:ro -v $xauth:$xauth -e XAUTHORITY=$xauth} \
		${entrypoint:+--entrypoint $entrypoint} \
		$tag "$@"
}

inspect() {
	entrypoint='/bin/bash -i' run "$@"
}

script() {
	interactive= script=1 run "$@"
}

start() {
	target=dist build && \
	docker run -d \
		${restart:+--restart $restart} \
		${name:+--name $name} \
		${data:+-v $data:$data} \
		${run:+-v $run:$run} \
		$tag \
		unix --bind $unix
}

stop() {
	docker stop $name "$@" && docker rm $name
}

push() {
	docker tag $tag $registry/$tag
	docker push $registry/$tag
}

create() {
	docker service create \
		--name $name \
		--mount type=bind,src=$PWD,dst=$PWD \
		${data:+--mount type=bind,src=$data,dst=$data} \
		$registry/$tag "$@"
}

destroy() {
	docker service rm $name
}

logs() {
	docker service logs $name "$@"
}

python() { python3 "$@"; }
python3() { python3.7 "$@"; }
python3.7() { run python3.7 "$@"; }

tcp() {
	python server.py tcp --port $port "$@"
}

unix() {
	python server.py unix --bind $unix "$@"
}

"$@"
