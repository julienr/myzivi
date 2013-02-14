#!/bin/bash
# Make the remote sentry available on local port 9000
ssh -L 9000:localhost:62155 myzivi@s8.wservices.ch
