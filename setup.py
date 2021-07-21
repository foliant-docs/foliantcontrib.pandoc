from setuptools import setup


SHORT_DESCRIPTION = 'Pandoc backend for Foliant doc maker. Produces PDF and DOCX.'

try:
    with open('README.md', encoding='utf8') as readme:
        LONG_DESCRIPTION = readme.read()

except FileNotFoundError:
    LONG_DESCRIPTION = SHORT_DESCRIPTION


setup(
    name='foliantcontrib.pandoc',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    version='1.1.1',
    author='Konstantin Molchanov',
    author_email='moigagoo@live.com',
    url='https://github.com/foliant-docs/foliantcontrib.pandoc',
    packages=['foliant.backends'],
    license='MIT',
    platforms='any',
    install_requires=[
        'foliant>=1.0.8',
        'foliantcontrib.flatten>=1.0.2',
        'foliantcontrib.meta>=1.3.2',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.6'
    ]
)
