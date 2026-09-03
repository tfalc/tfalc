#!/bin/sh
# Broader env filter: match by name or email containing 'github-actions'
if echo "$GIT_AUTHOR_NAME" | grep -qi "github-actions" || echo "$GIT_AUTHOR_EMAIL" | grep -qi "github-actions" ; then
  export GIT_AUTHOR_NAME='Thiago Falcão da Silva'
  export GIT_AUTHOR_EMAIL='thiago.falcao86@gmail.com'
fi
if echo "$GIT_COMMITTER_NAME" | grep -qi "github-actions" || echo "$GIT_COMMITTER_EMAIL" | grep -qi "github-actions" ; then
  export GIT_COMMITTER_NAME='Thiago Falcão da Silva'
  export GIT_COMMITTER_EMAIL='thiago.falcao86@gmail.com'
fi
