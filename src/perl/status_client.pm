package status_client;
use warnings;
use Net::Telnet;
use Exporter qw(import);
use strict;
use Data::Dumper qw(Dumper);
use Socket;
use IO::Socket;
our @EXPORT_OK = qw( ALL GET SET);




################################################
# ALL
# Description:
# Return a hash of the key value pairs in the 
# slotis_status_server
#
#
#
#
#
#
#
#################################################


sub ALL()
{
	# initialize host and port
	my $host = shift || 'localhost';
	my $port = shift || 5135;
	my $server = "localhost";  # Host IP running the server

	# create the socket, connect to the port
	my $sock = socket(SOCKET,PF_INET,SOCK_STREAM,(getprotobyname('tcp'))[2])
	   or die "Can't create a socket $!\n";
	connect( SOCKET, pack_sockaddr_in($port, inet_aton($server)))
	   or die "Can't connect to port $port! \n";
	
	send(SOCKET, "all\n", 0);
	my $line;
	my %data;
	my @list;
	while ($line = <SOCKET>) 
	{
		chomp($line);
		print "\n";
		if ( $line eq ".EOF")
		{
			last;
		}
		else
		{
			my @list = split / /, $line, 2;
			my ($key, $val) = @list;
			$data{$key} = $val;
		}
	}
	close SOCKET or die "close: $!";

	return \%data;
}

sub GET
{
	my ($keyword) = @_;
	# initialize host and port
	my $host = 'localhost';
	my $port = 5135;
	my $server = "localhost";  # Host IP running the server

	# create the socket, connect to the port
	my $sock = new IO::Socket::INET (
		PeerAddr => $host,
		PeerPort => $port,
		Proto => 'tcp',
		Timeout => 1.0
	);
	die unless $sock;

	
	$sock->send("get $keyword\n");

	my $keyval;
	$sock->recv($keyval, 100);
	chomp($keyval);
	my ($key, $val) = split / /, $keyval,  2;
	$sock->close();
	return $val

}

sub SET
{
	my ($keyword_or_hash, $value) = @_;
	# initialize host and port
	my $host = 'localhost';
	my $port = 5135;
	my $server = "localhost";  # Host IP running the server

	# create the socket, connect to the port
	my $sock = new IO::Socket::INET (
		PeerAddr => $host,
		PeerPort => $port,
		Proto => 'tcp',
		Timeout => 1.0
	);
	die unless $sock;
	
	if( ref($keyword_or_hash) eq "HASH" )
	{
		foreach my $key ( keys %{$keyword_or_hash})
		{
			my $value = $keyword_or_hash->{$key};
			$sock->send("set $key $value\n");
		}
	}
	else
	{
		$sock->send("set $keyword_or_hash $value\n");
	}
	#$sock->send("get $keyword $value\n");
	#my $keyval;
	#$sock->recv($keyval, 50);
	#chomp($keyval);
	#my ($key, $val) = split / /, $keyval,  2;
	$sock->close();
	#return $val

}
