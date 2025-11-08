from setuptools import find_packages, setup

_ = setup(
    name="jirasdk",
    verison="0.1.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=["requests", "tabulate"],
    entry_points={
        "console_scripts": [
            "jira=jirasdk.cli:main",
        ],
    },
)
