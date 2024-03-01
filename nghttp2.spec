# TODO: mruby, neverbleed?
#
# Conditional build:
%bcond_with	http3		# experimental HTTP/3 support
%bcond_with	libbpf		# BPF support (requires CC=clang)
%bcond_without	static_libs	# static libraries
%bcond_without	systemd		# don't include systemd support
%bcond_without	tests		# "make check" call

Summary:	HTTP/2.0 C library
Summary(pl.UTF-8):	Biblioteka C HTTP/2.0
Name:		nghttp2
Version:	1.60.0
Release:	1
License:	MIT
Group:		Libraries
#Source0Download: https://github.com/nghttp2/nghttp2/releases
Source0:	https://github.com/nghttp2/nghttp2/releases/download/v%{version}/%{name}-%{version}.tar.xz
# Source0-md5:	2b09aaea09a783b2f31e3e5adaeaecbd
URL:		https://nghttp2.org/
BuildRequires:	autoconf >= 2.61
BuildRequires:	automake
BuildRequires:	c-ares-devel >= 1.7.5
BuildRequires:	jansson-devel >= 2.5
%{?with_libbpf:BuildRequires:	libbpf-devel >= 0.7.0}
BuildRequires:	libev-devel
# for examples
BuildRequires:	libevent-devel >= 2.0.8
BuildRequires:	libstdc++-devel >= 6:5
BuildRequires:	libtool >= 2:2.2.6
BuildRequires:	libxml2-devel >= 1:2.6.26
%{?with_http3:BuildRequires:	nghttp3-devel >= 1.1.0}
# +ngtcp2-crypto-openssl or ngtcp2-crypto-boringssl
%{?with_http3:BuildRequires:	ngtcp2-devel >= 1.0.0}
BuildRequires:	openssl-devel >= 1.1.1
%{?with_http3:BuildRequires:	openssl-devel(quic)}
BuildRequires:	pkgconfig >= 1:0.20
BuildRequires:	python3 >= 1:3.8
BuildRequires:	rpmbuild(macros) >= 1.734
BuildRequires:	sed >= 4.0
%{?with_systemd:BuildRequires:	systemd-devel >= 1:209}
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	zlib-devel >= 1.2.3
Requires:	%{name}-libs = %{version}-%{release}
Requires:	c-ares >= 1.7.5
Requires:	jansson >= 2.5
# noinst examples only
#Requires:	libevent >= 2.0.8
Requires:	libxml2 >= 1:2.6.26
Requires:	openssl >= 1.1.1
Requires:	zlib >= 1.2.3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is an experimental implementation of Hypertext Transfer Protocol
version 2.0.

%description -l pl.UTF-8
Ta biblioteka jest eksperymentalną implementacją protokołu HTTP
(Hypertext Transfer Protocol) w wersji 2.0.

%package libs
Summary:	A library implementing the HTTP/2 protocol
Summary(pl.UTF-8):	Biblioteka implementująca protokół HTTP/2
Group:		Libraries
Obsoletes:	python3-nghttp2 < 1.55.1
Conflicts:	nghttp2 < 1.11.1-2

%description libs
libnghttp2 is a library implementing the Hypertext Transfer Protocol
version 2 (HTTP/2) protocol in C.

%description libs -l pl.UTF-8
libnghttp2 to napisana w C biblioteka implementująca protokół HTTP/2
(Hypertext Transfer Protocol w wersji 2).

%package devel
Summary:	Files needed for developing with libnghttp2
Summary(pl.UTF-8):	Pliki niezbędne do tworzenia aplikacji z użyciem libnghttp2
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Files needed for building applications with libnghttp2.

%description devel -l pl.UTF-8
Pliki niezbędne do tworzenia aplikacji z użyciem libnghttp2.

%package static
Summary:	Static libnghttp2 library
Summary(pl.UTF-8):	Statyczna biblioteka libnghttp2
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static libnghttp2 library.

%description static -l pl.UTF-8
Statyczna biblioteka libnghttp2.

%prep
%setup -q

%{__sed} -i -e '1s,/usr/bin/env python,%{__python3},' script/fetch-ocsp-response

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--enable-app \
	--enable-hpack-tools \
	%{?with_http3:--enable-http3} \
	--disable-silent-rules \
	%{!?with_static_libs:--disable-static} \
	--without-jemalloc \
	%{?with_libbpf:--with-libbpf}

%{__make}

%if %{with tests}
%{__make} check
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libnghttp2*.la
# packaged as %doc
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/nghttp2

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING ChangeLog README.rst
%attr(755,root,root) %{_bindir}/deflatehd
%attr(755,root,root) %{_bindir}/h2load
%attr(755,root,root) %{_bindir}/inflatehd
%attr(755,root,root) %{_bindir}/nghttp
%attr(755,root,root) %{_bindir}/nghttpd
%attr(755,root,root) %{_bindir}/nghttpx
%dir %{_datadir}/nghttp2
%attr(755,root,root) %{_datadir}/nghttp2/fetch-ocsp-response
%{_mandir}/man1/h2load.1*
%{_mandir}/man1/nghttp.1*
%{_mandir}/man1/nghttpd.1*
%{_mandir}/man1/nghttpx.1*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libnghttp2.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libnghttp2.so.14

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libnghttp2.so
%dir %{_includedir}/nghttp2
%{_includedir}/nghttp2/nghttp2*.h
%{_pkgconfigdir}/libnghttp2.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libnghttp2.a
%endif
