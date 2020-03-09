from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='rpmlogger',
    version='0.1.post1',
    description='RPM Packages version reporter',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="yum,dnf,rpm,packages,linux,centos,redhat",
    scripts=['rpmlogger.py'],
    include_package_data = False,
    package_data={
        '': ['etc/rpmlogger.conf-dist'],
    },
    data_files=[
        ('/etc/rpmlogger', ['etc/rpmlogger.conf-dist']),
        ('/usr/share/doc/rpmlogger', ['README.md', 'INSTALL.md']),
        ('/usr/share/licenses/rpmlogger', ['LICENSE']),
        ('/usr/lib/systemd/system', ['systemd/rpmlogger.service',
                                     'systemd/rpmlogger.timer',]),
        ('/etc/logrotate.d', ['systemd/rpmlogger.logrotate'])
    ],
    install_requires=[
        'rpm>=0.2.0',
        'PyYAML>=5.2',
        'psutil'
    ],
    python_requires='>=3.6',
    url='https://github.com/falon/rpmlogger',
    license='Apache License 2.0',
    author='Marco Favero',
    author_email='m.faverof@gmail.com',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Topic :: System",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Operating System",
        "Topic :: Utilities"
    ]
)
