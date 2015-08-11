import main.util.KyanToolKit_Py
ktk = main.util.KyanToolKit_Py.KyanToolKit_Py()

def getUserGravatar(email):
    base_src = "https://secure.gravatar.com/avatar/"
    email_md5 = ktk.md5(email) if email else "";
    return base_src + email_md5

