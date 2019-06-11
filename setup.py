import setuptools

install_requires = [
    'psycopg2',
]

setuptools.setup(
    name='cockroach',
    version='0.1',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
)
