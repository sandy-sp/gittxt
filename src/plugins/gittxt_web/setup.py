from setuptools import setup, find_packages

setup(
    name="gittxt_web",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "bottle",           # ~200 KB, single file
        # no FastAPI/Uvicorn
    ],
    entry_points={
        "gittxt.plugins": [
            "web = gittxt_web.plugin:cli_web_group"
        ],
    },
)
