"""Setup script for PayTechUZ package."""

import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='paytechuz',
    version='0.3.7',
    license='MIT',
    author="Muhammadali Akbarov",
    author_email='muhammadali17abc@gmail.com',
    description="Unified Python package for Uzbekistan payment gateways (Payme, Click, Atmos)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Muhammadali-Akbarov/paytechuz',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={
        '': ['*.py'],
    },
    python_requires='>=3.6',

    install_requires=[
        'requests>=2.0,<3.0',
        "dataclasses>=0.6,<1.0; python_version<'3.7'",
    ],

    extras_require={
        'django': [
            'django>=3.0,<5.0',
            'djangorestframework>=3.0,<4.0',
        ],
        'fastapi': [
            'fastapi>=0.68.0,<1.0.0',
            'sqlalchemy>=1.4,<3.0',
            'httpx>=0.20,<1.0',
            'python-multipart==0.0.20',
            'pydantic>=1.8,<2.0',
        ],
        'flask': [
            'flask>=2.0,<3.0',
            'flask-sqlalchemy>=2.5,<3.0',
        ],
    },

    keywords=[
        "paytechuz", "payme", "click", "atmos", "uzbekistan", "payment", "gateway",
        "payment-gateway", "payment-processing", "django", "flask", "fastapi"
    ],

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
