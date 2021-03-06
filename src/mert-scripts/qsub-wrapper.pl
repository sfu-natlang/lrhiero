#! /usr/bin/perl

# $Id: qsub-wrapper.pl 1317 2007-03-16 13:20:27Z maurocettolo $
use strict;

#######################
#Default parameters 
#parameters for submiiting processes through SGE
#NOTE: group name is ws06ossmt (with 2 's') and not ws06osmt (with 1 's')
my $queueparameters="-l ws06ossmt=true -l mem_free=0.5G";

# look for the correct pwdcmd 
my $pwdcmd = getPwdCmd();

my $workingdir = `$pwdcmd`; chomp $workingdir;
my $tmpdir="$workingdir/tmp$$";
my $jobscript="$workingdir/job$$";
my $qsubout="$workingdir/out.job$$";
my $qsuberr="$workingdir/err.job$$";


$SIG{INT} = \&kill_all_and_quit; # catch exception for CTRL-C

my $help="";
my $dbg="";
my $version="";
my $qsubname="WR$$";
my $cmd="";
my $cmdout="";
my $cmderr="";
my $parameters="";
my $old_sge = 0; # assume grid engine < 6.0

sub init(){
  use Getopt::Long qw(:config pass_through);
  GetOptions('version'=>\$version,
             'help'=>\$help,
             'debug'=>\$dbg,
             'qsub-prefix=s'=> \$qsubname,
             'command=s'=> \$cmd,
             'stdout=s'=> \$cmdout,
             'stderr=s'=> \$cmderr,
             'queue-parameter=s'=> \$queueparameters,
             'old-sge' => \$old_sge,
            ) or exit(1);
  $parameters="@ARGV";
  
  version() if $version;
  usage() if $help;
  print_parameters() if $dbg;
}

#######################
##print version
sub version(){
#    print STDERR "version 1.0 (29-07-2006)\n";
    print STDERR "version 1.1 (31-07-2006)\n";
    exit(1);
}

#usage
sub usage(){
  print STDERR "qsub-wrapper.pl [options]\n";
  print STDERR "Options:\n";
  print STDERR "-command <file> command to run\n";
  print STDERR "-stdout <file> file to save stdout of cmd (optional)\n";
  print STDERR "-stderr <file> file to save stderr of cmd (optional)\n";
  print STDERR "-qsub-prefix <string> name for sumbitted jobs (optional)\n";
  print STDERR "-queue-parameters <string>  parameter for the queue (optional)\n";
  print STDERR "-old-sge ... assume Sun Grid Engine < 6.0\n";
  print STDERR "-debug debug\n";
  print STDERR "-version print version of the script\n";
  print STDERR "-help this help\n";
  exit(1);
}

#printparameters
sub print_parameters(){
  print STDERR "command: $cmd\n";
  print STDERR "file for stdout: $cmdout\n";
  print STDERR "file for stderr: $cmderr\n";
  print STDERR "Qsub name: $qsubname\n";
  print STDERR "Queue parameters: $queueparameters\n";
  print STDERR "parameters directly passed to cmd: $parameters\n";
  exit(1);
}

#script creation
sub preparing_script(){
  my $scriptheader="\#\!/bin/csh\n\n";
  $scriptheader.="uname -a\n\n";

  $scriptheader.="cd $workingdir\n\n";
    
  open (OUT, "> ${jobscript}.csh");
  print OUT $scriptheader;

  if ($cmd =~ /PRO\.py/) {
    #print OUT "source /cs/natlang-sw/etc/natlang-login\n";
    #print OUT "module load NL/LTOOLS/MEGAM/0.92\n\n"
  }
  print OUT "($cmd $parameters > $tmpdir/cmdout$$ ) >& $tmpdir/cmderr$$\n\n";
  print OUT "echo exit status \$\?\n\n";

  if ($cmdout){
    print OUT "\\mv -f $tmpdir/cmdout$$ $cmdout\n\n";
    print OUT "echo exit status \$\?\n\n";
  }
  else{
    #print OUT "\\rm -f $tmpdir/cmdout$$\n\n";
    print OUT "echo exit status \$\?\n\n";
  }

  if ($cmderr){
    print OUT "\\mv -f $tmpdir/cmderr$$ $cmderr\n\n";
    print OUT "echo exit status \$\?\n\n";
  }
  else{
    #print OUT "\\rm -f $tmpdir/cmderr$$\n\n";
    print OUT "echo exit status \$\?\n\n";
  }
  close(OUT);

  #setting permissions of each script
  chmod(oct(755),"${jobscript}.csh");
}

