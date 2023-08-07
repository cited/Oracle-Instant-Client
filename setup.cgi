#!/usr/bin/perl


require 'oci-lib.pl';
require '../webmin/webmin-lib.pl';	#for OS detection
foreign_require('software', 'software-lib.pl');
foreign_require('apache', 'apache-lib.pl');

sub setup_checks{

	my %osinfo = &detect_operating_system();
	
	if( $osinfo{'os_type'} =~ /redhat/i){	#other redhat

		@pinfo = software::package_info('epel-release', undef, );
		if(!@pinfo){
			print "<p>Info: You can install epel-release to have more PHP packages. Install it manually or ".
					"<a href='../software/install_pack.cgi?source=3&update=epel-release&return=%2E%2E%2Foci%2F&returndesc=Oracle%20PHP&caller=oci'>click here</a> to have it downloaded and installed.</p>";
		}
	}
	my @pkg_deps;
	if(	( $osinfo{'real_os_type'} =~ /rocky/i) or	#Rocky
			($osinfo{'real_os_type'} =~ /centos/i)	or	#CentOS
			($osinfo{'real_os_type'} =~ /alma/i)	){	#Alma Linux
		@pkg_deps = ('php', 'php-devel', 'mod_fcgid', 'php-cli', 'httpd', 'libaio', 'make', 'gcc')

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
