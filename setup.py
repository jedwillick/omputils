from setuptools import setup

# Get the long description from the README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='omputils',
    version='0.1.0',
    description='A utility script for Oh My Posh (https://ohmyposh.dev/)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jedwillick/omputils',
    author='Jed Willick',
    license='MIT License',
    # author_email='',

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Oh My Posh :: CLI',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='OMP, Oh-My-Posh, CLI',

    packages=['omputils'],

    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires='>=3.8',

    install_requires=[],

    entry_points={
        'console_scripts': [
            'omputils=omputils.omputils:main',
        ],
    },

    project_urls={
        'Source': 'https://github.com/jedwillick/omputils',
        'Bug Reports': 'https://github.com/jedwillick/omputils/issues',
        'Oh My Posh': 'https://ohmyposh.dev/'
    },
)
