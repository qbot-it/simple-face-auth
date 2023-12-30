#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, END
from components.user.services.auth_service import AuthService
from components.video.exceptions.create_descriptor_exception import CreateDescriptorException
from components.video.services.descriptor_service import DescriptorService
from components.video.dto.frame import Frame
from components.video.services.face_service import FaceService
from components.user.exceptions.user_not_found import UserNotFoundException
from components.user.models.user import User
from components.user.exceptions.user_already_exists import UserAlreadyExistsException
from components.user.services.user_service import UserService
from components.state.service.state_service import StateService, Mode
from PIL import ImageTk, Image, ImageOps
from email_validator import validate_email, EmailNotValidError
import cv2


class MainApp:
    state_service: StateService
    user_service: UserService
    auth_service: AuthService
    face_service: FaceService
    descriptor_service: DescriptorService
    current_frame: Frame

    def __init__(self, master=None, translator=None):
        _ = translator
        if translator is None:
            def _(x): return x

        self.state_service = StateService()
        self.user_service = UserService()
        self.auth_service = AuthService()
        self.face_service = FaceService()
        self.descriptor_service = DescriptorService()
        self.current_frame = Frame()

        # build ui
        self.main_window = tk.Tk() if master is None else tk.Toplevel(master)
        self.main_window.geometry("576x576")
        self.main_window.resizable(False, False)
        # First object created
        self.setup_ttk_styles(self.main_window)
        self.frm_main = ttk.Frame(self.main_window)
        self.frm_controls = ttk.Frame(self.frm_main)
        self.frm_controls.configure(height=200, width=200)
        self.frm_mode = ttk.Labelframe(self.frm_controls)
        self.frm_mode.configure(
            height=70,
            labelanchor="nw",
            text=_('Mode'),
            width=180)
        self.rb_mode_auth = ttk.Radiobutton(self.frm_mode)
        self.rb_mode_auth.configure(
            state="normal", text=_('auth'), value="auth")
        self.rb_mode_auth.grid(
            column=0,
            padx=5,
            pady="0 5",
            row=0,
            sticky="ew")
        self.rb_mode_auth.configure(command=self.rb_mode_changed)
        self.rb_mode_add = ttk.Radiobutton(self.frm_mode)
        self.rb_mode_add.configure(state="normal", text=_('add'), value="add")
        self.rb_mode_add.grid(column=1, padx=5, pady="0 5", row=0, sticky="ew")
        self.rb_mode_add.configure(command=self.rb_mode_changed)
        self.frm_mode.grid(row=0, sticky="w")
        self.frm_email = ttk.Frame(self.frm_controls)
        self.frm_email.configure(
            cursor="boat",
            height=50,
            padding="10 0",
            width=200)
        self.lbl_email = ttk.Label(self.frm_email)
        self.lbl_email.configure(cursor="arrow", text=_('Email'))
        self.lbl_email.grid(column=0, row=0, sticky="ew")
        self.en_email = ttk.Entry(self.frm_email)
        self.en_email.grid(column=0, row=1, sticky="ew")
        self.frm_email.grid(column=1, row=0, sticky="e")
        self.frm_email.grid_propagate(0)
        self.frm_email.columnconfigure(0, pad=100, weight=1)
        self.btn_start = ttk.Button(self.frm_controls)
        self.btn_start.configure(text=_('Auth'))
        self.btn_start.grid(column=2, ipady=10, row=0, sticky="e")
        self.btn_start.configure(command=self.btn_start_clicked)
        self.frm_controls.place(
            anchor="nw",
            height=80,
            relx=0.09,
            rely=0.85,
            width=450,
            x=0,
            y=0)
        self.frm_controls.grid_anchor("center")
        self.frm_controls.columnconfigure(0, weight=00)
        self.frm_controls.columnconfigure(1, weight=1)
        self.frm_controls.columnconfigure(2, weight=1)
        self.frm_top = ttk.Frame(self.frm_main)
        self.frm_top.configure(height=40, width=200)
        self.btn_clear = ttk.Button(self.frm_top)
        self.btn_clear.configure(takefocus=True, text=_('Clear all'))
        self.btn_clear.grid(column=1, row=0, sticky="e")
        self.btn_clear.configure(command=self.btn_clear_clicked)
        self.lbl_version = ttk.Label(self.frm_top)
        self.lbl_version.configure(
            font="TkDefaultFont",
            padding=3,
            state="normal",
            text=_('version 0.0.1'))
        self.lbl_version.grid(column=0, row=0, sticky="w")
        self.frm_top.place(
            anchor="nw",
            relwidth=0.0,
            relx=0.09,
            rely=0.03,
            width=450,
            x=0,
            y=0)
        self.frm_top.columnconfigure(1, weight=1)
        self.frm_video = ttk.Frame(self.frm_main)
        self.lbl_video = ttk.Label(self.frm_video)
        self.lbl_video.configure(style="VideoLabel.TLabel")
        self.lbl_video.grid(column=0, padx=3, pady=3, row=0, sticky="nsew")
        self.frm_video.place(
            height=450,
            relx=0.09,
            rely=0.09,
            width=450,
            x=0,
            y=0)
        self.frm_video.rowconfigure(0, weight=1)
        self.frm_video.columnconfigure(0, weight=1)
        self.frm_main.grid(column=0, row=0, sticky="nsew")
        self.main_window.rowconfigure(0, weight=1)
        self.main_window.columnconfigure(0, weight=1)

        # Main widget
        self.mainwindow = self.main_window
        self.main_window.title('FaceAuth')
        self.rb_mode_auth.invoke()
        self.video_capture = cv2.VideoCapture(0)
        self.video_stream()

    def run(self):
        self.mainwindow.mainloop()

    def setup_ttk_styles(self, widget=None):
        # ttk styles configuration
        self.style = style = ttk.Style()
        style.configure("VideoLabel.TLabel", background="lightgray")
        style.configure("VideoFrameRed.TFrame", background="red")

    def rb_mode_changed(self):
        if self.rb_mode_auth.instate(['selected']):
            if self.state_service.get_mode() == Mode.ADD:
                self.en_email.delete(0, END)
                self.btn_start.configure(text='Auth')
                self.state_service.set_mode(Mode.AUTH)
                self.frm_video.configure(style='')
        elif self.rb_mode_add.instate(['selected']):
            if self.state_service.get_mode() == Mode.AUTH:
                self.en_email.delete(0, END)
                self.btn_start.configure(text='Save')
                self.state_service.set_mode(Mode.ADD)
                self.frm_video.configure(style='')

    def btn_start_clicked(self):
        if not self.state_service.is_processing():
            email = self.en_email.get()
            if self.state_service.get_mode() == Mode.ADD and len(email):
                try:
                    email_info = validate_email(email, check_deliverability=False)
                    email = email_info.original.lower()
                    self.set_processing(True)
                    descriptor = self.descriptor_service.create(self.current_frame)
                    try:
                        self.user_service.get_one(email)
                        self.user_service.update(email, descriptor)
                        messagebox.showinfo("Add User", "User updated.")
                    except UserNotFoundException:
                        self.user_service.create(email, descriptor)
                        messagebox.showinfo("Add User", "User added.")
                except CreateDescriptorException:
                    pass
                except UserAlreadyExistsException as e:
                    messagebox.showerror("Error", e.message)
                except EmailNotValidError as e:
                    messagebox.showerror("Error", e)
                except Exception as e:
                    print(e)
                    messagebox.showerror("Error", "Internal error occurred.")
                self.set_processing(False)
            elif self.state_service.get_mode() == Mode.AUTH and len(email) > 0:
                try:
                    self.set_processing(True)
                    self.frm_video.configure(style='VideoFrameRed.TFrame')
                    user = self.user_service.get_one(email)
                    self.state_service.set_auth_active(user)
                except UserNotFoundException as e:
                    messagebox.showerror("Error", e.message)
                    self.frm_video.configure(style='')
                    self.state_service.set_auth_inactive()
                    self.set_processing(False)
                except CreateDescriptorException:
                    pass

        else:
            if self.state_service.get_mode() == Mode.AUTH and self.state_service.get_auth_active():
                self.frm_video.configure(style='')
                self.state_service.set_auth_inactive()
                self.set_processing(False)


    def btn_clear_clicked(self):
        if not self.state_service.is_processing():
            answer = messagebox.askquestion("Truncate Database", "Are you sure?")
            match answer:
                case 'yes':
                    self.set_processing(True)
                    self.user_service.delete_all()
                    messagebox.showinfo("Truncate Database", "Database truncated.")
                    self.set_processing(False)
                case 'no':
                    pass

    def video_stream(self):
        if self.video_capture.isOpened():
            _, frame = self.video_capture.read()

            self.current_frame.color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_frame.gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.current_frame.faces = self.face_service.detect_faces(self.current_frame.gray)
            self.current_frame.roi = self.face_service.roi_frame(self.current_frame.gray, self.current_frame.faces)

            frame_color = self.face_service.add_roi_areas(self.current_frame.color, self.current_frame.faces)

            # for tests
            # frame_color = self.current_frame.roi if self.current_frame.roi is not None else frame_color

            image = Image.fromarray(frame_color)
            image = ImageOps.fit(image, (450, 450))
            imgtk = ImageTk.PhotoImage(image=image)

            self.lbl_video.imgtk = imgtk
            self.lbl_video.configure(image=imgtk)
            self.process_auth()
            self.lbl_video.after(60, self.video_stream)

    def set_processing(self, processing: bool):
        self.state_service.set_processing(processing)
        if processing:
            self.rb_mode_auth.configure(state='disabled')
            self.rb_mode_add.configure(state='disabled')
        else:
            self.rb_mode_auth.configure(state='normal')
            self.rb_mode_add.configure(state='normal')

    def process_auth(self):
        if self.state_service.get_auth_active():
            user = self.state_service.get_auth_user()
            if isinstance(user, User):
                try:
                    passes = self.auth_service.passes(user, self.descriptor_service.create(self.current_frame))
                    if passes:
                        self.frm_video.configure(style='')
                        messagebox.showinfo("Authentication", "Authentication successful.")
                        self.state_service.set_auth_inactive()
                        self.set_processing(False)
                except Exception as e:
                    pass


if __name__ == "__main__":
    app = MainApp()
    app.run()
