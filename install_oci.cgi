#!/usr/bin/perl

require './oci-lib.pl';

sub download_otn{
	my $ver = $_[0];
	my $ver2;
	my $name = $_[1];
	my $page_number = $_[2];

	($ver2 = $ver) =~ s/\.//g;

	my $time_limit = time().100;

	print "<hr>Downloading $name-$ver ...<br>";

	my $url = "http://download.oracle.com/otn_software/linux/instantclient/$ver2/instantclient-$name-linux.x64-".$ver."dbru.zip";
	my $tmpfile = &transname("instantclient-$name-linux.x64-$ver.zip");
	#my $tmpfile = "/tmp/instantclient-$name-linux.x64-$ver.zip";
	&error_setup(&text('install_err3', $url));

	#'testSessionCookie=Enabled'.
	#'; oraclelicense=accept-ic_linuxx8664-cookie'.
	#"; s_sq=oracleotnlive%2Coracleglobal%3D%2526pid%253Dotn%25253Aen-us%25253A%25252Ftopics%25252Flinuxx86-64soft-$page_number.html%2526pidt%253D1%2526oid%253Dfunctiononclick(event)%25257BacceptAgreement(window.self)%25253B%25257D%2526oidt%253D2%2526ot%253DRADIO".
	#my $cookie_value =	"gpw_e24=http%3A%2F%2Fwww.oracle.com%2Ftechnetwork%2Ftopics%2Flinuxx86-64soft-$page_number.html".
	#					'; oraclelicense=accept-securebackup-cookie'.
	#					'; s_cc=true'.
	#					"; s_nr=$time_limit";
	#print "Cookie: $cookie_value<br>";
	#my %cookie_headers = ('Cookie'=> $cookie_value);
	&http_download("download.oracle.com", 443, "/otn_software/linux/instantclient/$ver2/instantclient-$name-linux.x64-".$ver."dbru.zip",
					$tmpfile, \$error, undef, 1);#, undef, undef, 0, 0, 1, \%cookie_headers);
	return $tmpfile;
}

sub download_cdn{
	my $ver = $_[0];
	my $name = $_[1];

	my $cdn_host = '10.0.3.1';
	my $cdn_folder = '/12.1.0.2.0';

	print "<hr>Downloading $name-$ver ...<br>";

	my $url = "http://$cdn_host"."$cdn_folder/instantclient-$name-linux.x64-$ver.zip";
	my $tmpfile = &transname("instantclient-$name-linux.x64-$ver.zip");
	&error_setup(&text('install_err3', $url));

	&http_download($cdn_host, 80,"$cdn_folder/instantclient-$name-linux.x64-$ver.zip", $tmpfile);

	return $tmpfile;
}

sub install_oci8{
	my $oracle_home = $_[0];
	my $instantclient_home = $_[1];
	my $oci_ver;

	my %versions = get_versions();
	my @php_ver = split(/\./, $versions{'php'});
	if(($php_ver[0] == 8) and ($php_ver[1] == 2)){
		$oci_ver = '3.3.0';
	}elsif(($php_ver[0] == 8) and ($php_ver[1] == 1)){
		$oci_ver = '3.2.1';
	}elsif($php_ver[0] == 7){
		$oci_ver = '2.1.4';
	}elsif($php_ver[0] == 5){
		$oci_ver = '2.0.10';
	}elsif($php_ver[0] == 4){
		$oci_ver = '1.4.10';
	}else{
		&error("Error: oci8: Unsupported PHP version $versions{'php'}<br>");
	}

	my $oci8_home = "$oracle_home/src/oci8-$oci_ver";

	&make_dir($oracle_home.'/src', 0754, 1);

	#pecl download oci8
	my $url = "https://pecl.php.net/get/oci8-$oci_ver.tgz";
	my $tmpfile = &transname("oci8-$oci_ver.tgz");
	&error_setup(&text('install_err3', $url));
	&http_download("pecl.php.net", 443,"/get/oci8-$oci_ver.tgz", $tmpfile, \$error, undef, 1);

	my $cmd_out='';
	my $cmd_err='';
	print "<hr>Extracting $tmpfile to $oracle_home/src...<br>";
	local $out = &execute_command("tar -x --overwrite -f \"$tmpfile\" -C$oracle_home/src", undef, \$cmd_out, \$cmd_err, 0, 0);

	if($cmd_err){
		&error("Error: tar: $cmd_err");
	}else{
		$cmd_out =~ s/\r\n/<br>/g;
		print &html_escape($cmd_out);
	}

	#compile OCI 8 module
	my $orig_cwd = cwd;
	chdir $oci8_home;

	my @cmds = ('phpize',
				"./configure --with-oci8=share,instantclient,$oracle_home/instantclient/",
				"make && make install");
	foreach my $cmd (@cmds){
		my $cmd_out='';
		my $cmd_err='';
		local $out = &execute_command($cmd, undef, \$cmd_out, \$cmd_err, 0, 0);
		if($out != 0){
			&error($cmd_err);
		}
	}
	copy_source_dest("$oci8_home/modules/oci8.so", "$oracle_home/instantclient/oci8.so");

	chdir $orig_cwd;

	#Add PHP config for CLI and CGI
	print "Setting PHP ini files for CLI and CGI<br>";

	my $cgi_file = &transname('info.php');
	open(my $fh, '>', $cgi_file) or die "open:$!";
	print $fh "<?php phpinfo(); ?>";
	close $fh;

	my %php_cmds = ('php --ini'	=>"^Scan for additional .ini files in: (.*)",
					"REDIRECT_STATUS=200 REQUEST_METHOD=GET SCRIPT_FILENAME=$cgi_file SCRIPT_NAME=/info.php PATH_INFO=/ SERVER_NAME=site.tld SERVER_PROTOCOL=HTTP/1.1 REQUEST_URI=/nl/page HTTP_HOST=site.tld /usr/bin/php-cgi"=>"Scan this dir for additional \.ini files <\/td><td class=\"v\">([a-z0-9\/_\.-]+)");

	my %ext_file = ('extension'=>'oci8.so');

	$SIG{'TERM'} = 'ignore';
	foreach my $cmd (keys %php_cmds){
		&open_execute_command(CMD, $cmd, 1);

		my $pattern = $php_cmds{$cmd};
		my $php_confd = '';

		while(my $line = <CMD>) {
			if($line =~ /$pattern/){
				$php_confd = $1;
				last;
			}
		}
		close(CMD);

		if(-d $php_confd){
			write_file($php_confd.'/90-oci.ini', \%ext_file);
		}else{
			print "Warning: Failed to add OCI extension to $cmd ini files.<br>";
		}
	}
}

