#!/usr/bin/env bash

set -euo pipefail

show_help() {
  cat << EOS
Get resources for face recognintion.

Usage: $0 [options]

Options:
  -h, --help                           Print help info
  -f, --force                          Force update the resources
EOS
}
for OPT in "$@"
do
  case $OPT in
    -h | --help)
      show_help
      exit 1
    ;;
    -f | --force)
      force_update=true
      shift 1
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

force_update=${force_update-false}

SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 && pwd)"
PROJECT_ROOT="${SCRIPTS_DIR}/.."

RESOUCES_DIR="${PROJECT_ROOT}/resources"
CASCADE_DIR="${RESOUCES_DIR}/cv2_cascade"
MODELS_DIR="${RESOUCES_DIR}/models"
GOOGLE_DRIVE_ENDPOINT="https://drive.google.com/uc?export=download&id="


if [ -z "${CLASSES_URL+UNDEF}" -o -z "${DENSENET_URL+UNDEF}" -o -z "${RESNET_URL+UNDEF}" ] ; then
    echo "environment variables CLASSES_URL or DENSENET_URL or RESNET_URL missing"
    exit 1
fi

if [ ! -e "${CASCADE_DIR}" ] ; then
    mkdir -p "${CASCADE_DIR}"
fi

if [ ! -e "${CASCADE_DIR}/lbpcascade_animeface.xml" ] || "${force_update}" ; then
  curl -skL "https://github.com/nagadomi/lbpcascade_animeface/raw/master/lbpcascade_animeface.xml" -o "${CASCADE_DIR}/lbpcascade_animeface.xml"
fi

if [ ! -e "${MODELS_DIR}" ] ; then
    mkdir -p "${MODELS_DIR}"
fi

# download classes
if [ ! -e "${MODELS_DIR}/idol_recognition_classes.txt" ] || "${force_update}" ; then
  curl -skL "${GOOGLE_DRIVE_ENDPOINT}${CLASSES_URL}" -o "${MODELS_DIR}/idol_recognition_classes.txt"
fi
# download densenet model
if [ ! -e "${MODELS_DIR}/idol_recognition_densenet.model" ] || "${force_update}" ; then
  curl -skL "${GOOGLE_DRIVE_ENDPOINT}${DENSENET_URL}" -o "${MODELS_DIR}/idol_recognition_densenet.model"
fi
# download resnet model
if [ ! -e "${MODELS_DIR}/idol_recognition_resnet.model" ] || "${force_update}" ; then
  curl -skL "${GOOGLE_DRIVE_ENDPOINT}${RESNET_URL}" -o "${MODELS_DIR}/idol_recognition_resnet.model"
fi