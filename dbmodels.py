from google.appengine.ext import db


class User(db.Model):
    username = db.StringProperty(required=True)
    firstname = db.StringProperty(required=False)
    lastname = db.StringProperty(required=False)
    password = db.StringProperty(required=True)
    email = db.EmailProperty(required=True)
    createDate = db.DateTimeProperty(auto_now_add=True)
    modifiedDate = db.DateTimeProperty()
    deletedDate = db.DateTimeProperty()
    isLockedOut = db.BooleanProperty(default=False)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('username =', name).get()
        return u

    @classmethod
    def by_email(cls, email):
        u = User.all().filter('email =', email).get()
        return u


class Post(db.Model):
    user = db.ReferenceProperty(User)
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    postedDate = db.DateTimeProperty(auto_now_add=True)


class Spot(db.Model):
    name = db.StringProperty(required=True)
    website = db.LinkProperty(required=True)
    createDate = db.DateTimeProperty(auto_now_add=True)
    city = db.StringProperty(required=False)
    state = db.StringProperty(required=False)
    zipcode = db.StringProperty(required=False)

    @classmethod
    def by_id(cls, sid):
        return Spot.get_by_id(sid)

    @classmethod
    def by_name(cls, name):
        s = Spot.all().filter('name =', name).get()
        return s

    @classmethod
    def by_website(cls, website):
        s = Spot.all().filter('website =', website).get()
        return s


class PostSpot(db.Model):
    spot = db.ReferenceProperty(Spot)
    post = db.ReferenceProperty(Post)


class UserSpots(db.Model):
    user = db.ReferenceProperty(User)
    spot = db.ReferenceProperty(Spot)

    @classmethod
    def by_user(cls, user):
        userSpots = UserSpots.all().filter('user =', user).get()
        return userSpots
