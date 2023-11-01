%if 0%{?fedora} || 0%{?rhel} > 7
# Enable python3 build by default
%bcond_without python3
%else
%bcond_with python3
%endif

%if 0%{?rhel} > 7 || 0%{?fedora} > 30
# Disable python2 build by default
%bcond_with python2
%else
%bcond_without python2
%endif

Summary: A library for password generation and password quality checking
Name: libpwquality
Version: 1.4.4
Release: 6%{?dist}
# The package is BSD licensed with option to relicense as GPLv2+
# - this option is redundant as the BSD license allows that anyway.
License: BSD or GPLv2+
Source0: https://github.com/libpwquality/libpwquality/releases/download/libpwquality-%{version}/libpwquality-%{version}.tar.bz2

Patch100: libpwquality-1.4.4-rhel8-i18n.patch

%global _pwqlibdir %{_libdir}
%global _moduledir %{_libdir}/security
%global _secconfdir %{_sysconfdir}/security

Requires: cracklib-dicts >= 2.8
Requires: pam%{?_isa}
BuildRequires: gcc make
BuildRequires: cracklib-devel
BuildRequires: gettext
BuildRequires: pam-devel
%if %{with python2}
BuildRequires: python2-devel
%endif
%if %{with python3}
BuildRequires: python3-devel
%endif

URL: https://github.com/libpwquality/libpwquality/

# we don't want to provide private python extension libs
%define __provides_exclude_from ^(%{python_sitearch}|%{python3_sitearch})/.*\.so$.

%description
This is a library for password quality checks and generation
of random passwords that pass the checks.
This library uses the cracklib and cracklib dictionaries
to perform some of the checks.

%package devel
Summary: Support for development of applications using the libpwquality library
Requires: libpwquality%{?_isa} = %{version}-%{release}
Requires: pkgconfig

%description devel
Files needed for development of applications using the libpwquality
library.
See the pwquality.h header file for the API.

%if %{with python2}
%package -n python2-pwquality
%{?python_provide:%python_provide python2-pwquality}
Summary: Python bindings for the libpwquality library
Requires: libpwquality%{?_isa} = %{version}-%{release}

%description -n python2-pwquality
This is pwquality Python module that provides Python bindings
for the libpwquality library. These bindings can be used
for easy password quality checking and generation of random
pronounceable passwords from Python applications.
%endif

%if %{with python3}
%package -n python3-pwquality
Summary: Python bindings for the libpwquality library
Requires: libpwquality%{?_isa} = %{version}-%{release}

%description -n python3-pwquality
This is pwquality Python module that provides Python bindings
for the libpwquality library. These bindings can be used
for easy password quality checking and generation of random
pronounceable passwords from Python applications.
%endif

%prep
%setup -q

%if %{with python3} && %{with python2}
rm -rf %{py3dir}
cp -a . %{py3dir}
%endif
%patch100 -p1 -b .nodot

%build
%if %{with python2}
%configure \
	--with-securedir=%{_moduledir} \
	--with-pythonsitedir=%{python2_sitearch} \
	--with-python-binary=%{__python2} \
	--disable-static

make %{?_smp_mflags}
%endif
%if %{with python3} && %{with python2}
pushd %{py3dir}
%endif
%if %{with python3}
%configure \
	--with-securedir=%{_moduledir} \
	--with-pythonsitedir=%{python3_sitearch} \
	--with-python-binary=%{__python3} \
	--disable-static

make %{?_smp_mflags}
%endif
%if %{with python3} && %{with python2}
popd
%endif

%install
make install DESTDIR=$RPM_BUILD_ROOT INSTALL='install -p'

%if %{with python3} && %{with python2}
pushd %{py3dir}
make -C python install DESTDIR=$RPM_BUILD_ROOT INSTALL='install -p'
popd
%endif

