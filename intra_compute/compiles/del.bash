#!/bin/bash
for file in *.cu.out; do
  if [[ -x "$file" && ! -d "$file" ]]; then
    ./"$file"
  fi
done

