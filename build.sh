#!/bin/sh
# Build K2 from your own copy of the demo:
#     ./build.sh K2.zip             (or K2, the Spark archive off Acorn User CD 6)
# then: cd recomp && ./k2
# The steps are recipe.json's "build", run by SuperSpider's tools/weave.py.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
SUPERSPIDER="${SUPERSPIDER:-$HOME/stuff/superspider}"
[ $# -gt 0 ] || { echo "usage: $0 K2.zip | K2 | !k2-directory" >&2; exit 2; }
(cd "$SUPERSPIDER" && dune build)
WEAVE_RECIPES="$HERE" exec python3 -I "$SUPERSPIDER/tools/weave.py" build "$@"
