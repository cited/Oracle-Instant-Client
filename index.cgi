#!/usr/bin/perl

require './oci-lib.pl';
require '../webmin/webmin-lib.pl';	#for OS detection

# Check if config file exists
if (! -r $config{'oci_config'}) {
	&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1);
	print &text('index_econfig', "<tt>$config{'oci_config'}</tt>",
		    "$gconfig{'webprefix'}/config.cgi?$module_name"),"<p>\n";
	&ui_print_footer("/", $text{"index"});
	exit;
}

if(-f "$module_root_directory/setup.cgi"){
	&redirect("setup.cgi?mode=checks");
	exit;
}

my %version = get_versions();

&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1, 0,
	&help_search_link("oracle", "oci", "php", "google"), undef, undef,
	"InstantClient $version{'oci'} / PHP $version{'php'}");

push(@links, "php_install.cgi");
push(@titles, $text{'php_title'});
push(@icons, "images/php.png");

push(@links, "edit_oci.cgi");
push(@titles, $text{'oci_title'});
push(@icons, "images/oci.png");

&icons_table(\@links, \@titles, \@icons, 3);

&ui_print_footer("/", $text{"index"});
