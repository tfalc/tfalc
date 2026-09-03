#!/bin/sh
# Rewrite env filter: set author & committer to Thiago
TARGET_NAME="Thiago Falcão da Silva"
TARGET_EMAIL="thiago.falcao86@gmail.com"

# If author or committer differ, set them to target
export GIT_AUTHOR_NAME="$TARGET_NAME"
export GIT_AUTHOR_EMAIL="$TARGET_EMAIL"
export GIT_COMMITTER_NAME="$TARGET_NAME"
export GIT_COMMITTER_EMAIL="$TARGET_EMAIL"

# Done
