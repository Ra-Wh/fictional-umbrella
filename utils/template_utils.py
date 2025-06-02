from flask_login import current_user

def get_base_template():
    return "adminbase.html" if current_user.is_admin else "base.html"