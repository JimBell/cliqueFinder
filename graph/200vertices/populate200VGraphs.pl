#!/usr/bin/perl -w
use strict;

my @verticies = (200);
my @edges = (200, 3200, 6200, 9200, 12200, 15200, 18200);

my @kClique;
for (my $itr = 4; $itr < 201; $itr++) {
    push(@kClique,$itr);
}

my $fileList = "fileList_200v.txt";

open(FLST,">$fileList") or die "failed to open $fileList for writing\n";
for my $vert (@verticies) {
    for my $edge (@edges) {
	for my $kc (@kClique) {
	    my $cmd = "python ../../graphGenerator.py $vert $edge $kc";
	    my $out = `$cmd`;
	    chomp($out);
	    unless ($out =~ "Error") {
		print $out . "\n";
		print FLST $out . "\n";
	    }
	}
    }
}
close(FLST);
