from os.path import join

def get_package_data():
    return {'astropy_helpers': [join('src', 'compiler.c')]}
