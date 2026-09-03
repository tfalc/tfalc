#!/bin/sh
# Env filter to rewrite author/committer for github-actions[bot]
if [ "$GIT_AUTHOR_EMAIL" = "github-actions[bot]@users.noreply.github.com" ]; then
  export GIT_AUTHOR_NAME='Thiago Falcão da Silva'
  export GIT_AUTHOR_EMAIL='thiago.falcao86@gmail.com'
  export GIT_COMMITTER_NAME='Thiago Falcão da Silva'
  export GIT_COMMITTER_EMAIL='thiago.falcao86@gmail.com'
fi
