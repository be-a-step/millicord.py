
RESOUCES_DIR="./resources"
CASCADE_DIR="${RESOUCES_DIR}/cv2_cascade"
MODELS_DIR="${RESOUCES_DIR}/models"
GOOGLE_DRIVE_ENDPOINT="https://drive.google.com/uc?export=download&id="

if [ -z "${CLASSES_URL}" -o -z "${DENSENET_URL}" -o -z "${RESNET_URL}" ] ; then
    echo "environment variables CLASSES_URL or DENSENET_URL or RESNET_URL missing"
    exit 1
fi

if [ ! -e "${CASCADE_DIR}" ] ; then
    mkdir -p "${CASCADE_DIR}"
fi

curl -kL "https://github.com/nagadomi/lbpcascade_animeface/raw/master/lbpcascade_animeface.xml" -o "${CASCADE_DIR}/lbpcascade_animeface.xml"

if [ ! -e "${MODELS_DIR}" ] ; then
    mkdir -p "${MODELS_DIR}"
fi

# download classes
curl -kL "${GOOGLE_DRIVE_ENDPOINT}${CLASSES_URL}" -o "${MODELS_DIR}/idol_recognition_classes.txt"
# download densenet model
curl -kL "${GOOGLE_DRIVE_ENDPOINT}${DENSENET_URL}" -o "${MODELS_DIR}/idol_recognition_densenet.model"
# download resnet model
curl -kL "${GOOGLE_DRIVE_ENDPOINT}${RESNET_URL}" -o "${MODELS_DIR}/idol_recognition_resnet.model"
