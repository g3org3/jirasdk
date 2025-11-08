from setuptools import find_packages, setup

_ = setup(
    name="jirasdk",
    verison="0.0.1",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "jira=jirasdk.cli:main",
        ],
    },
)
