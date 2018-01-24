# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name='companiesprofiles',
    version='1.0',
    packages=find_packages(),
    # package_data={
    #     'companiesprofiles': ['importioXpaths/*.json']
    # },
    # include_package_data=True,
    entry_points={
        'scrapy': ['settings = companiesprofiles.settings']
    },
    zip_safe=False,
    )