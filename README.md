# Oracle Instant Client

## Webmin Module for installing Oracle Instant Client

![Oracle Instant Client](docs/_static/oracle-instant-client.png)

# About

Installs Oracle Instant Client Basic, jdbc, odbc, sdk, sqlplus, and tools packages


# Supported Operating Systems

Ubuntu 22

Rocky Linux 9

Alma Linux 9

# Install via Webmin

Webmin->Webmin Configuration->Webmin Modules->From ftp or http URL

URL: http://github.com/cited/Oracle-Instant-Client/raw/master/scripts/Oracle-Instant-Client.wbm.gz

Go to Servers->Apache Tomcat to complete set up using the setup Wizard (you may need to refresh page).

# Install via Script

Ubuntu (as root):

```bash
wget https://raw.githubusercontent.com/cited/Oracle-Instant-Client/master/scripts/ubuntu.sh
chmod +x pre-install.sh
./pre-install.sh
```

Rocky Linux or Alma Linux (as root):

```bash
wget https://raw.githubusercontent.com/cited/Oracle-Instant-Client/master/scripts/alma-rocky.sh
chmod +x pre-install.sh
./pre-install.sh
```

Go to Servers->Apache Tomcat to complete set up using the setup Wizard.

# Install via GIT

As Root:

```bash
git clone https://github.com/cited/Oracle-Instant-Client
mv Oracle-Instant-Client oci
tar -cvzf oci.wbm.gz oci/
```

Upload from Webmin->Webmin Configuration->Webmin Modules

Go to Servers->Oracle Instant Client (you may need to refresh page)

## **Issues**
Please report issue here

# Screen Shots

![Oracle Instant Client](docs/_static/6.png)

# SQLPlus Connection via Webmin Terminal

![Oracle Instant Client](docs/_static/9.png)



Copyright
---------

* Copyright AcuGIS, 2023
* Copyright Cited, Inc., 2023


