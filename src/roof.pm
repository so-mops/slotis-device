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


our @EXPORT_OK = qw( OPEN CLOSE STOP getInputs );

# This is the HTTP format string to send
# an open close or stop command to the
# cbw roof.
my $comFormatStr = "GET /state.xml?%sState=%i HTTP/1.1\nAuthorization: Basic bm9uZTp3ZWJyZWxheQ==\r\n\r\n";

# This is the HTTP string to querry the state of the cbw. 
my $querryStr =  "GET /state.xml HTTP/1.1\nAuthorization: Basic bm9uZTp3ZWJyZWxheQ==\r\n\r\n";

#cbw ip address
my $cbw_host = "140.252.86.97";

# cbw port. Might be good 
# to change thsi for 
# security
my $cbw_port = 80;


my $resp;
my $HTTP;

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
	my $sock = undef;
	$sock = Net::Telnet->new (
				Host 		=> $cbw_host,
                            	Port 		=> $cbw_port,
                            	Errmode 	=> "return",
                            	Timeout 	=> 1,
                            	Binmode 	=> 1,
                            	Telnetmode 	=> 0
                           );
        #bad socet
	return ( 0 , ()) unless $sock;

	$HTTP = sprintf( $comFormatStr, $openRelay, $state );
	$sock->put( $HTTP );
	$sock->recv( $resp, 1024 );

	
	close( $sock );
	return ( 1, inputsFromXML( $resp ) );
}

########################################################
# Name: close
# Args: N/A
# Returns: a list the first element is the success state
#      the second is a hash of limit switch values
# Description:
# Interfaces with cbw module to close the superlotis roof
# it then reads the xml string returned by the cbw socket
# Author: Scott Swindell
# Date:   8/15/2014
#######################################################
sub CLOSE()
{
        my $sock = undef;
        $sock = Net::Telnet->new (
                                Host            => $cbw_host,
                                Port            => $cbw_port,
                                Errmode         => "return",
                                Timeout         => 1,
                                Binmode         => 1,
                                Telnetmode      => 0
                           );
        return ( 0, () ) unless $sock;

        $HTTP = sprintf( $comFormatStr, $closeRelay, $state );
        $sock->put( $HTTP );
        $sock->recv( $resp, 1024 );


        close( $sock );
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
        my $sock = undef;
        $sock = Net::Telnet->new (
                                Host            => $cbw_host,
                                Port            => $cbw_port,
                                Errmode         => "return",
                                Timeout         => 1,
                                Binmode         => 1,
                                Telnetmode      => 0
                           );
        return ( 0, () ) unless $sock;

        $HTTP = sprintf( $comFormatStr, $stopRelay, $state );
        $sock->put( $HTTP );
        $sock->recv( $resp, 1024 );


        close( $sock );
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

	return ("closeSwitch" => $closeSwitch, "openSwitch" => $openSwitch );
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
my $sock = undef;
        $sock = Net::Telnet->new (
                                Host            => $cbw_host,
                                Port            => $cbw_port,
                                Errmode         => "return",
                                Timeout         => 1,
                                Binmode         => 1,
                                Telnetmode      => 0
                           );
        return (0, ("closeSwitch"=>-1 , "openSwitch"=>-1) ) unless $sock;
	$HTTP = $querryStr;
	$sock->put( $HTTP );
	$sock->recv( $resp, 1024 );
	return ( 1, inputsFromXML( $resp ) ) ;
}




 
