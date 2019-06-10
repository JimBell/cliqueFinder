#!/usr/bin/perl -w
use strict;

my @verticies = (50);
my @edges = (50, 150, 250, 350, 450, 550, 650, 750, 850, 950, 1050, 1150, 1225);
my @kClique = (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50);

my $fileList = "fileList_50v.txt";

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
