#! /usr/bin/perl -w

###########################################################
# This perl module is to interact with the 
# superlotis controlbyweb (cbw) module which controls
# the superlotis roof. With the exception of the
# slotis webpage all roof commands should come through
# here. 

# The slotis webpage currently uses a python
# cgi script (/usr/lib/cgi-bin) to control the roof. 
# If there is time I will change that to a perl script 
# that uses this module

# Scott Swindell 8/15/2014.
##########################################################

package roof;
use strict;
use warnings;
use Net::Telnet;
use Exporter qw(import);
use LWP::UserAgent;
use Data::Dumper qw(Dumper);
use status_client qw(GET);
use Scalar::Util qw(looks_like_number);
our @EXPORT_OK = qw( OPEN CLOSE STOP getInputs isSafe );
use DateTime;


# This is the HTTP format string to send
# an open close or stop command to the
# cbw roof.


my $cbw_host = "140.252.86.97";
my $cbw_realm = "secure_control"; # realm of the stuff behind HTTP Auth Basic
my $cbw_user = "admin";
my $cbw_pass = "mtops";

my $urlFormatStr = "http://".$cbw_host."/state.xml?%sState=%i";
my $urlGetState = "http://".$cbw_host."/state.xml";


#cbw ip address

# cbw port. Might be good 
# to change this for 
# security
my $cbw_port = 80;


my $resp;

my $openRelay  = "relay1";
my $closeRelay = "relay2";
my $stopRelay  = "relay3";



# On the cbw, State=2 pulses the relay,
# State=1 turns the relay on,
# State=0 turns the relay off.
# For our purposes we should only
# use a pulse.
my $state = 2;


# I probably should have put the socket stuff all in its
# own function but alas I did not. -Scott Swindell

########################################################
# Name: open
# Args:	N/A
# Returns: a list the first element is the success state
#      the second is a hash of limit switch values
# Description:
# Interfaces with cbw module to open the superlotis roof
# Author: Scott Swindell
# Date:	  8/15/2014
#######################################################
sub OPEN()
{
	my $safety = isSafe();
	if ( isSafe()  == 0.0 )
	{
		printf("Not opening because roof not safe says %f\n", $safety);
		return -1;
	}
	my $httpConnection = LWP::UserAgent->new;

	$httpConnection ->credentials(
	    $cbw_host.":".$cbw_port,
	    $cbw_realm,
	    $cbw_user => $cbw_pass 
	  );


	#build the URL string to open the roof.
        my $URL = sprintf( $urlFormatStr, $openRelay, $state );
	
	#open the roof and get a response
	my $resp = $httpConnection->get($URL)->content;

	print $URL."\n";
	print $resp."\n";
        return (0, ("closeSwitch"=>-1 , "openSwitch"=>-1) ) unless $resp;

	#return the parsed response
	return ( 1, inputsFromXML( $resp ) );
}

########################################################
# Name: close
# Args: N/A
# Returns: a list the first element is the success state
#      the second is a hash of limit switch values
# Description:
# Interfaces with cbw module to close the superlotis roof
# it then reads the xml string returned by the cbw HTTP
# connection
# Author: Scott Swindell
# Date:   8/15/2014
#######################################################
sub CLOSE()
{
	my $httpConnection = LWP::UserAgent->new;

	$httpConnection ->credentials(
	    $cbw_host.":".$cbw_port,
	    $cbw_realm,
	    $cbw_user => $cbw_pass 
	  );


	#build the URL string to clsoe the roof.
        my $URL = sprintf( $urlFormatStr, $closeRelay, $state );
	
	#Close the roof and get a response
	my $resp = $httpConnection->get($URL)->content;

	
        return (0, ("closeSwitch"=>-1 , "openSwitch"=>-1) ) unless $resp;

	#return the parsed response
	return ( 1, inputsFromXML( $resp ) );


}	



