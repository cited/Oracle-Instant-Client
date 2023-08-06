#!/usr/bin/perl


require 'oci-lib.pl';
require '../webmin/webmin-lib.pl';	#for OS detection
foreign_require('software', 'software-lib.pl');
foreign_require('apache', 'apache-lib.pl');

sub check_pg_ext_deps{
	my $pg_ver = $_[0];
	my @ext_pkgs;

	if( ($osinfo{'os_type'} =~ /debian/i)){
		@ext_pkgs = ("postgresql-$pg_ver-pgrouting-scripts", "postgresql-$pg_ver-pgrouting");
		if($pg_ver <= 13){
			push(@ext_pkgs, "postgresql-$pg_ver-postgis-2.5-scripts");
		}else{
			# from PG 14 postgis is >= 3
			push(@ext_pkgs, "postgresql-$pg_ver-postgis-3-scripts");
		}
	}elsif( $osinfo{'os_type'} =~ /redhat/i){
		my $pg_ver2;
		($pg_ver2 = $pg_ver) =~ s/\.//;
		my $postgis_pkg = get_postgis_pkg_name($pg_ver);
		@ext_pkgs = ($postgis_pkg, "pgrouting_$pg_ver2", "postgresql$pg_ver2-contrib");
	}

	my @pkg_missing;
	foreach my $pkg (@ext_pkgs){
		my @pinfo = software::package_info($pkg);
		if(!@pinfo){
			push(@pkg_missing, $pkg);
		}
	}

	if(@pkg_missing){
		my $url_pkg_list = '';
		foreach my $pkg (@pkg_missing){
			$url_pkg_list .= '&u='.&urlize($pkg);
		}
		my $pkg_list = join(', ', @pkg_missing);

		print "<p>Warning: Missing PG package dependencies - $pkg_list packages are not installed. Install them manually or ".
				"<a href='../package-updates/update.cgi?mode=new&source=3${url_pkg_list}&redir=%2E%2E%2Foci%2Fsetup.cgi&redirdesc=OCI%2CSetup'>click here</a> to have them installed.</p>";
	}
}

sub setup_checks{

	my %osinfo = &detect_operating_system();
	my @pkg_deps;
	if(	( $osinfo{'real_os_type'} =~ /rocky/i) or	#Rocky
			($osinfo{'real_os_type'} =~ /centos/i)	){	#CentOS
		@pkg_deps = ('php', 'php-devel', 'php-cgi', 'php-cli', 'httpd', 'libaio1', 'make', 'gcc')

	}elsif( ($osinfo{'real_os_type'} =~ /ubuntu/i) or
					($osinfo{'real_os_type'} =~ /debian/i) 	){	#ubuntu or debian
		@pkg_deps = ('php', 'php-dev', 'php-cgi', 'php-cli', 'apache2', 'libaio1', 'make', 'gcc');
		if($found_pg_repo == 1){
			push(@pkg_deps, ("postgresql-$pg_ver-mysql-fdw", "postgresql-$pg_ver-tds-fdw", "postgresql-server-dev-$pg_ver"));
		}
	}

	my @pkg_missing;
	foreach my $pkg (@pkg_deps){
		my @pinfo = software::package_info($pkg);
		if(!@pinfo){
			push(@pkg_missing, $pkg);
		}
	}

	if(@pkg_missing){
		my $url_pkg_list = '';
		foreach my $pkg (@pkg_missing){
			$url_pkg_list .= '&u='.&urlize($pkg);
		}
		my $pkg_list = join(', ', @pkg_missing);

		print "<p>Warning: Missing package dependencies - $pkg_list - are not installed. Install them manually or ".
				"<a href='../package-updates/update.cgi?mode=new&source=3${url_pkg_list}&redir=%2E%2E%2Foci%2Fsetup.cgi&redirdesc=Setup'>click here</a> to have them installed.</p>";
	}

	if(! -d '/opt/oracle'){
		print '<p>Oracle Instant Client is not installed. Install it from <a href="./edit_oci.cgi">OCI</a>';
	}

	print '<p>If you don\'t see any warning above, you can complete setup from '.
		  "<a href='setup.cgi?mode=cleanup&return=%2E%2E%2Foci%2F&returndesc=Setup&caller=oci'>here</a></p>";
}

#Remove all setup files
sub setup_cleanup{
	my $file = $module_root_directory.'/setup.cgi';
	print "Completing Installation</br>";
	&unlink_file($file);

	print &js_redirect("index.cgi");
}


&ui_print_header(undef, $text{'setup_title'}, "");

if($ENV{'CONTENT_TYPE'} =~ /boundary=(.*)$/) {
	&ReadParseMime();
}else {
	&ReadParse(); $no_upload = 1;
}

my $mode = $in{'mode'} || "checks";

if($mode eq "checks"){							setup_checks();
	&ui_print_footer('', $text{'index_return'});
	exit 0;
}elsif($mode eq "cleanup"){						setup_cleanup();
	&ui_print_footer('', $text{'index_return'});
	exit 0;

}elsif($mode eq "oracle_fdw"){						install_oracle_fdw();
	&ui_print_footer('', $text{'index_return'});
	exit 0;
}else{
	print "Error: Invalid setup mode\n";
}

&ui_print_footer('setup.cgi', $text{'setup_title'});
