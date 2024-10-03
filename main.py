import qrcode
import cv2
import imutils
import base64
from io import BytesIO
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.graphics.texture import Texture

from kivy.core.window import Window
Window.size = (412, 732)
# Import OpenCV QR code detector
qcd = cv2.QRCodeDetector()


# KV Lang UI
KV = '''
ScreenManager:
    LoginScreen:
    SignupScreen:
    DashboardScreen:
    CameraScreen:
    ReceiveScreen:
    QRScreen:
    ConfirmationScreen:
    TransactionSuccessScreen:

<LoginScreen>:
    name: 'login'
    FloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDLabel:
            text: "Welcome Back"
            halign: 'center'
            font_style: "Display"
            role: "medium"
            bold: True
            pos_hint: {'center_y': 0.8}
        MDTextField:
            id: login_email
            hint_text: "Email"
            icon_right: "email"
            mode: "outlined"
            size_hint_x: 0.9
            pos_hint: {'center_x': 0.5, 'center_y': 0.55}
        MDTextField:
            id: login_password
            hint_text: "Password"
            icon_right: "lock"
            password: True
            mode: "outlined"
            size_hint_x: 0.9
            pos_hint: {'center_x': 0.5, 'center_y': 0.45}
        MDButton:
            text: "Login"
            style: "elevated"
            pos_hint: {'center_x': 0.5, 'center_y': 0.3}
            size_hint_x: 0.9
            on_release: app.animate_button(self)
        MDButton:
            style: "text"
            text: "Don't have an account? Sign up"
            pos_hint: {'center_x': 0.5, 'center_y': 0.2}
            on_release: root.manager.current = 'signup'

<SignupScreen>:
    name: 'signup'
    FloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDLabel:
            text: "Create Account"
            halign: 'center'
            font_style: "Display"
            role: "medium"
            bold: True
            pos_hint: {'center_y': 0.8}
        MDTextField:
            id: signup_email
            hint_text: "Email"
            icon_right: "email"
            mode: "outlined"
            size_hint_x: 0.9
            pos_hint: {'center_x': 0.5, 'center_y': 0.55}
        MDTextField:
            id: signup_password
            hint_text: "Password"
            icon_right: "lock"
            password: True
            mode: "outlined"
            size_hint_x: 0.9
            pos_hint: {'center_x': 0.5, 'center_y': 0.45}
        MDButton:
            text: "Sign Up"
            style: "elevated"
            pos_hint: {'center_x': 0.5, 'center_y': 0.3}
            size_hint_x: 0.9
            on_release: app.animate_button(self)
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.1, "center_y": 0.95}
            on_release: root.manager.current = 'login'

<DashboardScreen>:
    name: 'dashboard'
    FloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDLabel:
            text: "Your Balance"
            halign: 'center'
            font_style: "Display"
            role: "medium"
            bold: True
            pos_hint: {'center_y': 0.8}
        MDLabel:
            text: "$5000"
            halign: 'center'
            font_style: "Display"
            role: "large"
            pos_hint: {'center_y': 0.6}
        MDButton:
            text: "Send"
            style: "elevated"
            size_hint_x: 0.9
            pos_hint: {'center_x': 0.5, 'center_y': 0.2}
            on_release:
                app.on_cam_click()
                root.manager.current = 'camera'
        MDIconButton:
            icon: "logout"
            pos_hint: {"center_x": 0.1, "center_y": 0.95}
            on_release: root.manager.current = 'login'
        MDButton:
            text: "Receive"
            style: "elevated"
            size_hint_x: 0.9
            pos_hint: {'center_x': 0.5, 'center_y': 0.1}
            on_release: root.manager.current = 'receive'

<ReceiveScreen>:
    name: 'receive'
    FloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDTextField:
            id: amount
            hint_text: "Amount to be received"
            size_hint_x: 0.9
            pos_hint: {'center_x': 0.5, 'center_y': 0.6}
        MDButton:
            text: "Confirm"
            style: "elevated"
            pos_hint: {'center_x': 0.5, 'center_y': 0.4}
            size_hint_x: 0.9
            on_release: app.generate_qr(amount.text)

<QRScreen>:
    name: 'qr'
    FloatLayout:
        md_bg_color: 1, 1, 1, 1
        Image:
            id: qr_code_img
            size_hint: 0.8, 0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.6}  # Adjust position higher
        MDButton:
            text: "Back to Dashboard"
            style: "elevated"
            size_hint_x: 0.9
            pos_hint: {'center_x': 0.5, 'center_y': 0.1}  # Keep the position lower to avoid overlap
            on_release:
                root.manager.current = 'dashboard'

<CameraScreen>:
    name: 'camera'
    BoxLayout:
        orientation: 'vertical'
        Image:
            id: img

    MDIconButton:
        icon: "arrow-left"
        pos_hint: {"center_x": 0.1, "center_y": 0.95}
        on_release:
            root.manager.current = 'dashboard'

<ConfirmationScreen>:
    name: 'confirm'
    FloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDLabel:
            id: qr_data
            text: "Send $0?"
            halign: 'center'
            font_style: "Display"
            role: "small"
            pos_hint: {'center_y': 0.6}
        MDButton:
            text: "Confirm"
            style: "elevated"
            pos_hint: {'center_x': 0.5, 'center_y': 0.4}
            size_hint_x: 0.9
            on_release:
                app.confirm_transaction()
        MDButton:
            text: "Cancel"
            style: "elevated"
            pos_hint: {'center_x': 0.5, 'center_y': 0.3}
            size_hint_x: 0.9
            on_release:
                root.manager.current = 'dashboard'

<TransactionSuccessScreen>:
    name: 'success'
    FloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDLabel:
            text: "Transaction Success!"
            halign: 'center'
            font_style: "Display"
            role: "small"
            pos_hint: {'center_y': 0.5}

'''

