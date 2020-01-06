import argparse
import asyncio
import sys

import websockets
from prompt_toolkit.shortcuts import button_dialog, yes_no_dialog, \
    message_dialog, input_dialog, radiolist_dialog
from prompt_toolkit.styles import Style

from application_builder import ApplicationBuilder
from application_state import ApplicationState
from document_editor import DocumentEditor
from message_service import MessageService


class ClientLauncher:
    """
    Launch an application
    """
    server_ip = "localhost"
    server_port = 8080
    style = Style.from_dict({"status": "reverse", "shadow": "bg:#440044", })

    def __init__(self):
        self.app_state = ApplicationState()
        parser = argparse.ArgumentParser(
            description='Multi text editor client launcher')

        parser.add_argument('-i', '--ip', type=str,
                            help='destination server ip',
                            required=False, default=self.server_ip)
        parser.add_argument('-p', '--port', type=int,
                            help='destination server port',
                            required=False, default=self.server_port)

        args = parser.parse_args()
        self.server_ip = args.ip
        self.server_port = args.port
        self.uri = f"ws://{self.server_ip}:{self.server_port}"

    def run(self) -> None:
        """
        Init launch of app
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__launch(self.uri))
        loop.close()

    async def __launch(self, uri) -> None:
        """
        Launch client application.
        :param uri: uri to connect
        :type uri: str
        """
        try:
            async with websockets.connect(uri, max_size=None,
                                          ping_timeout=100) as websocket:
                self.msg_service = MessageService(self.app_state, websocket)
                self.doc_editor = DocumentEditor(self.msg_service)
                await self.__run()

        except OSError as e:
            print(f"Failed to connect to {self.server_ip}:{self.server_port}")

    async def __do_filename_input(self) -> None:
        """
        Get filename from user.
        """
        while True:
            filename = await input_dialog(
                title="File name", text="Please type file name to create:",
                style=self.style
            ).run_async()
            filename = filename.strip() if filename else filename
            if not filename or any(x.isspace() for x in filename):
                await message_dialog(
                    title="Incorrect filename",
                    text=f"Try another filename...",
                ).run_async()
            else:
                self.app_state.current_filename = filename
                return

    @staticmethod
    def __exit_app(code=0) -> None:
        """
        Perform app exit with code
        :param code: exit code, default is 0
        :type code: int
        """
        sys.exit(code)

    async def __do_new_file_dialog(self) -> None:
        """
        Show file create dialog.
        """
        await self.__do_filename_input()
        await self.msg_service.send_request({"type": "create_file_request"})
        response = await self.msg_service.get_response()
        if not response["success"]:
            await message_dialog(
                title="Error", text=f"Error creating file, try again.",
            ).run_async()
        else:
            await message_dialog(
                title="Success", text=f"Successfully created new file.",
            ).run_async()

    async def __do_file_dialog(self) -> dict:
        """
        Show file open dialog.
        :return Return file object as dict.
        """
        await self.msg_service.send_request({"type": "all_files_request"})
        response = await self.msg_service.get_response()
        content = response.get("content")

        owned = [({"file": file, "owner": None}, file) for file in
                 content["files"]]
        shared = [({"file": file, "owner": owner}, f"{file} - {owner}")
                  for owner in content["shared_files"].keys() for file in
                  content["shared_files"][owner]]

        result = await radiolist_dialog(
            title="Open file",
            text="Select file to open",
            values=owned + shared + [({"file": None}, "Create new...")]
        ).run_async()

        if result is None:
            self.__exit_app()
        if result["file"] is None:
            await self.__do_new_file_dialog()
            return await self.__do_file_dialog()

        self.app_state.current_filename = result["file"]
        if result["owner"]:
            self.app_state.current_file_owner = result["owner"]
        await self.msg_service.send_request({"type": "file_request"})
        return await self.msg_service.get_response()

    async def __do_register(self) -> None:
        """
        Show user register dialog
        """
        while True:
            self.app_state.username = await input_dialog(
                title="Sign up username",
                text="Please type your username:",
                style=self.style
            ).run_async()

            if not self.app_state.username:
                self.__exit_app()

            self.app_state.password = await input_dialog(
                title="Sign up password",
                text="Please type password for new "
                     "account:",
                password=True, style=self.style
            ).run_async()

            if not self.app_state.password:
                self.__exit_app()

            await self.msg_service.send_request({"type": "user_register"})
            response = await self.msg_service.get_response()

            if response["success"]:
                await message_dialog(
                    title="Register ok",
                    text=f"Now logged in as {self.app_state.username}.",
                ).run_async()
                return

            try_again = await yes_no_dialog(
                style=self.style,
                title="Failed to register",
                text=f"{response['content']}, try again?"
            ).run_async()
            if not try_again:
                self.__exit_app()

    async def __do_login(self) -> None:
        """
        Show user login dialog.
        """
        while True:
            self.app_state.username = await input_dialog(
                title="Login username", text="Please type your username:",
                style=self.style
            ).run_async()

            if self.app_state.username is None:
                self.__exit_app()

            self.app_state.password = await input_dialog(
                title="Login password", text="Please type your password:",
                password=True, style=self.style
            ).run_async()

            if self.app_state.password is None:
                self.__exit_app()

            await self.msg_service.send_request({"type": "user_login"})
            response = await self.msg_service.get_response()

            if not response["success"]:
                try_again = await yes_no_dialog(
                    style=self.style,
                    title="Wrong credentials",
                    text="Failed to log in. Try again?"
                ).run_async()
                if not try_again:
                    self.__exit_app()
            else:
                await message_dialog(
                    title="Login ok",
                    text=f"Now logged in as {self.app_state.username}.",
                ).run_async()
                return

    async def __run(self) -> None:
        """
        Set up application state from user input,
        then build and launch an application.
        """
        need_register = await button_dialog(
            title="Text editor",
            text="Welcome to multi-user text editor!",
            buttons=[("Login", False), ("Sign up", True)],
        ).run_async()

        if need_register:
            await self.__do_register()
        else:
            await self.__do_login()

        file_result = await self.__do_file_dialog()

        self.app_state.current_file_id = file_result["file_id"]
        for patch in file_result["content"]:
            await self.doc_editor.update_text(patch)
            self.doc_editor.patch_set.append(patch)

        # send updates to server
        producer_task = asyncio.create_task(
            self.msg_service.send_worker())
        app_builder = ApplicationBuilder(app_state=self.app_state,
                                         doc_editor=self.doc_editor,
                                         msg_service=self.msg_service,
                                         style=self.style)

        application = app_builder.build_app()
        # listen server for updaters
        consumer_task = asyncio.create_task(
            self.msg_service.receive_worker(application.show_message,
                                            self.doc_editor))

        await application.run_async()

        # cancel tasks after app exit
        consumer_task.cancel()
        producer_task.cancel()


if __name__ == "__main__":
    launcher = ClientLauncher()
    launcher.run()
