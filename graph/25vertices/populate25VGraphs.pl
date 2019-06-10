#!/usr/bin/perl -w
use strict;

my @verticies = (25);
my @edges = (50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575);
my @kClique = (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25);

my $fileList = "fileList_25v.txt";

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
