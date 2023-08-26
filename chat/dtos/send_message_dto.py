from message.models import Message


class MessageDto:
    def __init__(self, message: Message):
        self.id = message.id
        self.image_path = message.image_path
        self.file_path = message.file_path
        self.type = message.type
        self.src_id = message.src_id
        self.dst_id = message.dst_id
        self.chat_id = message.chat_id
        self.timestamp = message.timestamp
