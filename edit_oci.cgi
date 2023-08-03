#!/usr/bin/perl

require './oci-lib.pl';

&ReadParse();
&ui_print_header(undef, $text{'oci_title'}, "");

my @oci_vers = get_oci_versions();
my $page_number = pop @oci_vers;
my %pkgs = ('basic'=>1, 'jdbc'=>1, 'sqlplus'=>0, 'sdk'=>1, 'odbc'=>1, 'tools'=>0);

print &ui_form_start("install_oci.cgi", "form-data");

print &ui_hidden('page_number', $page_number);
print &ui_table_start($text{'oci_install'}, undef, 2);

print &ui_table_row($text{'oci_version'}, &ui_select("oci_ver", undef, \@oci_vers, 1, 0));

my $pkg_checks='';
foreach my $name (sort keys %pkgs){
	$pkg_checks .= &ui_checkbox('pkg_'.$name, 1, $name, $pkgs{$name});
}
print &ui_table_row($text{'oci_packages'}, $pkg_checks, 2);

print &ui_table_end();

print &ui_form_end([ [ "", $text{'install_button'} ] ]);

&ui_print_footer("", $text{'index_return'});
