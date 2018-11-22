from mesos/mesos-centos 


# 'Mesos > 0.21.0' requires 'subversion > 1.8' devel package,
# which is not available in the default repositories.
# Create a WANdisco SVN repo file to install the correct version:
RUN curl https://gist.githubusercontent.com/dciangot/eb2a5ca46df675510c9cd6860df05ca3/raw/df39227304d7abe3161359584e28c80989b70ef5/repo-mesos.repo -o /etc/yum.repos.d/wandisco-svn.repo 

# Parts of Mesos require systemd in order to operate. However, Mesos
# only supports versions of systemd that contain the 'Delegate' flag.
# This flag was first introduced in 'systemd version 218', which is
# lower than the default version installed by centos. Luckily, centos
# 7.1 has a patched 'systemd < 218' that contains the 'Delegate' flag.
# Explicity update systemd to this patched version.
RUN yum update systemd

# Install essential development tools.
RUN yum groupinstall -y "Development Tools"
RUN yum install -y apache-maven python-devel python-six python-virtualenv java-1.8.0-openjdk-devel zlib-devel libcurl-devel openssl-devel cyrus-sasl-devel cyrus-sasl-md5 apr-devel subversion-devel apr-util-devel

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python get-pip.py
RUN pip install mesos.scheduler mesos.interface mesos.executor
