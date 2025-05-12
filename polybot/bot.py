import requests  # for HTTP call to Yolo service
import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
from polybot.img_proc import Img

user_sessions = {}


class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])


class ImageProcessingBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        chat_id = msg['chat']['id']
        user_id = msg['from']['id']
        text = msg.get('text', '')
        caption = msg.get('caption', '')
        user_input = text.lower() if text else caption.lower() if caption else ""
        session = user_sessions.get(user_id, {'images': [], 'awaiting_direction': False})

        # in case the image is sent
        if self.is_current_msg_photo(msg):
            try:
                img_path = self.download_user_photo(msg)
                session['images'].append(img_path)
                user_sessions[user_id] = session
            except Exception as e:
                logger.error(f"Error downloading user photo: {e}")
                self.send_text(chat_id, f"Error while downloading the image: {e}")
                return

        # segment
        if user_input == "segment":
            try:
                logger.info(f"Applying segment for user {user_id}")
                img = Img(session['images'][0])
                img.segment()
                new_path = img.save_img()
                session['images'][-1] = new_path  # update the path in session
                self.send_photo(chat_id, str(new_path))
            except Exception as e:
                self.send_text(chat_id, f"Error while segmenting image: {e}")
            finally:
                user_sessions[user_id] = session
            return

        # concat
        if user_input == "concat":
            if len(session['images']) < 2:
                self.send_text(chat_id, "Please send at least 2 images")
                return
            logger.info(f"Applying concat for user {user_id}")
            session['awaiting_direction'] = True
            user_sessions[user_id] = session
            self.send_text(chat_id, "Which direction? Type *horizontal* or *vertical*.", parse_mode='Markdown')
            return

        # direction input
        if session.get('awaiting_direction'):
            direction = text.lower()
            if direction not in ('horizontal', 'vertical'):
                self.send_text(chat_id, "Please type *horizontal* or *vertical*.", parse_mode='Markdown')
                return
            try:
                img1 = Img(session['images'][0])
                img2 = Img(session['images'][1])
                img1.concat(img2, direction)
                new_path = img1.save_img()
                self.send_photo(chat_id, str(new_path))
            except Exception as e:
                logger.error(f"Error applying concat: {e}")
                self.send_text(chat_id, f"Error while concatenating: {e}")
            finally:
                user_sessions[user_id] = session
            return

        # rotate
        if user_input == "rotate":
            if not session["images"]:
                self.send_text(chat_id, "Please send an image first!")
                return
            try:
                logger.info(f"AppLying rotate for user {user_id}")
                img = Img(session['images'][-1])  # for loading the latest image
                img.rotate()
                new_path = img.save_img()
                session['images'][-1] = new_path  # update the path in session
                self.send_photo(chat_id, str(new_path))
            except Exception as e:
                logger.error(f"Error applying rotate: {e}")
                self.send_text(chat_id, f"Error while rotating: {e}")
            finally:
                user_sessions[user_id] = session
            return

        # salt_n_pepper
        if user_input == "salt and pepper":
            if not session["images"]:
                self.send_text(chat_id, "Please send an image first!")
                return
            try:
                logger.info(f"Applying salt_n_pepper for user {user_id}")
                img = Img(session['images'][-1])  # load the latest image
                img.salt_n_pepper()
                new_path = img.save_img()
                session['images'][-1] = new_path  # update the path in session
                self.send_photo(chat_id, str(new_path))
            except Exception as e:
                logger.error(f"Error applying salt_n_pepper: {e}")
                self.send_text(chat_id, f"Error while adding noise to the image: {e}")
            finally:
                user_sessions[user_id] = session
            return

        # blur
        if user_input == "blur":
            if not session["images"]:
                self.send_text(chat_id, "Please send an image first!")
                return
            try:
                logger.info(f"Applying blur for user {user_id}")
                img = Img(session['images'][-1])
                img.blur()
                new_path = img.save_img()
                session['images'][-1] = new_path
                self.send_photo(chat_id, str(new_path))
            except Exception as e:
                logger.error(f"Error applying blur: {e}")
                self.send_text(chat_id, f"Error while blurring the image: {e}")
            finally:
                user_sessions[user_id] = session
            return

        # contour
        if user_input == "contour":
            if not session["images"]:
                self.send_text(chat_id, "Please send an image first!")
                return
            try:
                logger.info(f"Applying contour for user {user_id}")
                img = Img(session['images'][-1])
                img.contour()
                new_path = img.save_img()
                session['images'][-1] = new_path
                self.send_photo(chat_id, str(new_path))
            except Exception as e:
                logger.error(f"Error applying contour: {e}")
                self.send_text(chat_id, f"Error while applying contour to the image: {e}")
            finally:
                user_sessions[user_id] = session
            return

        # detect
        if user_input == "detect":
            if not session["images"]:
                self.send_text(chat_id, "Please send an image first!")
                return

            ENV = os.environ.get("ENV", "dev").lower()
            if ENV == "prod":
                yolo_ip = os.environ.get("YOLO_PRIVATE_IP")
                if not yolo_ip:
                    logger.error("YOLO_PRIVATE_IP not set in prod environment.")
                    self.send_text(chat_id, "Server error: YOLO IP not configured.")
                    return
                yolo_url = f"http://{yolo_ip}:8080/predict"
            else:
                yolo_url = "http://localhost:8080/predict"

            image_path = session["images"][-1]

            try:
                logger.info(f"Sending image to YOLO server: {image_path}")
                with open(image_path, 'rb') as img_file:
                    response = requests.post(
                        yolo_url,
                        files={"file": ("image.jpg", img_file, "image/jpeg")},
                        timeout=10
                    )
                    response.raise_for_status()
                    result = response.json()
                    objects = result.get("labels", [])
                    if not objects:
                        self.send_text(chat_id, "No objects detected in the image.")
                    else:
                        detected_list = ", ".join(objects)
                        self.send_text(chat_id, f"Detected objects: {detected_list}")
                # self.send_photo(chat_id, str(image_path))
            except Exception as e:
                logger.error(f"Error calling YOLO server: {e}")
                self.send_text(chat_id, f"Something went wrong with object detection: {e}")
            return

        # clear
        if user_input == "clear":
            session = {'images': [], 'awaiting_direction': False}
            user_sessions[user_id] = session
            self.send_text(chat_id, "Session cleared!")
            return

        if user_input in ("/start", "/help", "hello", "hi"):
            self.send_text(chat_id,
                           "👋 Hey there! I'm your image buddy - here to help you mess around with your pictures a bit\n\n"
                           "Sooo, what can i do?\n"
                           "- segment - highlights key parts of your image\n"
                           "- rotate - gives your image a little spin\n"
                           "- salt and pepper - adds a bit of noisy spice 🍿\n"
                           "- blur - smooth out your image a bit\n"
                           "- contour - outlines the edges in your image\n"
                           "- concat - combine 2 images side by side or on top (here you must send 2 images!)\n"
                           "- detect - runs object detection on your image with YOLO\n"
                           "- clear - resets everything if you want a fresh start\n\n"
                           "Just send me a photo to begin. Then type any of the commands above <b>exactly as written<b>. \n"
                           "I'll take care of the rest and send you back the edited image. Let's go! 🚀"
                           )
