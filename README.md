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

## License

The MIT License (MIT)

Copyright (c) 2019 Tanner Hobson

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
