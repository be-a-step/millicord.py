
set -euo pipefail

show_help() {
  cat << EOS
Get resources for face recognintion.

Usage: $0 [options]

Options:
  -h, --help                           Print help info
  -f, --force                          Force update the resources
  -t, --target                         Target stage. Default: release. (develop|release)
EOS
}

declare -a get_resource_args=()

while (( $# > 0 ))
do
  case "$1" in
    -h | --help)
      show_help
      exit 1
    ;;
    -f | --force)
      get_resource_args=( "${get_resource_args[@]}" -f )
      shift 1
    ;;
    -t | --target)
      if [[ -z "$2" ]] || [[ "$2" =~ ^-+ ]]; then
        echo "option requires an argument: $1"
        exit 1
      fi
      target="$2"
      shift 2
    ;;
    -- | -)
      shift 1
      param+=( "$@" )
      break
    ;;
    -*)
      echo "illegal option: $1"
      exit 1
    ;;
    *)
      if [[ ! -z "$1" ]] && [[ ! "$1" =~ ^-+ ]]; then
        echo "illegal argument: $1"
        show_help
        exit 1
      fi
    ;;
  esac
done

SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 && pwd)"

echo "===== Get resources ====="
PROJECT_ROOT="${SCRIPTS_DIR}/.."

. "${PROJECT_ROOT}/.env"
"${SCRIPTS_DIR}/get_resources.sh" ${get_resource_args[@]}

echo "==== Build docker ====="
if [ -z "${target+UNDEF}" ] ; then
  target=release
fi
docker build -t millicord:${target} "${PROJECT_ROOT}" --target ${target}
