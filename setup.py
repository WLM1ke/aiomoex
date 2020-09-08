import setuptools

name = "aiomoex"
python_minimal = "3.8"
version = "2.0.0"

with open("README.rst") as file:
    long_description = file.read()

setuptools.setup(
    name=name,
    version=version,
    description="Asyncio MOEX ISS API",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://wlm1ke.github.io/aiomoex/",
    author="Mikhail Korotkov aka WLMike",
    author_email="wlmike@gmail.com",
    license="http://unlicense.org",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Natural Language :: Russian",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Utilities",
    ],
    keywords="asyncio moex iss",
    project_urls={"Source": "https://github.com/WLM1ke/aiomoex"},
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=["aiohttp"],
    python_requires=f">={python_minimal}",
)