camera_id = 0
delay = 1
window_name = 'OpenCV QR Code'

qcd = cv2.QRCodeDetector()
cap = cv2.VideoCapture(camera_id)

class LoginScreen(Screen):
    pass

class SignupScreen(Screen):
    pass

class DashboardScreen(Screen):
    pass

class ReceiveScreen(Screen):
    pass

class QRScreen(Screen):
    pass

class CameraScreen(Screen):
    pass

class ConfirmationScreen(Screen):
    pass

class TransactionSuccessScreen(Screen):
    pass

class MyApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Light"  # or "Dark"
        self.theme_cls.primary_palette = "Blue"  # Adjust the primary palette
        self.theme_cls.accent_palette = "Amber"  # Adjust the accent color
        self.username = None
        self.capture = None
        return Builder.load_string(KV)

    def login(self):
        login_screen = self.root.get_screen('login')
        self.username = login_screen.ids.login_email.text
        self.root.current = 'dashboard'

    def sign_up(self):
        signup_screen = self.root.get_screen('signup')
        self.username = signup_screen.ids.signup_email.text
        self.root.current = 'dashboard'

    def animate_button(self, button):
        if button.text == "Login":
            self.root.current = 'dashboard'
            img = qrcode.make('Some data here')
            img.save("some_file.png")
        elif button.text == "Sign Up":
            self.root.current = 'dashboard'

    def send(self):
        print("Send button clicked")

    def on_cam_click(self):
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.load_camera_frame, 1.0 / 60.0)

    def load_camera_frame(self, dt):
        ret, frame = self.capture.read()
        if ret:
            ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
            if ret_qr:
                for s, p in zip(decoded_info, points):
                    if s:
                        self.qr_data = s
                        print(s)
                        self.capture.release()
                        Clock.unschedule(self.load_camera_frame)
                        self.root.current = 'success'
                        self.show_confirmation_screen()
                        return
                    else:
                        color = (0, 0, 255)
                    frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
            frame = imutils.resize(frame, width=375, height=200)
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            img = self.root.get_screen('camera').ids.img
            img.texture = image_texture

    def show_confirmation_screen(self):
        confirmation_screen = self.root.get_screen('confirm')
        confirmation_screen.ids.qr_data.text = f"Send ${self.qr_data}?"
        self.root.current = 'confirm'
        Clock.unschedule(self.load_camera_frame)
        self.capture.release()

    def confirm_transaction(self):
        # Show transaction success for a moment, then go back to dashboard
        self.root.current = 'success'
        Clock.schedule_once(self.go_back_to_dashboard, 2)

    def go_back_to_dashboard(self, dt):
        self.root.current = 'dashboard'


    def generate_qr(self, amount):
        # Generate a QR code with the login name and amount to be received
        qr_data = f"{self.username} Php{amount}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        
        buf = BytesIO()
        img.save(buf, format='PNG')
        byte_data = buf.getvalue()
        base64_data = base64.b64encode(byte_data).decode('utf-8')
        img_base64 = f'data:image/png;base64,{base64_data}'

        qr_screen = self.root.get_screen('qr')
        qr_screen.ids.qr_code_img.source = img_base64

        # Switch to the QR screen
        self.root.current = 'qr'

    def on_stop(self):
        if self.capture:
            self.capture.release()

if __name__ == '__main__':
    MyApp().run()