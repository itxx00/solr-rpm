%define debug_package %{nil}
%define tdp_dir /usr/hdp/2.2.0.0-2041
%define base_install_dir %{tdp_dir}/%{name}
%define solr_group solr
%define solr_user solr

Name:           solr
Version:        6.5.1
Release:        1
Summary:        A distributed, highly available, RESTful search engine

Group:          System Environment/Daemons
License:        ASL 2.0
URL:            http://lucene.apache.org/solr/
Source0:        http://archive.apache.org/dist/lucene/solr/%{version}/solr-%{version}.tgz
Source1:        init.d-solr
Source2:        sysconfig-solr
Patch0:         solr.xml.patch
Patch1:         log4j.properties.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArchitectures: noarch

Requires:       lsof

Requires(post): chkconfig initscripts
Requires(pre):  chkconfig initscripts
Requires(pre):  shadow-utils

Provides: solr

%description
A distributed, highly available, RESTful search engine

%prep
%setup -q -n %{name}-%{version}

%patch0 -p0
%patch1 -p0

%build
true

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/hdp/2.2.0.0-2041/solr
mkdir -p $RPM_BUILD_ROOT/etc/solr/conf
mkdir -p $RPM_BUILD_ROOT/var/log/solr
mkdir -p $RPM_BUILD_ROOT/var/run/solr

cp -r * $RPM_BUILD_ROOT/usr/hdp/2.2.0.0-2041/solr/
rm -f $RPM_BUILD_ROOT/usr/hdp/2.2.0.0-2041/solr/*.txt


# config
%{__mkdir} -p %{buildroot}%{_sysconfdir}/solr
%{__install} -p -m 644 server/solr/README.txt %{buildroot}%{_sysconfdir}/%{name}
%{__install} -p -m 644 server/solr/solr.xml %{buildroot}%{_sysconfdir}/%{name}
%{__install} -p -m 644 server/solr/zoo.cfg %{buildroot}%{_sysconfdir}/%{name}
%{__install} -p -m 644 server/resources/log4j.properties %{buildroot}%{_sysconfdir}/%{name}
ln -sf %{_sysconfdir}/%{name}/log4j.properties %{buildroot}%{base_install_dir}/server/resources/log4j.properties

%{__install} -p -m 644 server/resources/jetty-logging.properties %{buildroot}%{_sysconfdir}/%{name}
ln -sf %{_sysconfdir}/%{name}/jetty-logging.properties %{buildroot}%{base_install_dir}/server/resources/jetty-logging.properties

# data
%{__mkdir} -p %{buildroot}%{_localstatedir}/lib/%{name}
%{__mkdir} -p %{buildroot}%{_localstatedir}/lib/%{name}/lib
ln -sf %{_sysconfdir}/%{name}/solr.xml %{buildroot}%{_localstatedir}/lib/%{name}/solr.xml

# logs
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{name}
ln -sf %{_localstatedir}/log/%{name} %{buildroot}%{base_install_dir}/server/logs

# plugins
%{__mkdir} -p %{buildroot}%{base_install_dir}/plugins

# sysconfig and init
%{__mkdir} -p %{buildroot}%{_sysconfdir}/rc.d/init.d
%{__mkdir} -p %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/rc.d/init.d/%{name}
%{__install} -m 755 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

%{__mkdir} -p %{buildroot}%{_localstatedir}/run/%{name}
%{__mkdir} -p %{buildroot}%{_localstatedir}/lock/subsys/%{name}

%pre
getent group %{solr_group} >/dev/null || groupadd -r %{solr_group}
getent passwd %{solr_user} >/dev/null || /usr/sbin/useradd --comment "Solr Daemon User" --shell /sbin/nologin -M -r -g %{solr_group} --home %{base_install_dir} %{solr_user}

%post
#/sbin/chkconfig --add %{name}
mkdir -p /usr/hdp/current
ln -s /usr/hdp/2.2.0.0-2041/solr /usr/hdp/current/solr

%preun
if [ $1 -eq 0 ]; then
  /sbin/service %{name} stop >/dev/null 2>&1
#  /sbin/chkconfig --del %{name}
fi

%postun
if [ $1 -eq 0 ]; then
  rm -rf /usr/hdp/current/solr
  rm -rf /usr/hdp/2.2.0.0-2041/solr
  rm -rf /var/run/solr
fi


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_sysconfdir}/rc.d/init.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%dir %{base_install_dir}
%{base_install_dir}/bin/*
%{base_install_dir}/dist/*
%{base_install_dir}/docs/*
%{base_install_dir}/example/*
%{base_install_dir}/contrib/*
%docdir %{base_install_dir}/docs/solr-core
%{base_install_dir}/licenses/*
%docdir %{base_install_dir}/licenses
%{base_install_dir}/server/*
%dir %{base_install_dir}/plugins
%config(noreplace) %{_sysconfdir}/%{name}
%defattr(-,%{solr_user},%{solr_group},-)
%dir %{_localstatedir}/lib/%{name}
%{_localstatedir}/lib/%{name}/solr.xml
%dir %{_localstatedir}/lib/%{name}/lib
%{_localstatedir}/run/%{name}
%dir %{_localstatedir}/log/%{name}


%changelog
* Sun Apr 30 2017 itxx00 <itxx00@gmail.com> - 6.5.1-1
- bump version to 6.5.1