sub setup_instant_libs{
	my $instantclient_home = $_[0];

	print "<hr>Setting Oracle Instant Client libs in /etc/ld.so.conf.d/instantclient.conf<br>";

	opendir(DIR, $instantclient_home) or die $!;
    my @libs
        = grep {
			/\.so([0-9\.]+)?$/       			# Has .so* extension
			&& -f "$instantclient_home/$_"  # and is a file
	} readdir(DIR);
    closedir(DIR);

	&make_dir($instantclient_home.'/lib', 0755, 1);

	for my $lib (@libs){
		symlink_file($instantclient_home.'/'.$lib,
					 $instantclient_home."/lib/$lib");
	}

	open(my $fh, '>', '/etc/ld.so.conf.d/instantclient.conf') or die "open:$!";
	print $fh '/opt/oracle/instantclient/lib';
	close $fh;

	#echo '/usr/lib/grass64/lib/'		 > /etc/ld.so.conf.d/grass.conf
	#echo '/usr/lib/jvm/java-7-openjdk-amd64/jre/lib/amd64/server/' > /etc/ld.so.conf.d/jvm.conf

	my $cmd_out='';
	my $cmd_err='';
	local $out = &execute_command('ldconfig', undef, \$cmd_out, \$cmd_err, 0, 0);
	if($out != 0){
		&error($cmd_err);
	}
}

sub setup_instant_env{
	my $instantclient_home = $_[0];
	my $instantclient_ver = $_[1];

	my %os_env;

	$os_env{'INSTANTCLIENT_VERSION'} = $instantclient_ver;
	$os_env{'INSTANTCLIENT_HOME'}	 = $instantclient_home;
	$os_env{'ORACLE_HOME'}				 = $instantclient_home;

	print "<hr>Setting Oracle Instant Client environment...";

	if(-d '/etc/profile.d/'){
		$os_env{'PATH'} = "\$PATH:$instantclient_home";
		write_env_file('/etc/profile.d/instantclient.sh', \%os_env, 1);
	}else{
		read_env_file('/etc/environment', \%os_env);
		$os_env{'PATH'} = "$os_env{'PATH'}:$instantclient_home";
		write_env_file('/etc/environment', \%os_env, 0);
	}
}

$| = 1;

if ($ENV{REQUEST_METHOD} eq "POST") {
	&ReadParseMime();
}else {
	&ReadParse();
	$no_upload = 1;
}

&ui_print_header(undef, $text{'install_title'}, "");

my $oci_ver = $in{'oci_ver'};
my $page_number = $in{'page_number'};
my @pkgs = ('basic', 'jdbc', 'sqlplus', 'sdk', 'odbc', 'tools');


my $oracle_home = "/opt/oracle";
&make_dir($oracle_home, 0755, 1);

if(-d $oracle_home.'/instantclient_'.$oci_ver){
	print "Error: Oracle Instant Client $oci_ver is already installed!<br>";
	&ui_print_footer("", $text{'index_return'});
	exit;
}

#download and unzip selected packages
foreach my $pkg_name (@pkgs){
	if($in{'pkg_'.$pkg_name} == 1){
		my $zip_file = download_otn($oci_ver, $pkg_name, $page_number);
		unzip_file($zip_file, $oracle_home);
	}
}

my @oci_ver_digits = split(/\./, $oci_ver);

&rename_file($oracle_home.'/instantclient_'.$oci_ver_digits[0].'_'.$oci_ver_digits[1],
			 $oracle_home.'/instantclient_'.$oci_ver);
my $instantclient_home = $oracle_home.'/instantclient_'.$oci_ver;

symlink_file($instantclient_home, $oracle_home.'/instantclient');

#link clntsh and occi libs
symlink_file($instantclient_home.'/libclntsh.so.'.$oci_ver_digits[0].'.'.$oci_ver_digits[1],
			 $oracle_home.'/instantclient/libclntsh.so');
symlink_file($instantclient_home.'/libocci.so.'.$oci_ver_digits[0].'.'.$oci_ver_digits[1],
			 $oracle_home.'/instantclient/libocci.so');

install_oci8($oracle_home);

setup_instant_libs($instantclient_home);
setup_instant_env($instantclient_home, $oci_ver);

&ui_print_footer("", $text{'index_return'});