#######################
#Script starts here

init();

usage() if $cmd eq "";

safesystem("mkdir -p $tmpdir") or die;
#$queueparameters = "-l mem=7gb,vmem=7gb,walltime=5:00:00";
$queueparameters = "-l mem=7gb,walltime=5:00:00";
$queueparameters =~ s/__/ /;

preparing_script();

my $maysync = $old_sge ? "" : "-sync y";

# submit the main job
my $qsubcmd="qsub $queueparameters -V -o $qsubout -e $qsuberr -N $qsubname ${jobscript}.csh >& ${jobscript}.log";
#my $qsubcmd="qsub -l mem=8gb,pvmem=8gb,walltime=8:00:00 -V -o $qsubout -e $qsuberr -N $qsubname ${jobscript}.csh >& ${jobscript}.log";
safesystem($qsubcmd) or die;

#getting id of submitted job
my $res;
open (IN,"${jobscript}.log") or die "Can't read main job id: ${jobscript}.log";
chomp($res=<IN>);
split(/\./,$res);
my $id=$_[0];
close(IN);

print SDTERR " res:$res\n";
print SDTERR " id:$id\n";


# need to wait for extract to complete, add another job that will wait for the main one
# prepare a fake waiting script; use the -W depend=afterok option for qsub
my $syncscript = "${jobscript}.sync_workaround_script.sh";
safesystem("echo '/bin/ls' > $syncscript") or kill_all_and_quit();

my $checkpointfile = "${jobscript}.sync_workaround_checkpoint";
safesystem("\\rm -f $checkpointfile") or die;    # ensure checkpoint does not exist

# start the 'hold' job, i.e. the job that will wait
$cmd="qsub -l mem=200m -l walltime=00:03:00 -W depend=afterok:$id -j oe -o $checkpointfile -e /dev/null -N $qsubname.W $syncscript >& $qsubname.W.log";
safesystem($cmd) or kill_all_and_quit();

# and wait for checkpoint file to appear
my $nr=0;
while (!-e $checkpointfile) {
    sleep(60);
    $nr++;
    print STDERR "w" if $nr % 3 == 0;
}
safesystem("\\rm -f $checkpointfile $syncscript") or die();
print STDERR "End of waiting workaround.\n";

my $failure=&check_exit_status();
print STDERR "check_exit_status returned $failure\n";

&kill_all_and_quit() if $failure;

&remove_temporary_files() if !$dbg;

sub check_exit_status(){
  my $failure=0;

  print STDERR "check_exit_status of submitted job $id\n";
  open(IN,"$qsubout") or die "Can't read $qsubout";
  while (<IN>){
    $failure=1 if (/exit status 1/);
  }
  close(IN);
  return $failure;
}

sub kill_all_and_quit(){
  print STDERR "kill_all_and_quit\n";
  print STDERR "qdel $id\n";
  safesystem("qdel $id");

  print STDERR "The submitted jobs died not correctly\n";
  print STDERR "Send qdel signal to the submitted jobs\n";

  exit(1);
}

sub remove_temporary_files(){
  #removing temporary files

  unlink("${jobscript}.csh");
  unlink("${jobscript}.log");
  unlink("$qsubname.W.log");
  unlink("$qsubout");
  unlink("$qsuberr");
  rmdir("$tmpdir");
}

sub safesystem {
  print STDERR "Executing: @_\n";
  system(@_);
  if ($? == -1) {
    print STDERR "Failed to execute: @_\n  $!\n";
    exit(1);
  }
  elsif ($? & 127) {
    printf STDERR "Execution of: @_\n  died with signal %d, %s coredump\n",
      ($? & 127),  ($? & 128) ? 'with' : 'without';
    exit(1);
  }
  else {
    my $exitcode = $? >> 8;
    print STDERR "Exit code: $exitcode\n" if $exitcode;
    return ! $exitcode;
  }
}

# look for the correct pwdcmd (pwd by default, pawd if it exists)
# I assume that pwd always exists
sub getPwdCmd(){
	my $pwdcmd="pwd";
	my $a;
	chomp($a=`which pawd | head -1 | awk '{print $1}'`);
	if ($a && -e $a){	$pwdcmd=$a;	}
	return $pwdcmd;
}

