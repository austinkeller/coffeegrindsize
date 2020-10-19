import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="coffeegrindsize",
    version="0.2.0",
    author="Jonathan Gagné",
    author_email="jonathan.gagne@montreal.ca",
    maintainer="Austin Keller",
    maintainer_email="atkeller@uw.edu",
    description="An app to measure your coffee grind size distribution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/austinkeller/coffeegrindsize",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'coffeegrindsize = coffeegrindsize.scripts.coffeegrindsize:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'click',
        'matplotlib',
        'numpy',
        'pandas',
        'Pillow',
    ]
)
