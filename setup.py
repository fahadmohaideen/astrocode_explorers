from setuptools import setup, find_packages

setup(
    name="orbital",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'pygame>=2.0.0',
        'numpy>=1.19.0',
    ],
    # Add other metadata as needed
    author="Your Name",
    author_email="your.email@example.com",
    description="A space-themed game",
    url="https://github.com/yourusername/astrocode-explorers",
)
