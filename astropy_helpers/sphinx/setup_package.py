# Licensed under a 3-clause BSD style license - see LICENSE.rst


def get_package_data():
    # Install the theme files
    return {
        'astropy_helpers.sphinx': [
            'local/*.inv',
            'themes/bootstrap-astropy/*.*',
            'themes/bootstrap-astropy/static/*.*']}