%if "%{_pwqlibdir}" != "%{_libdir}"
pushd $RPM_BUILD_ROOT%{_libdir}
mv libpwquality.so.* $RPM_BUILD_ROOT%{_pwqlibdir}
ln -sf %{_pwqlibdir}/libpwquality.so.*.* libpwquality.so
popd
%endif
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_moduledir}/*.la

mkdir $RPM_BUILD_ROOT%{_secconfdir}/pwquality.conf.d

%find_lang libpwquality

%check
# Nothing yet

%ldconfig_scriptlets

%files -f libpwquality.lang
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc README NEWS AUTHORS
%{_bindir}/pwmake
%{_bindir}/pwscore
%{_moduledir}/pam_pwquality.so
%{_pwqlibdir}/libpwquality.so.*
%config(noreplace) %{_secconfdir}/pwquality.conf
%{_secconfdir}/pwquality.conf.d
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*

%files devel
%{_includedir}/pwquality.h
%{_libdir}/libpwquality.so
%{_libdir}/pkgconfig/*.pc
%{_mandir}/man3/*

%if %{with python2}
%files -n python2-pwquality
%{python2_sitearch}/pwquality.so
%{python2_sitearch}/*.egg-info
%endif

%if %{with python3}
%files -n python3-pwquality
%{python3_sitearch}/*.so
%{python3_sitearch}/*.egg-info
%endif

%changelog
* Tue Feb 14 2023 Dmitry Belyavskiy <dbelyavs@redhat.com> - 1.4.4-6
- rebuilt

* Mon Feb 13 2023 Dmitry Belyavskiy - 1.4.4-5
- rebuilt

* Tue Aug 30 2022 Dmitry Belyavskiy - 1.4.4-4
- Japan translation update (remove extra dot)
  Resolves: rhbz#2122609

* Mon Feb 22 2021 Dmitry Belyavskiy <dbelyavs@redhat.com> - 1.4.4-3
- Resolves: rhbz#1919026 libpwquaily rpm requires cracklib to function but RPM missing requirement [updated]

* Wed Feb 17 2021 Dmitry Belyavskiy <dbelyavs@redhat.com> - 1.4.4-2
- Resolves: rhbz#1919026 libpwquaily rpm requires cracklib to function but RPM missing requirement

* Tue Oct 13 2020 Tomáš Mráz <tmraz@redhat.com> 1.4.4-1
- Translation updates
- Add usersubstr check for substrings of N characters from the username
  patch by Danny Sauer
- pam_pwquality: Abort the retry loop if user requests it
- Allow setting retry, enforce_for_root, and local_users_only options
  in the pwquality.conf config file

* Mon Oct 22 2018 Tomáš Mráz <tmraz@redhat.com> 1.4.0-9
- Fix an issue found in Coverity scan

* Fri Jun 22 2018 Tomáš Mráz <tmraz@redhat.com> 1.4.0-8
- Properly conditionalize the python buildrequires

* Thu Mar 22 2018 Tomáš Mráz <tmraz@redhat.com> 1.4.0-7
- Add conditionals for Python2 and Python3

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Feb 03 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.4.0-5
- Switch to %%ldconfig_scriptlets

* Sun Dec 17 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 1.4.0-4
- Python 2 binary package renamed to python2-pwquality
  See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri May 26 2017 Tomáš Mráz <tmraz@redhat.com> 1.4.0-1
- Do not try to check presence of too short username in password
- Make the user name check optional (via usercheck option)
- Add an 'enforcing' option to make the checks to be warning-only
  in PAM
- The difok = 0 setting will disable all old password similarity
  checks except new and old passwords being identical
- Updated translations from Zanata

* Mon Aug 24 2015 Tomáš Mráz <tmraz@redhat.com> 1.3.0-2
- Fix possible stack overflow in the generate function (#1255935)

* Thu Jul 23 2015 Tomáš Mráz <tmraz@redhat.com> 1.3.0-1
- Change the defaults for credits, difok, and minlen
- Make the cracklib check optional but on by default
- Add implicit support for parsing  <cfgfile>.d/*.conf files
- Add libpwquality API manual page

* Wed Aug  6 2014 Tomáš Mráz <tmraz@redhat.com> 1.2.4-1
- fix license handling (by Tom Callaway)
- add Python3 module subpackage

* Thu Sep 12 2013 Tomáš Mráz <tmraz@redhat.com> 1.2.3-1
- fix problem with parsing the pam_pwquality options
  patch by Vladimir Sorokin.
- updated translations from Transifex
- treat empty user or password as NULL
- move the library to /usr

* Wed Jun 19 2013 Tomas Mraz <tmraz@redhat.com> 1.2.2-1
- manual page fixes
- make it possible to set the maxsequence configuration value
- updated translations from Transifex

* Thu Dec 20 2012 Tomas Mraz <tmraz@redhat.com> 1.2.1-1
- properly free pwquality settings
- add extern "C" to public header
- updated translations from Transifex

* Thu Aug 16 2012 Tomas Mraz <tmraz@redhat.com> 1.2.0-1
- add maxsequence check for too long monotonic character sequence.
- clarified alternative licensing to GPLv2+.
- add local_users_only option to skip the pwquality checks for
  non-locals. (thanks to Stef Walter)

* Wed Jun 13 2012 Tomas Mraz <tmraz@redhat.com> 1.1.1-1
- use rpm built-in filtering of provides (rhbz#830153)
- remove strain debug fprintf() (rhbz#831567)

* Thu May 24 2012 Tomas Mraz <tmraz@redhat.com> 1.1.0-1
- fix leak when throwing PWQError exception
- added pkgconfig file
- call the simplicity checks before the cracklib check
- add enforce_for_root option to the PAM module
- updated translations from Transifex

* Thu Dec  8 2011 Tomas Mraz <tmraz@redhat.com> 1.0.0-1
- added a few additional password quality checks
- bugfix in configuration file parsing

* Fri Nov 11 2011 Tomas Mraz <tmraz@redhat.com> 0.9.9-1
- added python bindings and documentation

* Mon Oct 10 2011 Tomas Mraz <tmraz@redhat.com> 0.9-2
- fixes for problems found in review (missing BR on pam-devel,
  License field, Source URL, Require pam, other cleanups)

* Mon Oct  3 2011 Tomas Mraz <tmraz@redhat.com> 0.9-1
- first spec file for libpwquality
