import webapp2

import jinja2
import os
import re

import utils
from dbmodels import User

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def renderString(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.write(renderString(template, **kw))

    def write(self, *a, **kw):
        self.response.write(*a, **kw)


class UserSignup(BaseHandler):
    def get(self):
        self.render('user-signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        firstname = self.request.get('firstname')
        lastname = self.request.get('lastname')
        verify = self.request.get('verify')
        email = self.request.get('email')

        userError = ''
        passwordError = ''
        verifyError = ''
        emailError = ''

        if not(username and valid_username(username)):
            userError = USERNAME_ER
        if not (password and valid_password(password)):
            passwordError = PASSWORD_ER
        if not (verify and (verify == password)):
            verifyError = VERIFY_ER
        if not (valid_email(email)):
            emailError = EMAIL_ER

        if(userError or passwordError or verifyError or emailError):
            self.render('user-signup.html', username=username,
                                            firstname=firstname,
                                            lastname=lastname,
                                            email=email,
                                            usernameError=userError,
                                            passwordError=passwordError,
                                            verifyError=verifyError,
                                            emailError=emailError)
        else:
            pw_hash = utils.make_pw_hash(username, password)
            if pw_hash:
                u = User(username=username, password=pw_hash, firstname=firstname, lastname=lastname, email=email)
                u.put()
                id_string = str(u.key().id())
                cookieHsh = utils.make_secure_val(id_string)
                self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' %
                cookieHsh)
                self.redirect('/')
            else:
                self.render('user-signup.html', username=username,
                                            email=email,
                                            usernameError=userError,
                                            passwordError=passwordError,
                                            verifyError=verifyError,
                                            emailError=emailError)


class Welcome(BaseHandler):
    def get(self):
        #username = self.request.get('username')
        username = ''
        cookie_data = self.request.cookies.get('user_id')

        if cookie_data and utils.valid_secure_val(cookie_data):
            user_id = long(cookie_data.split('|')[0])
            u = User.by_id(user_id)
            username = u.username
            self.render('welcome.html', username=username)
        else:
            self.redirect('/signup')


class Login(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        userError = ''
        passwordError = ''
        invalidError = ''

        user_id = ''

        if not username:
            userError = USERNAME_ER
        if not password:
            passwordError = PASSWORD_ER

        if not(userError or passwordError):

            u = User.by_name(username)
            if not (u and utils.valid_pw(username, password, u.password)):
                invalidError = INVALID_ER
            else:
                user_id = str(u.key().id())

        if(userError or passwordError or invalidError):
            self.render('login.html', username=username,
                                      usernameError=userError,
                                      passwordError=passwordError,
                                      invalidError=invalidError)
        else:
            id_string = user_id
            cookieHsh = utils.make_secure_val(id_string)
            self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' %
            cookieHsh)
            self.redirect('/')


class Logout(BaseHandler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

USERNAME_ER = 'Username is not valid'
PASSWORD_ER = 'Password is not valid'
VERIFY_ER = 'Passwords do not match'
EMAIL_ER = 'Email is not valid'
INVALID_ER = 'Invalid Login'

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")


def valid_username(username):
    if User.by_name(username):
        return False

    return USER_RE.match(username)


def valid_password(password):
    return PASSWORD_RE.match(password)


def valid_email(email):
    if email and not User.by_email(email):
        return EMAIL_RE.match(email)

app = webapp2.WSGIApplication(
                                     [('/signup', UserSignup),
                                     ('/login', Login),
                                     ('/logout', Logout)],
                                     debug=True)


def main():
    app.run()

if __name__ == '__main__':
    main()
