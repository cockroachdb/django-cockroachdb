from setuptools import find_packages, setup

setup(
    name='django-cockroachdb',
    version=__import__('django_cockroachdb').__version__,
    python_requires='>=3.5',
    url='https://github.com/cockroachdb/django-cockroachdb',
    maintainer='Cockroach Labs',
    maintainer_email='python@cockroachlabs.com',
    description='Django backend for CockroachDB',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    project_urls={
        'Source': 'https://github.com/cockroachdb/django-cockroachdb',
        'Tracker': 'https://github.com/cockroachdb/django-cockroachdb/issues',
    },
)
