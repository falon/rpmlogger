# Install

We provide three installation types. You can clone from github,
install by pip, or use yum.

## Git clone
With clone you can import the code in your environment:

    git clone https://github.com/falon/rpmlogger.git

Don't use virtual env, because rpm module doesn't support it.


Rename the `rpmlogger.conf-dist` in `rpmlogger.conf`.
    
## Install with pip

At the moment the package is only under the test pypi. So you can

    pip3 install --index-url https://test.pypi.org/simple rpmlogger

## Red Hat Installation

If you like there is an easy installation under Red Hat.
Red Hat or Centos >=7 is required. The deployment requires systemd.

If you are in a Red Hat 8 system, then

    curl -1sLf \
      'https://dl.cloudsmith.io/public/csi/rpmlogger/cfg/setup/bash.rpm.sh' \
      | sudo bash
    
If you are in a Red Hat 7 system, then

    curl -1sLf \
      'https://dl.cloudsmith.io/public/csi/rpmlogger/cfg/setup/bash.rpm.sh' \
      | sudo distro=el codename=8 bash

Finally:

    yum install rpmlogger

With this installation all must work as is. The setup provides configuration,
 services and timers.

    systemctl enable rpmlogger.timer

In EL8 remember to set the default python as

    alternatives --set python /usr/bin/python3
