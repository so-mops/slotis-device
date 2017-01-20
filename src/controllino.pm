#! /usr/bin/perl -w

###########################################################
# This perl module is to interact with the 
# superlotis controllino module which controls
# the superlotis pullizi's and reads the rainbit. 
# It uses ng style syntax to communicate. 

# Scott Swindell 1/19/2017.
##########################################################

package controllino;
use strict;
use warnings;
use Net::Telnet;
use Exporter;

our @ISA = qw(Exporter);
our @EXPORT_OK=qw(isRaining CmdPlz ReqPlz);

######################################################
#Subroutine converse
#Args: $comd_str->string to send to remote host
#	$ip -> address of remote host
#	$port -> port of remote host
#Description:
#	send an NG style command to the remote
#	host and return the reply all over
#	a tcp socket.
#
#
##########################
sub converse
{
	my( $cmd_str, $ip, $port ) = @_;
	my $sock = undef;
	my $resp;

	if ( not defined $ip )
	{
		$ip = '140.252.86.98' ;
	}
	if (not defined $port)
	{
		$port =5750;
	}
	$port = 5750 unless $port;
	if( not $cmd_str )
	{
		return -1;
	}
        $sock = Net::Telnet->new (
                                Host            => "140.252.86.98",
                                Port            => 5750,
                                Errmode         => "return",
                                Timeout         => 0.5,
                                Binmode         => 1,
                                Telnetmode      => 0
                           );
        #bad socket
	#return $cmd_str;
        return ( -1, ()) unless $sock;
	$sock->put( $cmd_str );
	$sock->recv( $resp, 1024 );
	chomp $resp;
	return $resp;




}

#####################################################
#Subroutine request
#Args: $args -> request arguments to send to converse
#	$refnum -> optional refnum to to attach to 
#		ng style request
#Description:
#	Send a request to the remote host via 
#	converse and return the response.
#
#
#
####################################################
sub request
{
	my( $args, $refnum ) = @_;
	
	if (not defined $refnum) 
	{
		$refnum = 123;
	}

	my $outstr = sprintf( "SLOTIS CONTROLLINO1 %i REQUEST %s\n", $refnum, $args );

	return converse( $outstr );
}

#####################################################
#Subroutine command
#Args: $args -> command arguments to send to converse
#	$refnum -> optional refnum to to attach to 
#		ng style request
#Description:
#	Send a command to the remote host via 
#	converse and return the response.
#
#
#
####################################################

sub command
{
	my( $args, $refnum ) = @_;
	if (not defined $refnum) 
	{
		$refnum = 123;
	}
	my $outstr = sprintf( "SLOTIS CONTROLLINO1 %i COMMAND %s\n", $refnum, $args );
	return converse( $outstr );
}


##################################################
# Subroutine isRaining
# args: None
# Description:
# 	reads the rainbit from the controllino
#	and returns a 1 if it is raining and
#	0 if it is not raining
#
#
##################################################
sub isRaining
{
	my $resp = request("RAIN_BIT");
	if ( $resp == 1 )
	{
		return 0;
	}
	else 
	{
		return 1;
	}
}


##################################################
# Subroutine CmdPlz
# args: $plz_num-> pullizi number (1-4)
#	$state-> 0 for turn off and 1 for turn on
# Description:
#	Turns the pullizi power outlets 1-4 on or off
#	and returns the response of the command
#
##################################################
sub CmdPlz
{
	my( $plz_num, $state ) = @_;
	my $str_state;
	if (not defined $plz_num || not defined $state )
	{
		print "Not enough arguments, need plz_num and state";
		return -1;
	}
	if($state == 1) 
	{
		$str_state = "ON";
	}
	else
	{
		$str_state = "OFF";
	}
	my $cmd = sprintf( "PLZ %i %s", $plz_num, $str_state );
	return command( $cmd  );
}


##################################################
# Subroutine ReqPlz
# args: $plz_num-> pullizi number (1-4)
# Description:
#	Returns the state 0 for off and 1 for on
#	of the plz_num
#
##################################################

sub ReqPlz
{
	my( $plz_num ) = @_;
	if ( not defined $plz_num )
	{
		print "Not enough arguments, need plz_num and state";
		return -1;
	}

	my $req = sprintf( "PLZ %i STAT", $plz_num ); 
	return request( $req );
}

