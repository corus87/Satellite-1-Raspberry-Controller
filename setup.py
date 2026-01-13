from setuptools import setup, find_packages

setup(
    name="sat1_control",
    version="1.0.2",    
    description="Basic control for FutureProofHomes Satellite 1 with a Raspberry PI",
    url="https://github.com/corus87/Satellite-1-Raspberry-Controller/",
    author="Corus87",
    license="MIT license",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["spidev",
                      "smbus2",                   
                      ],
    entry_points={
        'console_scripts': [
            'sat1-control = sat1_control.__main__:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.8"
        "Programming Language :: Python :: 3.9"
        "Programming Language :: Python :: 3.10"
        "Programming Language :: Python :: 3.11"
        "Programming Language :: Python :: 3.12"
    ],
)
