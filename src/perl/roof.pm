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

our @EXPORT_OK = qw( OPEN CLOSE STOP getInputs isSafe );

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
		printf("not opening because ops_safe_to_open says %f\n", $safety);
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
	
	#Close the roof and get a response
	my $resp = $httpConnection->get($URL)->content;

	
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
	my $httpConnection = LWP::UserAgent->new;

	$httpConnection ->credentials(
	    $cbw_host.":".$cbw_port,
	    $cbw_realm,
	    $cbw_user => $cbw_pass 
	  );
	
	my $resp = $httpConnection->get($urlGetState)->content;
       
	return ( 1, inputsFromXML( $resp ) ) ;
	
}



1;



# The SLOTIS status socket server.                     
my $slotis_status_server_host = "slotis.kpno.noao.edu";
my $slotis_status_server_port = 5135;                  
                                                       

# Sends the status information to the status server.             
sub isSafe{                                       
                                                                 
  # The command to set a value in the status server.             
  my $cmd = "";       
  my $val = "-1.0"; 
  my $key = "-1.0";                                          
  # Connect to the status socket server.                         
  my $sock = Net::Telnet->new (Host => $slotis_status_server_host,  
                            Port =>  $slotis_status_server_port, 
                            Errmode => "return",                 
                            Timeout => 1,                        
                            Binmode => 1,                        
                            Telnetmode => 0                      
                           );                                    

	my $resp = 0.0;
	if ( $sock ) {
		$cmd = "get ops_safe_to_open\n";                     
		my $rtn_status = $sock->put($cmd) if length($cmd) > 0;     
		# put() returns 1 if all data was successfully written.    
		# print $cmd if $debug;                                    
		print "Error writing to status server\n" unless $rtn_status; 
		# Returning the .EOF                                       
		my $line = $sock->getline();
		($key, $val) = split / /, $line;
		
	}                                                            
	$sock->close() if $sock;                                       
	undef($sock);                                                  
	return $val;
}
