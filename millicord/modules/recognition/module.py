import os
from discord import Message, Attachment
import imghdr
from io import BytesIO

from millicord.utils.module_base import IdolModuleBase
from millicord import modules as M
from millicord.utils.idol_exceptions import IdolConfigError
from .idol_recognition import IdolRecognition

import numpy as np
import cv2
from PIL import Image


class FaceRecognitionModule(IdolModuleBase):
    MODULE_REQUIREMENTS = {
        M.OnMentionedModule,
        M.IdolStateModule
    }

    DEFAULT_CONFIG = {
        "model_path": None,
        "cascade_path": None,
        "classes_path": None,
        "model_name": None,
        "label_translator": None
    }

    DEFAULT_SCRIPT = {
        "message_response": "{label} appeared in the picture.",
        "mention_response": "{label} appeared in the picture.",
    }

    def __init__(self):
        self.chain_super_function("__init__", FaceRecognitionModule)()
        self.model = self.init_model()
        self.label_translator = self.find_config(
            FaceRecognitionModule, "label_translator")

    def translate_label(self, label):
        if self.label_translator is None:
            return label
        return self.label_translator.get(label)

    def init_model(self):
        model_path = self.find_config(FaceRecognitionModule, "model_path")
        if not os.path.exists(model_path):
            raise IdolConfigError(f"Model file {model_path} not found.")
        cascade_path = self.find_config(FaceRecognitionModule, "cascade_path")
        if not os.path.exists(cascade_path):
            raise IdolConfigError(f"Cascade file {cascade_path} not found.")
        classes_path = self.find_config(FaceRecognitionModule, "classes_path")
        if not os.path.exists(classes_path):
            raise IdolConfigError(f"Class file {classes_path} not found.")
        model_name = self.find_config(FaceRecognitionModule, "model_name")
        return IdolRecognition(
            model_name=model_name,
            model_path=model_path,
            cascade_path=cascade_path,
            classes_path=classes_path
        )

    async def on_message(self, message: Message):
        """
        busyならメッセージを無視するようにするコルーチン

        Parameters
        ----------
        message : Message
        """
        if self.is_busy():
            return
        predicted = None
        attachments = list(self.extract_png_attachments(message))
        if len(attachments) > 0:
            predicted = self.translate_label(self.predict(attachments[0]))
        if predicted:
            script = self.find_script(FaceRecognitionModule, 'on_mentioned')
            script = script.format(label=predicted)
            await self.send_message(message.channel, script, message.author.id)
            return
        sc = self.chain_super_coroutine('on_message', FaceRecognitionModule)
        await sc(message)

    async def on_mentioned(self, message: Message):
        """
        mentionを受けたとき、busyなら謝って断るモジュール

        Parameters
        ----------
        message : Message
        """
        predicted = None
        attachments = await self.extract_png_attachments(message)
        if len(attachments) > 0:
            predicted = self.translate_label(await self.predict(attachments[0]))
        if predicted:
            script = self.find_script(
                FaceRecognitionModule, 'mention_response')
            script = script.format(label=predicted)
            await self.send_message(message.channel, script, message.author.id)
            return
        sc = self.chain_super_coroutine('on_mentioned', FaceRecognitionModule)
        await sc(message)

    async def extract_png_attachments(self, message: Message):
        s = BytesIO()
        rets = []
        for attachment in message.attachments:
            s.flush()
            await attachment.save(s, seek_begin=True)
            if imghdr.what(None, h=s.getvalue()) in ["png", "jpeg"]:
                rets.append(attachment)
        return rets

    async def predict(self, attachment: Attachment):
        s = BytesIO()
        # self.model.get_image(attachment.url)
        await attachment.save(s, seek_begin=True)
        image_array = np.asarray(bytearray(s.getvalue()), dtype="uint8")
        image = Image.fromarray(cv2.imdecode(image_array, cv2.IMREAD_COLOR))
        faces = self.model.triming_face(image)
        predicted = self.model.predict_faces(faces)
        # print([self.model.classes[res] for res in predicted])
        for res in predicted:
            idol_name = self.model.classes[res]
            if self.translate_label(idol_name) is not None:
                return idol_name
        return None
