from setuptools import setup, find_packages

setup(
    name="secondpath",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "python-dotenv>=0.19.0",
        "pydantic>=2.0.0",
        "rich>=10.0.0",
    ],
    python_requires=">=3.11",
    author="Andy Lee",
    description="A terminal-based agent engine that simulates a Strategic Council",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
    ],
) 