#!/bin/bash

tree -tf -L 1 -F --noreport --charset ascii -P \*.md $1 | \
  sed -e 1d -e 's/| \+/  /g' -e 's/[|`]-\+/*/g' -e 's:\(* \)\(\(.*/\)\(.\+\)\):\1[\4](\2):g' -e 's:.md]:]:g'