########################################################
# Name: stop
# Args: N/A
# Returns: a list the first element is the success state
#      the second is a hash of limit switch values
# Description:
# Interfaces with cbw module to stop the superlotis roof
# it then reads the xml string returned by the cbw socket
# Author: Scott Swindell
# Date:   8/15/2014
#######################################################
sub STOP()
{
	my $httpConnection = LWP::UserAgent->new;

	$httpConnection ->credentials(
	    $cbw_host.":".$cbw_port,
	    $cbw_realm,
	    $cbw_user => $cbw_pass 
	  );


	#build the URL string to stop the roof.
        my $URL = sprintf( $urlFormatStr, $stopRelay, $state );
	my $resp;
	#Close the roof and get a response
	#my $resp = $httpConnection->get($URL)->content;

	
        return (0, ("closeSwitch"=>-1 , "openSwitch"=>-1) ) unless $resp;

	#return the parsed response
	return ( 1, inputsFromXML( $resp ) );



}




#####################################################
# Name:	inputsFromXML
# Args: $XML 
# Returns: a hash of closeSwitch and openSwitch values
# Decscription: 
# Takes in the cbw XML string as an arg and extracts
# the input1state and input2state values then it 
# populates the hash to be returned.
# Author: Scott Swindell
# Date:	  8/15/2014
#####################################################
sub inputsFromXML
{
	my ($XML) = @_;
	my ( $openSwitch, $closeSwitch ) = ( $XML =~ /<datavalues>.*<input1state>(\d)<\/input1state>.*<input2state>(\d)<\/input2state>.*<\/datavalues>/ );
	
	#logic is reversed 
	#$closeSwitch = $closeSwitch ^ 1;
	#$openSwitch = $openSwitch ^ 1;
	my %resp_hash = ( closeSwitch => $closeSwitch, openSwitch => $openSwitch );
	return %resp_hash;
}


#####################################################
# Name: getInputs
# Args: N/A
# Returns: a hash of closeSwitch and openSwitch values
# Decscription: 
# Takes in the cbw XML string as an arg and extracts
# the input1state and input2state values then it 
# populates the hash to be returned.
# Author: Scott Swindell
# Date:   8/15/2014
#####################################################
sub getInputs
{
	my $httpConnection = LWP::UserAgent->new;

	$httpConnection ->credentials(
	    $cbw_host.":".$cbw_port,
	    $cbw_realm,
	    $cbw_user => $cbw_pass 
	  );
	
	my $resp = $httpConnection->get($urlGetState)->content;
       
	return ( 1, inputsFromXML( $resp ) ) ;
	
}

sub safe_by_key
{
	my ($safe_key) = @_;
        my $safe = status_client::GET($safe_key);
        if ( looks_like_number($safe) )
	{
		if( $safe == 1 )
		{
			return 1.0;
		}
		else
		{
			return 0.0;
		}
	}
	else
	{
		#Its not a number
		return 1.0;
	}
}


sub isSafeFor30
{
	#check the safety suppressor that expires in 30 mins	
	my $unsafe_delay = status_client::GET( "safe_for_30" );
	if ( $unsafe_delay eq "" )
	{
		return 0;
	}
	my $dt = DateTime->now;
	my @list = split("-", $unsafe_delay);
	my $unsafe_time = DateTime->new(
		year		=>$list[0],
		month		=>$list[1], 
		day		=>$list[2],
		hour		=>$list[3], 
		minute		=>$list[4], 
		second		=>$list[5], 
		nanosecond	=>0
	);
	my $dur = $dt-$unsafe_time;
	#return true if the safe_for_30 timestamp is less than 30 minutes old
	return ( $dur->in_units("minutes") <30 );

}

sub isSafe
{
#	if( isSafeFor30() )
#	{
#		return 1;
#	}
	if( !safe_by_key("ops_safe_to_open") || !safe_by_key("safe_to_reopen") || !safe_by_key("scott_safe_to_open") )
	{
		return 0;
	}
	else
	{
		return 1;
	}
}




                                                       



