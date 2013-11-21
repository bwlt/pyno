#!/usr/bin/perl
#
#  installer: an installer for pyno
#
#  Copyright 2013 Mauro Ghedin
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
# @author Mauro Ghedin
# @contact domyno88 at gmail dot com
# @version 0.1

use warnings;
use strict;

print "\nInstaller and configurator for fbcmd and pyno\n";
print "-" x 75 . "\n\n";

# Check of fbcmd and php if exist
my $fbcmdPATH	= "/usr/bin/fbcmd";
my $phpPATH		= "/usr/bin/php";

if ( !-e $fbcmdPATH ){
	die "No \'$fbcmdPATH\' found. Install fbcmd first\n\n";
}
if ( !-e $phpPATH ){
	die "No \"$phpPATH\' found. Install PHP first\n\n";
}

# Check php setting
print "Testing php\n";
print "-" x 75 . "\n\n";

my $phpTest		= "ini_get(\'allow_url_fopen\')";
print $phpTest."\t\t: ";
system("php -r \"echo ".$phpTest.";\" > /dev/null 2>&1") == 0 ? print "OK\n" : die "NOT OK\n";

$phpTest		= "function_exists(\'curl_init\')";
print $phpTest."\t\t: ";
system("php -r \"echo ".$phpTest.";\" > /dev/null 2>&1") == 0 ? print "OK\n" : die "NOT OK\n";

$phpTest		= "function_exists(\'json_decode\')";
print $phpTest."\t\t: ";
system("php -r \"echo ".$phpTest.";\" > /dev/null 2>&1") == 0 ? print "OK\n" : die "NOT OK\n";

# Download of fbcmd_update.php
print "\n\nDownloading of fbcmd_update.php\n";
print "-" x 75 . "\n\n";

system("rm fbcmd_update.php") if -e "./fbcmd_update.php";											#	delete 'old' php file

my $wgetXtCode	= system("wget https://raw.github.com/dtompkins/fbcmd/master/fbcmd_update.php");	#	download new php file

die "Unable to download fbcmd_update.php\n\n" 	if $wgetXtCode;
die "Unable to locate fbcmd_update.php\n\n" 	if !-e "./fbcmd_update.php";

# Start php 'scritp'
print "Start \"php fbcmd_update.php\"\n";
system("php fbcmd_update.php");
print "\n\nStart \"sudo hp fbcmd_update.php sudo\"\n";
system("sudo php fbcmd_update.php sudo");

# Test fbcmd
print "\n\nTest of fbcmd\n";
system("fbcmd") ? die "Error on fbcmd\n" : print "\nfbcmd test OK\n";

# Basic access
print "\nGet basic access\t: ";
system("fbcmd go access") ? die "Error on fbcmd\n" : print "fbcmd access OK\n";

print "\nHave you see a webpage with SUCCESS message [y\\n]? ";
while ( my $retVal = <STDIN> ) {
	chomp $retVal;
	lc $retVal eq "n" ? die "Oh shit!!!!!\n" : ( lc $retVal eq "y" ? last : print "Type Y or N\n" );
}

# fbcmd obtain authorization code
print "\nObtain authorization code\n";
system("fbcmd go auth") ? die "Error on fbcmd\n" : print "Type autorization code: ";
my $authCode;
while ( $authCode = <STDIN> ){
	chomp $authCode;
	last if $authCode ne "";
	print "Enter valid code: ";
}

system("fbcmd auth ".$authCode) ? die "Error on fbcmd\n" : print "Type autorization code: ";


# Obtain addition authorization
system("fbcmd addperm") ? die "Error on fbcmd\n" : print "\nAdditional authorization obtained\n";


# Test autorization
system("fbcmd test") ? die "Error on fbcmd\n" : print "\nText cmd start sucesfully\n";

print "-" x 75 . "\n\n";

print "FBCMD CONFIGURATION COMPLETED\n\n";

print "-" x 75 . "\n\n";

print "Starting pyno...\n\n";

-e "./pyno.py" ? system("./pyno.py > /dev/null 2>&1 &") : die "pyno.py not found";
