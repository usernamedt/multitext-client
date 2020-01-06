class ApplicationState:
    """
    Application state.

    is_saving - indicates if app in saving state
    current_filename - filename of file currently opened
    username - logged in user name
    password - logged in user password
    current_file_id - file_id of file currently opened
    logged_in - if user is logged in
    current_file_owner - owner login of opened document, it could be current
    user or other user if file is shared

    """
    def __init__(self):
        self.is_saving: bool = False
        self.current_filename: str = ""
        self.username: str = ""
        self.password: str = ""
        self.current_file_id: str or None = None
        self.logged_in: bool = False
        self.current_file_owner: str or None = None
