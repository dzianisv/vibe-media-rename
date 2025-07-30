#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vibe-media-rename",
    version="1.0.2",
    author="Vibe Tools",
    author_email="tools@vibe.dev",
    description="A tool to rename media files based on location metadata with smart heuristics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vibe-tools/vibe-media-rename",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Video",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "Pillow>=9.0.0",
        "exifread>=3.0.0",
        "geopy>=2.3.0",
    ],
    extras_require={
        "video": ["ffmpeg-python>=0.2.0"],
    },
    entry_points={
        "console_scripts": [
            "vibe_media_rename=vibe_media_rename.cli:main",
        ],
    },
    keywords="media, rename, gps, exif, photo, video, location, metadata",
    project_urls={
        "Bug Reports": "https://github.com/vibe-tools/vibe-media-rename/issues",
        "Source": "https://github.com/vibe-tools/vibe-media-rename",
    },
)