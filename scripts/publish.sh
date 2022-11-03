#!/bin/bash

set -e 

./scripts/build.sh
docker push tom010/epub_to_markdown
