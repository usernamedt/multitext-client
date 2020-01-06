import asyncio
import json

from prompt_toolkit.application import get_app


class MessageService:
    """
    Service to exchange data with server using websocket.
    """
    def __init__(self, app_state, websocket):
        self.app_state = app_state
        self.send_queue = asyncio.Queue()
        self.websocket = websocket

    def prepare_send_request(self, message) -> bytes:
        """
        Add credentials to message, serialize to json and encode.
        :param message: message to send
        :type message: dict
        :return: bytes of encoded message
        """
        message_data = {"username": self.app_state.username,
                        "password": self.app_state.password,
                        "filename": self.app_state.current_filename,
                        **message}
        if self.app_state.current_file_owner:
            message_data["owner"] = self.app_state.current_file_owner
        if self.app_state.current_file_id:
            message_data["file_id"] = self.app_state.current_file_id
        return json.dumps(message_data).encode("utf-8")

    async def send_request(self, message) -> None:
        """
        Immediately send a request to websocket.
        :param message: message to send
        :type message: dict
        """
        await self.websocket.send(self.prepare_send_request(message))

    def put_message(self, message) -> None:
        """
        Put message to send queue
        :param message: message to send
        :type message: bytes
        """
        self.send_queue.put_nowait(message)

    async def get_response(self) -> dict:
        """
        Wait for closest message on websocket, deserialize and return it.
        :return: message object as dict
        """
        response = await self.websocket.recv()
        return json.loads(response.decode("utf-8"))

    async def receive_worker(self, notify, doc_editor) -> None:
        """
        Waits for messages on websocket and apply updates to internal
        application state.
        :param notify: application notification function
        :param doc_editor: document editor
        :type notify: functions
        :type doc_editor: DocumentEditor
        """
        try:
            async for message in self.websocket:
                packet = json.loads(message.decode("utf-8"))
                if packet["type"] == "patch" and packet["content"] not in \
                        doc_editor.patch_set:
                    await doc_editor.update_text(packet["content"])
                    doc_editor.patch_set.append(packet["content"])
                if packet["type"] == "save_file_response":
                    self.app_state.is_saving = False
                    if packet["success"]:
                        notify("File save",
                               "File has been saved on server.")
                    else:
                        notify("File save",
                               "Error saving a file :(")
                    get_app().invalidate()
                if packet["type"] == "file_share_response":
                    if packet["success"]:
                        notify("File share", "File has been shared.")
                    else:
                        notify("File share", "Error sharing a file :( Try "
                                             "another username?")
                    get_app().invalidate()

        finally:
            return

    async def send_worker(self) -> None:
        """
        Sends messages from send_queue to websocket.
        """
        while True:
            next_message = await self.send_queue.get()

            await self.websocket.send(next_message)

            # Notify the queue that the item has been processed.
            self.send_queue.task_done()
