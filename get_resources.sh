
RESOUCES_DIR="./resources"
CASCADE_DIR="${RESOUCES_DIR}/cv2_cascade"
MODELS_DIR="${RESOUCES_DIR}/models"

if [ ! -e "${CASCADE_DIR}" ] ; then
    mkdir -p "${CASCADE_DIR}"
fi

curl -kL "https://github.com/nagadomi/lbpcascade_animeface/raw/master/lbpcascade_animeface.xml" -o "${CASCADE_DIR}/lbpcascade_animeface.xml"

if [ ! -e "${MODELS_DIR}" ] ; then
    mkdir -p "${MODELS_DIR}"
fi

