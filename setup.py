from setuptools import find_packages, setup

KEYWORDS = ("cython cythonize pyinstaller")

with open(u"requirements.txt", u"r") as f:
    required = f.read().splitlines()


with open("README.md", "r") as f:
    readme = f.read()


setup(
    name="cython_compiler",
    version="1.0.2",
    description="Cythonize your project, securing it's source, while still be able to test with python and bundle with PyInstaller",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="JessicaTegner",
    url="https://github.com/JessicaTegner/cython-compiler",
    license="GNU LGPLv3",
    keywords=KEYWORDS,
    zip_safe=False,
    include_package_data=True,
    install_requires=required,
    packages=["cython_compiler"],
    entry_points="""
    [console_scripts]
    cython-compiler=cython_compiler.compiler:main
    cython_compiler=cython_compiler.compiler:main
    """,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Topic :: Software Development :: Build Tools",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
