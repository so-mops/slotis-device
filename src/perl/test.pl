#!/usr/bin/perl -w

use strict;
use warnings;
# use Tk;
# use Math::Trig;
#use RRDs;
use roof qw( OPEN CLOSE STOP getInputs isSafe );
use Net::Telnet;
use Data::Dumper qw(Dumper);
use status_client qw(ALL GET SET);
use slotis_email qw(send);
use DateTime;
use DateTime::Format::ISO8601;

sub test_roof
{
	my ($test_what) = @_;
	if ($test_what eq "open")
	{
		roof::OPEN();
	}
	elsif ($test_what eq "close")
	{

		roof::CLOSE();
	}
	elsif ($test_what eq "stop")
	{
		roof::STOP();
	}
	elsif ($test_what eq "getInputs")
	{
		my ($success, %status) = roof::getInputs;
		print "Closed: ".$status{"closeSwitch"}."\n";
		print "Opened: ".$status{"openSwitch"}."\n";
	}
	elsif ($test_what eq "isSafe")
	{
		if( roof::isSafe() )
		{
			print "Roof is safe"."\n";
		}
		else
		{
			print "Roof is not safe"."\n";
		}
	}

	else
	{
		print "roof test options are `open`, `close`, `stop` or `getInputs`\n";
		
	}
	
}


sub test_status_client
{
	my ($test_what, $var1, $var2) = @_;
	#print "args are $test_what $var1 $var2\n";
	if ($test_what eq "GET")
	{
		if( ! defined $var1)
		{
			print "Which value to get?\n";
		}
		else
		{
			my $resp = status_client::GET($var1);
			print $var1." is ".$resp."\n";
		}

	}
	elsif ($test_what eq "SET")
	{
		if( ! defined $var1)
		{
			print "Which value to SET?\n";
		}
		elsif( ! defined $var2 )
		{
			print "What value to set it to?\n";
		}
		else
		{
			print "Attempting to set $var1 to $var2\n";
			status_client::SET( $var1, $var2 );
		}
	}
	elsif( $test_what eq "ALL" )
	{
		my $status_hash;
		$status_hash = status_client::ALL();
		print Dumper $status_hash;
		foreach my $key ( keys %{ $status_hash } )
		{
			my $val = $status_hash->{$key};
			print "$key is $val\n";
		}
	}

	else
	{
		print "your choices for status are GET SET and ALL\n";
	}

}


sub test_set_multi
{
	my %set_hash = ("test1" => "foobar", "galil_roofshut_status" => 1, "test2"=> "another test");

	status_client::SET(\%set_hash);
}


my $usage = "This program is used to test the perl modules in this repository. \n Usage: test.pl <module> <subprocess>\n like: test.pl roof open\n";

if ( scalar(@ARGV) lt 2 )
{
	print $usage;
	exit;
}


if( $ARGV[0] eq "roof" )
{
	test_roof( $ARGV[1] );
}


elsif( $ARGV[0] eq "status_client" )
{
	if ($ARGV[1] eq "multi")
	{
		test_set_multi();
	}
	else
	{
		my @args = @ARGV;
		splice @args, 0,1;
		test_status_client( @args  );
	}
}

elsif( $ARGV[0] eq "email" )
{
	slotis_email::send("trsl\@as.arizona.edu", "test", "PREPARE TO BE SPAMMED \n --Scott Swindell" );
}

elsif( $ARGV[0] eq "time" )
{
	my $dt = DateTime->now;
	if( $ARGV[1] eq "safe")
	{
		
		status_client::SET( "safe_for_30", $dt->strftime( '%Y-%m-%d-%H-%M-%S' ) );
	}
	else
	{
		my $unsafe_delay = status_client::GET( "safe_for_30" );
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
		print $dur->in_units("minutes");
		
	}
	
}

else
{
	print "your choices are roof or status_client\n";
}










