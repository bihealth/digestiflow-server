#!/usr/bin/env bash

echo "***********************************************"
echo "Apt-get update"
echo "***********************************************"
apt-get -y update

echo "***********************************************"
echo "Installing OS dependencies"
echo "***********************************************"
apt-get -y install apt-utils
apt-get -y install build-essential
apt-get -y install supervisor

echo "***********************************************"
echo "Installing translation requirements"
echo "***********************************************"
apt-get -y install gettext

echo "***********************************************"
echo "Installing django-extensions dependencies"
echo "***********************************************"
apt-get -y install graphviz-dev

echo "***********************************************"
echo "Installing LDAP/AD dependencies"
echo "***********************************************"
apt-get -y install libsasl2-dev
apt-get -y install libldap2-dev
