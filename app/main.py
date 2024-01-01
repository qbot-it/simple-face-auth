#!/usr/bin/python3
import pathlib
import tkinter.ttk as ttk
from tkinter import messagebox, END
import pygubu
from PIL import ImageTk, Image, ImageOps
from email_validator import validate_email, EmailNotValidError
import cv2

from components.video.exceptions.descriptor_creator_not_found_exception import DescriptorCreatorNotFoundException
from components.video.exceptions.face_detector_not_found_exception import FaceDetectorNotFoundException
from components.video.exceptions.matcher_not_found_exception import MatcherNotFoundException
from components.user.exceptions.user_already_exists import UserAlreadyExistsException
from components.user.exceptions.user_not_found import UserNotFoundException
from components.video.exceptions.create_descriptor_exception import CreateDescriptorException
from components.state.enums.mode import Mode
from components.user.dto.descriptor import Descriptor
from components.user.models.user import User
from components.state.enums.method import Method
from components.video.services.descriptor_creator_factory import DescriptorCreatorFactory
from components.video.services.face_detector_factory import FaceDetectorFactory
from components.video.services.matcher_factory import MatcherFactory
from components.state.service.state_service import StateService
from components.user.services.descriptor_service import DescriptorService
from components.user.services.user_service import UserService
from components.video.dto.frame import Frame
from components.video.services.descriptor.dl_descriptor_creator import DlDescriptorCreator
from components.video.services.descriptor.lbph_descriptor_creator import LbphDescriptorCreator
from components.video.services.detector.haar_face_detector import HaarFaceDetector
from components.video.services.matcher.dl_matcher import DlMatcher
from components.video.services.matcher.lbph_matcher import LbphMatcher

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "files/main.ui"


class MainApp:

    state_service: StateService
    user_service: UserService
    face_matcher: LbphMatcher | DlMatcher
    face_detector: HaarFaceDetector
    descriptor_creator: LbphDescriptorCreator | DlDescriptorCreator
    descriptor_service: DescriptorService
    current_frame: Frame

    def __init__(self, master=None):
        self.state_service = StateService()
        self.user_service = UserService()
        self.set_method(Method.LBPH)
        self.descriptor_service = DescriptorService()
        self.current_frame = Frame()

        self.style = None
        self.builder = builder = pygubu.Builder(
            on_first_object=self.setup_ttk_styles)
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.main_window = builder.get_object("main_window", master)

        self.rb_mode_auth = builder.get_object('rb_mode_auth')
        self.rb_mode_add = builder.get_object('rb_mode_add')
        self.rb_lbph = builder.get_object('rb_lbph')
        self.rb_dl = builder.get_object('rb_dl')
        self.en_email = builder.get_object('en_email')
        self.btn_start = builder.get_object('btn_start')
        self.frm_video = builder.get_object('frm_video')
        self.lbl_video = builder.get_object('lbl_video')
        self.main_window.title('FaceAuth')
        self.rb_mode_auth.invoke()
        self.rb_lbph.invoke()

        self.video_capture = cv2.VideoCapture(0)
        self.video_stream()
        builder.connect_callbacks(self)

    def run(self):
        self.main_window.mainloop()

    def setup_ttk_styles(self, widget=None):
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

    def rb_method_changed(self):
        if self.rb_lbph.instate(['selected']):
            self.set_method(Method.LBPH)
        elif self.rb_dl.instate(['selected']):
            self.set_method(Method.DL)

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

            self.current_frame.raw = frame
            self.current_frame.color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_frame.faces = self.face_detector.faces(frame)
            frame_color = self.face_detector.mark_faces(self.current_frame.color, self.current_frame.faces)

            # for tests
            # frame_color = self.current_frame.roi if self.current_frame.roi is not None else frame_color

            image = Image.fromarray(frame_color)
            image = ImageOps.fit(image, (450, 450))
            imgtk = ImageTk.PhotoImage(image=image)

            self.lbl_video.imgtk = imgtk
            self.lbl_video.configure(image=imgtk)
            self.check_auth()
            self.lbl_video.after(30, self.video_stream)

    def set_processing(self, processing: bool):
        self.state_service.set_processing(processing)
        if processing:
            self.rb_mode_auth.configure(state='disabled')
            self.rb_mode_add.configure(state='disabled')
            self.rb_lbph.configure(state='disabled')
            self.rb_dl.configure(state='disabled')
        else:
            self.rb_mode_auth.configure(state='normal')
            self.rb_mode_add.configure(state='normal')
            self.rb_lbph.configure(state='normal')
            self.rb_dl.configure(state='normal')

    def check_auth(self):
        if self.state_service.get_auth_active():
            user = self.state_service.get_auth_user()
            if isinstance(user, User):
                try:
                    passes = self.face_matcher.match(
                        Descriptor.from_json(user.descriptor),
                        self.descriptor_creator.create(self.current_frame)
                    )
                    if passes:
                        self.frm_video.configure(style='')
                        messagebox.showinfo("Authentication", "Authentication successful.")
                        self.state_service.set_auth_inactive()
                        self.set_processing(False)
                except Exception as e:
                    print(e)
                    pass

    def set_method(self, method: Method):
        try:
            self.face_detector = FaceDetectorFactory.get_instance(method)
            self.descriptor_creator = DescriptorCreatorFactory.get_instance(method)
            self.face_matcher = MatcherFactory.get_instance(method)
        except (FaceDetectorNotFoundException, DescriptorCreatorNotFoundException, MatcherNotFoundException) as e:
            messagebox.showerror("Error", e.message)
        except Exception as e:
            print(e)
            messagebox.showerror("Error", "Internal error occurred.")


if __name__ == "__main__":
    app = MainApp()
    app.run()
