# !/bin/bash -e
# Tomcat Module Script for CentOS and Ubuntu
# For use on clean CentOS or Ubuntu box only
# Usage:
# wget https://raw.githubusercontent.com/cited/Tomcat-Webmin-Module/master/scripts/pre-install.sh
# chmod +x pre-installer
# ./pre-installer.sh

function install_webmin(){

	echo "deb http://download.webmin.com/download/repository sarge contrib" > /etc/apt/sources.list.d/webmin.list
	wget -qO - http://www.webmin.com/jcameron-key.asc | apt-key add -
	apt-get -y update
	apt-get -y install webmin
 
 }	


function download_oci_module(){
pushd /tmp/
	wget https://github.com/cited/Oracle-Instant-Client/archive/master.zip
	unzip master.zip
	mv Oracle-Instant-Client-master oci
	tar -czf /opt/oci.wbm.gz oci
	rm -rf oci master.zip
popd
}

function install_oci_module(){
pushd /opt/
	
	/usr/share/webmin/install-module.pl oci.wbm.gz
  
popd
        echo -e "Tomcat module is now installed. Go to Servers > Tomcat to complete installation"
	
}



function download_certbot_module(){
pushd /tmp/
	wget https://github.com/cited/Certbot-Webmin-Module/archive/master.zip
	unzip master.zip
	mv Certbot-Webmin-Module-master certbot
	tar -czf /opt/certbot.wbm.gz certbot
	rm -rf certbot master.zip
popd
}

function install_apache(){
	
 		apt-get -y install apache2
	
}

function install_certbot_module(){
pushd /opt/
	
	/usr/share/webmin/install-module.pl certbot.wbm.gz
  
popd
        echo -e "Certbot is now installed. Go to Servers > Certbot to complete installation"
	
}

function get_deps(){

		apt-get -y install wget unzip
}

get_deps;
# Uncomment line(s) below if you wish to install Webmin, Apache HTTP Server, and Certbot as well.
#install_webmin;
#install_apache;
#download_certbot_module;
#install_certbot_module;
download_oci_module;
install_oci_module;
