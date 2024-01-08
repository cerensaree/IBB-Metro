import setuptools

setuptools.setup(
    name="metro-api",
    version="1.0.0",
    author="Ceren Sare KILIÇARSLAN",
    author_email="cerensare@staj.com",
    description="Metro API",
    url="https://gitlab.mantam.com.tr/ibb1/metro-mobile/metro-api",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    platforms="all",
    classifiers=[
        "Topic :: Internet",
        "Topic :: Software Development",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Operating System :: Ubuntu",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ],

    install_requires=['Flask==3.0.0', 'Flask-SQLAlchemy==3.1.1', 'redis==5.0.1', 'psycopg2-binary', 'requests'],
    packages=setuptools.find_packages(),
    scripts=['bin/metro-api']
)
