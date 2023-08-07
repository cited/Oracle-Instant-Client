#!/usr/bin/perl

require './oci-lib.pl';
require '../webmin/webmin-lib.pl';	#for OS detection
foreign_require('software', 'software-lib.pl');

sub get_packages_yum{

	my $cmd_out='';
	my $cmd_err='';
	local $out = &execute_command("yum search php", undef, \$cmd_out, \$cmd_err, 0, 0);

	if($out != 0){
		&error("Error: yum: $cmd_err");
		return 1;
	}

	my %pkgs;
	my @lines = split /\n/, $cmd_out;
	foreach my $line (@lines){
		if($line =~ /^(php[a-z0-9_\.-]+)\.(noarch|x86_64)+ : (.*)/i){
			$pkgs{$1} = $3;
		}
	}
	return %pkgs;
}

sub get_installed_yum{
	my $href = $_[0];

	my $pkg_list = "";
	foreach my $pkg (keys %$href){
		$pkg_list .= " $pkg";
	}

	my $cmd_out='';
	my $cmd_err='';
	local $out = &execute_command("rpm -q --queryformat \"%{NAME}\n\" $pkg_list", undef, \$cmd_out, \$cmd_err, 0, 0);

	my %pkgs;
	my @lines = split /\n/, $cmd_out;
	foreach my $line (@lines){
		if($line =~ /^package\s+([a-z0-9_\.-]+)\s/i){	#package php is not installed
			$pkgs{$1} = 0;
		}else{
			$pkgs{$line} = 1;
		}
	}
	return %pkgs;
};

sub get_packages_apt{

	my $cmd_out='';
	my $cmd_err='';
	local $out = &execute_command("apt-cache search '^php'", undef, \$cmd_out, \$cmd_err, 0, 0);

	if($cmd_err ne ""){
		&error("Error: apt-cache: $cmd_err");
		return 1;
	}

	my %pkgs;
	my @lines = split /\n/, $cmd_out;
	foreach my $line (@lines){
		if($line =~ /^(php.*) - (.*)/i){
			$pkgs{$1} = $2;
		}
	}
	return %pkgs;
}

sub get_installed_apt{
	my $href = $_[0];	#package names

	my %pkgs;

	my $cmd_out='';
	my $cmd_err='';
	local $out = &execute_command("dpkg -l 'php*'", undef, \$cmd_out, \$cmd_err);

	if($cmd_err ne ""){
		&error("Error: dpkg: $cmd_err");
		return %pkgs;
	}

	#set all packages to not installed, since dpkg won't list them
	foreach my $name (keys %$href){
		$pkgs{$name} = 0;
	}

	my @lines = split /\n/, $cmd_out;
	foreach my $line (@lines){
		if($line =~ /^(..)\s+(php[a-z0-9_\.-]+)\s+/i){
			my $pkg = $2;
			if($1 =~ /[uirph]i/){
				$pkgs{$pkg} = 1;
			}
		}
	}
	return %pkgs;
};

sub update_packages{
	my $pkgs_install = $_[0];
	my $pkgs_remove  = $_[1];	#\@lref

	if($pkgs_install ne ""){
		software::update_system_install($pkgs_install, undef);
	}

	if(@$pkgs_remove){
		print "<br><p>Removing packages</p>";
		my %opts = ('depstoo'=>1);
		my $error = "";
		if (defined(&delete_packages)) {
			$error = software::delete_packages($pkgs_remove, \%opts, undef);
		}else{
			foreach my $pkg (@$pkgs_remove){
				$error .= software::delete_package($pkg, \%opts, undef)
			}
		}

		if($error ne ""){
			&error($error);
		}else{
			foreach my $pkg (@$pkgs_remove){
				print "<tt>Deleted $pkg</tt><br>"
			}
		}

	}
}

&ui_print_header(undef, $text{'php_inst_title'}, "", "intro", 1, 1);

my $no_install = 1;
if($ENV{'CONTENT_TYPE'} =~ /boundary=(.*)$/) {
	&ReadParseMime();
	$no_install = 0;
}else{
	&ReadParse();
	$no_install = 1;
}

my %pkgs;
my %pkgs_installed;

my %osinfo = &detect_operating_system();
if( $osinfo{'os_type'} =~ /redhat/i){	#other redhat

	%pkgs 			= get_packages_yum();
	%pkgs_installed = get_installed_yum(\%pkgs);

}elsif( $osinfo{'real_os_type'} =~ /ubuntu/i){	#ubuntu
	%pkgs 			= get_packages_apt();
	%pkgs_installed = get_installed_apt(\%pkgs);
}

#Check what is updated
if ($ENV{REQUEST_METHOD} eq "POST" && $no_install == 0) {
	#find what was changed
	my @pkgs_remove;
	my $pkgs_install="";
	foreach my $pkg (sort keys %pkgs_installed){
		if($in{$pkg.'_status'} != $pkgs_installed{$pkg}){
			if($in{$pkg.'_status'} == 1){
				$pkgs_install .= " $pkg";
			}else{
				push(@pkgs_remove, $pkg);
			}
		}
	}
	update_packages($pkgs_install, \@pkgs_remove);

	&ui_print_footer("", $text{'index_return'});
	exit;
}

print &ui_form_start("php_install.cgi", "form-data");
print &ui_table_start($text{'php_inst_edit'}, "width=100%", 3);

foreach my $pkg (sort keys %pkgs){
	print &ui_table_row($pkg, ui_yesno_radio($pkg.'_status', $pkgs_installed{$pkg}).$pkgs{$pkg} ,3);
}

print &ui_table_end();
print &ui_form_end([ [ "", $text{'php_inst_save'} ] ]);

&ui_print_footer("", $text{'index_return'});
