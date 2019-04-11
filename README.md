# Virtual Reality Remote Desktop Viewer

This is a demo of a simple remote desktop viewer using WebRTC and WebVR (so, no cables and no installs). The end goal is to be able to situate the virtual monitors in a relaxing virtual environment, like in the woods or at a beach.

[Live Demo](https://vrdp.is.mediocreatbest.xyz)

## Running a Local Instance

This project uses Docker, but all of that is hidden away in the `go.sh` script. To build and run the demo, use:

```console
$ ./go.sh build
$ ./go.sh tcp
```

This will build the Docker image and then run a TCP server on port 8800. Then you can connect to your instance at http://localhost:8800. If you want to run this on a remote server, then due to WebRTC restrictions, you'll need to have an HTTPS certificate. Running on localhost should _just work_ :tm:.
