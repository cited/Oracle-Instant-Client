BEGIN { push(@INC, ".."); };
use WebminCore;
#use File::Copy;
init_config();

sub get_oci_config
{
my $lref = &read_file_lines($config{'oci_conf'});
my @rv;
my $lnum = 0;
foreach my $line (@$lref) {
    my ($n, $v) = split(/\s+/, $line, 2);
    if ($n) {
      push(@rv, { 'name' => $n, 'value' => $v, 'line' => $lnum });
      }
    $lnum++;
    }
return @rv;
}

sub get_versions
{
	local %version;

	my $cmd_out='';
	my $cmd_err='';
	local $out = &execute_command("php -v", undef, \$cmd_out, \$cmd_err, 0, 0);

	if($cmd_err ne ""){
		&error("Error: php: $cmd_err");
		return 1;
	}

	my @lines = split /\n/, $cmd_out;
	foreach my $line (@lines){
		if($line =~ /^PHP ([0-9\.-]+)/i){
			$version{'php'} = $1;
		}
	}
	$version{'oci'} = installed_instantclient_version();

	return %version;
}

sub file_basename
{
	my $rv = $_[0];
	$rv =~ s/^.*[\/\\]//;
	return $rv;
}

sub installed_instantclient_version(){
	my %os_env;
	if(-f '/etc/profile.d/instantclient.sh'){
		read_env_file('/etc/profile.d/instantclient.sh', \%os_env);
	}else{
		read_env_file('/etc/environment', \%os_env);
	}
	return $os_env{'INSTANTCLIENT_VERSION'};
}

sub get_instantclient_home(){
	my %os_env;
	if(-f '/etc/profile.d/oci.sh'){
		read_env_file('/etc/profile.d/oci.sh', \%os_env);
	}else{
		read_env_file('/etc/environment', \%os_env);
	}
	return $os_env{'INSTANTCLIENT_HOME'};
}

#Parse available OCI versions from OTN
sub get_oci_versions(){
	my $error;

	$url = "https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html";
	$tmpfile = &transname("oci.html");
	&error_setup(&text('install_err3', $url));
	my %cookie_headers = ('Cookie'=> 'oraclelicense=accept-securebackup-cookie');
	&http_download("www.oracle.com", 443,"/database/technologies/instant-client/linux-x86-64-downloads.html",
					$tmpfile, \$error, undef, 1, undef, undef, 0, 0, 1, \%cookie_headers);

	my @oci_versions;
	open($fh, '<', $tmpfile) or die "open:$!";
	while(my $line = <$fh>){
		if($line =~ /Version ([0-9\.]+)/){
			push(@oci_versions, $1);
		}
	}
	close $fh;

	push(@oci_versions, $page_number);

	return @oci_versions;
}

sub download_file{
	my $url = $_[0];

	my ($proto, $x, $host, $path) = split('/', $url, 4);
	my @paths = split('/', $url);
	my $filename = $paths[-1];
	if($filename eq ''){
		$filename = 'index.html';
	}

	my $sslmode = $proto eq 'https:';
	my $port = 80;
	if($sslmode){
		$port = 443;
	}

	&error_setup(&text('install_err3', $url));
	my $tmpfile = &transname($filename);
	$progress_callback_url = $url;

	&http_download($host, $port, '/'.$path, $tmpfile, \$error, \&progress_callback, $sslmode);

	if($error){
		print &html_escape($error);
		return '';
	}
	return $tmpfile;
}

sub exec_cmd{
	my $cmd = $_[0];
	my $cmd_out='';

	my $rv = &execute_command($cmd, undef, \$cmd_out, \$cmd_out, 0, 0);
	if($cmd_out){
  	$cmd_out = &html_escape($cmd_out);
  	$cmd_out =~ s/[\r\n]/<\/br>/g;
  	print $cmd_out;
  }
  return $rv;
}

sub unzip_file{
	my $file  = $_[0];
	my $unzip_dir = $_[1];

	my $unzip_out;
	my $unzip_err;
	print "<hr>Unzipping $file to $unzip_dir ...<br>";
	local $out = &execute_command("unzip -ou \"$file\" -d \"$unzip_dir\"", undef, \$unzip_out, \$unzip_err, 0, 0);

	if($unzip_err){
		&error("Error: unzip: $unzip_err");
	}else{
		$unzip_out = s/\r\n/<br>/g;
		print &html_escape($unzip_out);
	}
	return $unzip_dir;
}
