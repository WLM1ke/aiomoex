import setuptools

with open('README.md') as file:
    long_description = file.read()

setuptools.setup(
    name='aiomoex',
    version='1.0.0',
    description='Asyncio MOEX ISS API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/WLM1ke/aiomoex',
    author='Mikhail Korotkov aka WLMike',
    author_email='wlmike@gmail.com',
    license='http://unlicense.org',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities'],
    keywords='asyncio moex iss',
    project_urls={
        'Documentation': 'https://wlm1ke.github.io/aiomoex/',
        'Source': 'https://github.com/WLM1ke/aiomoex'},
    packages=setuptools.find_packages(exclude=['tests']),
    install_requires=['aiohttp'],
    python_requires='>=3.6')
