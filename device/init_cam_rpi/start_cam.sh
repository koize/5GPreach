#!/bin/bash

raspivid -o - -t 0 -w 640 -h 480 -fps 90 -n | cvlc -vvv
stream:///dev/stdin --sout &#39;#rtp{sdp=rtsp://:8080/}&#39; :demux=h264