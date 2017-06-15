FROM centos
ADD http://rpms.adiscon.com/v8-stable/rsyslog.repo /etc/yum.repos.d
ADD http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-9.noarch.rpm /tmp/epel.rpm

RUN rpm -ivh /tmp/epel.rpm \ 
    && curl -s https://packagecloud.io/install/repositories/madecom/public/script.rpm.sh | bash \
    && yum install -y rsyslog-8.27.0_experimental_d6d5a0913-1.x86_64 \
    && mkdir -p /run/rsyslog

COPY rsyslog.conf /etc/rsyslog.conf
COPY rsyslog-http.rb /etc/rsyslog-http.rb
COPY error-level.lookup /etc/error-level.lookup
VOLUME ["/run/rsyslog/"]
CMD ["rsyslogd", "-dn"]
