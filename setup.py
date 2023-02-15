from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='UETSchedule',
    version='0.1.4',
    description='A script to auto schedule UET courses',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ppvan/autotkb',
    author='ppvan',
    author_email='phuclaplace@gmail.com',
    license='GPL-3.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords=['uet', 'schedule'],
    python_requires='>=3.7',
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={
        'console_scripts': [
            'schedule = schedule.cli:main',
        ],
    },
)
